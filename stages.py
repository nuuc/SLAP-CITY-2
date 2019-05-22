import controller_handler, characters
from typing import *


def in_bound(ecb: List[float], bounds: List) -> bool:
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

    def __init__(self) -> None:
        raise NotImplementedError

    def handle_stage(self, char_control_map: Dict) -> None:
        for character in char_control_map:
            char_input = controller_handler.controller_input[char_control_map[character]]
            prev_ecb = character.get_attr()['ecb']
            character.update()
            center = character.center
            ecb = character.ecb
            for floor in self.floor:
                x_bounds = [floor[0], floor[1]]
                y_level = floor[2]
                if in_bound(ecb, x_bounds):
                    if ecb[3] > y_level >= prev_ecb[3]:
                        if character.action_state[0] == 'airdodge':
                            character.ground_speed = character.air_speed[0]
                            character.action_state = ['waveland', 0, 'grounded', 0]
                            character.update_center(center[0], y_level + (center[1] - ecb[3]))
                            # ecb[3] should be the ecb for when the character is on the ground, not when it's in the
                            # air. I'm thinking of writing a get_ecb() function that gets ecb based on action state
                            # and frame so that this properly updates.
                            character.invincible = [False, 0]
                            character.update_air_speed(0, 0)
                            character.jumped = False
                        elif not char_input.get_axis(1) <= -0.3 or not floor[3]:
                            character.update_air_speed(0, 0)
                            character.jumped = False
                            character.action_state = ['grounded', 0, 'grounded', 0]
                            character.update_center(center[0], y_level + (center[1] - ecb[3]))
                            # Same thing as last comment here.
                            character.hitboxes = [[], [], False]
                    elif char_input.get_axis_change(1, 0.25, 0.3) and char_input.axis_list[0][1] < 0 \
                            and ecb[3] == y_level and floor[3]:
                        character.update_center(center[0], center[1] + 1)
                        character.update_air_speed(0, -character.attributes['max_vair_speed'])
                        character.action_state = ['airborne', 0, 'airborne', 0]
                elif in_bound(prev_ecb, x_bounds) and ecb[3] == y_level:
                    character.update_air_speed(character.ground_speed, 0)
                    character.action_state = ['airborne', 0, 'airborne', 0]
            for wall in self.walls:
                x_level = wall[2]
                y_bounds = [wall[0], wall[1]]
                if in_bound([ecb[2], ecb[3]], y_bounds):
                    if prev_ecb[1] <= x_level <= ecb[1]:
                        character.update_center(x_level + (center[0] - ecb[1]), center[1])
                        character.update_air_speed(0, character.air_speed[1])
                        character.ground_speed = 0
                    elif ecb[0] <= x_level <= prev_ecb[0]:
                        character.update_center(x_level + (center[0] - ecb[0]), center[1])
                        character.update_air_speed(0, character.air_speed[1])
                        character.ground_speed = 0

class Battlefield(Stage):

    def __init__(self) -> None:
        super(Stage, self).__init__()
        self.ceiling = [[(300, 700), (900, 700)]]
        self.floor = [[290, 990, 500, False], [345, 540, 370, True], [740, 935, 370, True], [545, 735, 235, True]]
        self.walls = [[500, 700, 290], [500, 700, 990]]

