from __future__ import annotations
from typing import *
from geometries import *
import misc_functions as mf
from math import sin, cos, atan2


#These constants are going to be put in the data file later.
UNIV_LANDING_LAG = 2
SHIELD_REGEN = 0.1
SHIELD_DEGEN = 0.2
MAX_SHIELD = 86
ASDI_CONSTANT = 10
REDASH = 0.75
KD_THRESHOLD = 80
MAX_DI = 0.2
KB_LAUNCH_RATIO = 0.15
GROUND_KB_RATIO = -0.8
DI_METER_RATIO = 1
ACTIONABLE_STATES = ('wait',
                     'walk',
                     'dash_start',
                     'dash_turn',
                     'dash_lock',
                     'squat',
                     'tumble',
                     'ledge_wait')

# These states only correspond to grounded states, since waveland can only
# happen while grounded.
NON_WAVELAND_STATES = ('walk',
                       'dash_start',
                       'dash_turn',
                       'dash_lock',
                       'kd_wait',
                       'kd_rollf',
                       'kd_rollb',
                       'techrollf',
                       'techrollb',
                       'rollf',
                       'rollb',
                       'ledge_roll',
                       'ledge_getup')
REPEATING_STATES = ('dash_lock',
                    'dash_turn',
                    'walk',
                    'squat',
                    'shield',
                    'grabbing',
                    'grabbed')


