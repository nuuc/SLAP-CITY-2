import pygame, controller_handler, characters, engine, stages, random

tony = characters.CharOne([500, 300], False, ['airborne', 0, 'airborne', 0])
stage = stages.FD()


def loop(screen: pygame.Surface) -> None:
    # TODO: 1) Detect inputs

    controller_handler.handle(tony, 4)

    # TODO: 2) Update characters, run engine to check event data (possibly in reverse order)
    engine.run(stage, [tony])
    tony.update()

    # For 2), update each character using their update function
    # TODO: 3) Draw screen
    screen.fill((255, 255, 255))
    engine.draw(tony.hurtboxes, screen)
    engine.draw(tony.hitboxes, screen)
    for floor in stages.FD().floor:
        pygame.draw.line(screen, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                         floor[0], floor[1], 1)
    pygame.display.update()


def check_exit() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False
