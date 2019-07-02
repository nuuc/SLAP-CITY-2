import pygame, copy, pickle, os, time, sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog
from pygame.locals import *
from shapely import affinity
from shapely.geometry import *
from shapely.ops import *
from typing import *
from math import *
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 16)
flags = DOUBLEBUF

root = os.path.dirname(os.path.realpath(__file__))

screen = pygame.display.set_mode((1600, 900), flags)


circle_cursor = pygame.transform.scale(pygame.image.load('assets/animator/circle.png').convert_alpha(), (20, 20))
line_cursor = pygame.transform.scale(pygame.image.load('assets/animator/line.png').convert_alpha(), (20, 20))
move_cursor = pygame.transform.scale(pygame.image.load('assets/animator/move.png').convert_alpha(), (20, 20))
rotate_cursor = pygame.transform.scale(pygame.image.load('assets/animator/rotate.png').convert_alpha(), (20, 20))
button_default = pygame.transform.scale(pygame.image.load('assets/animator/button_default.png').convert_alpha(), (120, 40))
button_click = pygame.transform.scale(pygame.image.load('assets/animator/button_click.png').convert_alpha(), (120, 40))
button_hover = pygame.transform.scale(pygame.image.load('assets/animator/button_hover.png').convert_alpha(), (120, 40))


