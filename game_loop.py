import pygame

def loop(screen: pygame.Surface) -> None:
    #TODO: 1) Detect inputs
    #TODO: 2) Update characters
    #For 2), update each character using their update function
    #TODO: 3) Draw screen

def check_exit() -> None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False