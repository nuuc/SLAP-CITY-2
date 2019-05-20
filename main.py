import pygame, time, game_loop, datetime

pygame.init()
clock = pygame.time.Clock()
bounds = (1280, 720)
screen = pygame.display.set_mode(bounds)
pygame.display.set_caption('Slap City 2')
frame = True
while not game_loop.check_exit():
    game_loop.loop(screen)
    clock.tick(60)

print(clock.get_fps())