class Node:

    pos: Tuple
    radius: float
    node_type: str
    connect: List
    main: bool
    image: str
    image_size: Tuple
    image_center: Tuple
    image_rotation: float
    base_image_size: Tuple

    def __init__(self, pos: Tuple, radius: float, node_type: str, main=False, image=None,
                 image_size=(0, 0), image_center=(0, 0)):
        self.pos = pos
        self.radius = radius
        self.node_type = node_type
        self.main = main
        self.parent = None
        self.connect = []
        self.clicking = False
        self.image = image
        if image_size == (0, 0):
            self.image_size = (self.radius, self.radius)
        else:
            self.image_size = image_size
        if image_center == (0, 0):
            self.image_center = self.pos
        else:
            self.image_center = image_center
        self.base_image_size = (0, 0)
        self.image_rotation = 0

    @staticmethod
    def connect_hitbox(center1: Tuple, center2: Tuple, radius: float) -> Polygon:
        if center1 != center2:
            line = LineString([tuple(center1), tuple(center2)])
            length = line.length
            delx = abs(center2[0] - center1[0])
            dely = abs(center2[1] - center1[1])
            if (center2[0] > center1[0] and center1[1] < center2[1]) or \
                    (center2[0] < center1[0] and center1[1] > center2[1]):
                coords1 = list(affinity.translate(line, radius * dely / length, -radius * delx / length).coords)
                coords2 = list(affinity.translate(line, -radius * dely / length, radius * delx / length).coords)
            elif (center2[0] > center1[0] and center1[1] > center2[1]) or \
                    (center2[0] < center1[0] and center1[1] < center2[1]):
                coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
                coords2 = list(affinity.translate(line, -radius * dely / length, -radius * delx / length).coords)
            else:
                coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
                coords2 = list(affinity.translate(line, -radius * dely / length, -radius * delx / length).coords)
            circle1 = Point(tuple(center1)).buffer(radius)
            circle2 = Point(tuple(center2)).buffer(radius)
            connecter = Polygon([coords1[0], coords1[1], coords2[1], coords2[0]])
            return cascaded_union([circle1, circle2, connecter])
        return Point(tuple(center1)).buffer(radius)

    @staticmethod
    def connecter_hitbox(center1: Tuple, center2: Tuple, radius: float) -> List:
        if center1 != center2:
            line = LineString([tuple(center1), tuple(center2)])
            length = line.length
            delx = abs(center2[0] - center1[0])
            dely = abs(center2[1] - center1[1])
            if (center2[0] > center1[0] and center1[1] < center2[1]) or \
                    (center2[0] < center1[0] and center1[1] > center2[1]):
                coords1 = list(affinity.translate(line, radius * dely / length, -radius * delx / length).coords)
                coords2 = list(affinity.translate(line, -radius * dely / length, radius * delx / length).coords)
            elif (center2[0] > center1[0] and center1[1] > center2[1]) or \
                    (center2[0] < center1[0] and center1[1] < center2[1]):
                coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
                coords2 = list(affinity.translate(line, -radius * dely / length, -radius * delx / length).coords)
            else:
                coords1 = list(affinity.translate(line, radius * dely / length, radius * delx / length).coords)
                coords2 = list(affinity.translate(line, -radius * dely / length, -radius * delx / length).coords)
            connecter = Polygon([coords1[0], coords1[1], coords2[1], coords2[0]])
            return list(connecter.exterior.coords)
        return []

    def add_node(self, node: 'Node'):
        self.connect.append(node)
        node.parent = self

    def add_image(self, image: pygame.Surface, image_size=(0, 0)):
        if image_size == (0, 0):
            factor = image.get_width() / self.radius
            self.image_size = (self.radius, int(image.get_height() / factor))
        else:
            self.image_size = image_size
        image.convert_alpha()
        self.base_image_size = (image.get_width(), image.get_height())
        self.image = pygame.image.tostring(image, 'RGBA')
        self.image_center = self.pos

    def rotate_around(self, rotation: float, node: 'Node') -> None:
        self.pos = (cos(rotation)*(self.pos[0]-node.pos[0])-sin(rotation)*(self.pos[1]-node.pos[1])+node.pos[0],
                    sin(rotation)*(self.pos[0]-node.pos[0])+cos(rotation)*(self.pos[1]-node.pos[1])+node.pos[1])
        if self.image is not None:
            self.image_center = (cos(rotation)*(self.image_center[0]-node.pos[0])-sin(rotation) *
                                 (self.image_center[1]-node.pos[1])+node.pos[0],
                                    sin(rotation)*(self.image_center[0]-node.pos[0])+cos(rotation) *
                                 (self.image_center[1]-node.pos[1])+node.pos[1])

    def rotate_node(self, rotation: float, node: 'Node') -> None:
        self.rotate_around(rotation, node)
        for nodes in self.connect:
            nodes.rotate_node(rotation, node)

    def move_node(self, offset: Tuple):
        self.pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])
        if self.image is not None:
            self.image_center = (self.image_center[0] + offset[0], self.image_center[1] + offset[1])
        for nodes in self.connect:
            nodes.move_node(offset)

    def rotate_image(self, rotation: float):
        self.image_rotation = degrees(rotation)

    def move_image(self, offset: Tuple):
        if self.image is not None:
            self.image_center = (self.image_center[0] + offset[0], self.image_center[1] + offset[1])

    def scale_image(self, factor: float):
        self.image_size = (int(self.image_size[0] * factor), int(self.image_size[1] * factor))

    def draw_image(self, screen: pygame.Surface):
        if self.image is not None:
            old_center = self.image_center
            topleft = (int(self.image_center[0] - self.image_size[0] / 2),
                                int(self.image_center[1] - self.image_size[1] / 2))
            rotated = pygame.transform.rotate(
                pygame.transform.scale(pygame.image.frombuffer(self.image, self.base_image_size, 'RGBA'),
                                       self.image_size), self.image_rotation)
            rotated_center = (rotated.get_width() / 2 + topleft[0], rotated.get_height() / 2 + topleft[1])
            self.center = rotated_center
            offset = (-self.center[0] + old_center[0], -self.center[1] + old_center[1])
            new_topleft = (offset[0] + topleft[0], offset[1] + topleft[1])
            screen.blit(rotated, new_topleft)

    def draw_nodes(self, screen: pygame.Surface, color: Tuple, ignore=False, image=True):
        if self.parent and self.parent.node_type == 'line' and self.node_type == 'line':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.parent.pos), int(self.parent.radius))
            pygame.draw.polygon(screen, color, Node.connecter_hitbox(self.parent.pos, self.pos, self.radius))
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
        elif self.parent and self.parent.node_type == 'line' and self.node_type == 'circle':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
        elif self.parent and self.parent.node_type == 'circle' and self.node_type == 'line':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.parent.pos), int(self.parent.radius))
            pygame.draw.polygon(screen, color, Node.connecter_hitbox(self.parent.pos, self.pos, self.radius))
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
        else:
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
        for nodes in self.connect:
            nodes.draw_nodes(screen, color, ignore, image)
        if not ignore:
            self.draw_selecter(screen, (128, 0, 0))
        if image:
            self.draw_image(screen)

    def draw_selecter(self, screen: pygame.Surface, color: Tuple):
        if self.parent and self.parent.node_type == 'line' and self.node_type == 'line':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius * 0.8))
        elif self.parent and self.parent.node_type == 'circle' and self.node_type == 'line':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius * 0.8))
        elif self.main:
            pygame.draw.circle(screen, (255, 255, 0), tuple(int(p) for p in self.pos), int(self.radius * 0.8))
        else:
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius * 0.8))
        for nodes in self.connect:
            nodes.draw_selecter(screen, color)
        self.draw_image(screen)

    def highlight_node(self, screen: pygame.Surface, color: Tuple):
        if self.parent and self.parent.node_type == 'line' and self.node_type == 'line':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.parent.pos), int(self.parent.radius))
            pygame.draw.polygon(screen, color, Node.connecter_hitbox(self.parent.pos, self.pos, self.radius))
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
            pygame.draw.circle(screen, (128, 0, 0), tuple(int(p) for p in self.pos), int(self.radius * 0.8))
            if self.parent.main:
                pygame.draw.circle(screen, (255, 255, 0), tuple(int(p) for p in self.parent.pos),
                                   int(self.parent.radius * 0.8))
            else:
                pygame.draw.circle(screen, (128, 0, 0), tuple(int(p) for p in self.parent.pos),
                                   int(self.parent.radius * 0.8))
        elif self.parent and self.parent.node_type == 'line' and self.node_type == 'circle':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
        elif self.parent and self.parent.node_type == 'circle' and self.node_type == 'line':
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.parent.pos), int(self.parent.radius))
            pygame.draw.polygon(screen, color, Node.connecter_hitbox(self.parent.pos, self.pos, self.radius))
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
            pygame.draw.circle(screen, (128, 0, 0), tuple(int(p) for p in self.pos), int(self.radius * 0.8))
        else:
            pygame.draw.circle(screen, color, tuple(int(p) for p in self.pos), int(self.radius))
            pygame.draw.circle(screen, (255, 255, 0), tuple(int(p) for p in self.pos), int(self.radius * 0.8))
        self.draw_image(screen)

    def scale_node(self, factor: float):
        self.pos = (self.pos[0] * factor, self.pos[1] * factor)
        self.radius *= factor
        if self.image is not None:
            self.image_center = (self.image_center[0] * factor, self.image_center[1] * factor)
            self.image_size = (self.image_size[0] * factor, self.image_size[1] * factor)
        for nodes in self.connect:
            nodes.scale_node(factor)

    def transform_node(self, center: Tuple):
        self.pos = (self.pos[0] - center[0], self.pos[1] - center[1])
        if self.image is not None:
            self.image_center = (self.image_center[0] - center[0], self.image_center[1] - center[0])
        for nodes in self.connect:
            nodes.transform_node(center)

    def polygonize(self) -> Polygon:
        if self.parent and self.parent.node_type == 'line' and self.node_type == 'line':
            if not self.main and not self.connect:
                return Node.connect_hitbox(self.parent.pos, self.pos, self.radius)
            elif not self.main and self.connect:
                poly_list = []
                for nodes in self.connect:
                    poly_list.append(nodes.polygonize())
                    poly_list.append(Node.connect_hitbox(self.parent.pos, self.pos, self.radius))
                return cascaded_union(poly_list)
            else:
                poly_list = [Point(self.pos).buffer(self.radius)]
                for nodes in self.connect:
                    poly_list.append(nodes.polygonize())
                return cascaded_union(poly_list)
        elif self.parent and self.parent.node_type == 'line' and self.node_type == 'circle':
            return Point(self.pos).buffer(self.radius)
        elif self.parent and self.parent.node_type == 'circle' and self.node_type == 'line':
            if not self.main and not self.connect:
                return Node.connect_hitbox(self.parent.pos, self.pos, self.radius)
            elif not self.main and self.connect:
                poly_list = []
                for nodes in self.connect:
                    poly_list.append(nodes.polygonize())
                    poly_list.append(Node.connect_hitbox(self.parent.pos, self.pos, self.radius))
                return cascaded_union(poly_list)
            else:
                poly_list = [Point(self.pos).buffer(self.radius)]
                for nodes in self.connect:
                    poly_list.append(nodes.polygonize())
                return cascaded_union(poly_list)
        else:
            if not self.main and not self.connect:
                return Node.connect_hitbox(self.parent.pos, self.pos, self.radius)
            elif not self.main and self.connect:
                poly_list = []
                for nodes in self.connect:
                    poly_list.append(nodes.polygonize())
                    poly_list.append(Node.connect_hitbox(self.parent.pos, self.pos, self.radius))
                return cascaded_union(poly_list)
            else:
                poly_list = [Point(self.pos).buffer(self.radius)]
                for nodes in self.connect:
                    poly_list.append(nodes.polygonize())
                return cascaded_union(poly_list)

    def get_min_max(self) -> List:
        _min = list(self.pos)
        _max = list(self.pos)
        for nodes in self.connect:
            node_minmax = nodes.get_min_max()
            # check x
            if node_minmax[0][0] < _min[0]:
                _min[0] = node_minmax[0][0]
            elif node_minmax[1][0] > _max[0]:
                _max[0] = node_minmax[1][0]
            # check y
            if node_minmax[0][1] < _min[1]:
                _min[1] = node_minmax[0][1]
            elif node_minmax[1][1] > _max[1]:
                _max[1] = node_minmax[1][1]
        return [tuple(_min), tuple(_max)]

    def select_node(self, pos: Tuple):
        if pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2,
                       self.radius * 2).collidepoint(pos):
            return self
        else:
            for nodes in self.connect:
                if nodes.select_node(pos) is not None:
                    return nodes.select_node(pos)

    def delete_node(self):
        if self.parent is not None:
            self.parent.connect.remove(self)


