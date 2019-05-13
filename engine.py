import pygame, stages, characters, random
from typing import *


def run(stage: stages.Stage, character_list: List[characters.Character]) -> None:
    for character in character_list:
        width = character.attributes['width']
        height = character.attributes['height']
        for floor in stage.floor:
            if height + character.center[1] - character.air_speed[1] > floor[0][1]\
                    and character.center[0] + width > floor[0][0] and character.center[0] - width < floor[1][0]:
                if character.action_state[0] == 'airborne':
                    character.update_center(character.center[0], floor[0][1] - height)
                    character.action_state = ['grounded', 0, 'grounded', 0]
                    character.hitboxes = []
                    character.air_speed = [0, 0]
                elif character.action_state[0] == 'airdodge':
                    pass


def draw(obj: List[pygame.Rect], screen: pygame.Surface) -> None:
    for thing in obj:
        pygame.draw.rect(screen, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), thing)