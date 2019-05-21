import pygame, stages, characters, controller_handler
from typing import *


def run(stage: stages.Stage, char_control_map: Dict) -> None:
    stage.handle_stage(char_control_map)
    hitbox_collision(char_control_map)



def hitbox_collision(char_control_map: Dict) -> None:
    for character in char_control_map:
        if not character.hitboxes[2]:
            copy = char_control_map.copy()
            del copy[character]
            other_character = list(copy.keys())[0]
            for i in range(len(character.hitboxes[0])):
                hitbox = character.hitboxes[0][i]
                if not hitbox.collidelist(other_character.hurtboxes) == -1:
                    character.hitboxes[2] = True
                    hitbox_data = character.hitboxes[1][i]
                    other_character.damage += hitbox_data['damage']
                    multiplier = hitbox_data['base_kb'] * hitbox_data['kb_growth']
                    other_character.air_speed = [hitbox_data['direction'][0] * multiplier,
                                                 hitbox_data['direction'][1] * multiplier]
                    print(multiplier / 10)
                    other_character.action_state = ['airborne', 0, 'hitstun', int(multiplier / 10)]




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