class InfoContainer:
    frame_data: List

    def __init__(self):
        self.frame_data = []

    def add_frame(self, hurtboxNode: Node, hitbox_ids: Dict):
        self.frame_data.append({'hurtboxNode': hurtboxNode, 'hitbox_ids': hitbox_ids})

    def goto_frame(self, frame: int):
        return [self.frame_data[frame - 1]['hurtboxNode'], self.frame_data[frame - 1]['hitbox_ids']]

    def insert_frame(self, frame: int, hurtboxNode: Node, hitboxNodes: Dict):
        self.frame_data.insert(frame, {'hurtboxNode': copy.deepcopy(hurtboxNode),
                                       'hitbox_ids': copy.deepcopy(hitboxNodes)})

    def update_frame(self, frame: int, hurtboxNode: Node, hitbox_ids: Dict):
        self.frame_data[frame - 1] = {'hurtboxNode': copy.deepcopy(hurtboxNode),
                                       'hitbox_ids': copy.deepcopy(hitbox_ids)}

    def delete_frame(self, frame: int):
        try:
            del self.frame_data[frame - 1]
        except:
            print('Frame out of range')

    def transform_all(self, center: Tuple):
        _copy = copy.deepcopy(self)
        for frame in _copy.frame_data:
            frame['hurtboxNode'].transform_node(center)
            for ids in frame['hitbox_ids']:
                frame['hitbox_ids'][ids]['node'].transform_node(center)
        return _copy

    def scale_all(self, factor: float):
        _copy = copy.deepcopy(self)
        for frame in _copy.frame_data:
            frame['hurtboxNode'].scale_node(factor)
            for ids in frame['hitbox_ids']:
                frame['hitbox_ids'][ids]['node'].scale_node(factor)
        return _copy

    def polygonize(self) -> List:
        frames_polygonized = []
        for frame in self.frame_data:
            hurtboxPoly = frame['hurtboxNode'].polygonize()
            hitboxPolys = {}
            for ids in frame['hitbox_ids']:
                hitboxPolys[ids] = {}
                hitboxPolys[ids]['polygon'] = frame['hitbox_ids'][ids]['node'].polygonize()
                for attribute in frame['hitbox_ids'][ids]:
                    if attribute != 'node':
                        hitboxPolys[ids][attribute] = frame['hitbox_ids'][ids][attribute]
            frames_polygonized.append({'hurtboxPoly': hurtboxPoly, 'hitboxPolys': hitboxPolys})
        return frames_polygonized

    def convert(self, center: Tuple, factor: float):
        # This function will parse each frame in frame data to be readable by Characters
        _copy = copy.deepcopy(self)
        _copy.transform_all(center)
        _copy.scale_all(factor)
        converted = self.transform_all(center).scale_all(factor).polygonize()
        path, _filter = QFileDialog.getSaveFileName(None, 'Save File', filter='PLYPK(*.plypk)')
        with open(path, 'wb') as output:
            pickle.dump(converted, output, pickle.HIGHEST_PROTOCOL)

    def save_animation(self):
        path, _filter = QFileDialog.getSaveFileName(None, 'Save File', filter='ANIPK(*.anipk)')
        with open(path, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def load_animation(self):
        path, _filter = QFileDialog.getOpenFileName(None, 'Open File', filter='ANIPK(*.anipk)')
        try:
            with open(path, 'rb') as input:
                self.frame_data = pickle.load(input).frame_data
        except:
            print('File not found.')


class TextPrompt:

    @staticmethod
    def text_prompt(surf: pygame.Surface, width: int, height: int, prompt: str):
        pygame.mouse.set_visible(True)
        done = False
        click = False

        delx = surf.get_width() - width
        dely = surf.get_height() - height

        text = ''
        textBox = pygame.Rect(delx / 2, dely / 2, width, height)

        buttons = [Button('close', 'Close', pygame.Rect(0, 0, 120, 40))]

        for button in buttons:
            button.button_rect.move_ip((delx / 2) - button.button_rect.width + width,
                                        (dely / 2) - (button.button_rect.height / 2))

        while not done:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
                    if TextPrompt.button_handle(mouse_pos, buttons):
                        done = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    click = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                        pygame.mouse.set_visible(False)
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
            pygame.draw.rect(surf, (255, 255, 255), textBox)
            pygame.draw.rect(surf, (0, 0, 0), textBox, 10)

            text_render = font.render(text, False, (0, 0, 0))
            prompt_render = font.render(prompt, False, (0, 0, 0))

            inside_delx = textBox.width - text_render.get_width()
            inside_dely = textBox.height - text_render.get_height()

            inside_delx_prompt = textBox.width - prompt_render.get_width()

            surf.blit(text_render, (textBox.left + (inside_delx / 2), textBox.top + (inside_dely / 2)))
            surf.blit(prompt_render, (textBox.left + (inside_delx_prompt / 2), textBox.top + 20))

            TextPrompt.draw_GUI(mouse_pos, click, surf, buttons)
            pygame.display.update()
            clock.tick(60)
        pygame.mouse.set_visible(False)
        return None

    @staticmethod
    def bool_prompt(surf: pygame.Surface, width: int, height: int, prompt: str):
        pygame.mouse.set_visible(True)
        done = False
        click = False

        delx = surf.get_width() - width
        dely = surf.get_height() - height

        textBox = pygame.Rect(delx / 2, dely / 2, width, height)

        buttons = [Button('close', 'Close', pygame.Rect(0, 0, 120, 40)),
                   Button('yes', 'Yes', pygame.Rect(-2 * width / 4, height / 2, 120, 40)),
                   Button('no', 'No', pygame.Rect(-width / 4, height / 2 , 120, 40))]

        for button in buttons:
            button.button_rect.move_ip((delx / 2) - button.button_rect.width + width,
                                       (dely / 2) - (button.button_rect.height / 2))

        while not done:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
                    if TextPrompt.button_handle(mouse_pos, buttons):
                        done = True
                        return TextPrompt.button_handle(mouse_pos, buttons)
                elif event.type == pygame.MOUSEBUTTONUP:
                    click = False
            pygame.draw.rect(surf, (255, 255, 255), textBox)
            pygame.draw.rect(surf, (0, 0, 0), textBox, 10)

            prompt_render = font.render(prompt, False, (0, 0, 0))

            inside_delx_prompt = textBox.width - prompt_render.get_width()

            surf.blit(prompt_render, (textBox.left + (inside_delx_prompt / 2),
                                      textBox.top + 20))

            TextPrompt.draw_GUI(mouse_pos, click, surf, buttons)
            pygame.display.update()
            clock.tick(60)
        pygame.mouse.set_visible(False)
        return False

    @staticmethod
    def error_prompt(surf: pygame.Surface, width: int, height: int, prompt: str):
        pygame.mouse.set_visible(True)
        done = False
        click = False

        delx = surf.get_width() - width
        dely = surf.get_height() - height

        textBox = pygame.Rect(delx / 2, dely / 2, width, height)

        buttons = [Button('ok', 'Ok', pygame.Rect(-width / 2 + 60, height / 2 + 20, 120, 40))]

        for button in buttons:
            button.button_rect.move_ip((delx / 2) - button.button_rect.width + width,
                                       (dely / 2) - (button.button_rect.height / 2))

        while not done:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
                    if TextPrompt.button_handle(mouse_pos, buttons):
                        done = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    click = False
            pygame.draw.rect(surf, (255, 255, 255), textBox)
            pygame.draw.rect(surf, (0, 0, 0), textBox, 10)

            prompt_render = font.render(prompt, False, (0, 0, 0))

            inside_delx_prompt = textBox.width - prompt_render.get_width()

            surf.blit(prompt_render, (textBox.left + (inside_delx_prompt / 2), textBox.top + 20))

            TextPrompt.draw_GUI(mouse_pos, click, surf, buttons)
            pygame.display.update()
            clock.tick(60)
        pygame.mouse.set_visible(False)
        return None



    @staticmethod
    def button_handle(pos: Tuple, buttons: List):
        for button in buttons:
            if button.within(pos):
                if button.name == 'close':
                    return True
                elif button.name == 'yes':
                    return True
                elif button.name == 'ok':
                    return True
                elif button.name == 'no':
                    return False
        return False

    @staticmethod
    def draw_GUI(pos: Tuple, click: bool, surf: pygame.Surface, buttons: List):
        for button in buttons:
            button.draw(pos, click, surf)


class Button:

    name: str
    hint: pygame.Surface
    button_rect: pygame.Rect
    color: Tuple
    hover_color: Tuple
    click_color: Tuple

    def __init__(self, name: str, hint: str, button_rect: pygame.Rect):
        self.name = name
        self.hint = font.render(hint, True, (255, 255, 255))
        self.button_rect = button_rect

    def within(self, pos: Tuple):
        return self.button_rect.collidepoint(pos)

    def display_hinter(self, surf: pygame.Surface):
        delx = self.button_rect.width - self.hint.get_width()
        dely = self.button_rect.height - self.hint.get_height()
        surf.blit(self.hint, (self.button_rect.x + delx / 2, self.button_rect.y + dely / 2))

    def draw(self, pos: Tuple, click: bool, surf: pygame.Surface):
        if self.within(pos) and not click:
            surf.blit(button_hover, self.button_rect.topleft)

        elif self.within(pos) and click:
            surf.blit(button_click, self.button_rect.topleft)

        else:
            surf.blit(button_default, self.button_rect.topleft)
        self.display_hinter(surf)



# === DECLARING BUTTONS ===

line = Button('line', 'Line', pygame.Rect(0, 0, 120, 40))
circle = Button('circle', 'Circle', pygame.Rect(0, 40, 120, 40))
inc_radius = Button('inc_radius', '+ Radius', pygame.Rect(120, 0, 120, 40))
dec_radius = Button('dec_radius', '- Radius', pygame.Rect(120, 40, 120, 40))
create_hitbox = Button('create_hitbox', 'Make hitbox', pygame.Rect(240, 40, 120, 40))
create_hurtbox = Button('create_hurtbox', 'Make hurtbox', pygame.Rect(240, 0, 120, 40))
edit = Button('edit', 'Edit', pygame.Rect(360, 0, 120, 40))
duplicate = Button('duplicate', 'Duplicate', pygame.Rect(360, 40, 120, 40))
insert_frame = Button('insert_frame', 'Add frame', pygame.Rect(480, 0, 120, 40))
delete_frame = Button('delete_frame', 'Delete frame', pygame.Rect(480, 40, 120, 40))
update_frame = Button('update_frame', 'Update frame', pygame.Rect(600, 0, 120, 40))
goto_frame = Button('goto_frame', 'Go to frame', pygame.Rect(600, 40, 120, 40))
save_animation = Button('save_animation', 'Save', pygame.Rect(720, 0, 120, 40))
load_animation = Button('load_animation', 'Load', pygame.Rect(720, 40, 120, 40))
convert_poly = Button('convert_poly', 'Convert polygon', pygame.Rect(840, 0, 120, 40))
radius_select = Button('radius_select', 'Select radius', pygame.Rect(840, 40, 120, 40))
play_ani = Button('play_ani', 'Play', pygame.Rect(960, 0, 120, 40))
stop_ani = Button('stop_ani', 'Stop', pygame.Rect(960, 40, 120, 40))
select_center = Button('select_center', 'Move center', pygame.Rect(1080, 0, 120, 40))
num_onions = Button('num_onions', 'Choose onions', pygame.Rect(1080, 40, 120, 40))
select_scale = Button('select_scale', 'Select scale', pygame.Rect(1200, 0, 120, 40))
ruler_inc = Button('ruler_inc', 'Select ruler inc', pygame.Rect(1200, 40, 120, 40))
add_image = Button('add_image', 'Add img to node', pygame.Rect(1320, 0, 120, 40))
move_image = Button('move_image', 'Move image', pygame.Rect(1320, 40, 120, 40))
rotate_image = Button('rotate_image', 'Rotate image', pygame.Rect(1440, 0, 120, 40))
scale_image = Button('scale_image', 'Scale image', pygame.Rect(1440, 40, 120, 40))

buttons_list = [line, circle, inc_radius, dec_radius, create_hitbox, create_hurtbox, edit, delete_frame,
                insert_frame, update_frame, goto_frame, save_animation, load_animation, convert_poly, radius_select,
                play_ani, stop_ani, duplicate, select_center, ruler_inc, num_onions, select_scale, add_image,
                move_image, rotate_image, scale_image]


class Animator:
    frame: int
    radius: int
    mode: str

    frame_data: InfoContainer
    logs: List

    onions: int

    main_screen: pygame.Surface
    GUI_screen: pygame.Surface
    frames_screen: pygame.Surface
    # onion_surfaces: List[pygame.Surface]

    scale: float
    ruler_start: Tuple
    ruler_increment: int
    center: Tuple

    hurtboxNode: Node
    hitbox_ids: Dict
    selectedNode: Node

    buttons: List
    clicking: bool

    playing: bool

    def __init__(self, main_screen: pygame.Surface, onions=3, scale=1, ruler_start=(0, 700), ruler_increment=15,
                 center=(800, 700)):
        self.frame = 1
        self.frame_data = InfoContainer()
        self.hurtboxNode = None
        self.hitbox_ids = {}
        self.selectedNode = None
        self.radius = 30
        self.mode = 'make hurtbox'
        self.buttons = buttons_list
        self.clicking = False
        self.main_screen = main_screen
        self.GUI_screen = pygame.Surface((1600, 150))
        self.frames_screen = pygame.Surface((1600, 200))
        self.frames_screen.fill((56, 128, 255))
        self.update_prev_frames()
        self.onions = onions
        self.playing = False
        self.scale = scale
        self.ruler_start = ruler_start
        self.ruler_increment = ruler_increment
        self.center = center
        self.logs = []

    @staticmethod
    def get_angle(pos1: Tuple, pos2: Tuple, pos3: Tuple) -> float:
        a = (pos1[0] - pos2[0], pos1[1] - pos2[1], 0)
        b = (pos1[0] - pos3[0], pos1[1] - pos3[1], 0)
        # dot_product = a[0] * b[0] + a[1] * b[1]
        length_a = hypot(a[0], a[1])
        length_b = hypot(b[0], b[1])
        angle = asin(np.cross(a, b)[2] / (length_a * length_b))
        return angle

    @staticmethod
    def get_offset(pos1: Tuple, pos2: Tuple) -> Tuple:
        return tuple((pos1[0] - pos2[0], pos1[1] - pos2[1]))

    def log(self):
        self.logs.append({'frame_data': copy.deepcopy(self.frame_data),
                          'nodes': [copy.deepcopy(self.hurtboxNode), copy.deepcopy(self.hitbox_ids)]})
        if len(self.logs) > 10:
            del self.logs[0]

    def undo(self):
        if self.logs:
            log = self.logs.pop()
            self.frame_data = log['frame_data']
            self.hurtboxNode = log['nodes'][0]
            self.hitbox_ids = log['nodes'][1]
            self.selectedNode = None
            try:
                self.update_nodes(self.frame)
            except:
                self.frame -= 1
                try:
                    self.update_nodes(self.frame)
                except:
                    self.frame = 1
                    self.update_nodes(0)
            self.update_prev_frames()

    def change_mode(self, mode: str):
        self.mode = mode

    def goto_frame(self, frame: int):
        if frame <= len(self.frame_data.frame_data):
            self.frame = frame
            self.update_nodes(self.frame)
            self.update_prev_frames()

    def insert_frame(self):
        self.log()
        self.frame_data.insert_frame(self.frame, self.hurtboxNode, self.hitbox_ids)
        if self.frame == len(self.frame_data.frame_data):
            self.frame += 1
        self.update_prev_frames()

    def update_frame(self):
        if self.frame - 1 < len(self.frame_data.frame_data):
            self.log()
            self.frame_data.update_frame(self.frame, self.hurtboxNode, self.hitbox_ids)

    def delete_frame(self):
        self.log()
        self.frame_data.delete_frame(self.frame)
        if self.frame != 1:
            self.frame -= 1
        self.update_nodes(self.frame)

    def update_nodes(self, frame: int):
        if self.get_nodes(frame) is not None:
            self.hurtboxNode = self.get_nodes(frame)[0]
            self.hitbox_ids = self.get_nodes(frame)[1]
            self.selectedNode = None
        self.update_prev_frames()
        # self.update_onions()

    def get_nodes(self, frame: int) -> List:
        try:
            return [copy.deepcopy(self.frame_data.frame_data[frame - 1]['hurtboxNode']),
                    copy.deepcopy(self.frame_data.frame_data[frame - 1]['hitbox_ids'])]
        except:
            pass

    def add_node(self, node: Node):
        self.log()
        self.selectedNode.add_node(node)

    def delete_node(self):
        self.log()
        delete_id = None
        for ids in self.hitbox_ids:
            if self.selectedNode == self.hitbox_ids[ids]['node']:
                delete_id = ids
        if delete_id is not None:
            del self.hitbox_ids[delete_id]
        self.selectedNode.delete_node()
        parent = self.selectedNode.parent
        if self.selectedNode == self.hurtboxNode:
            self.hurtboxNode = None
        self.selectedNode = parent

    def create_hurtbox(self, pos: Tuple):
        self.log()
        node = Node(pos, self.radius, 'line', True)
        self.hurtboxNode = node
        self.selectedNode = node

    def create_hitbox(self, pos: Tuple):
        self.log()
        node = Node(pos, self.radius, 'line', True)
        idn = TextPrompt.text_prompt(self.main_screen, 300, 100, 'id number:')
        damage = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Damage:')
        angle = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Angle from vertical:')
        kbg = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Knockback growth:')
        bkb = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Base knockback:')
        wbkb = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Weight based knockback:')
        shield_damage = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Shield damage:')
        for attribute in (idn, damage, angle, kbg, bkb, wbkb, shield_damage):
            if attribute is None:
                return None
        self.hitbox_ids['id{}'.format(idn)] = {'node': node, 'damage': int(damage), 'angle': int(angle), 'kbg': int(kbg),
                                             'bkb': int(bkb), 'wbkb': int(wbkb), 'shield_damage': int(shield_damage)}
        self.selectedNode = node
        self.clicking = False

    def select_node(self, pos: Tuple):
        if self.mode == 'select hurtbox':
            if self.hurtboxNode is not None:
                if self.hurtboxNode.select_node(pos) is not None:
                    self.selectedNode = self.hurtboxNode.select_node(pos)
                    return True
        elif self.mode == 'select hitbox':
            for ids in self.hitbox_ids:
                if self.hitbox_ids[ids]['node'].select_node(pos) is not None:
                    self.selectedNode = self.hitbox_ids[ids]['node']
                    return True
        else:
            if self.hurtboxNode is not None:
                if self.hurtboxNode.select_node(pos) is not None:
                    self.selectedNode = self.hurtboxNode.select_node(pos)
                    return True
                else:
                    for ids in self.hitbox_ids:
                        if self.hitbox_ids[ids]['node'].select_node(pos) is not None:
                            self.selectedNode = self.hitbox_ids[ids]['node'].select_node(pos)
                            return True
        return False

    def button_handle(self, pos: Tuple):
        for buttons in self.buttons:
            if buttons.button_rect.collidepoint(pos):
                if buttons.name == 'line':
                    self.change_mode('line')
                elif buttons.name == 'circle':
                    self.change_mode('circle')
                elif buttons.name == 'inc_radius':
                    self.radius += 1
                elif buttons.name == 'dec_radius':
                    self.radius -= 1
                elif buttons.name == 'create_hitbox':
                    self.change_mode('add hitbox')
                elif buttons.name == 'create_hurtbox':
                    self.change_mode('make hurtbox')
                elif buttons.name == 'edit':
                    self.change_mode('edit')
                elif buttons.name == 'delete_frame':
                    self.delete_frame()
                elif buttons.name == 'insert_frame':
                    self.insert_frame()
                elif buttons.name == 'update_frame':
                    self.update_frame()
                elif buttons.name == 'goto_frame':
                    frame = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Frame:')
                    if frame is not None:
                        try:
                            self.goto_frame(int(frame))
                        except:
                            TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid frame argument')
                elif buttons.name == 'save_animation':
                    self.frame_data.save_animation()
                elif buttons.name == 'load_animation':
                    self.load_animation()
                elif buttons.name == 'convert_poly':
                    self.frame_data.convert(self.center, 1 / self.scale)
                elif buttons.name == 'radius_select':
                    radius = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Radius:')
                    if radius is not None:
                        try:
                            self.radius = int(radius)
                        except:
                            TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid radius argument')
                elif buttons.name == 'play_ani':
                    fps = TextPrompt.text_prompt(self.main_screen, 300, 100, 'FPS:')
                    if fps is not None:
                        try:
                            self.play_animation(int(fps))
                        except:
                            TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid FPS argument')
                elif buttons.name == 'stop_ani':
                    self.playing = False
                elif buttons.name == 'duplicate':
                    self.change_mode('duplicate')
                elif buttons.name == 'select_center':
                    self.change_mode('select center')
                elif buttons.name == 'num_onions':
                    onions = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Onions:')
                    if onions is not None:
                        try:
                            self.onions = int(onions)
                        except:
                            TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid onion argument')
                elif buttons.name == 'select_scale':
                    scale = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Scale:')
                    if scale is not None:
                        try:
                            self.scale = int(scale)
                        except:
                            TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid scale argument')
                elif buttons.name == 'ruler_inc':
                    ruler_inc = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Ruler increment:')
                    if ruler_inc is not None:
                        try:
                            self.ruler_increment = int(ruler_inc)
                        except:
                            TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid ruler increment argument')
                elif buttons.name == 'add_image':
                    selected_image = pygame.image.load(TextPrompt.text_prompt(self.main_screen,
                                                                              300, 100, 'Add image to node'))
                    try:
                        self.selectedNode.add_image(selected_image)
                    except:
                        TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid image')
                elif buttons.name == 'move_image':
                    self.change_mode('move image')
                elif buttons.name == 'rotate_image':
                    self.change_mode('rotate image')
                elif buttons.name == 'scale_image':
                    scale = TextPrompt.text_prompt(self.main_screen, 300, 100, 'Scale:')
                    try:
                        self.selectedNode.scale_image(float(scale))
                    except:
                        TextPrompt.error_prompt(self.main_screen, 300, 100, 'Invalid scale argument')
                self.clicking = False
                return True
        for frames in range(1, 4):
            frame_rect = pygame.Rect(80 + 480 * (frames - 1), 725, 480, 150)
            if frame_rect.collidepoint(pos) and self.frame - frames > 0:
                self.goto_frame(self.frame - frames)
                return True
        return False

    def load_animation(self):
        self.frame = 1
        self.frame_data.load_animation()
        self.update_nodes(self.frame)

    def save_animation(self):
        self.frame_data.save_animation()

    # Legacy method of creating onion layers, removed because it slowed down processing.
    # def update_onions(self):
    #     onion = 0
    #     for onion_surface in self.onion_surfaces:
    #         onion += 1
    #         onion_surface.fill((255, 255, 255))
    #         if self.frame - onion > 0:
    #             frame_nodes = self.get_nodes(self.frame - onion)
    #             if frame_nodes is not None:
    #                 frame_nodes[0].draw_nodes(onion_surface, (0, 0, 0))
    #                 for hitboxNodes in frame_nodes[1]:
    #                     hitboxNodes.draw_nodes(onion_surface, (255, 0, 0))

    def update_prev_frames(self):
        frames_copy = self.frame_data.scale_all(0.3)
        self.frames_screen.fill((56, 128, 255))
        for frames in range(1, 4):
            pygame.draw.rect(self.frames_screen, (255, 255, 255), (80 + 480 * (frames - 1), 25, 480, 150))
            pygame.draw.rect(self.frames_screen, (0, 0, 0), (80 + 480 * (frames - 1), 25, 480, 150), 5)
            if self.frame - frames > 0:
                frame = font.render(str(self.frame - frames), True, (0, 0, 0))
                self.frames_screen.blit(frame, (90 + 480 * (frames - 1), 25))
                frame_nodes = frames_copy.goto_frame(self.frame - frames)
                if frame_nodes is not None:
                    frame_nodes[0].move_node((80 + 480 * (frames - 1), -35))
                    frame_nodes[0].draw_nodes(self.frames_screen, (0, 0, 0), ignore=True)
                    for ids in frame_nodes[1]:
                        frame_nodes[1][ids]['node'].move_node((80 + 480 * (frames - 1), -35))
                        frame_nodes[1][ids]['node'].draw_nodes(self.frames_screen, (0, 0, 0), ignore=True)

    def draw_guidance_rulers(self):
        needed_ruler_x = round((1600 - self.ruler_start[0]) / (self.scale * self.ruler_increment))
        needed_rulers_y = round((self.ruler_start[1] - self.GUI_screen.get_size()[1]) /
                              (self.scale * self.ruler_increment))
        for x_ruler in range(1, needed_ruler_x):
            pygame.draw.line(self.main_screen, (128, 128, 128), (x_ruler * self.scale * self.ruler_increment, 100),
                             (x_ruler * self.scale * self.ruler_increment, self.ruler_start[1]), 2)
        for y_ruler in range(needed_rulers_y):
            pygame.draw.line(self.main_screen, (128, 128, 128),
                             (0, self.ruler_start[1] - (y_ruler * self.scale * self.ruler_increment)),
                             (1600, self.ruler_start[1] - (y_ruler * self.scale * self.ruler_increment)), 2)

    def draw_onions(self):
        for onions in range(self.onions, 0, -1):
            if self.frame - onions > 0:
                frame_nodes = self.get_nodes(self.frame - onions)
                val = (onions / (self.onions + 1)) * 255
                if frame_nodes is not None:
                    frame_nodes[0].draw_nodes(self.main_screen, (val, val, val))
                    for ids in frame_nodes[1]:
                        frame_nodes[1][ids]['node'].draw_nodes(self.main_screen, (val, 0, 0))

    def draw_nodes(self):
        if self.hurtboxNode is not None:
            self.hurtboxNode.draw_nodes(self.main_screen, (0, 0, 0))
        for ids in self.hitbox_ids:
            self.hitbox_ids[ids]['node'].draw_nodes(self.main_screen, (255, 0, 0))
        if self.selectedNode is not None:
            self.selectedNode.highlight_node(self.main_screen, (0, 0, 255))

    def draw_buttons(self, pos: Tuple, surf: pygame.Surface):
        for buttons in self.buttons:
            buttons.draw(pos, self.clicking, surf)

    def draw_GUI(self, pos: Tuple):
        # Resetting the GUI surface
        self.GUI_screen.fill((56, 128, 255))

        # Rendering texts
        frame_display = font.render('Frame: {}'.format(str(self.frame)), True, (0, 0, 0))
        mode_display = font.render('Mode: {}'.format(str(self.mode)), True, (0, 0, 0))
        radius_display = font.render('Radius: {}'.format(str(self.radius)), True, (0, 0, 0))
        fps_display = font.render('FPS: {}'.format(str(round(clock.get_fps()))), True, (0, 0, 0))
        mouse_pos_display = font.render(str(mouse_pos), True, (0, 0, 0))
        center_display = font.render('Center: {}'.format(str(self.center)), True, (0, 0, 0))
        onions_display = font.render('Onions: {}'.format(str(self.onions)), True, (0, 0, 0))
        scale_display = font.render('Scale: {}'.format(str(self.scale)), True, (0, 0, 0))
        ruler_inc_display = font.render('Ruler increment (scaled): {}'.format(str(self.ruler_increment)),
                                        True, (0, 0, 0))

        # Drawing texts
        self.GUI_screen.blit(frame_display, (0, 120))
        self.GUI_screen.blit(mode_display, (0, 80))
        self.GUI_screen.blit(radius_display, (0, 100))
        self.GUI_screen.blit(scale_display, (200, 80))
        self.GUI_screen.blit(ruler_inc_display, (200, 100))
        self.GUI_screen.blit(center_display, (200, 120))
        self.GUI_screen.blit(onions_display, (500, 80))
        self.GUI_screen.blit(mouse_pos_display, (500, 100))
        self.GUI_screen.blit(fps_display, (700, 80))
        self.draw_buttons(pos, self.GUI_screen)

        # Placed here so the center is drawn under the GUI screen
        if self.clicking and self.mode == 'select center':
            self.center = pos
        pygame.draw.circle(self.main_screen, (255, 0, 255), self.center, 10)

        # Draw the GUI screen onto the main surface
        self.main_screen.blit(self.GUI_screen, (0, 0))

        # Drawing the cursor/node to duplicate
        if self.mode == 'circle':
            self.main_screen.blit(circle_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))
        elif self.mode == 'line':
            self.main_screen.blit(line_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))
        elif self.mode == 'duplicate':
            if self.selectedNode is not None and not self.selectedNode.main:
                offset = Animator.get_offset(self.selectedNode.pos, self.selectedNode.parent.pos)
                offsetted = (pos[0] + offset[0], pos[1] + offset[1])
                if self.selectedNode.parent.node_type == 'line' and self.selectedNode.node_type == 'line':
                    pygame.draw.circle(screen, (0, 0, 255), pos, int(self.selectedNode.parent.radius))
                    pygame.draw.polygon(screen, (0, 0, 255),
                                        connecter_hitbox(pos, offsetted, self.selectedNode.parent.radius))
                    pygame.draw.circle(screen, (0, 0, 255), tuple(int(p) for p in offsetted), int(self.radius))
                    pygame.draw.circle(screen, (128, 0, 0), pos, int(self.selectedNode.parent.radius))
                    pygame.draw.circle(screen, (128, 0, 0), tuple(int(p) for p in offsetted), int(self.radius))
            else:
                self.main_screen.blit(move_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))
                # need to work on the other cases.
        else:
            self.main_screen.blit(move_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))

    def draw_prev_frames(self):
        # Draws the frames screen, which updates upon frame change
        self.main_screen.blit(self.frames_screen, (0, 700))

    def play_animation(self, fps: int):
        self.playing = True
        self.draw_guidance_rulers()
        self.draw_prev_frames()
        frame = 0
        while self.playing:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.button_handle(mouse_pos)
            frame = (frame + 1) % (len(self.frame_data.frame_data) + 1)
            self.main_screen.fill((255, 255, 255))
            self.draw_guidance_rulers()
            frame_nodes = self.get_nodes(frame)
            if frame_nodes is not None:
                frame_nodes[0].draw_nodes(self.main_screen, (0, 0, 0), ignore=True)
                for ids in frame_nodes[1]:
                    frame_nodes[1][ids]['node'].draw_nodes(self.main_screen, (255, 0, 0), ignore=True)
            self.draw_prev_frames()
            self.draw_GUI(mouse_pos)

            if self.mode == 'circle':
                self.main_screen.blit(circle_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))
            elif self.mode == 'line':
                self.main_screen.blit(line_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))
            else:
                self.main_screen.blit(move_cursor, (mouse_pos[0] - 5, mouse_pos[1] - 5))
            pygame.display.update()
            clock.tick(fps)


