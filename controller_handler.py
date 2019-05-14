import pygame, characters, math
from typing import *

pygame.init()
pygame.joystick.init()


def controller_mapping(x: int, y: int, dead_zone: float) -> List:
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


class Input:
    button_list: List
    axis_list: List
    joystick_id: int

    def __init__(self, joystick_id: int) -> None:
        inputs = [[], []]
        joystick = pygame.joystick.Joystick(joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs[0].insert(i, joystick.get_button(i))
        for i in range(0, 4, 2):
            inputs[1].insert(i, controller_mapping(joystick.get_axis(i), joystick.get_axis(i+1), 0.15)[0])
            inputs[1].insert(i + 1, controller_mapping(joystick.get_axis(i), joystick.get_axis(i + 1), 0.15)[1])
        self.button_list = [inputs[0], inputs[0]]
        self.axis_list = [inputs[1], inputs[1]]
        self.joystick_id = joystick_id

    def update(self) -> None:
        self.button_list = [self.get_input()[0], self.button_list[0]]
        self.axis_list = [self.get_input()[1], self.axis_list[0]]

    def get_button_change(self, button: int) -> bool:
        if self.button_list[0][button] and not self.button_list[1][button]:
            return True
        return False

    def get_axis_change(self, axis: int) -> bool:
        if self.axis_list[0][axis] and not self.axis_list[1][axis]:
            return True
        return False

    def get_input(self) -> List:
        inputs = [[], []]
        joystick = pygame.joystick.Joystick(self.joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs[0].insert(i, joystick.get_button(i))
        for i in range(0, 4, 2):
            inputs[1].insert(i, controller_mapping(joystick.get_axis(i), joystick.get_axis(i+1), 0.15)[0])
            inputs[1].insert(i + 1, controller_mapping(joystick.get_axis(i), joystick.get_axis(i + 1), 0.15)[1])
        return inputs


controller_input = []
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()
    controller_input.append(Input(i))


def handle(char: characters.Character, joystick_id: int) -> None:
    joystick = pygame.joystick.Joystick(joystick_id)
    joystick_input = controller_input[joystick_id]
    joystick_input.update()
    control_stick_tilt = [joystick.get_axis(0), joystick.get_axis(1)]
    cstick_tilt = [joystick.get_axis(3), -1 * joystick.get_axis(2)]
    control_stick_mapping = controller_mapping(control_stick_tilt[0], control_stick_tilt[1], 0.15)
    cstick_mapping = controller_mapping(cstick_tilt[0], cstick_tilt[1], 0.15)
    if control_stick_mapping != [0, 0]:
        char.move(control_stick_tilt[0])
    else:
        char.move(0)
    if char.action_state[2] == 'airborne':
        if joystick_input.get_button_change(1) or joystick_input.get_axis_change(2) \
                or joystick_input.get_axis_change(3):
            if control_stick_mapping == [0, 1] or cstick_mapping == [0, 1]:
                char.upair()
            if control_stick_mapping == [0, -1] or cstick_mapping == [0, -1]:
                char.dair()
            if char.direction:
                if control_stick_mapping == [1, 0] or cstick_mapping == [1, 0]:
                    char.fair()
                elif control_stick_mapping == [-1, 0] or cstick_mapping == [-1, 0]:
                    char.bair()
            elif not char.direction:
                if control_stick_mapping == [1, 0] or cstick_mapping == [1, 0]:
                    char.bair()
                elif control_stick_mapping == [-1, 0] or cstick_mapping == [-1, 0]:
                    char.fair()
        elif joystick_input.get_button_change(3):
            char.fullhop()
    if char.action_state[0] == 'grounded':
        if abs(control_stick_tilt[0]) > 0.25 and joystick_input.get_button_change(1):
            char.ftilt()
        elif joystick_input.get_button_change(3):
            char.fullhop()
        elif joystick_input.get_button_change(0):
            char.shorthop()
