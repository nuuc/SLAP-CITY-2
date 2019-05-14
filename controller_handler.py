import pygame, characters, math
from typing import *

pygame.init()
pygame.joystick.init()


class Input:
    input_list: List
    joystick_id: int

    def __init__(self, joystick_id: int) -> None:
        inputs = []
        joystick = pygame.joystick.Joystick(joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs.insert(i, joystick.get_button(i))
        self.input_list = [inputs, inputs]
        self.joystick_id = joystick_id

    def update(self) -> None:
        self.input_list = [self.get_input(), self.input_list[0]]

    def get_change(self, button: int) -> bool:
        if self.input_list[0][button] and not self.input_list[1][button]:
            return True
        return False

    def get_input(self) -> List:
        inputs = []
        joystick = pygame.joystick.Joystick(self.joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs.insert(i, joystick.get_button(i))
        return inputs


controller_input = []
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()
    controller_input.append(Input(i))


def controller_mapping(x: int, y: int) -> List:
    if math.sqrt(x ** 2 + y ** 2) < 0.15:
        return [0, 0]
    else:
        if x > abs(y):
            return [1, 0]
        elif x < -1 * abs(y):
            return [-1, 0]



def handle(char: characters.Character, joystick_id: int) -> None:
    joystick = pygame.joystick.Joystick(joystick_id)
    joystick_input = controller_input[joystick_id]
    joystick_input.update()
    x_tilt = joystick.get_axis(0)
    y_tilt = joystick.get_axis(1)
    mapping = controller_mapping(x_tilt, y_tilt)
    if mapping != [0, 0]:
        char.move(x_tilt)
    else:
        char.move(0)
    if char.action_state[2] == 'airborne':
        if char.direction and joystick_input.get_change(1):
            if mapping == [1, 0]:
                char.fair()
            elif mapping == [-1, 0]:
                char.bair()
        elif not char.direction and joystick_input.get_change(1):
            if mapping == [1, 0]:
                char.bair()
            elif mapping == [-1, 0]:
                char.fair()
        elif joystick_input.get_change(3):
            char.fullhop()
    if char.action_state[0] == 'grounded':
        if abs(x_tilt) > 0.25 and joystick_input.get_change(1):
            char.ftilt()
        elif joystick_input.get_change(3):
            char.fullhop()
        elif joystick_input.get_change(0):
            char.shorthop()
