import controller_handler, characters
from typing import *


def in_bound(ecb: List, bounds: List) -> bool:
    if bounds[0] < ecb[1] and ecb[0] < bounds[1]:
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
        for character in char_control_map:
            char_input = controller_handler.controller_input[char_control_map[character]]
            prev_ecb = character.ecb.copy()
            character.update()
            center = character.center
            ecb = character.ecb
            for floor in self.floor:
                x_bounds = [floor[0], floor[1]]
                y_level = floor[2]
                if in_bound([ecb[1][0], ecb[3][0]], x_bounds):
                    if ecb[0][1] > y_level >= prev_ecb[0][1]:
                        if character.action_state[0] == 'airdodge':
                            character.ground_speed = character.air_speed[0]
                            character.action_state = ['waveland', 0, 'grounded', 0]
                            character.invincible = False
                            character.update_ecb()
                            character.update_center(center[0], y_level + (center[1] - character.ecb[0][1]))
                            character.update_air_speed(0, 0)
                            character.jumped = False

                        elif (character.action_state[2] == 'hitstun' and character.misc_data['KB'] >= 80) \
                                or character.action_state[2] == 'tumble':
                            character.update_air_speed(0, 0)
                            character.jumped = False
                            character.action_state = ['knockdown', 0, 'knockdown', 0]
                            character.update_air_speed(0, 0)
                            character.update_ecb()
                            character.update_center(center[0], y_level + (center[1] - character.ecb[0][1]))

                        elif (not char_input.get_axis(1) <= -0.3 or not floor[3]) \
                                or (character.action_state[2] == 'hitstun' and character.misc_data['KB'] < 80):
                            character.ground_speed = character.air_speed[0]
                            character.update_air_speed(0, 0)
                            character.jumped = False
                            character.action_state = ['grounded', 0, 'grounded', 0]
                            character.update_ecb()
                            character.update_center(center[0], y_level + (center[1] - character.ecb[0][1]))
                            character.hitboxes['regular'] = [[], [], False]

                    elif char_input.get_axis_change(1, 0.25, 0.3) and char_input.axis_list[0][1] < 0 \
                            and ecb[0][1] == y_level and floor[3]:
                        character.update_center(center[0], center[1] + 1)
                        character.update_air_speed(0, -character.attributes['max_vair_speed'])
                        character.action_state = ['airborne', 0, 'airborne', 0]

                elif in_bound([prev_ecb[1][0], prev_ecb[3][0]], x_bounds) and ecb[0][1] == y_level:
                    character.update_air_speed(character.ground_speed, 0)
                    character.action_state = ['airborne', 0, 'airborne', 0]

            for wall in self.walls:
                x_level = wall[2]
                y_bounds = [wall[0], wall[1]]
                if in_bound([ecb[2][1], ecb[0][1]], y_bounds):
                    if prev_ecb[3][0] <= x_level <= ecb[3][0]:
                        character.update_center(x_level + (center[0] - ecb[3][0]), center[1])
                        character.update_air_speed(0, character.air_speed[1])
                        character.ground_speed = 0

                    elif ecb[1][0] <= x_level <= prev_ecb[1][0]:
                        character.update_center(x_level - (center[0] - ecb[3][0]), center[1])
                        character.update_air_speed(0, character.air_speed[1])
                        character.ground_speed = 0

            for ledges in self.ledges:
                # 1) Improve logic
                # 2) Make code less messy
                if character.action_state[0] == 'airborne' and character.direction == ledges[2] \
                        and character.air_speed[1] < 0 and not char_input.get_axis(1) <= -0.3:
                    if center[1] - character.attributes['edge_link'][2] > ledges[1] > \
                         center[1] - character.attributes['edge_link'][2] - character.attributes['edge_link'][1]:
                        if character.direction:
                            if center[0] < ledges[0] < center[0] + character.attributes['edge_link'][0]:
                                character.action_state = ['ledge_grab', 7, 'ledge_grab', 0]
                                character.update_ecb()
                                character.update_center(ledges[0] - (character.ecb[3][0] - character.center[0]),
                                                        ledges[1] + (character.center[1] - character.ecb[2][1]))
                        else:
                            if center[0] > ledges[0] > center[0] - character.attributes['edge_link'][0]:
                                character.action_state = ['ledge_grab', 7, 'ledge_grab', 0]
                                character.update_ecb()
                                character.update_center(ledges[0] + (character.center[0] - character.ecb[1][0]),
                                                        ledges[1] + (character.center[1] - character.ecb[2][1]))


class Battlefield(Stage):

    def __init__(self) -> None:
        super(Stage, self).__init__()
        self.ceiling = [[(300, 700), (900, 700)]]
        self.floor = [[290, 990, 500, False], [345, 540, 370, True], [740, 935, 370, True], [545, 735, 235, True]]
        self.walls = [[500, 700, 290], [500, 700, 990]]
        self.ledges = [(290, 500, True), (990, 500, False)]


