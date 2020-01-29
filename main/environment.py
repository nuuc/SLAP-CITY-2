import controller, characters
import misc_functions as mf
from geometries import *


DROPDOWN_THRESHOLD = -0.75
FORCE_IN_STATES = ('rollf',
                   'rollb',
                   'kd_rollf',
                   'kd_rollb',
                   'techrollf',
                   'techrollb')

"""
This file will contain the Environment class, which is just a fancy name for
stage. The reason I want to rename it Environment from now on is because it's
a more abstract representation of what the should be in here.
"""


class Environment:
    """
    Want to create an abstract class for this since I want the stage process
    method to call on a method that works for any Environment object.

    There are definitely limitations to how I'm designing this, particularly
    when two environment objects are close to one another and have the
    potential to repeatedly push the character between them, but, we'll try
    to design around that since the MTV depends directly on the separating
    axis theorem, which depends on convex polygons.
    """

    def __init__(self, floor: Line) -> None:
        """
        Floor should be defined from left to right.
        """
        self.floor = floor

    def within_xbounds(self, ecb: ECB) -> bool:
        """
        This method checks any point of the ECB is within the x bounds of
        this environment. There's no sense in checking for collision if an ECB
        is off the map. The purpose of this is to save whatever computational
        power we can.
        This only checks the floor, which fits our design fine, since every
        environment object should only have one straight line as a floor,
        which contains all of the other vertices within its bounds.
        """
        x_bounds = [self.floor.points[i].x for i in self.floor.points]
        l_bound = min(x_bounds)
        r_bound = max(x_bounds)

        if ecb.get_point('L') <= r_bound or ecb.get_point('R') >= l_bound:
            return True

        return False

    def get_MTV(self, ecb: ECB) -> Vector:
        raise NotImplementedError

    def bounds(self, side: str) -> Vector:
        if side == 'l':
            return self.floor.points[0]
        elif side == 'r':
            return self.floor.points[1]
        return Vector((0, 0))


class EnvironmentObject(Environment):
    """
    Meant to represent any polygon that is considered an environment.
    """

    def __init__(self, geom: Polygon, floor: Line) -> None:
        """
        floor must correspond to one of the edges on geom. It is crucial to
        know which edge is the floor, and searching for it based on geom
        can be ambiguous, so we accept it as an argument to avoid that.
        """
        super().__init__(floor)
        self.geom = geom

    def curr_collide(self, ecb: ECB) -> bool:
        if self.within_xbounds(ecb):
            return self.geom.collide(ecb.polygon)
        return False

    def path_collide(self, ecb: ECB, prev_ecb: ECB) -> bool:
        """
        In high velocity cases, an ECB may pass right through an environment
        from one frame to another, and this is to catch that.
        """
        pass

    def get_MTV(self, ecb: ECB) -> Vector:
        return ecb.get_MTV(self.geom)


class Platform(Environment):
    """
    Basically a wrapper class for line to keep consistency in Stage.
    """

    def __init__(self, platform: Line) -> None:
        """
        Platforms must be a straight line parallel to the y axis.
        """
        super().__init__(platform)

    def path_collide(self, ecb: ECB, prev_ecb: ECB) -> bool:
        """
        Have to check whether previous 'D' ecb was above platform and is now
        below platform.
        """
        return prev_ecb.get_point('D').y < \
               self.floor.points[0].y < \
               ecb.get_point('D').y

    def get_MTV(self, ecb: ECB) -> Vector:
        """
        This should ONLY be called when the collision check for the ECB passes.
        Also, this isn't really using the SAT.
        """
        return Vector((0, self.floor.points[0].y - ecb.get_point('D').y))


class Ledge:

    def __init__(self, point: Vector, geom: Polygon, direction: int) -> None:
        self.point = point
        self.geom = geom
        self.occupied = None
        self.direction = direction

    def grab_ledge(self, character: characters.Character):
        """
        Makes character grab this ledge.
        """
        character.modify_env_state('ledge')
        character.change_act_state('ledge', 0)
        character.modify_speed((0, 0))
        self.occupied = character

    def release_ledge(self) -> None:
        self.occupied = None

    def collide(self, character: characters.Character) -> bool:
        direction = character.int_data('direction')
        if not self.direction == direction:
            return False

        edge_link = character.int_data('edge_link')
        pos = Vector(character.pos())
        link_height = Vector((0, edge_link['height'])) + pos
        link_length = Vector((0, edge_link['length']))
        if direction:
            link_width = Vector((edge_link['width'], 0))
        else:
            link_width = Vector((-edge_link['width'], 0))

        link_box = Rectangle((link_height,
                              link_height + link_length,
                              link_height + link_length + link_width,
                              link_height + link_width))
        return link_box.collide(self.geom)


