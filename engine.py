import pygame, stages, characters, math, game_loop, misc_functions, numpy, controller_handler
from typing import *
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)
HITSTUN = 0.4
KB_LAUNCH_CONVERSION = 0.15
GROUND_KB_CONVERSION = 0.8
MAX_DI = 30


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
        if not character.hitboxes['regular'][2]:
            copy = char_control_map.copy()
            del copy[character]
            other_character = list(copy.keys())[0]
            if not other_character.invincible:
                for i in range(len(character.hitboxes['regular'][0])):
                    hitbox = character.hitboxes['regular'][0][i]
                    if misc_functions.intersect_list(hitbox, other_character.hurtboxes) \
                            and not character.hitboxes['regular'][2]:
                        character.hitboxes['regular'][2] = True
                        attack_data = character.hitboxes['regular'][1][i]
                        damage = attack_data['damage']
                        if other_character.action_state[0] != 'shielded':
                            other_character.damage += damage
                            other_character.enter_hitlag(int(damage / 3) + 3, attack_data)
                            character.enter_hitlag(int(damage / 3) + 3, None)
                        else:
                            other_character.misc_data['shield_health'] -= damage
                            other_character.action_state = ['shielded', 0, 'shieldstun', int((damage + 4.45) * 0.447)]
                            other_character.ground_speed = (2 * other_character.attributes['traction'] * damage
                                                            + (-27 * other_character.attributes['traction'] + 3.2))\
                                                           * numpy.sign(other_character.center[0] - character.center[0])
                            other_character.enter_hitlag(int(damage / 3) + 3, None)
                            character.enter_hitlag(int(damage / 3) + 3, None)
                for projectile in character.hitboxes['projectile']:
                    if misc_functions.intersect_list(projectile[0], other_character.hurtboxes):
                        projectile[3] = False
                        attack_data = projectile[1]
                        damage = projectile[1]['damage']
                        if other_character.action_state[0] != 'shielded':
                            other_character.damage += damage
                            other_character.enter_hitlag(int(damage / 3) + 3, attack_data)
                        else:
                            other_character.misc_data['shield_health'] -= damage
                            other_character.action_state = ['shielded', 0, 'shieldstun', int((damage + 4.45) * 0.447)]
                            other_character.ground_speed = (2 * other_character.attributes['traction'] * damage
                                                            + (-27 * other_character.attributes['traction'] + 3.2)) \
                                                           * numpy.sign(other_character.center[0] - character.center[0])
                            other_character.enter_hitlag(int(damage / 3) + 3, None)
                        character.hitboxes['projectile'].remove(projectile)


def handle_hit(character: characters.Character, attack_data: Dict, di=None) -> None:
    """
    Handles a hit on the last frame of hitlag, taking in a DI input to adjust direction sent.
    """
    KB = (attack_data['KBG'] / 100) * ((14 * character.damage * (attack_data['damage'] + 2)
                                                / (character.attributes['weight'] + 100)) + 18) + attack_data['BKB']
    direction = attack_data['direction']
    if di is not None:
        di = math.degrees(di)
        max_angles = [angle_converter(direction + 90), angle_converter(direction - 90)]
        angle_delta = [angle_diff(di, max_angles[0]), angle_diff(di, max_angles[1])]

        if angle_delta[0] < angle_delta[1]:
            influence = angle_converter(direction + (((90 - angle_delta[0]) / 90) * MAX_DI))
        elif angle_delta[0] > angle_delta[1]:
            influence = angle_converter(direction - (((90 - angle_delta[1]) / 90) * MAX_DI))
        else:
            influence = direction
    else:
        influence = direction

    if character.misc_data['action_state'][0] == 'grounded' and -180 < direction < 0:
        hitstun = int(KB * HITSTUN)
        character.misc_data.update({'action_state': ['hitstun', hitstun, 'hitstun', 0], 'KB': KB})
        character.update_air_speed(math.cos(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION,
                                -math.sin(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION * GROUND_KB_CONVERSION)
    else:
        hitstun = int(KB * HITSTUN)
        character.misc_data.update({'action_state': ['hitstun', hitstun, 'hitstun', 0], 'KB': KB})
        character.update_air_speed(math.cos(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION,
                                   math.sin(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION)


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
        damage = font.render(str(character.damage), False, (0, 0, 0))
        shield_health = font.render(str(int(character.misc_data['shield_health'])), False, (0, 0, 0))
        if character.invincible:
            draw_poly(character.hurtboxes, screen, (0, 0, 255))
        elif character.action_state[0] == 'waveland':
            draw_poly(character.hurtboxes, screen, (0, 255, 255))
        else:
            draw_poly(character.hurtboxes, screen, (0, 0, 0))
        draw_poly(character.hitboxes['regular'][0], screen, (255, 0, 0))
        draw_ecb(screen, character)
        if character.action_state[0] == 'shielded':
            draw_shield(screen, character)
        for projectile in character.hitboxes['projectile']:
            pygame.draw.polygon(screen, (255, 0, 0), list(projectile[0].exterior.coords))
        screen.blit(damage, (300 + 100 * char_control_map[character], 650))
    fps = font.render(str(round(game_loop.clock.get_fps())), False, (128, 128, 128))
    screen.blit(fps, (0, 0))
    draw_lines(stage.floor, screen, (0, 255, 0), True)
    draw_lines(stage.walls, screen, (0, 0, 255), False)
    pygame.display.update()


def draw_boxes(obj: List[pygame.Rect], screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
    for thing in obj:
        pygame.draw.rect(screen, color, thing)


def draw_poly(obj: List, screen: pygame.Surface, color: Tuple) -> None:
    for thing in obj:
        pygame.draw.polygon(screen, color, thing.exterior.coords)


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
    pygame.draw.polygon(screen, (128, 128, 128), character.ecb)


def draw_shield(screen: pygame.Surface, character: characters.Character) -> None:
    pygame.draw.circle(screen, (255, 128, 255), [int(i) for i in character.ecb[2]], int(character.misc_data['shield_health'] * 50 / 86))