# === DECLARATIONS ===
bruh = Animator(screen)

app = QApplication(sys.argv)

prev_mode = None

pygame.mouse.set_visible(False)

total_elapsed = 0
t = 1
times = []

loop = True

clock = pygame.time.Clock()

"""
=== KEYMAPPING ===
Types: 
    click: Functions on a single press of the key
    hold: Functions upon key hold

Keys:
    d:
        Type: click
        Description: Deletes the selected node
            
    e:
        Type: hold
        Description: Puts the animator into edit mode, where branch nodes can be resized. If the main node is 'edited', 
        it will simply move the entire node
    c:
        Type: hold
        Description: Duplicates the selected node to the node where user next clicks
    
    Space:
        Type: click
        Description:
            Adds frame
    1:
        Type: click
        Description: Decrements frame
    2:
        Type: click
        Description: Increments frame
            
    CTRL:
        Type: hold
        Description: Overrides selecting any node. This is used in junction with creating lines, circles, hitboxes,
        hurtboxes to create a node over the selection area of an existing node
    
    q:
        Type: click
        Description: Increments radius
    w:
        Type: click
        Description: Decrements radius
    
    r:
        Type: hold
        Description: Mouse click while holding to select only a hurtbox
    t:
        Type: hold
        Description: Mouse click while holding to only select a hitbox
    
    CTRL + z:
        Type: click
        Description: Undos the last action, up to 10 times
"""

