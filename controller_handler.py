import pygame, characters, math, game_loop
from typing import *

pygame.init()
pygame.joystick.init()
CTRL_STICK_RADIUS = 0.8

class Input:
    button_list: List
    axis_list: List
    joystick_id: int
    """
    Don't worry too much about the implementation of this. Basically, button_list stores the current and previous
    frame's button data, and the axis_list does the same, respectively. The class methods should be pretty
    self-explanatory and they should be simple enough to understand that you'll get it almost immediately.
    """

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
        self.button_list = [self.get_input()[0], self.button_list[0]]
        self.axis_list = [self.get_input()[1], self.axis_list[0]]

    @staticmethod
    def controller_mapping(x: float, y: float, dead_zone: float) -> List:
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
    def max_of_angle(angle: List) -> List:
        radius = math.sqrt(angle[0] ** 2 + angle[1] ** 2)
        ratio = CTRL_STICK_RADIUS / radius
        return [angle[0] * ratio, angle[1] * ratio]

    def get_button_change(self, button: int) -> bool:
        if self.button_list[0][button] and not self.button_list[1][button]:
            return True
        return False

    def get_axis_change(self, axis: int, prev_dead_zone: float, curr_dead_zone: float) -> bool:
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
        return self.axis_list[0][axis]


controller_input = []
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()
    controller_input.append(Input(i))


def handle(char_control_map: Dict) -> None:
    for character in char_control_map:
        joystick_input = controller_input[char_control_map[character]]
        joystick_input.update()
        ctrl_stick_tilt = [joystick_input.get_axis(0), joystick_input.get_axis(1)]
        cstick_tilt = [joystick_input.get_axis(3), joystick_input.get_axis(2)]
        ctrl_stick_mapping = joystick_input.controller_mapping(ctrl_stick_tilt[0], ctrl_stick_tilt[1], 0.15)
        cstick_mapping = joystick_input.controller_mapping(cstick_tilt[0], cstick_tilt[1], 0.15)
        if joystick_input.get_button_change(12):
            game_loop.freeze(20)
        if ctrl_stick_mapping != [0, 0]:
            character.move(ctrl_stick_tilt[0])
        else:
            character.move(0)
        if character.action_state[2] == 'airborne':
            if joystick_input.get_button_change(1) or joystick_input.get_axis_change(2, 0.1, 0.11) \
                    or joystick_input.get_axis_change(3, 0.1, 0.11):
                if ctrl_stick_mapping == [0, 1] or cstick_mapping[1] == 1:
                    character.upair()
                if ctrl_stick_mapping == [0, -1] or cstick_mapping[1] == -1:
                    character.dair()
                if character.direction:
                    if ctrl_stick_mapping == [1, 0] or cstick_mapping[0] == 1:
                        character.fair()
                    elif ctrl_stick_mapping == [-1, 0] or cstick_mapping[0] == -1:
                        character.bair()
                elif not character.direction:
                    if ctrl_stick_mapping == [1, 0] or cstick_mapping[0] == 1:
                        character.bair()
                    elif ctrl_stick_mapping == [-1, 0] or cstick_mapping[0] == -1:
                        character.fair()
            elif joystick_input.get_button_change(3):
                character.fullhop()
            elif joystick_input.get_button_change(4) or joystick_input.get_button_change(5):
                if ctrl_stick_mapping != [0, 0]:
                    character.airdodge(joystick_input.max_of_angle(ctrl_stick_tilt))
                else:
                    character.airdodge([0, 0])
        elif character.action_state[0] == 'grounded' or character.action_state[0] == 'waveland':
            if abs(ctrl_stick_tilt[0]) > 0.25 and joystick_input.get_button_change(1):
                character.ftilt()
            elif joystick_input.get_button_change(3):
                character.fullhop()
            elif joystick_input.get_button_change(0):
                character.shorthop()
        elif character.action_state[0] == 'fullhop_jumpsquat' or character.action_state[0] == 'shorthop_jumpsquat':
            if ctrl_stick_mapping != [0, 0]:
                character.auto_wavedash(joystick_input.max_of_angle(ctrl_stick_tilt))
