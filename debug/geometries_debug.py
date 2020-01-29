import pygame
from geometries import *
import random


class Polygons:

    def __init__(self):
        # self.floor = Rectangle(((400, 600), (800, 600), (800, 700), (400, 700)))
        self.floor = Polygon(((400, 700), (800, 700), (800, 500)))
        self.polygons = []
        self.selected = self.floor

    def translate_selected(self, dir):
        speed = 20
        self.selected.translate_to(dir * speed)

    def select_inc(self, dir):
        if self.selected in self.polygons:
            index = self.polygons.index(self.selected)
            if self.selected is not self.floor:
                self.selected = self.polygons[(index + dir) % len(self.polygons)]
            elif index == 0 and dir == -1:
                self.selected = self.floor
        else:
            self.selected = self.polygons[0]

    def select_floor(self):
        self.selected = self.floor

    def add_polygon(self, polygon):
        self.polygons.append(polygon)

    def run(self):
        for polygon in self.polygons:
            if polygon.collide(self.floor):
                mtv = polygon.get_MTV(self.floor)
                polygon.translate_to(mtv)

    def draw(self, screen):
        screen.fill((255, 255, 255))
        floor_points = [vert.get_values() for vert in self.floor.vertices]
        pygame.draw.polygon(screen,
                            (random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255)),
                            floor_points)
        for polygon in self.polygons:
            points = [vert.get_values() for vert in polygon.vertices]
            pygame.draw.polygon(screen,
                                (random.randint(0, 255),
                                 random.randint(0, 255),
                                 random.randint(0, 255)),
                                points)
        pygame.display.flip()

    @staticmethod
    def pop_tuple(item: Any, tup: Tuple) -> Tuple:
        return tuple((obj for obj in tup if obj is not item))

    @staticmethod
    def create_polygon(points):
        return Polygon(points)

    @staticmethod
    def enumerate_points(screen):
        stop = False
        points = []
        while not stop:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    points.append(Vector(pygame.mouse.get_pos()))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        stop = True
                        return tuple(points)
            for point in points:
                pygame.draw.circle(screen, (0, 0, 0), point.get_values(), 5)
            pygame.display.flip()

pygame.init()

screen = pygame.display.set_mode((1280, 720))
polygons = Polygons()
exit = False
clock = pygame.time.Clock()
pygame.key.set_repeat(10)
while not exit:
    clock.tick(60)
    keystate = pygame.key.get_pressed()
    if keystate[pygame.K_UP]:
        polygons.translate_selected(Vector((0, -1)))
    if keystate[pygame.K_DOWN]:
        polygons.translate_selected(Vector((0, 1)))
    if keystate[pygame.K_LEFT]:
        polygons.translate_selected(Vector((-1, 0)))
    if keystate[pygame.K_RIGHT]:
        polygons.translate_selected(Vector((1, 0)))
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                points = polygons.enumerate_points(screen)
                polygons.add_polygon(polygons.create_polygon(points))
            elif event.key == pygame.K_i:
                polygons.select_inc(1)
            elif event.key == pygame.K_j:
                polygons.select_inc(-1)
            elif event.key == pygame.K_k:
                polygons.select_floor()

    polygons.run()
    polygons.draw(screen)

