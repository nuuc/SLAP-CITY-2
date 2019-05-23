import pygame, characters, math, game_loop, engine
from typing import *

CTRL_STICK_RADIUS = 0.8
pygame.init()
pygame.joystick.init()


class Input:
    """
    A class containing information and methods of a controller, including previous button presses.

    === PUBLIC ATTRIBUTES ==
    'button_list': A list with the first index containing the current button press, and the second containing the
    button presses on the previous frame.
    'axis_list': A list with the first index containing the current axis input, and the second containing the axis
    input on the previous frame.
    joystick_id: An integer that maps which controller an Input object is connected to.
    """
    button_list: List
    axis_list: List
    joystick_id: int

    def __init__(self, joystick_id: int) -> None:
        inputs = [[], []]
        joystick = pygame.joystick.Joystick(joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs[0].insert(i, joystick.get_button(i))
        for i in range(joystick.get_numaxes()):
            inputs[1].insert(i, joystick.get_axis(i))
        self.button_list = [inputs[0], inputs[0]]
        self.axis_list = [inputs[1], inputs[1]]
        self.joystick_id = joystick_id

    def update(self) -> None:
        """
        Updates the button and axis list to the current frame.
        """
        self.button_list = [self.get_input()[0], self.button_list[0]]
        self.axis_list = [self.get_input()[1], self.axis_list[0]]

    @staticmethod
    def controller_mapping(x: float, y: float, dead_zone: float) -> List:
        """
        Takes an input of the axis position and maps the controller into five regions: Left, right, up, down, and a
        dead zone region, according to 'dead_zone'.
        """
        if math.sqrt(x ** 2 + y ** 2) < dead_zone:
            return [0, 0]
        else:
            if x > abs(y):
                return [1, 0]
            elif x < -1 * abs(y):
                return [-1, 0]
            elif abs(x) < y:
                return [0, 1]
            elif -1 * abs(x) > y:
                return [0, -1]
        return [0, 0]

    @staticmethod
    def get_angle(tilt: List) -> float:
        """
        Gets the angle of tilt in radians.
        """
        return math.atan2(tilt[1], tilt[0])

    def get_button_change(self, button: int) -> bool:
        """
        Checks if 'button' is pressed this frame, and is not pressed last frame.
        """
        if self.button_list[0][button] and not self.button_list[1][button]:
            return True
        return False

    def get_axis_change(self, axis: int, prev_dead_zone: float, curr_dead_zone: float) -> bool:
        """
        Checks if axis was within 'prev_dead_zone' last frame and is not within curr_dead_zone this frame.
        """
        if axis < 2:
            prev = self.controller_mapping(self.axis_list[1][0], self.axis_list[1][1], prev_dead_zone)
            curr = self.controller_mapping(self.axis_list[0][0], self.axis_list[0][1], curr_dead_zone)
            if prev == [0, 0] and curr[axis]:
                return True
            return False
        else:
            prev = self.controller_mapping(self.axis_list[1][3], self.axis_list[1][2], prev_dead_zone)
            curr = self.controller_mapping(self.axis_list[0][3], self.axis_list[0][2], curr_dead_zone)
            if prev == [0, 0] and curr[axis - 2]:
                return True
            return False

    def get_input(self) -> List:
        """
        A helper function that records the input to be used in the update function.
        """
        inputs = [[], []]
        joystick = pygame.joystick.Joystick(self.joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs[0].insert(i, joystick.get_button(i))
        for i in range(joystick.get_numaxes()):
            inputs[1].insert(i, joystick.get_axis(i))
        inputs[1][1] *= -1
        inputs[1][2] *= -1
        return inputs

    def get_axis(self, axis: int) -> float:
        """
        Returns the axis value on this frame.
        """
        return self.axis_list[0][axis]

    def get_button(self, button: int) -> bool:
        """
        Returns the button value on this frame.
        """
        return self.button_list[0][button]


controller_input = []
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()
    controller_input.append(Input(i))


def handle(char_control_map: Dict) -> None:
    """
    Handles character inputs according to which controller they are mapped to.
    """
    for character in char_control_map:
        controller = controller_input[char_control_map[character]]
        controller.update()
        ctrl_stick = [controller.get_axis(0), controller.get_axis(1)]
        cstick = [controller.get_axis(3), controller.get_axis(2)]
        ctrl_stick_mapping = controller.controller_mapping(ctrl_stick[0], ctrl_stick[1], 0.15)
        cstick_mapping = controller.controller_mapping(cstick[0], cstick[1], 0.15)
        if controller.get_button_change(12):
            game_loop.freeze(20)
        if ctrl_stick_mapping != [0, 0]:
            character.move(ctrl_stick[0])
        else:
            character.move(0)
        if character.action_state[0] == 'airborne':
            if controller.get_button_change(1) or controller.get_axis_change(2, 0.1, 0.11) \
                    or controller.get_axis_change(3, 0.1, 0.11):
                if ctrl_stick_mapping[1] == 1 or cstick_mapping[1] == 1:
                    character.upair()
                elif ctrl_stick_mapping[1] == -1 or cstick_mapping[1] == -1:
                    character.dair()
                if character.direction:
                    if ctrl_stick_mapping[0] == 1 or cstick_mapping[0] == 1:
                        character.fair()
                    elif ctrl_stick_mapping[0] == -1 or cstick_mapping[0] == -1:
                        character.bair()
                elif not character.direction:
                    if ctrl_stick_mapping[0] == 1 or cstick_mapping[0] == 1:
                        character.bair()
                    elif ctrl_stick_mapping[0] == -1 or cstick_mapping[0] == -1:
                        character.fair()
            elif controller.get_axis_change(1, 0.25, 0.3) and character.air_speed[1] < 0:
                character.update_air_speed(character.air_speed[0], -character.attributes['max_vair_speed'])
            elif controller.get_button_change(3):
                character.jump(True)
            elif controller.get_button_change(4) or controller.get_button_change(5):
                if ctrl_stick_mapping != [0, 0]:
                    character.airdodge(controller.get_angle(ctrl_stick))
                else:
                    character.airdodge([0, 0])

        elif character.action_state[0] == 'grounded' or character.action_state[0] == 'waveland':
            if abs(ctrl_stick[0]) > 0.25 and controller.get_button_change(1):
                character.ftilt()
            elif controller.get_button_change(3):
                character.jump(False)
            elif controller.get_button_change(0):
                character.jump(True)
            elif character.action_state[2] == 'jumpsquat' and controller.button_list[0][5] \
                    and not ctrl_stick_mapping == [0, 0]:
                character.auto_wavedash(controller.get_angle(ctrl_stick))

        elif character.action_state[0] == 'hitlag' and character.action_state[1] == 2 and \
                character.action_state[3] is not None:
            if ctrl_stick_mapping != [0, 0]:
                engine.handle_hit(character, character.action_state[3], controller.get_angle(ctrl_stick))
            else:
                engine.handle_hit(character, character.action_state[3], None)

