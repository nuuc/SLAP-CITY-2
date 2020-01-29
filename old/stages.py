import controller_handler, characters, loops
from typing import *

KD_THRESHOLD = 80


def in_bound(ecb: List, bounds: List) -> bool:
    if bounds[0] < ecb[1] and ecb[0] < bounds[1]:
        return True
    return False


def bottom_in_bound(x: float, bounds: List) -> bool:
    if bounds[0] < x < bounds[1]:
        return True
    return False


class Stage:
    """
    An abstract representation of a Slap City 2 stage.
    Every stage is only going to have straight lines.
    === REPRESENTATION INVARIANTS ===
    For every attribute in Stage, index 1 < index 2
    For every attribute in Stage, the first index of each object is its x/y start, second is its x/y end, and third
    is its x/y level, depending on its orientation.

    === PUBLIC ATTRIBUTES ===
    ceiling: A list of all the ceilings in the stage.
    floor: A list of all the floors in the stage. The fourth index for every floor is True if a character can drop down
    from it, and False if it can not.
    walls: A list of all the walls in the stage.
    """
    ceiling: List
    floor: List
    walls: List
    ledges: List

    def __init__(self) -> None:
        raise NotImplementedError

    def handle_stage(self, char_control_map: Dict) -> None:
        """
        Handles stage interactions.
        """
        for controller in char_control_map:
            character = char_control_map[controller]
            prev_ecb = character.ecb.copy()
            character.update()
            center = character.center
            ecb = character.ecb
            copy = char_control_map.copy()
            del copy[controller]
            other_character = list(copy.values())[0]
            for floor in self.floor:
                x_bounds = [floor[0], floor[1]]
                y_level = floor[2]
                if bottom_in_bound(ecb[0][0], x_bounds):
                    if ecb[0][1] > y_level >= prev_ecb[0][1]:
                        if character.action_state[0] == 'airdodge':
                            character.update_speed(character.speed[0], 0)
                            character.action_state = ['waveland', 0]
                            character.data.update({'sliding': True})
                            character.env_state = 'grounded'
                            character.data['invincibility'] = 0
                            character.update_ecb()
                            character.update_center(center[0], y_level + (center[1] - character.ecb[0][1]))
                            character.jumped = False

                        elif (character.action_state[0] == 'hitstun' and character.data['kb'] >= KD_THRESHOLD) \
                                or character.action_state[0] == 'tumble':
                            character.env_state = 'grounded'
                            character.update_ecb()
                            character.update_center(center[0], y_level + (center[1] - character.ecb[0][1]))
                            character.jumped = False
                            if character.data['tech'] >= 33:
                                character.data.update({'sliding': False})
                                if isinstance(controller, controller_handler.Joystick):
                                    character.action('techroll', controller.map_axes('control')[0])
                                elif isinstance(controller, controller_handler.Keyboard):
                                    character.action('techroll', controller.get_vaxis('x'))
                            else:
                                character.action_state = ['kd_bounce', 25]
                                character.update_speed(character.speed[0] * 0.5)

                        elif (not controller.get_axis('y') <= -0.3 or not floor[3]) \
                                or (character.action_state[0] == 'hitstun' and character.data['kb'] < KD_THRESHOLD):
                            character.update_speed(character.speed[0], 0)
                            character.jumped = False
                            character.data['sliding'] = True
                            character.action_state = ['lag', character.data['landing_lag']]
                            character.data['landing_lag'] = characters.UNIV_LANDING_LAG
                            character.env_state = 'grounded'
                            character.update_ecb()
                            character.update_center(center[0], y_level + (center[1] - character.ecb[0][1]))
                            character.hitboxes['regular'] = {'ids': {}, 'hit': True}

                    elif ((character.action_state[0] == 'startsquat' and character.action_state[1] == 3) \
                            or character.action_state[0] in ('shielded', 'shield_off')) \
                            and controller.map_axes('control', 0.45)[1] == -1 \
                            and ecb[0][1] == y_level and floor[3]:
                        character.action_state = ['jump', 0]
                        character.env_state = 'airborne'
                        character.update_ecb()
                        character.update_center(center[0], center[1] + 1)
                        character.update_speed(0, -character.attributes['max_vair_speed'])

                elif bottom_in_bound(prev_ecb[0][0], x_bounds) and ecb[0][1] == y_level:
                    if (character.action_state[0] == 'rollf' and character.direction) \
                            or(character.action_state[0] == 'rollb' and not character.direction) \
                            or character.action_state[0] in ('kd_rollr', 'techrollr'):
                        character.update_center(x_bounds[1] - 1, character.center[1])

                    elif (character.action_state[0] == 'rollb' and character.direction) \
                            or (character.action_state[0] == 'rollf' and not character.direction) \
                            or character.action_state[0] in ('kd_rolll', 'techrolll'):
                        character.update_center(x_bounds[0] + 1, character.center[1])
                    else:
                        character.action_state = ['jump', 0]
                        character.env_state = 'airborne'
                        character.update_speed(character.speed[0])

            for wall in self.walls:
                x_level = wall[2]
                y_bounds = [wall[0], wall[1]]
                if in_bound([prev_ecb[2][1], prev_ecb[0][1]], y_bounds):
                    if wall[3]:
                        buffer_region = [x_level - (ecb[3][0] - ecb[1][0]), x_level]
                        if in_bound([ecb[1][0], ecb[3][0]], buffer_region):
                            character.update_center(x_level + (ecb[3][0] - ecb[1][0]) / 2,
                                                    character.center[1])
                    else:
                        buffer_region = [x_level, x_level + (ecb[3][0] - ecb[1][0])]
                        if in_bound([ecb[1][0], ecb[3][0]], buffer_region):
                            character.update_center(x_level - (ecb[3][0] - ecb[1][0]) / 2,
                                                    character.center[1])

            for ledges in self.ledges:
                # 1) Improve logic
                # 2) Make code less messy
                if character.env_state == 'airborne' and character.direction == ledges[2] \
                        and character.speed[1] < 0 and not controller.get_axis('y') <= -0.3 \
                        and not other_character.data['on_ledge'] == ledges:
                    if center[1] - character.attributes['edge_link'][2] > ledges[1] > \
                         center[1] - character.attributes['edge_link'][2] - character.attributes['edge_link'][1]:
                        if character.direction:
                            if center[0] < ledges[0] < center[0] + character.attributes['edge_link'][0]:
                                character.action_state = ['ledge_grab', 7]
                                character.env_state = 'ledge'
                                character.update_ecb()
                                character.update_center(ledges[0] - (character.ecb[3][0] - character.center[0]),
                                                        ledges[1] + (character.center[1] - character.ecb[2][1]))
                                character.data['on_ledge'] = ledges
                        else:
                            if center[0] > ledges[0] > center[0] - character.attributes['edge_link'][0]:
                                character.action_state = ['ledge_grab', 7]
                                character.env_state = 'ledge'
                                character.update_ecb()
                                character.update_center(ledges[0] + (character.center[0] - character.ecb[1][0]),
                                                        ledges[1] + (character.center[1] - character.ecb[2][1]))
                                character.data['on_ledge'] = ledges


class Battlefield(Stage):

    def __init__(self) -> None:
        super(Stage, self).__init__()
        self.ceiling = [[(300, 700), (900, 700)]]
        self.floor = [[290, 990, 500, False], [345, 540, 370, True], [740, 935, 370, True], [545, 735, 235, True]]
        self.walls = [[500, 700, 290, False], [500, 700, 990, True]]
        self.ledges = [(290, 500, True), (990, 500, False)]


class FinalDestination(Stage):

    def __init__(self) -> None:
        super(Stage, self).__init__()
        self.ceiling = [[(300, 700), (900, 700)]]
        self.floor = [[290, 990, 500, False], [345, 540, 370, True], [740, 935, 370, True], [545, 735, 235, True]]
        self.walls = [[500, 700, 290, False], [500, 700, 990, True]]
        self.ledges = [(290, 500, True), (990, 500, False)]