class Character:
    """
    An abstract representation of a Super Slam Brothers: Jam character.

    Note: Character position should ONLY be updated by the update_pos() method
    which is a function of the character's speed, except in special cases, like
    when a character dies. This is for use in the environment handler
    """
    action_state: Dict
    env_state: str
    hitboxes: CharHitboxes
    hurtbox: CharHurtboxes
    ECB: ECB
    internal_data: Dict

    def __init__(self, pos: Tuple) -> None:
        """
        In the future, we may change things like position and speed to be Vector
        objects because Vector addition/multiplication is much easier than
        component-wise.
        """
        self.action_state = {'action': 'rebirth', 'frame': 0}
        self.env_state = 'rebirth'

        # Hitboxes and hurtboxes will be changed to hitbox/hurtbox objects
        self.hitboxes = CharHitboxes()
        self.hurtboxes = CharHurtboxes()

        self.internal_data = {'pos': pos,
                              'damage': 0,
                              'speed': (0, 0),
                              'shield_health': MAX_SHIELD,
                              'invincibility': 30,
                              'invincible': True,
                              'waveland': False,
                              'landing_lag': UNIV_LANDING_LAG,
                              'jumped': False,
                              'tech_valid': True,
                              'tech_cd': 0,
                              'tech_buffer': False,
                              'ASDI': 0,
                              'held_act_state': {},
                              'direction': 1,
                              'tilt': (0, 0),
                              'stored_tilt': (0, 0),
                              'attack_data': {},
                              'receiver': False,
                              'KB': 0,
                              'meter': 0,
                              'grabbed_by': None,
                              'grabbing': None,
                              'grab_length': 0
                              }
        # ECB is currently initialized as a list, but will most likely be
        # changed to an ECB object later.
        self.ECB = ECB()
        self.traits = {}
        self.Helper = CharacterHelper(self)
        # moves will be initialized in the subclasses of Character.
        self.moves = {}

    def act_state(self, index: str) -> Union[str, int]:
        return self.action_state[index]

    def modify_act_state(self, index: str, value: Union[str, int]) -> None:
        self.action_state[index] = value

    def change_act_state(self, action: str, frame: int) -> None:
        """
        This differs in modify_act_state in that it changes both the 'action'
        and 'frame' part of action state.
        """
        self.modify_act_state('action', action)
        self.modify_act_state('frame', frame)

    def increment_act_state(self, value: int) -> None:
        self.action_state['frame'] += value

    def get_ECB(self) -> ECB:
        return self.ECB

    def modify_env_state(self, env_state: str) -> None:
        self.env_state = env_state

    def int_data(self, index: str) -> Any:
        return self.internal_data[index]

    def modify_int_data(self, index: str, value: Any) -> None:
        self.internal_data[index] = value

    def speed(self, component:Union[str, bool] = False) -> Union[Tuple, float]:
        # Maybe I could have used keyworded arguments for these instead, but
        # I'll leave it as is, since I've already done a lot of code with this.
        if not component:
            return self.int_data('speed')
        elif component == 'x':
            return self.speed()[0]
        elif component == 'y':
            return self.speed()[1]

    def modify_speed(self, speed: Union[float, Tuple],
                     component: Union[str, None] = None) -> None:
        if component is None:
            self.modify_int_data('speed', speed)
        elif component == 'x':
            self.modify_speed((speed, self.speed('y')))
        elif component == 'y':
            self.modify_speed((self.speed('x'), speed))

    def increment_speed(self, speed: Tuple) -> None:
        current_speed = self.speed()
        new_speed = (current_speed[0] + speed[0], current_speed[1] + speed[0])
        self.modify_int_data('speed', new_speed)

    def pos(self, component: Union[str, bool] = False) -> Union[Tuple, float]:
        if not component:
            return self.int_data('pos')
        elif component == 'x':
            return self.pos()[0]
        elif component == 'y':
            return self.pos()[1]

    def modify_pos(self, pos: Tuple) -> None:
        self.modify_int_data('pos', pos)
        self.update_ECB()

    def increment_pos(self, pos_inc: Tuple) -> None:
        current_pos = self.pos()
        new_pos = (current_pos[0] + pos_inc[0], current_pos[1] + pos_inc[1])
        self.modify_int_data('pos', new_pos)
        self.update_ECB()

    def update_pos(self, **kwargs) -> None:
        """
        !!! IMPORTANT !!!
        The reason why I want to create this seemingly useless method is because
        of pygame coordinates having y increase as you go down the screen. That
        means whenever you try to update position with speed using increment_pos
        with a positive y speed, it will send you DOWN. To avoid confusion and
        having to reverse the sign every time increment_pos is called with
        respect to speed, USE THIS INSTEAD BECAUSE IT ACCOUNTS FOR IT
        """
        if 'speed' in kwargs:
            speed = kwargs['speed']
            self.increment_pos(speed)
        else:
            speed = self.speed()
            self.increment_pos((speed[0], -speed[1]))

    def update(self) -> None:
        """
        TODO: Finish
        List of things to update (in no particular order):
        - Invincibility timer/invincibility status
        - Tech-availability status
        - Shield health
        - Standard and character specific projectiles
        - Hitlag status and ASDI inputs
        - Environmental state grounded:
            - All of the possible action states while grounded
            - Grounded attacks (not a separate case, but a special case)
        - Environmental state airborne:
            - All of the possible action states while airborne
        - Environmental state ledge:
            - ...
        """
        helper = self.Helper
        helper.misc_update()
        self.handle_proj()

        helper.nonstandard_update()

    def update_hurtbox(self) -> None:
        raise NotImplementedError

    def update_ECB(self) -> None:
        action = self.act_state('action')
        if action in self.moves['standard']:
            self.ECB = self.moves['standard'][action]['ECB'].translate(
                Vector(self.pos()))
        else:
            # TODO: For things like jump, where ECB is dependent on velocity.
            pass

    def actionable(self) -> bool:
        """
        Returns if a character is actionable or not, regardless of character
        specific actionability.
        """
        return self.act_state('action') in ACTIONABLE_STATES

    def deal_hit(self, character: Character, hitbox: Hitbox) -> None:
        """
        Deal a hit to character. Certain characters may do something special,
        like Inkling deals more damage and knockback based on ink, so we leave
        this as a generic method, and maybe some character will override this
        method.
        """
        if hitbox is not None:
            character.receive_hit(hitbox=hitbox, character=self)
            if isinstance(hitbox, GrabHitbox):
                # This line will be changed for characters that have special
                # grabs, like C. Falcon
                self.change_act_state('grabbing', 0)
            else:
                self.enter_hitlag(hitbox.get_data(), False)

    def receive_hit(self, **kwargs) -> None:
        """
        This method may be overwritten in subclasses since different characters
        may be 'damaged' differently. For example, a Marth will not take damage
        in his counter state.

        Two kwargs: hitbox, character.

        This will handle
        grabs
        shielded
        counter (if applicable)
        ...
        """
        if isinstance(kwargs['hitbox'], GrabHitbox):
            # If grabber is in kwargs, that already means this character is not
            # invincible, and this character will ALWAYS get grabbed in this
            # scenario.
            self.change_act_state('grabbed', 0)
            # P1
            # TODO: Finish
            # Teleport next to character
            # Modify grab_length according to some formula
        elif self.act_state('action') in ('shielded', 'shieldstun'):
            attack_data = kwargs['hitbox'].get_data()
            damage = attack_data['damage']
            shield_damage = attack_data['shield_damage']
            shield_health = self.int_data('shield_health')
            self.modify_int_data('shield_health',
                                 shield_health - (damage + shield_damage))
            if not self.int_data('shield_health') <= 0:
                self.change_act_state('shieldstun',
                                      self.Helper.shieldstun_duration(damage))
                self.modify_speed(
                    self.Helper.shieldstun_speed(damage, kwargs['character']),
                    'x')
            else:
                self.change_act_state('shieldbreak', 0)
        else:
            attack_data = kwargs['hitbox'].get_data()
            new_damage = self.int_data('damage') + attack_data['damage']
            self.modify_int_data('damage', new_damage)
            self.enter_hitlag(attack_data, True)

    def enter_hitlag(self, attack_data: Dict, receiver: bool) -> None:
        """
        This method will put the character into hitlag as a function of damage
        taken. If receiver is False, this will freeze the character into hitlag
        for some amount of frames and return them back into whatever action
        state they were in. If receiver is True, this will do the same thing,
        except place the character into hitstun as a function of attack_data
        after hitlag is finished.
        """
        self.modify_int_data('receiver', receiver)
        self.modify_int_data('attack_data', attack_data.copy())
        self.change_act_state('hitlag', int(attack_data['damage'] / 3))
        self.modify_int_data('held_act_state', self.action_state.copy())

    def handle_proj(self) -> None:
        """
        This is to be implemented in subclasses because each character has
        different projectiles and they behave differently.
        """
        raise NotImplementedError

    def land(self) -> None:
        """
        This method will handle what happens when a character lands on the ground
        based on the action state they are in. This should account for landing
        lag as well as what happens if, for example, Fox Up B's down into the
        stage.

        put character in grounded

        If airdodge, waveland
        If hitstun and KB greater than KD_THRESHOLD or tumble
            Tech input true: take tilt input and techroll
            Tech input false: kd_bounce

        If jump or hitstun (assertion that hitstun < KD_THRESHOLD)
            put in lag with UNIV_LANDING_LAG
        else
            put in lag according to landing lag of action state
        """
        pass

    def hit_wall(self) -> None:
        """
        When a character hits a wall, handling if they tech or not.
        """
        if self.int_data('tech_buffer'):
            self.env_state = 'suspended'
            self.change_act_state('wall_tech', 0)
        else:
            curr_speed = self.speed()
            self.modify_speed((-curr_speed[0], -curr_speed[1]))

    def update_tilt(self, tilt: Tuple) -> None:
        self.modify_int_data('tilt', tilt)

    def action(self, **kwargs) -> bool:
        """
        Called by the control handler, providing extra arguments when needed.
        Control handler will provide an action based on the env_state and inputs
        and action() will handle whether that action will go off, and more
        specific details.

        Essentially, this is the action handler.

        Handles:
        pummel
        walk
        dash
        airdodge
        throws
        ...
        """
        current_action = self.act_state('action')
        action = kwargs['action']
        tilt = self.int_data('tilt')

        if not self.actionable():
            return False

        if action == 'airdodge':
            self.modify_int_data('stored_tilt', self.int_data('tilt'))
            self.change_act_state('airdodge', 0)

        elif action == 'dash_start':
            tilt_dir = mf.sign(tilt[0])

            # Preserves speed when switching dash direction on dash startup
            if current_action == 'dash_start':
                if not tilt_dir == self.int_data('direction'):
                    self.modify_int_data('direction', tilt_dir)
                    self.modify_speed(tilt_dir * self.speed('x'), 'x')
                    self.change_act_state('dash_start', 0)

            # Puts character into dash_turn if they're currently locked
            elif current_action == 'dash_lock':
                self.modify_int_data('direction', tilt_dir)
                self.change_act_state('dash_turn', 0)
            else:
                self.modify_int_data('direction', tilt_dir)

        else:
            self.change_act_state(action, 0)

        return True


