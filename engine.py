import pygame, stages, characters, random
from typing import *


def run(stage: stages.Stage, character_list: List[characters.Character]) -> None:
    for character in character_list:
        pcenter = character.center[:]
        character.update()
        center = character.center
        size = [character.attributes['width'], character.attributes['height']]
        for floor in stage.floor:
            if pcenter[1] + size[1] <= floor[2]:
                if in_bound(center[0], size[0], [floor[0], floor[1]]):
                    if center[1] + size[1] >= floor[2] > pcenter[1] + size[1]:
                        character.update_center(center[0], floor[2] - size[1])
                        character.action_state = ['grounded', 0, 'grounded', 0]
                        character.hitboxes = []
                else:
                    if in_bound(pcenter[0], size[0], [floor[0], floor[1]]) and center[1] + size[1] == floor[2]:
                        character.update_air_speed(ground_speed, 0)
                        character.action_state = ['airborne', 0, 'airborne', 0]
        for wall in stage.walls:
            if wall[0] < center[1] + size[1] and center[1] - size[1] < wall[1]:
                if pcenter[0] + size[0] / 2 <= wall[2] <= center[0] + size[0] / 2:
                    character.update_center(wall[2] - size[0] / 2, center[1])
                    character.update_air_speed(0, character.air_speed[1])
                    character.ground_speed = 0
                elif center[0] - size[0] / 2 <= wall[2] <= pcenter[0] - size[0] / 2:
                    character.update_center(wall[2] + size[0] / 2, center[1])
                    character.update_air_speed(0, character.air_speed[1])
                    character.ground_speed = 0


def in_bound(pos: float, size: float, bounds: List) -> bool:
    if bounds[0] < pos + size / 2 and pos - size / 2 < bounds[1]:
        return True
    return False


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