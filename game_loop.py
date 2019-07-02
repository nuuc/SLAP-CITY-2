import pygame, controller_handler, characters, engine, stages
font = pygame.font.SysFont('Comic Sans MS', 30)
tony = characters.Phrog([500, 200], False, ['jump', 0], 'airborne')
ben = characters.Phrog([600, 200], False, ['jump', 0], 'airborne')
char_control_map = {tony: 0, ben: 2}
stage = stages.Battlefield()
clock = pygame.time.Clock()


def loop(screen: pygame.Surface) -> None:
    clock.tick(60)
    controller_handler.handle(char_control_map)
    engine.run(screen, char_control_map, stage)


def check_exit() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False
