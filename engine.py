import pygame, stages, characters, math
from typing import *
HITSTUN = 0.4
KB_LAUNCH_CONVERSION = 0.15
GROUND_KB_CONVERSION = 0.8


def run(screen: pygame.Surface, char_control_map: Dict, stage: stages.Stage) -> None:
    """
    Handles stage interactions, draws the screen, and then detects hitbox collision.
    """
    stage.handle_stage(char_control_map)
    developer_draw_all(screen, char_control_map, stage)
    hitbox_collision(char_control_map)


def hitbox_collision(char_control_map: Dict) -> None:
    """
    Detects collision between a character's hitbox and another character's hurtbox.
    """
    for character in char_control_map:
        if not character.hitboxes[2]:
            copy = char_control_map.copy()
            del copy[character]
            other_character = list(copy.keys())[0]
            for i in range(len(character.hitboxes[0])):
                hitbox = character.hitboxes[0][i]
                if not hitbox.collidelist(other_character.hurtboxes) == -1:
                    character.hitboxes[2] = True
                    attack_data = character.hitboxes[1][i]
                    other_character.damage += attack_data['damage']
                    other_character.enter_hitlag(int(attack_data['damage'] / 3) + 3, attack_data)


def handle_hit(character: characters.Character, attack_data: Dict, di: float):
    """
    Handles a hit after hitlag completes, taking in a DI input to adjust direction sent.
    """
    di = math.degrees(di)
    multiplier = (attack_data['KBG'] / 100) * ((14 * character.damage * (attack_data['damage'] + 2)
                                                / (character.attributes['weight'] + 100)) + 18) + attack_data['BKB']
    direction = attack_data['direction']
    max_angles = [angle_converter(direction + 90), angle_converter(direction - 90)]
    angle_delta = [angle_diff(di, max_angles[0]), angle_diff(di, max_angles[1])]

    if angle_delta[0] < angle_delta[1]:
        influence = angle_converter(direction + (((90 - angle_delta[0]) / 90) * 18))
    elif angle_delta[0] > angle_delta[1]:
        influence = angle_converter(direction - (((90 - angle_delta[1]) / 90) * 18))
    else:
        influence = 0

    if not character.action_state[0] == 'grounded' or not -180 < direction < 0:
        hitstun = int(multiplier * HITSTUN)
        character.action_state = ['airborne', 0, 'hitstun', hitstun]
        character.update_air_speed(math.cos(math.radians(influence)) * multiplier * KB_LAUNCH_CONVERSION,
                               math.sin(math.radians(influence)) * multiplier * KB_LAUNCH_CONVERSION)
    else:
        hitstun = int(multiplier * GROUND_KB_CONVERSION * HITSTUN)
        character.action_state = ['airborne', 0, 'hitstun', hitstun]
        character.update_air_speed(math.cos(math.radians(influence)) * multiplier * KB_LAUNCH_CONVERSION,
                               -math.sin(math.radians(influence)) * multiplier * KB_LAUNCH_CONVERSION)


def angle_converter(angle: float) -> float:
    if angle >= 360:
        return 360 - angle
    if angle >= 180:
        return angle - 360
    return angle


def angle_diff(angle_one: float, angle_two: float) -> float:
    if angle_one >= -180 and angle_two < 180:
        return min(abs(360 + angle_one - angle_two),  abs(-angle_one + angle_two))
    elif angle_one < 180 and angle_two >= -180:
        return angle_diff(angle_two, angle_one)


def developer_draw_all(screen: pygame.Surface, char_control_map: Dict, stage: stages.Stage) -> None:
    screen.fill((255, 255, 255))
    for character in char_control_map:
        if character.invincible[0]:
            draw_boxes(character.hurtboxes, screen, (0, 0, 255))
        else:
            draw_boxes(character.hurtboxes, screen, (0, 0, 0))
        draw_boxes(character.hitboxes[0], screen, (255, 0, 0))
        draw_ecb(screen, character)
    draw_lines(stage.floor, screen, (0, 255, 0), True)
    draw_lines(stage.walls, screen, (0, 0, 255), False)
    pygame.display.update()


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
