import pygame, copy
from typing import *
from shapely.geometry import *
from shapely.ops import *
from shapely import affinity


def x_reflect(polygon: Polygon, axis: float, direction: bool) -> Polygon:
    if direction:
        return polygon
    reflected_coords = [(axis * 2 - coord[0], coord[1]) for coord in list(polygon.exterior.coords)]
    return Polygon(reflected_coords)


def x_reflect_list(lst: List, axis: float, direction: bool) -> List:
    if direction:
        return lst
    return [(axis * 2 - coord[0], coord[1]) for coord in lst]


def x_reflect_point(point: List, axis: float, direction: bool) -> List:
    if direction:
        return point
    dis = point[0] - axis
    return [axis - dis, point[1]]


def draw_polygon(screen: pygame.Surface, color: Tuple, polygon: Polygon) -> None:
    pygame.draw.polygon(screen, color, list(polygon.exterior.coords))


def intersect_list(polygon: Polygon, polygon_list: List) -> bool:
    for other_polygon in polygon_list:
        if polygon.intersects(other_polygon):
            return True
    return False


def in_relation(center: List, coordinates: List) -> List:
    return [[center[0] + coord[0], center[1] + coord[1]] for coord in coordinates]


def in_relation_poly(poly: Polygon, center: Tuple):
    return affinity.translate(copy.deepcopy(poly), center[0], center[1])


def in_relation_point(center: List, coordinates: List) -> List:
    return [center[0] + coordinates[0], center[1] + coordinates[1]]


def auto_transform(poly: Polygon, direction: bool, center: Tuple) -> Polygon:
    if not direction:
        reflected = affinity.affine_transform(copy.deepcopy(poly), [-1, 0, 0, 1, 0, 0])
        return in_relation_poly(reflected, center)
    else:
        return in_relation_poly(poly, center)

def hitbox_rotate(center: List, hitbox: Polygon, direction: bool, angle: float) -> Polygon:
    if not direction:
        angle *= -1
    return affinity.rotate(hitbox, angle, tuple(center))


def dir_inc(value: float, increment: float, cross: float) -> float:
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


def connect_hitbox(center1: List, center2: List, radius: float) -> Polygon:
    if center1 != center2:
        line = LineString([tuple(center1), tuple(center2)])
        length = line.length
        delx= abs(center2[0] - center1[0])
        dely = abs(center2[1] - center1[1])
        if center2[0] > center1[0] and center1[1] < center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, -radius * delx / length).coords)
            coords2 = list(affinity.translate(line, -radius * dely / length, radius * delx / length).coords)
        elif center2[0] > center1[0] and center1[1] > center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
            coords2 = list(affinity.translate(line, - radius * dely / length, -radius * delx / length).coords)
        elif center2[0] < center1[0] and center1[1] < center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
            coords2 = list(affinity.translate(line, - radius * dely / length, -radius * delx / length).coords)

        elif center2[0] < center1[0] and center1[1] > center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, -radius * delx / length).coords)
            coords2 = list(affinity.translate(line, -radius * dely / length, radius * delx / length).coords)
        else:
            coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
            coords2 = list(affinity.translate(line, -radius * dely / length, -radius * delx / length).coords)
        circle1 = Point(tuple(center1)).buffer(radius)
        circle2 = Point(tuple(center2)).buffer(radius)
        connecter = Polygon([coords1[0], coords1[1], coords2[1], coords2[0]])
        return cascaded_union([circle1, circle2, connecter])
    return Point(tuple(center1)).buffer(radius)


def connecter_hitbox(center1: List, center2: List, radius: float) -> List:
    if center1 != center2:
        line = LineString([tuple(center1), tuple(center2)])
        length = line.length
        delx= abs(center2[0] - center1[0])
        dely = abs(center2[1] - center1[1])
        if center2[0] > center1[0] and center1[1] < center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, -radius * delx / length).coords)
            coords2 = list(affinity.translate(line, -radius * dely / length, radius * delx / length).coords)
        elif center2[0] > center1[0] and center1[1] > center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
            coords2 = list(affinity.translate(line,- radius * dely / length, -radius * delx / length).coords)
        elif center2[0] < center1[0] and center1[1] < center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
            coords2 = list(affinity.translate(line, - radius * dely / length, -radius * delx / length).coords)

        elif center2[0] < center1[0] and center1[1] > center2[1]:
            coords1 = list(affinity.translate(line, radius * dely / length, -radius * delx / length).coords)
            coords2 = list(affinity.translate(line, -radius * dely / length, radius * delx / length).coords)
        else:
            coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
            coords2 = list(affinity.translate(line, -radius * dely / length, -radius * delx / length).coords)
        connecter = Polygon([coords1[0], coords1[1], coords2[1], coords2[0]])
        return list(connecter.exterior.coords)
    return []