class Stage:

    def __init__(self) -> None:
        self.bounds = (0, 0)
        self.ledges = ()
        self.environment = ()

    def ledge_update(self, character: characters.Character) -> None:
        """
        This may end up being deleted. I can imagine certain instances where
        this updates improperly. At the very least, this will change.

        Instead, we might have it so that one of the internal data values of
        character would be 'ledge' which is mapped to a Ledge object and
        character update will call on release_ledge.

        Alternatively, we could have this be called for every character before
        process() happens.
        """
        for ledge in self.ledges:
            if ledge.occupied is not None and ledge.occupied is character \
                    and not character.env_state == 'ledge':
                    ledge.release_ledge()

    def left_bounds(self, ecb: ECB, prev_ecb: ECB) -> bool:
        """
        Returns True if a character was previously in bound of an environment
        but now is not.
        """
        for env in self.environment:
            if env.within_xbounds(prev_ecb) and not env.within_xbounds(ecb):
                return True
        return False

    def force_inbound(self, character: characters.Character) -> None:
        """
        Precondition that character 'x' speed is non-zero.
        This forces a character to remain on a floor if they have travelled off
        of it.

        There is definitely a cleaner way to implement this, but this will do
        for now.
        P3
        TODO: Clean
        """
        direction = mf.sign(character.speed('x'))
        ecb = character.get_ECB()
        bottom = ecb.get_point('D')
        floor = self.search_floor(ecb)
        if direction > 0:
            right_boundx = floor.bounds('r')
            translation = right_boundx - bottom
        else:
            left_boundx = floor.bounds('l')
            translation = left_boundx - bottom
        character.increment_pos(translation.get_values())

    def collide_env(self, character: characters.Character) -> bool:
        """
        Not only will this return True if it's collided, it'll handle the
        collision in here as well.
        """
        speed = character.speed()
        ecb = character.ECB
        prev_ecb = ecb.transform_to(Vector(speed) * -1)
        for env in self.environment:
            # If it goes through a platform and character isn't holding down
            if isinstance(env, Platform) and env.path_collide(ecb, prev_ecb) \
                    and not character.int_data('tilt')[1] < DROPDOWN_THRESHOLD:
                character.increment_pos(env.get_MTV(ecb).get_values())
                return True

            else:
                # P2
                # TODO: Also check for passing through
                if env.curr_collide(ecb):
                    character.increment_pos(env.get_MTV(ecb).get_values())
                    return True
                elif env.path_collide(ecb, prev_ecb):
                    pass

    def on_floor(self, ecb: ECB) -> bool:
        """
        Tests to see if the lower point on the ECB is on the line for the floor.
        """
        for env in self.environment:
            a, b, c = env.floor.get_standard().values()
            ecb_foot = ecb.get_point('D')
            return a * ecb_foot + b * ecb_foot + c == 0

    def search_floor(self, ecb: ECB) -> Environment:
        """
        Returns the floor that a character's ECB is on, with the precondition
        that they ARE on a floor.
        """
        for env in self.environment:
            a, b, c = env.floor.get_standard().values()
            ecb_foot = ecb.get_point('D')
            if a * ecb_foot + b * ecb_foot + c == 0:
                return env

    def on_platform(self, ecb: ECB) -> bool:
        for env in self.environment:
            a, b, c = env.floor.get_standard().values()
            ecb_foot = ecb.get_point('D')
            if isinstance(env, Platform) and \
                    a * ecb_foot + b * ecb_foot + c == 0:
                return True
        return False

    @staticmethod
    def dropdown_action_valid(action: str, frame: int) -> bool:
        """
        Helper method for dropdown_valid to keep code clean.
        """
        return action in ('shielded', 'shield_off') or \
               (action == 'squat' and frame == 3)

    def dropdown_valid(self, character: characters.Character) -> bool:
        y_tilt = character.int_data('tilt')[1]

        # Preemptive fail check.
        if y_tilt >= DROPDOWN_THRESHOLD:
            return False

        action = character.act_state('action')
        frame = character.act_state('frame')
        ecb = character.ECB
        return self.dropdown_action_valid(action, frame) and \
               self.on_platform(ecb)

    def collide_ledge(self, character: characters.Character) -> bool:
        y_tilt = character.int_data('tilt')[1]

        # Preemptive fail check.
        if y_tilt < DROPDOWN_THRESHOLD:
            return False

        for ledge in self.ledges:
            if not ledge.occupied and ledge.collide(character):
                ledge.grab_ledge(character)
                return True
        return False

    def ECB_collide(self, characters: Tuple) -> None:
        """
        Moves the characters ECB out of one another. This method cannot push
        characters off the stage if they're grounded.
        """
        pass

    def handle_update_pos(self, character: characters.Character) -> None:
        """
        Handles updating position specifically for when the character is on the
        ground, in the case where the ground is sloped. Otherwise, updates
        position regularly.
        """
        env_state = character.env_state
        if env_state == 'grounded':
            ecb = character.get_ECB()
            speed = Vector(character.speed())

            axis = self.search_floor(ecb).floor.vectorize().normalize()
            proj = (axis * (speed * axis)).get_values()

            character.update_pos(speed=proj)
        else:
            character.update_pos()

    def reprocess(self, character: characters.Character) -> None:
        """
        A 'second' process, where it corrects some of the mistakes that arise
        from an ECB update from the first process. For example, when a character
        grabs ledge and has its ECB updated, the top of the ECB may not line
        up with the ledge point because the ECB is updated from the character's
        position, which is at the bottom of the ECB. Or, when a character wall-
        techs and update_ECB makes the ECB go into the wall.
        """
        character.update_ECB()
        env_state = character.env_state
        action = character.act_state('action')

        if env_state == 'ledge':
            # P1
            # TODO: Fix character position w/ respect to ECB and ledge point
            pass
        elif env_state == 'suspended' and action == 'wall_tech':
            self.collide_env(character)

    def process(self, CharControl: controller.CharacterControl) -> None:
        """
        The control structure for this is pretty tricky, but here's what I plan
        to do.

        Note: Previous position is always obtainable since the only way a
        character is moved is when update_pos is called, which depends on speed.
        Therefore, we can use the speed to find the previous position of a
        character, always.

        P1
        TODO: Finish

        Check environment states
        If grounded
            previously in bound: make airborne EXCEPT for when
            the action states are: rollf, rollb, kd_rollf, kd_rollb, techrollf,
            techrollb. In that case, keep them grounded and have them roll right
            to the edge of the floor.
            on a platform:
                if (squatting on 3rd frame (always 3rd frame, regardless of
                squat animation) or shielded, shield off) and tilt above
                threshold: make airborne and set vertical speed to max

        If airborne, check collision (also, check if previously above a floor
        and now below a floor in case of high speeds).
            Check if pass through platform
                Check if holding down: pass through
                Else, move by MTV and make grounded
            Check if now on floor
                Make grounded
                Call character's land method
            Check if grab ledge


        """
        character = CharControl.Character
        env_state = character.env_state
        action = character.act_state('action')
        # Not sure on the best way to do this, but I want set prev_ecb to the
        # actual previous ECB.
        prev_ecb = character.get_ECB().copy()
        character.update_pos()
        ecb = character.get_ECB()

        self.ledge_update(character)

        if env_state == 'grounded':
            if self.left_bounds(ecb, prev_ecb):
                if action not in FORCE_IN_STATES:
                    character.modify_env_state('airborne')
                    character.change_act_state('jump', 0)
                else:
                    self.force_inbound(character)

            elif self.dropdown_valid(character):
                # Need to move them downwards on this frame so the platform
                # doesn't detect them passing through and stops them.
                character.modify_env_state('airborne')
                character.change_act_state('jump', 0)
                character.modify_speed(-character.traits['y_max_speed'], 'y')
                character.update_pos()

        # May change action to be in a character's ledge_valid trait
        elif env_state in ('airborne', 'suspended') and action == 'jump':
            if self.collide_env(character):
                if self.on_floor(ecb):
                    character.land()
                else:
                    character.hit_wall()

            self.collide_ledge(character)

        self.reprocess(character)


