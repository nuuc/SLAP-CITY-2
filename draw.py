import pygame, characters, stages, game_loop
from typing import *

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 128, 255)
GRAY = (128, 128, 128)


def developer_draw(screen: pygame.Surface, character_lst: List[characters.Character], stage: stages.Stage) -> None:
    screen.fill(WHITE)

    # Draw character specific hit/hurtboxes, etc.
    for character in character_lst:
        # Initialize damage, action state
        damage = font.render(str(character.damage), True, BLACK)
        state = font.render(str(character.action_state), True, BLACK)

        # Draw hurt
        draw_hurtbox(screen, character, BLACK)
        draw_reg_hitbox(screen, character, RED)
        draw_ecb(screen, character, GRAY)

        if character.action_state[0] in ('shielded', 'hitstun'):
            draw_shield(screen, character, PINK)

        screen.blit(damage, (300 + character_lst.index(character) * 250, 550))
        screen.blit(state, (300 + character_lst.index(character) * 250, 600))

    draw_stage_lines(screen, stage.floor, GREEN, True)
    draw_stage_lines(screen, stage.walls, BLUE, False)

    fps = font.render(str(round(game_loop.clock.get_fps())), True, BLACK)
    screen.blit(fps, (0, 0))

    pygame.display.update()


def draw_ecb(screen: pygame.Surface, character: characters.Character, color: Tuple) -> None:
    pygame.draw.polygon(screen, color, character.ecb)


def draw_hurtbox(screen: pygame.Surface, character: characters.Character, color: Tuple) -> None:
    pygame.draw.polygon(screen, color, list(character.hurtboxes.exterior.coords))


def draw_reg_hitbox(screen: pygame.Surface, character: characters.Character, color: Tuple) -> None:
    for regular_hitbox in character.hitboxes['regular']['ids']:
        pygame.draw.polygon(screen, color, list(regular_hitbox.exterior.coords))


def draw_shield(screen: pygame.Surface, character: characters.Character, color: Tuple) -> None:
    pygame.draw.circle(screen, color, [int(i) for i in character.ecb[2]],
                       int(character.misc_data['shield_health'] * 50 / 86))


def draw_stage_lines(screen: pygame.Surface, line_lst: List, color: Tuple, orientation: bool) -> None:
    if orientation:
        for line in line_lst:
            coord = [(line[0], line[2]), (line[1], line[2])]
            pygame.draw.line(screen, color, coord[0], coord[1], 2)
    else:
        for line in line_lst:
            coord = [(line[2], line[0]), (line[2], line[1])]
            pygame.draw.line(screen, color, coord[0], coord[1], 2)