class CharacterHelper:
    """
    This class is simply to keep the Character class clean. There are many
    methods we need Character to use that will never be called outside of the
    Character class, and thus we store them here.
    """

    def __init__(self, character: Character) -> None:
        self.Character = character

    @staticmethod
    def airdodge_multi(frame: int) -> float:
        return (605535 / (frame + 29.65) ** 3.24) - 0.25

    @staticmethod
    def shieldstun_duration(damage: float) -> int:
        return int((damage + 4.45) * 0.447)

    @staticmethod
    def compute_DI(DI: float, angle_base: float) -> float:
        spread = math.pi * MAX_DI / 2
        angle_DI = min(mf.delta_angle(DI, mf.std_angle(angle_base + spread)),
                       mf.delta_angle(DI, mf.std_angle(angle_base - spread)))
        return angle_DI


    @staticmethod
    def delta_DI(angle_DI: float, angle_base: float, hitstun: float,
                 gravity: float) -> float:
        """
        P2
        TODO: FINISH
        Returns the distance between how far a character would travel with and
        without DI being factored. Will look into optimizing this formula, as
        gravity may not be included, but can be factored in by means of the
        METER_DI ratio.
        """
        pass

    def shieldstun_speed(self, damage, character: Character) -> float:
        traction = self.Character.traits['traction']
        return (2 * damage * traction + (-27 * traction + 3.2)) * \
               (mf.sign(self.Character.pos('x') - character.pos('x')))

    def KB_formula(self, attack_data: Dict) -> float:
        """
        Don't even bother trying to read this formula. Just know that it's
        pulled from the website and that it's correct.
        """
        damage = self.Character.int_data('damage')
        weight = self.Character.traits['weight']
        return int(attack_data['KBG'] / 100) * \
            ((14 * damage * (attack_data['damage'] + 2) /
                (weight + 100)) + 18) + attack_data['BKB']

    def handle_air_speed(self) -> None:
        """
        Updates air speed. Don't worry too much about the specifics.
        """
        tilt = self.Character.int_data('tilt')[0]
        target_speed = tilt * self.Character.traits['x_max_speed']
        current_x_speed = self.Character.speed('x')
        current_y_speed = self.Character.speed('y')
        if target_speed == 0:
            # Update x speed
            # Starts slowing the character down, up to 0 x speed.
            self.Character.modify_speed(mf.cross_inc(current_x_speed,
                                        -self.Character.traits['air_friction'],
                                        0), 'x')

        elif not self.Character.speed('x') == target_speed:
            # Update x speed
            # Starts speeding/slowing the character up/down, trying to hit the
            # target speed.
            self.Character.modify_speed(mf.cross_inc(current_x_speed,
                                        -self.Character.traits['x_acc'],
                                        target_speed), 'x')

        # Update y speed and makes sure it doesn't exceed the terminal y speed.
        if not current_y_speed <= -self.Character.traits['y_max_speed']:
            self.Character.modify_speed(mf.cross_inc(current_y_speed,
                                        -self.Character.traits['y_acc'],
                                        -self.Character.traits['y_max_speed']),
                                        'y')

    def handle_ground_speed(self) -> None:
        """
        Handles ground movement.
        """
        tilt = self.Character.int_data('tilt')[0]
        action = self.Character.act_state('action')
        current_speed = self.Character.speed('x')

        if action == 'walk':
            # If a character hasn't stopped, continue until it has hit the
            # target_speed
            target_speed = tilt * self.Character.traits['walk_max_speed']

            if not current_speed == 0:
                self.Character.modify_speed(mf.cross_inc(
                    current_speed,
                    -self.Character.traits['walk_acc'],
                    target_speed))

            # If the axis is within the dead zone and character has stopped,
            # then put them into the neutral 'wait' state.
            elif target_speed == 0:
                self.Character.change_act_state('wait', 0)

        elif action in ('dash_start', 'dash_lock'):
            # Precondition: Controller axis stays above some value during
            # each dash_start iteration
            target_speed = self.Character.traits['dash_max_speed'] * \
                           mf.sign(tilt)
            self.Character.modify_speed(mf.cross_inc(
                current_speed,
                -self.Character.traits['dash_acc'],
                target_speed))

            if self.Character.speed('x') == 0:
                self.Character.change_act_state('wait', 0)

        elif action == 'dash_turn':

            # Keeps turning until speed is 0
            if not current_speed == 0:
                self.Character.modify_speed(mf.cross_inc(
                    current_speed,
                    -self.Character.traits['dash_acc'],
                    0))

            # If speed not 0 and controller axis value is over REDASH, then
            # put character back into dash_start
            elif abs(tilt) > REDASH:
                self.Character.change_act_state('dash_start', 0)

            # Otherwise, character is back to the walk state
            else:
                self.Character.change_act_state('wait', 0)

    def misc_update(self) -> None:
        """
        Handles miscellaneous updates such as invincibility, tech availability,
        and shield health.
        """

        # Counts down invincibility, turning off 'invincible' when invincibility
        # runs out
        invincibility = self.Character.int_data('invincibility')

        if invincibility > 0:
            self.Character.modify_int_data('invincibility', invincibility - 1)
            if self.Character.int_data('invincibility') == 0:
                self.Character.modify_int_data('invincible', False)

        # Regenerates shield up to the constant MAX_SHIELD
        shield_health = self.Character.int_data('shield_health')
        if not self.Character.act_state('action') == 'shielded':
            self.Character.modify_int_data('shield_health',
                                           mf.cross_inc(shield_health,
                                                        -SHIELD_REGEN,
                                                        MAX_SHIELD))

        # Counts down when a tech input is ready to be taken again.
        tech_cd = self.Character.int_data('tech_cd')
        if tech_cd > 0:
            self.Character.modify_int_data('tech_cd', tech_cd - 1)
            if self.Character.int_data('tech_cd') == 0:
                self.Character.modify_int_data('tech_valid', True)

    def account_DI(self) -> None:
        """
        P2
        TODO: Finish
        This method is called when hitlag ends and the receiver takes a DI
        input. It sets the initial velocity of launch based on the DI input.
        Additionally, it will charge the character's meter based on how they
        DI.
        """
        DI = mf.angle(self.Character.int_data('tilt'))
        angle_base = self.Character.int_data('attack_data')['angle']
        angle_DI = self.compute_DI(DI, angle_base)

        speed_mag = self.Character.int_data('KB') * KB_LAUNCH_RATIO
        x_speed = speed_mag * math.cos(angle_DI)
        y_speed = speed_mag * math.sin(angle_DI)

        if self.Character.env_state == 'grounded' and y_speed < 0:
            y_speed *= GROUND_KB_RATIO

        self.Character.modify_speed((x_speed, y_speed))

        curr_meter = self.Character.int_data('meter')
        hitstun = self.Character.act_state('frame')
        gravity = self.Character.traits['y_acc']
        meter_gain = self.delta_DI(angle_DI,
                                   angle_base,
                                   hitstun,
                                   gravity) * DI_METER_RATIO
        self.Character.modify_int_data('meter', curr_meter + meter_gain)

    def non_increasing_updates(self) -> None:
        """
        This method calls the updates for all of the action states that don't
        increase their frame count per frame.
        """
        self.shieldstun_update()
        self.hitlag_update()
        self.hitstun_update()

    def shieldstun_update(self) -> None:
        if self.Character.act_state('action') == 'shieldstun':
            self.Character.increment_act_state(-1)
            if self.Character.act_state('frame') == 0:
                self.Character.change_act_state('wait', 0)
                self.Character.modify_speed(0, 'x')

    def hitstun_update(self) -> None:
        if self.Character.act_state('action') == 'hitstun':
            self.Character.increment_act_state(-1)
            if self.Character.act_state('frame') == 0:
                if self.Character.int_data('KB') < 80:
                    self.Character.change_act_state('jump', 0)
                else:
                    self.Character.change_act_state('tumble', 0)
            else:
                speed = self.Character.speed()
                y_acc = self.Character.traits['y_acc']
                y_max_speed = self.Character.traits['y_max_speed']
                self.Character.modify_speed((mf.cross_inc(speed[0], 0.19, 0),
                                             mf.cross_inc(speed[1],
                                                          -y_acc,
                                                          y_max_speed)))

    def hitlag_update(self) -> None:
        """
        When a character is in hitlag, this is called. Once hitlag is over,
        the character has a chance to ASDI and 'wiggle' very slightly.
        """
        if self.Character.act_state('action') == 'hitlag':
            self.Character.increment_act_state(-1)
            if self.Character.act_state('frame') == 0:
                receiver = self.Character.int_data('receiver')
                if receiver:
                    attack_data = self.Character.int_data('attack_data')
                    KB = self.KB_formula(attack_data)
                    ASDI = self.Character.int_data('ASDI')

                    # Accounts for ASDI
                    self.Character.update_pos(speed=(cos(ASDI) * ASDI_CONSTANT,
                                                     sin(ASDI) * ASDI_CONSTANT))

                    # Puts character into hitstun and accounts for DI
                    self.Character.change_act_state('hitstun',
                                                    int(KB))
                    self.Character.modify_int_data('KB', KB)
                    self.account_DI()
                else:
                    held = self.Character.int_data('held_act_state')
                    self.Character.change_act_state(held['action'],
                                                    held['frame'])

    def grabbed_update(self) -> None:
        grab_length = self.Character.int_data('grab_length')
        self.Character.modify_int_data('grab_length', grab_length - 1)
        if grab_length - 1 <= 0:
            self.Character.change_act_state('break_free', 0)
            grabber = self.Character.int_data('grabbed_by')
            grabber.change_act_state('grab_release', 0)

    def throw_update(self) -> None:
        """
        P1
        TODO: Finish
        Updates this character if it is being thrown.
        """
        pass

    def airdodge(self) -> None:
        multiplier = self.airdodge_multi(self.Character.act_state('frame'))
        angle = mf.angle(self.Character.int_data('stored_tilt'))

        self.Character.modify_speed((cos(angle) * multiplier,
                                     sin(angle) * multiplier))

    def waveland(self) -> None:
        """
        This is used for when a character airdodges into the ground and preserve
        aerial momentum transferred to ground momentum, and 'slides' along the
        ground.
        """
        if self.Character.int_data('waveland') and \
                self.Character.act_state('action') not in NON_WAVELAND_STATES:
            speed = self.Character.speed('x')
            traction = self.Character.traits['traction']
            if abs(speed) > self.Character.traits['high_traction_speed']:
                self.Character.modify_speed(
                    mf.cross_inc(speed, -2 * traction, 0), 'x')
            else:
                self.Character.modify_speed(
                    mf.cross_inc(speed, -traction, 0), 'x')

    def action_length(self) -> int:
        """
        Gets the length of the action that the character is in.
        """
        action = self.Character.act_state('action')
        for type_ in self.Character.moves:
            if action in self.Character.moves[type_]:
                return len(self.Character.moves[type_][action]['frame_data'])

    def end_state_update(self) -> None:
        """
        Since different moves can end in putting the character in different
        env states/action states, we account for that by having some data
        attached the move and calling this function when a move ends.

        There are some special cases where the end state is triggered by
        something else, like speed or controller input and that may not be
        included in here.

        In the future we MAY end up storing the end action state in addition to
        the end env state to simplify the code a little bit, but for now, I'll
        keep writing this without that intention. Accounting for that change
        would be very easy so there's no reason to stop progressing like this
        for now.
        """
        action = self.Character.act_state('action')
        action_data = self.Character.moves['standard'][action]

        if action_data['end_env_state'] == 'grounded':
            self.Character.modify_env_state('grounded')

            # Special cases where an action state doesn't end in the neutral
            # wait state

            # These ones continually loops the action
            if action in REPEATING_STATES:
                self.Character.change_act_state(action, 0)
            elif action == 'squat_start':
                self.Character.change_act_state('squat', 0)
            elif action == 'pummel':
                self.Character.change_act_state('grabbing', 0)
            elif action == 'kd_bounce':
                self.Character.change_act_state('kd_wait', 0)

            # Every other case ends in the neutral wait state
            else:
                self.Character.change_act_state('wait', 0)

        elif action_data['end_env_state'] == 'airborne':
            self.Character.modify_env_state('airborne')

            # Special cases

            # Very special case. On the frame auto wavedash ends (the first
            # airborne frame), an airdodge is buffered. Essentially, this case
            # updates two frames at once to account for the airdodge buffer
            # and it's why we want an airdodge method: to keep the code clean
            if action == 'auto_wavedash':
                self.Character.change_act_state('jump', 0)
                self.Character.action(action='airdodge')
                self.airdodge()
            elif action in ('airdodge', 'freefall'):
                self.Character.change_act_state('freefall', 0)
            else:
                self.Character.change_act_state('jump', 0)

    def standard_update(self) -> bool:
        """
        This is used to handle a class of action states that need no instruction
        from the game other than to keep incrementing the action state frame.
        This method will return True if an action was completed, False otherwise

        ***May need to account for the frame indices being different.***
        """
        action = self.Character.act_state('action')
        action_data = self.Character.moves['standard'][action]

        # Extra special cases where frame is not incremented up
        if action in ('hitlag', 'hitstun', 'shieldstun'):
            return False

        self.Character.increment_act_state(1)
        # Check if the action is completed
        if self.Character.act_state('frame') > self.action_length():
            self.end_state_update()
            return True

        # If action is not completed, then update the character according to the
        # frame data and any other updates.
        self.Character.modify_speed(action_data['frame_data']['speed'])

        return False

    def nonstandard_update(self) -> bool:
        """
        P1
        TODO: Finish
        This is used to handle a class of action states that need extra
        instruction from the game. For example, the game must know how to handle
        dashing and shielding differently.
        This method will return True if an action was completed, False otherwise
        """
        # First update hitlag/hitstun if necessary, THEN run the updates. This
        # is just a design decision and there is a minimal effect to this choice
        self.non_increasing_updates()

        # Check if the action was completed.
        if self.standard_update():
            return True
        # The reason I'm structuring the code like this is to prevent all of the
        # action-specific updates to be nested in an if/else statement, since
        # returning a value will break out of the function and no else statement
        # would be needed

        # No need to account for walk or any of the dash states because that's
        # processed in the control handler
        action = self.Character.act_state('action')
        env_state = self.Character.env_state

        if env_state == 'grounded':
            self.waveland()
            self.handle_ground_speed()
            if action == 'shielded':
                shield_health = self.Character.int_data('shield')
                self.Character.modify_int_data('shield',
                                               shield_health - SHIELD_DEGEN)
            elif action == 'grabbed':
                self.grabbed_update()

        elif env_state == 'airborne' and \
                action not in ('hitstun', 'hitlag', 'airdodge', 'ledge_jump'):
            self.handle_air_speed()

        return False


class Phrog(Character):

    def __init__(self, pos: Tuple) -> None:
        """
        P3
        TODO: Get traits from character file
        """
        super(Phrog).__init__(pos)
        self.traits = {
            "dash_max_speed": 11.5,
            "dash_acc": 1.5,
            "walk_max_speed": 5,
            "walk_acc": 0.5,
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
            "edge_link": {'height': 50, 'width': 50, 'length': 30}}
