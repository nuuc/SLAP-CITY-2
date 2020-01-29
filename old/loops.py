import pygame, controller_handler, characters, engine, stages
font = pygame.font.SysFont('Comic Sans MS', 30)
tony = characters.Dummy()
ben = characters.Dummy()
tony.center = [500, 500]
ben.center = [600, 500]
default_mapping = {'a': 1, 'b': 2, 'y': 3, 'x': 0, 'rtrigger': 4, 'ltrigger': 5, 'dpadup': 12, 'dpaddown': 14,
                   'dpadleft': 15, 'dpadright': 13, 'z': 7, 'start': 9}
char_control_map = {0: tony, 2: ben}
ch = controller_handler.ControllerHandler(char_control_map,
                                          {0: controller_handler.InputMapping(default_mapping, 'default'),
                                           2: controller_handler.InputMapping(default_mapping, 'default')})
stage = stages.Battlefield()
clock = pygame.time.Clock()


def game_loop(screen: pygame.Surface) -> None:
    clock.tick(60)
    ch.handle_controls()
    engine.run(screen, ch.char_control_map, stage)


def menu_loop(screen: pygame.Surface) -> None:
    pass


def check_exit() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False
