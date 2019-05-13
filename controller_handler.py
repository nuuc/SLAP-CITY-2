import pygame, characters
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


def handle(char: characters.Character, joystick_id: int) -> None:
    joystick = pygame.joystick.Joystick(joystick_id)
    joystick_input = controller_input[joystick_id]
    joystick_input.update()
    x_tilt = joystick.get_axis(0)
    y_tilt = joystick.get_axis(1)
    char.move(x_tilt)
    if char.action_state[2] == 'airborne':
        if char.direction and joystick_input.get_change(1):
            if abs(y_tilt) < 0.25 < x_tilt:
                char.fair()
            if x_tilt < -0.25 < -1 * abs(y_tilt):
                char.bair()
        if not char.direction and joystick_input.get_change(1):
            if abs(y_tilt) < 0.25 < x_tilt:
                char.bair()
            if x_tilt < -0.25 < -1 * abs(y_tilt):
                char.fair()
        if joystick_input.get_change(3):
            char.fullhop()
    if char.action_state[0] == 'grounded':
        if abs(x_tilt) > 0.25 and joystick_input.get_change(1):
            char.ftilt()
        elif joystick_input.get_change(3):
            char.fullhop()
        elif joystick_input.get_change(0):
            char.shorthop()
