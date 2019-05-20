import pygame, controller_handler, characters, engine, stages, random

tony = characters.CharOne([500, 200], False, ['airborne', 0, 'airborne', 0])
ben = characters.CharOne([600, 200], False, ['airborne', 0, 'airborne', 0])
char_control_map = {tony: 1, ben: 4}
stage = stages.FD()


def loop(screen: pygame.Surface) -> None:
    controller_handler.handle(char_control_map)
    engine.run(stage, char_control_map)
    screen.fill((255, 255, 255))
    for character in char_control_map:
        if character.invincible[0]:
            engine.draw_boxes(character.hurtboxes, screen, (0, 0, 255))
        else:
            engine.draw_boxes(character.hurtboxes, screen, (0, 0, 0))
        engine.draw_boxes(character.hitboxes, screen, (255, 0, 0))

    engine.draw_lines(stage.floor, screen, (0, 255, 0), True)
    engine.draw_lines(stage.walls, screen, (0, 0, 255), False)
    engine.draw_ecb(screen, tony)
    engine.draw_ecb(screen, ben)
    pygame.display.update()


def check_exit() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False
