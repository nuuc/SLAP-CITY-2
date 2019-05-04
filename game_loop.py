import pygame, controller_handler, characters

tony = characters.CharOne([500, 500], False, ["grounded", 0])


def loop(screen: pygame.Surface) -> None:
    # TODO: 1) Detect inputs

    controller_handler.handle(tony)

    # TODO: 2) Update characters, run engine to check event data (possibly in reverse order)

    tony.update()

    # For 2), update each character using their update function
    # TODO: 3) Draw screen
    screen.fill((255, 255, 255))
    for hitbox in tony.hitboxes:
        pygame.draw.rect(screen, (0, 255, 255), hitbox)
    for hurtbox in tony.hurtboxes:
        pygame.draw.rect(screen, (0, 0, 255), hurtbox)
    pygame.display.update()


def check_exit() -> None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False