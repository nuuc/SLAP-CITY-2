import pygame, stages, characters, controller_handler
from typing import *


def run(stage: stages.Stage, char_control_map: Dict) -> None:
    stage.handle_stage(char_control_map)


def draw_boxes(obj: List[pygame.Rect], screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
    for thing in obj:
        pygame.draw.rect(screen, color, thing)


def draw_lines(obj: List, screen: pygame.Surface, color: Tuple[int, int, int], orientation: bool) -> None:
    if orientation:
        for thing in obj:
            coord = [(thing[0], thing[2]), (thing[1], thing[2])]
            pygame.draw.line(screen, color, coord[0], coord[1], 2)
    else:
        for thing in obj:
            coord = [(thing[2], thing[0]), (thing[2], thing[1])]
            pygame.draw.line(screen, color, coord[0], coord[1], 2)


def draw_ecb(screen: pygame.Surface, character: characters.Character) -> None:
    x = character.center[0]
    y = character.center[1]
    pygame.draw.line(screen, (128, 128, 128), (x, character.ecb[2]), (x, character.ecb[3]))
    pygame.draw.line(screen, (128, 128, 128), (character.ecb[0], y), (character.ecb[1], y))