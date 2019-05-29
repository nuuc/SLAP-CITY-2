import pygame, game_loop

pygame.init()
bounds = (1280, 720)
screen = pygame.display.set_mode(bounds)
pygame.display.set_caption('Slap City 2')
while not game_loop.check_exit():
    # for event in pygame.event.get():
    #     if event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_LEFT:
    #             game_loop.loop(screen)

    game_loop.loop(screen)

