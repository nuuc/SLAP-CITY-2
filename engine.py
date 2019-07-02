import pygame, stages, characters, math, draw, numpy
import misc_functions as mf
from typing import *
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)
HITSTUN = 0.4
KB_LAUNCH_CONVERSION = 0.15
GROUND_KB_CONVERSION = 0.8
MAX_DI = 30

t = 0
total_elapsed = 0
total_list = []


def run(screen: pygame.Surface, char_control_map: Dict, stage: stages.Stage) -> None:
    """
    Handles stage interactions, draws the screen, and then detects hitbox collision.
    """
    stage.handle_stage(char_control_map)

    char_lst = [c for c in char_control_map]

    draw.developer_draw(screen, char_lst, stage)
    hitbox_collision(char_lst)


def hitbox_collision(character_lst: List) -> None:
    """
    Detects collision between a character's hitbox and another character's hurtbox.
    """
    for character in character_lst:
        _copy = character_lst.copy()
        _copy.remove(character)
        other_character = _copy[0]
        if not other_character.invincible:
            if not character.hitboxes['regular']['hit']:
                for id in character.hitboxes['regular']['ids']:
                    hitbox = character.hitboxes['regular']['ids'][id]
                    if mf.intersect_list(hitbox, other_character.hurtboxes):
                        attack_data = character.moves[character.action_state[0]]['ids'][id]['attributes'].copy()
                        damage = attack_data['damage']
                        if character.direction:
                            attack_data.update({'angle': angle_converter(90 - attack_data['angle'])})
                        else:
                            attack_data.update({'angle': angle_converter(90 + attack_data['angle'])})
                        if other_character.action_state[0] != 'shielded':
                            other_character.damage += damage
                            other_character.direction = not character.direction
                            other_character.enter_hitlag(int(damage / 3) + 3, attack_data)
                            character.enter_hitlag(int(damage / 3) + 3, None)
                        else:
                            other_character.misc_data['shield_health'] -= damage
                            other_character.action_state = ['shieldstun', int((damage + 4.45) * 0.447)]
                            other_character.speed[0] = (2 * other_character.attributes['traction'] * damage
                                                            + (-27 * other_character.attributes['traction'] + 3.2))\
                                                           * numpy.sign(other_character.center[0] - character.center[0])
                            other_character.enter_hitlag(int(damage / 3) + 3, None)
                            character.enter_hitlag(int(damage / 3) + 3, None)
                        character.hitboxes['regular']['hit'] = True
                        if character.hitboxes['regular']['hit']:
                            break
            for id in character.hitboxes['grab']:
                grab_hitbox = mf.connect_hitbox(character.hitboxes['grab'][id][0],
                                                character.hitboxes['grab'][id][1],
                                                character.hitboxes['grab'][id][2])
                if mf.intersect_list(grab_hitbox, other_character.hurtboxes):
                    if character.direction:
                        other_character.update_center(character.ecb[3][0] + 50, character.ecb[0][1])
                    else:
                        other_character.update_center(character.ecb[1][0] - 50, character.ecb[0][1])
                    other_character.direction = not character.direction
                    other_character.update_ecb()
                    other_character.update_hurtbox()
                    other_character.action_state = ['grabbed', 0]
                    character.misc_data.update({'jack': other_character})
                    character.hitboxes.update({'grab': {}})
                    character.action_state = ['grabbing', 0]

            # for projectile in character.hitboxes['projectile']:
            #     if misc_functions.intersect_list(projectile[0], other_character.hurtboxes):
            #         projectile[3] = False
            #         attack_data = projectile[1]
            #         damage = projectile[1]['damage']
            #         if other_character.action_state[0] != 'shielded':
            #             other_character.damage += damage
            #             other_character.enter_hitlag(int(damage / 3) + 3, attack_data)
            #         else:
            #             other_character.misc_data['shield_health'] -= damage
            #             other_character.action_state = ['shielded', 0, 'shieldstun', int((damage + 4.45) * 0.447)]
            #             other_character.ground_speed = (2 * other_character.attributes['traction'] * damage
            #                                             + (-27 * other_character.attributes['traction'] + 3.2)) \
            #                                            * numpy.sign(other_character.center[0] - character.center[0])
            #             other_character.enter_hitlag(int(damage / 3) + 3, None)
            #         character.hitboxes['projectile'].remove(projectile)


def handle_hit(character: characters.Character, attack_data: Dict, di=None) -> None:
    """
    Handles a hit on the last frame of hitlag, taking in a DI input to adjust direction sent.
    """
    KB = (attack_data['kbg'] / 100) * ((14 * character.damage * (attack_data['damage'] + 2)
                                            / (character.attributes['weight'] + 100)) + 18) + attack_data['bkb']
    direction = attack_data['angle']
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

    print(get_DI_diff(direction, influence, KB * KB_LAUNCH_CONVERSION, character.attributes['vair_acc'], KB * HITSTUN))
    if character.env_state == 'grounded' and -180 < direction < 0:
        hitstun = int(KB * HITSTUN)
        character.misc_data.update({'action_state': ['hitstun', hitstun], 'kb': KB})
        character.update_speed(math.cos(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION,
                                -math.sin(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION * GROUND_KB_CONVERSION)
    else:
        hitstun = int(KB * HITSTUN)
        character.misc_data.update({'action_state': ['hitstun', hitstun], 'kb': KB})
        character.update_speed(math.cos(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION,
                                   math.sin(math.radians(influence)) * KB * KB_LAUNCH_CONVERSION)
        character.env_state = 'airborne'


def get_DI_diff(no_di: float, di: float, factor: float, vair_acc: float, hitstun: int) -> float:

    no_di_speed = (math.cos(math.radians(no_di)) * factor, math.sin(math.radians(no_di)) * factor)
    di_speed = (math.cos(math.radians(di)) * factor, math.sin(math.radians(di)) * factor)

    no_di_y = no_di_speed[1] * hitstun - (vair_acc * (hitstun ** 2))
    no_di_x = mf.dir_inc(no_di_speed[0], -hitstun * 0.19, 0)

    di_y = di_speed[1] * hitstun - (vair_acc * (hitstun ** 2))
    di_x = mf.dir_inc(di_speed[0], -hitstun * 0.19, 0)

    displacement_diff = math.sqrt(di_y ** 2 + di_x ** 2) - math.sqrt(no_di_y ** 2 + no_di_x ** 2)
    return displacement_diff


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


