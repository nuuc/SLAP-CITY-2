from typing import *
from shapely.geometry import *
UNIV_LANDING_LAG = 2


class Character:
    """
    An abstract representation of a Super Slam Brothers: Jam character.
    """
    action_state: Dict
    env_state: str
    hitboxes: Dict
    hurtbox: Polygon
    ECB: List[Tuple]
    internal_data: Dict

    def __init__(self) -> None:
        # Some of these class attributes are not well fleshed out, and we will
        # have to come back to them and complete them (like internal_data and ECB)
        # Below the initializer are a collection of helper methods that are rather
        # self-explanatory, up to update.
        """
        TODO: Complete class attributes
        - internal_data: The internal_data dictionary is far from complete,
        but with how it's implemented, we can come back to add to it or change
        it whenever we want.

         - hitboxes: I hope to finish the structure of hitboxes soon because
         hitboxes are a core part of the game and we have to provide a solid
         foundation for how hitboxes are done. We will discuss this ASAP.

         - ECB: To be honest, I'm not quite sure how to implement ECB, but I
         think where we begin is deciding what exactly ECB will do for us. For
         example, do we want an ECB that can handle sloped floors? Do we want
         an ECB that can replicate a diamond with sides such that it the
         environment pushes the sides away?"""
        self.action_state = {'action': 'rebirth', 'frame': 0}
        self.env_state = 'rebirth'
        self.hitboxes = {'reg': {}, 'proj': [], 'grab': {}}
        self.internal_data = {'pos': (500, 500),
                              'damage': 0,
                              'speed': (0, 0),
                              'shield_health': 86,
                              'invincibility': 30,
                              'waveland': False,
                              'landing_lag': UNIV_LANDING_LAG,
                              'jumped': False,
                              'tech_valid': False,
                              'tech_cd': 0}
        self.ECB = []
        self.traits = {}

    def get_act_state(self, index: str) -> Union[str, int]:
        return self.action_state[index]

    def modify_act_state(self, index: str, value: Union[str, int]) -> None:
        self.action_state[index] = value

    def get_int_data(self, index: str) -> Union[str, int, bool, Tuple]:
        return self.internal_data[index]

    def modify_int_data(self, index: str, value: Union[str, int, bool, Tuple]) \
            -> None:
        self.internal_data[index] = value

    def damaged(self, damage: int) -> None:
        current_damage = self.get_int_data('damage')
        new_damage = current_damage + damage
        self.modify_int_data('damage', new_damage)

    def get_speed(self, component:Union[str, bool] = False) -> Union[Tuple, float]:
        if not component:
            return self.get_int_data('speed')
        elif component == 'x':
            return self.get_speed()[0]
        elif component == 'y':
            return self.get_speed()[1]

    def modify_speed(self, speed: Tuple) -> None:
        self.modify_int_data('speed', speed)

    def increment_speed(self, speed: Tuple) -> None:
        current_speed = self.get_speed()
        new_speed = (current_speed[0] + speed[0], current_speed[1] + speed[0])
        self.modify_int_data('speed', new_speed)

    def get_pos(self, component: Union[str, bool] = False) -> Tuple:
        if not component:
            return self.get_int_data('pos')
        elif component == 'x':
            return self.get_pos()[0]
        elif component == 'y':
            return self.get_pos()[1]

    def modify_pos(self, pos: Tuple) -> None:
        self.modify_int_data('pos', pos)

    def increment_pos(self, pos_inc: Tuple) -> None:
        current_pos = self.get_pos()
        new_pos = (current_pos[0] + pos_inc[0], current_pos[1] + pos_inc[1])
        self.modify_int_data('pos', new_pos)

    def update_pos(self) -> None:
        self.increment_pos(self.get_speed())

    def update(self) -> None:
        # We will definitely have to talk about the specifics of update.
        """
        TODO: Talk about update steps and update order.
        Additionally, in the previous version of the code, I had enlisted the
        help of many helper methods in Character to make the update less messy,
        but what ended up happening was that it made Character a lot more messy.
        What I'm thinking about doing this time is defining nested functions in
        here to be called in certain events.

        List of things to update (in no particular order):
        - Invincibility timer/invincibility status
        - Tech-availability status
        - Standard and character specific projectiles
        - Shield health
        - Hitlag status and ASDI inputs
        - Environmental state grounded:
            - All of the possible action states while grounded
            - Grounded attacks (not a separate case, but a special case)
        - Environmental state airborne:
            - All of the possible action states while airborne
        - Environmental state ledge:
            - ...
        - Hitbox/hurtbox updater (tentative: this will very likely be called
        right after the environmental handler finishes. The reason is explained
        in the following section)

        Needless to say, update order is very important and must take careful
        thought and consideration. Right now, I can't think of any reason why
        the current order should be changed, except the hitbox/hurtbox update.
        The reason it may make more sense to call it after the environmental
        handler runs is to reduce redundancy. For example, imagine a character
        is in the middle of an aerial attack on frame X. On this frame, the
        hitbox/hurtbox updater is called, but then the environmental handler
        detects that the character has landed and would have to go through
        another update to remove the aerial hitboxes and update the hurtboxes
        to being grounded.

        To be honest, this is a relatively small detail, and if we organize
        our code well, we will be able to interchange when the hitbox/hurtbox
        updates are called to our needs and to optimize it.
        """
        pass

    def update_hurtbox(self) -> None:
        raise NotImplementedError

    def update_ECB(self) -> None:
        raise NotImplementedError

    def actionable(self) -> bool:
        """
        TODO: Create a table of all possible action states to handle return values
        Apart from creating the table to handle return values of this function,
        creating a table of all possible action states is useful for when we
        start designing how inputs are handled: certain inputs can have an
        effect on the certain characters while they're not 'actionable'
        """
        pass

    def enter_hitlag(self, attack_data: Dict, receiver: bool) -> None:
        """
        TODO: To be completed after hitboxes and how attack data is stored are done
        This method will put the character into hitlag as a function of damage
        taken. If receiver is False, this will freeze the character into hitlag
        for some amount of frames and return them back into whatever action state
        they were in. If receiver is True, this will do the same thing, except
        place the character into hitstun as a function of attack_data after
        hitlag is finished.
        """
        pass

    @staticmethod
    def cross_inc(value: float, increment: float, cross: float = 0) \
            -> float:
        """
        This static function does the following:
        Increments value if value is higher than cross. If value is then lower
        than cross, it will return cross, otherwise it will return value.
        Decrements value if value is lower than cross. If value is then higher
        than cross, it will return cross, otherwise it will return value.

        In practise, what this is used for is when you want to increment
        directionally. For example, if you want to lower speed, it's trivial
        when the speed is positive. However, when it is negative, this function
        comes in handy, since you can set a negative increment, and this
        function will handle both when speed is negative or when it is positive.

        Additionally, since most of the time, when you increment directionally,
        you don't want to increment PAST a certain "cross," this function
        handles that.

        Example:
            cross_inc(10, -5, 0) returns 5
            cross_inc(-10, -5, 0) returns -5
            cross_inc(-3, -5, 0) returns 0

        Message me if there's any confusion since this is a very important
        helper function.
        """
        if value > cross:
            value += increment
            if value < cross:
                return cross
            return value
        elif value < cross:
            value -= increment
            if value > cross:
                return cross
            return value
        return value

    def update_air_speed(self, drift: float) -> None:
        """
        Updates air speed. Don't worry too much about the specifics. This is
        called every update cycle and takes in 'drift' which corresponds to
        the x-axis value of the control stick.
        """
        target_speed = drift * self.traits['x_max_speed']
        current_x_speed = self.get_speed('x')
        current_y_speed = self.get_speed('y')
        if target_speed == 0:
            # Update x speed
            # Starts slowing the character down, up to 0 x speed.
            self.modify_speed((self.cross_inc(current_x_speed,
                                              -self.traits['air_friction'],
                                              0),
                               current_y_speed))

        elif not self.get_speed('x') == target_speed:
            # Update x speed
            # Starts speeding/slowing the character up/down, trying to hit the
            # target speed.
            self.modify_speed((self.cross_inc(current_x_speed,
                                              -self.traits['x_acc'],
                                              target_speed),
                               current_y_speed))

        # Update y speed and makes sure it doesn't exceed the terminal y speed.
        if not current_y_speed <= -self.traits['y_max_speed']:
            self.modify_speed((self.get_speed('x'),
                               self.cross_inc(current_y_speed,
                                              -self.traits['y_acc'],
                                              -self.traits['y_max_speed'])))


class Phrog(Character):

    def __init__(self) -> None:
        super(Phrog).__init__()
        # This is only temporary. This data will eventually be stored elsewhere.
        self.traits = {
            "gr_max_speed": 11.5,
            "y_acc": 1.18,
            "y_max_speed": 14.34,
            "x_acc": 0.41,
            "x_max_speed": 4.27,
            "fullhop_velocity": 18.84,
            "shorthop_velocity": 10.41,
            "traction": 0.24,
            "high_traction_speed": 8.19,
            "weight": 30,
            "air_friction": 0.1,
            "dash_frames": 11,
            "turnaround_frames": 30,
            "edge_link": [
                50,
                30,
                50]}
