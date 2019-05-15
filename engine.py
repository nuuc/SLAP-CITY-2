import pygame, stages, characters, random
from typing import *


def run(stage: stages.Stage, character_list: List[characters.Character]) -> None:
    for character in character_list:
        center = character.center
        air_speed = character.air_speed
        projected_center = [center[0] + air_speed[0], center[1] - air_speed[1]]
        width = character.attributes['width']
        height = character.attributes['height']
        for wall in stage.walls:
            if wall[0][1] < center[1] < wall[1][1]:
                if center[0] + width / 2 <= wall[0][0] <= projected_center[0] + width / 2:
                    character.update_center(wall[0][0] - width / 2, center[1])
                    character.update_air_speed(0, air_speed[1])
                    character.air_speed[0] = 0
                elif projected_center[0] - width / 2 <= wall[1][0] <= center[0] - width / 2:
                    character.update_center(wall[1][0] + width / 2, center[1])
                    character.update_air_speed(0, air_speed[1])
        for floor in stage.floor:
            if center[0] + width / 2 > floor[0][0] and center[0] - width / 2 < floor[1][0]:
                if projected_center[1] + height > floor[0][1]:
                    if character.action_state[0] == 'airborne':
                        character.update_center(center[0], floor[0][1] - height)
                        character.update_air_speed(0, 0)
                        character.action_state = ['grounded', 0, 'grounded', 0]
                        character.hitboxes = []
                        character.jumped = False
                    elif character.action_state[0] == 'airdodge':
                        pass
            else:
                if character.action_state[0] == 'grounded':
                    character.air_speed[0] = character.ground_speed
                    character.action_state = ['airborne', 0, 'airborne', 0]


def draw_boxes(obj: List[pygame.Rect], screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
    for thing in obj:
        pygame.draw.rect(screen, color, thing)


def draw_lines(obj: List, screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
    for thing in obj:
        pygame.draw.line(screen, color, thing[0], thing[1], 1)