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
            prev_ecb = character.get_attr()['ecb']
            character.update()
            center = character.center
            ecb = character.ecb
            for floor in self.floor:
                x_bounds = [floor[0], floor[1]]
                y_level = floor[2]
                if prev_ecb[3] <= y_level:
                    if in_bound(ecb, x_bounds):
                        if ecb[3] >= y_level > prev_ecb[3]:
                            if not controller_handler.get_axis(char_control_map[character])[1] <= -0.5 or not floor[3]:
                                character.action_state = ['grounded', 0, 'grounded', 0]
                                character.update_center(center[0], y_level + (center[1] - ecb[3]))
                                character.hitboxes = []
                        if controller_handler.get_axis(char_control_map[character])[1] <= -0.5 and ecb[3] == y_level \
                                and floor[3]:
                            character.update_center(center[0], center[1] + 1)
                            character.action_state = ['airborne', 0, 'airborne', 0]
                    else:
                        if in_bound(prev_ecb, x_bounds) and ecb[3] == y_level:
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


class FD(Stage):

    def __init__(self) -> None:
        super(Stage, self).__init__()
        self.ceiling = [[(300, 700), (900, 700)]]
        self.floor = [[400, 600, 375, True], [550, 700, 300, True], [800, 1000, 350, True], [300, 900, 500, False]]
        self.walls = [[500, 700, 300], [500, 700, 900]]

