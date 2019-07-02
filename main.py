import pygame, game_loop, characters, engine

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

# num_ms = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
# print(engine.total_elapsed / engine.t)
# print(engine.total_list)
# for time in engine.total_list:
#     ms = round(time * 1000)
#     num_ms[ms] += 1
# print(num_ms)