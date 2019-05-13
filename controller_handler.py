import pygame, characters

pygame.init()
pygame.joystick.init()
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()


def handle(char: characters.Character, joystick_id: int) -> None:
    joystick = pygame.joystick.Joystick(joystick_id)
    x_tilt = joystick.get_axis(0)
    y_tilt = joystick.get_axis(1)
    char.move(x_tilt)
    if char.action_state[2] == 'airborne':
        if char.direction and joystick.get_button(1):
            if abs(y_tilt) < 0.25 < x_tilt:
                char.fair()
            if x_tilt < -0.25 < -1 * abs(y_tilt):
                char.bair()
        if not char.direction and joystick.get_button(1):
            if abs(y_tilt) < 0.25 < x_tilt:
                char.bair()
            if x_tilt < -0.25 < -1 * abs(y_tilt):
                char.fair()
    if char.action_state[0] == 'grounded':
        if abs(x_tilt) > 0.25 and joystick.get_button(1):
            char.ftilt()
        elif joystick.get_button(3):
            char.fullhop()
        elif joystick.get_button(0):
            char.shorthop()
