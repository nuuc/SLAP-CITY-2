import pygame, characters

pygame.init()
pygame.joystick.init()
joystick_one = pygame.joystick.Joystick(4) # Hard coding this for now, will need to change to account all controllers
# How I would account for all controllers would be to do something like:
# for c in range(pygame.joystick.get_count())
#   pygame.joystick.Joystick(c).init()
joystick_one.init()


def handle(char: characters.Character) -> None:
    x_tilt = joystick_one.get_axis(0)
    char.walk(x_tilt)
    if abs(x_tilt) > 0.3 and joystick_one.get_button(1):
        if char.action_state[0] != 'ftilt':
            char.ftilt()