try:
    while loop:
        mouse_pos = pygame.mouse.get_pos()
        radius_text = font.render(str(bruh.radius), False, (0, 0, 0))
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                bruh.clicking = True
                bruh.draw_guidance_rulers()
                bruh.draw_onions()
                bruh.draw_nodes()
                bruh.draw_GUI(mouse_pos)
                bruh.draw_prev_frames()
                if bruh.mode == 'override':
                    if prev_mode == 'line':
                        node = Node(mouse_pos, bruh.radius, 'line')
                        bruh.add_node(node)
                        bruh.selectedNode = node
                    elif prev_mode == 'circle':
                        circle_radius = sqrt((mouse_pos[0] - bruh.selectedNode.pos[0]) ** 2 +
                                      (mouse_pos[1] - bruh.selectedNode.pos[1]) ** 2)
                        node = Node(mouse_pos, circle_radius, 'circle')
                        bruh.add_node(node)
                        bruh.selectedNode = node
                    elif prev_mode == 'add hitbox':
                        bruh.create_hitbox(mouse_pos)
                        bruh.change_mode('line')
                        prev_mode = 'line'
                elif bruh.mode == 'duplicate' and bruh.selectedNode is not None:
                    if not bruh.selectedNode.main:
                        dupe = copy.deepcopy(bruh.selectedNode)
                        dupe.connect = []
                        bruh.select_node(mouse_pos)
                        dupe.move_node(Animator.get_offset(bruh.selectedNode.pos, dupe.parent.pos))
                        bruh.add_node(dupe)
                    bruh.change_mode('line')
                elif bruh.button_handle(mouse_pos):
                    pass
                elif bruh.select_node(mouse_pos):
                    pass
                elif bruh.mode == 'make hurtbox':
                    bruh.create_hurtbox(mouse_pos)
                    bruh.mode = 'line'
                elif bruh.mode == 'add hitbox':
                    bruh.create_hitbox(mouse_pos)
                    bruh.change_mode('line')
                elif bruh.selectedNode is not None:
                    if bruh.mode == 'line':
                        node = Node(mouse_pos, bruh.radius, 'line')
                        bruh.add_node(node)
                        bruh.selectedNode = node
                    elif bruh.mode == 'circle':
                        circle_radius = sqrt((mouse_pos[0] - bruh.selectedNode.pos[0]) ** 2 +
                                      (mouse_pos[1] - bruh.selectedNode.pos[1]) ** 2)
                        node = Node(mouse_pos, circle_radius, 'circle')
                        bruh.add_node(node)
                        bruh.selectedNode = node
                    elif bruh.mode == 'edit':
                        bruh.selectedNode.move_node(Animator.get_offset(mouse_pos, bruh.selectedNode.pos))
            elif event.type == pygame.MOUSEMOTION and bruh.clicking \
                    and bruh.mode in ('line', 'circle', 'make_hurtbox', 'add hitbox', 'edit', 'move image', 'rotate image',
                                      'select hitbox', 'select hurtbox'):
                if bruh.mode == 'edit' or (bruh.selectedNode is not None and bruh.selectedNode.main):
                    bruh.selectedNode.move_node(Animator.get_offset(mouse_pos, bruh.selectedNode.pos))
                elif bruh.mode == 'move image':
                    bruh.selectedNode.move_image(Animator.get_offset(mouse_pos, bruh.selectedNode.image_center))
                elif bruh.mode == 'rotate image':
                    angle = atan2(mouse_pos[1] - bruh.selectedNode.image_center[1],
                                 mouse_pos[0] - bruh.selectedNode.image_center[0])
                    bruh.selectedNode.rotate_image(-angle)
                elif bruh.selectedNode is not None and not bruh.selectedNode.main:
                    angle = Animator.get_angle(bruh.selectedNode.parent.pos, bruh.selectedNode.pos, mouse_pos)
                    bruh.selectedNode.rotate_node(angle, bruh.selectedNode.parent)

            elif event.type == pygame.MOUSEBUTTONUP:
                bruh.clicking = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    if bruh.select_node(mouse_pos):
                        bruh.delete_node()

                elif event.key == pygame.K_SPACE:
                    bruh.insert_frame()
                elif event.key == pygame.K_1:
                    if bruh.frame not in (0, 1):
                        bruh.goto_frame(bruh.frame - 1)
                elif event.key == pygame.K_2:
                    if bruh.frame < len(bruh.frame_data.frame_data):
                        bruh.goto_frame(bruh.frame + 1)
                    elif bruh.frame == len(bruh.frame_data.frame_data):
                        bruh.frame += 1
                        bruh.update_prev_frames()

                elif event.key == pygame.K_e:
                    prev_mode = bruh.mode
                    bruh.change_mode('edit')
                elif event.key == pygame.K_c:
                    prev_mode = bruh.mode
                    bruh.change_mode('duplicate')

                elif event.key == 306:
                    prev_mode = bruh.mode
                    bruh.change_mode('override')

                elif event.key == pygame.K_s:
                    bruh.draw_guidance_rulers()
                    bruh.draw_nodes()
                    pygame.image.save(screen, 'screenshot.jpg')

                elif event.key == pygame.K_q:
                    bruh.radius -= 1
                elif event.key == pygame.K_w:
                    bruh.radius += 1

                elif event.key == pygame.K_r:
                    prev_mode = bruh.mode
                    bruh.change_mode('select hurtbox')
                elif event.key == pygame.K_t:
                    prev_mode = bruh.mode
                    bruh.change_mode('select hitbox')

                elif pygame.KMOD_CTRL and event.key == pygame.K_z:
                    bruh.undo()

                elif event.key == pygame.K_o:
                    print("pwease don't remove me i swear i'm useful uwu")
                    None.add_node()
            elif event.type == pygame.KEYUP:
                if prev_mode is not None:
                    bruh.change_mode(prev_mode)
                    prev_mode = None

        bruh.draw_prev_frames()
        bruh.draw_guidance_rulers()
        bruh.draw_onions()
        bruh.draw_nodes()
        bruh.draw_GUI(mouse_pos)

        pygame.display.update()
        clock.tick(60)

except Exception as e:
    bruh.undo()
    bruh.save_animation()
    print('An exception has occured: {}'.format(e))

# doing stuff with time
# tome = []
# for timez in range(0, 100):
#     tome.append(times.count(timez))
# print(tome)
pygame.quit()
