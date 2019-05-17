import pygame, time, game_loop

pygame.init()

bounds = (1280, 720)
screen = pygame.display.set_mode(bounds)
pygame.display.set_caption('Slap City 2')

while not game_loop.check_exit():
    game_loop.loop(screen)
    time.sleep(0.016666)
