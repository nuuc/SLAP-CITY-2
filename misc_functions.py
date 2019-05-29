import pygame
from typing import *
from shapely.geometry import *
from shapely import affinity


def x_reflect(polygon: Polygon, axis: float, direction: bool) -> Polygon:
    if direction:
        return polygon
    reflected_coords = [(axis * 2 - coord[0], coord[1]) for coord in list(polygon.exterior.coords)]
    return Polygon(reflected_coords)


def draw_polygon(screen: pygame.Surface, color: Tuple, polygon: Polygon) -> None:
    pygame.draw.polygon(screen, color, list(polygon.exterior.coords))


def intersect_list(polygon: Polygon, polygon_list: List) -> bool:
    for other_polygon in polygon_list:
        if polygon.intersects(other_polygon):
            return True
    return False


def in_relation(center: List, coordinates: List) -> List:
    return [[center[0] + coord[0], center[1] + coord[1]] for coord in coordinates]


def hitbox_maker(center: List, hitbox_bounds: List, char_dir: bool, damage: int, attack_dir: float, kbg: int, bkb: int)\
        -> List:
    import engine
    if char_dir:
        attack_dir = engine.angle_converter(90 - attack_dir)
    else:
        attack_dir = engine.angle_converter(90 + attack_dir)
    return [x_reflect(Polygon(in_relation(center, hitbox_bounds)), center[0], char_dir),
            {'damage': damage, 'direction': attack_dir, 'KBG': kbg, 'BKB': bkb}]


def hitbox_updater(center: List, hitbox_bounds: List, direction: bool, xoff=0, yoff=0) -> Polygon:
    if not direction:
        xoff *= -1
    return affinity.translate(x_reflect(Polygon(in_relation(center, hitbox_bounds)), center[0], direction), xoff, yoff)


def hitbox_rotate(center: List, hitbox: Polygon, direction: bool, angle: float) -> Polygon:
    if not direction:
        angle *= -1
    return affinity.rotate(hitbox, angle, tuple(center))


def directional_incrementer(value: float, increment: float, cross: float) -> float:
    if value > cross:
        value += increment
        if value < cross:
            return cross
        return value
    elif value < cross:
        value -= increment
        if value > cross:
            return cross
        return value
    return value
