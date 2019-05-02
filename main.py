import pygame, time, game_loop

pygame.init()

bounds = (1280, 720)
screen = pygame.set_display(bounds)
pygame.set_caption('Slap City 2')

while not game_loop.check_exit():
    game_loop.loop(screen)
    time.sleep(0.01666)