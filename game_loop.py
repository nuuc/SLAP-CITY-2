import pygame, controller_handler, characters, engine, stages
font = pygame.font.SysFont('Comic Sans MS', 30)
tony = characters.CharOne([500, 200], False, ['airborne', 0, 'airborne', 0])
ben = characters.CharOne([600, 200], False, ['airborne', 0, 'airborne', 0])
char_control_map = {tony: 1, ben: 0}
stage = stages.Battlefield()
clock = pygame.time.Clock()


def loop(screen: pygame.Surface) -> None:
    controller_handler.handle(char_control_map)
    engine.run(screen, char_control_map, stage)
    clock.tick(60)


def freeze(frame: int) -> None:
    while frame > 0:
        frame -= 1
        clock.tick(60)


def check_exit() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False
