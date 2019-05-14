import pygame, stages, characters, random
from typing import *


def run(stage: stages.Stage, character_list: List[characters.Character]) -> None:
    for character in character_list:
        width = character.attributes['width']
        height = character.attributes['height']
        for floor in stage.floor:
            if character.center[0] + width / 2 > floor[0][0] and character.center[0] - width / 2 < floor[1][0]:
                if height + character.center[1] - character.air_speed[1] > floor[0][1]:
                    if character.action_state[0] == 'airborne':
                        character.update_center(character.center[0], floor[0][1] - height)
                        character.action_state = ['grounded', 0, 'grounded', 0]
                        character.hitboxes = []
                        character.jumped = False
                        character.update_air_speed(0, 0)
                    elif character.action_state[0] == 'airdodge':
                        pass
            else:
                if character.action_state[0] == 'grounded':
                    character.air_speed[0] = character.ground_speed
                    character.action_state = ['airborne', 0, 'airborne', 0]


def draw(obj: List[pygame.Rect], screen: pygame.Surface) -> None:
    for thing in obj:
        pygame.draw.rect(screen, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), thing)