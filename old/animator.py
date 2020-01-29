import pygame, copy, pickle, os, time, sys, tkinter, threading
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk
import numpy as np
from pygame.locals import *
from shapely import affinity
from shapely.geometry import *
from shapely.ops import *
from typing import *
from math import *
pygame.font.init()
font = pygame.font.SysFont('Arial', 16)

root_path = os.path.dirname(os.path.realpath(__file__))


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

    def add_frame(self, hurtboxNode: Node, hitbox_ids: Dict, center: Tuple, pan: Tuple, zoom: float, disp_center: Tuple):
        self.frame_data.append({'hurtboxNode': copy.deepcopy(hurtboxNode), 'hitbox_ids': copy.deepcopy(hitbox_ids),
                                'center': center, 'pan': pan, 'zoom': zoom, 'disp_center': disp_center})

    def goto_frame(self, frame: int):
        return [self.frame_data[frame - 1]['hurtboxNode'], self.frame_data[frame - 1]['hitbox_ids'],
                self.frame_data[frame - 1].get('center', (640, 720)), self.frame_data[frame - 1].get('pan', (0, 0)),
                self.frame_data[frame - 1].get('zoom', 1), self.frame_data[frame - 1].get('disp_center', (640, 720))]

    def insert_frame(self, frame: int, hurtboxNode: Node, hitbox_ids: Dict, center: Tuple, pan: Tuple, zoom: float, disp_center: Tuple):
        self.frame_data.insert(frame, {'hurtboxNode': copy.deepcopy(hurtboxNode), 'hitbox_ids': copy.deepcopy(hitbox_ids),
                                       'center': center, 'pan': pan, 'zoom': zoom, 'disp_center': disp_center})

    def update_frame(self, frame: int, hurtboxNode: Node, hitbox_ids: Dict, center: Tuple, pan: Tuple, zoom: float, disp_center: Tuple):
        self.frame_data[frame - 1] = {'hurtboxNode': copy.deepcopy(hurtboxNode),
                                       'hitbox_ids': copy.deepcopy(hitbox_ids),
                                      'center': center, 'pan': pan, 'zoom': zoom, 'disp_center': disp_center}

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

    def transform_per_frame(self):
        _copy = copy.deepcopy(self)
        for frame in _copy.frame_data:
            frame['hurtboxNode'].transform_node(frame.get('center', (640, 720)))
            for ids in frame['hitbox_ids']:
                frame['hitbox_ids'][ids]['node'].transform_node(frame.get('center', (640, 720)))
        return _copy

    def scale_all(self, factor: float):
        _copy = copy.deepcopy(self)
        for frame in _copy.frame_data:
            frame['hurtboxNode'].scale_node(factor)
            for ids in frame['hitbox_ids']:
                frame['hitbox_ids'][ids]['node'].scale_node(factor)
        return _copy

    def polygonize(self, factor) -> List:
        frames_polygonized = []
        frame_count = -1
        for frame in self.frame_data:
            frame_count += 1
            hurtboxPoly = frame['hurtboxNode'].polygonize()
            hitboxPolys = {}
            for ids in frame['hitbox_ids']:
                hitboxPolys[ids] = {}
                hitboxPolys[ids]['polygon'] = frame['hitbox_ids'][ids]['node'].polygonize()
                for attribute in frame['hitbox_ids'][ids]:
                    if attribute != 'node':
                        hitboxPolys[ids][attribute] = frame['hitbox_ids'][ids][attribute]
            frames_polygonized.append({'hurtboxPoly': hurtboxPoly, 'hitboxPolys': hitboxPolys,
                                       'increment': self.get_increment(self.frame_data, frame_count, factor)})
        return frames_polygonized

    def get_increment(self, frame_data, frame_index, factor):
        if frame_index != 0:
            return [(frame_data[frame_index]['center'][0] - frame_data[frame_index - 1]['center'][0]) * factor,
                    (frame_data[frame_index]['center'][1] - frame_data[frame_index - 1]['center'][1]) * factor]
        return [0.0, 0.0]

    def convert(self, factor: float, path):
        # This function will parse each frame in frame data to be readable by Characters
        converted = self.transform_per_frame().scale_all(factor).polygonize(factor)
        with open('{}.plypk'.format(path), 'wb') as output:
            pickle.dump(converted, output, pickle.HIGHEST_PROTOCOL)

    def save_animation(self, path):
        with open('{}.anipk'.format(path), 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def load_animation(self, path):
        try:
            with open(path, 'rb') as _input:
                self.frame_data = pickle.load(_input).frame_data
        except:
            print('File not found.')


class Animator:
    frame: int
    radius: int
    mode: str

    frame_data: InfoContainer
    logs: List

    onions: int

    main_screen: pygame.Surface
    frames_screen: pygame.Surface

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

    def __init__(self, main_screen: pygame.Surface, onions=3, scale=8, ruler_start=(0, 720), ruler_increment=15,
                 center=(640, 720)):
        self.frame = 1
        self.frame_data = InfoContainer()
        self.hurtboxNode = None
        self.hitbox_ids = {}
        self.selectedNode = None
        self.radius = 30
        self.mode = 'make hurtbox'
        self.clicking = False
        self.main_screen = main_screen
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
        self.prev_mode = None
        self.zoom = 1
        self.pan = (0, 0)
        self.background = pygame.Surface((1280, 720))
        self.background.fill((255, 255, 255))
        self.bg_pan = (0, 0)
        self.real_center = self.center
        self.onion_follow = 0

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

    def change_radius(self, radius: int):
        self.radius = radius

    def change_mode(self, mode: str):
        self.mode = mode

    def goto_frame(self, frame: int):
        if frame <= len(self.frame_data.frame_data):
            self.frame = frame
            self.update_nodes(self.frame)
            self.update_prev_frames()

    def insert_frame(self):
        self.log()
        self.frame_data.insert_frame(self.frame, self.hurtboxNode, self.hitbox_ids, self.real_center, self.pan, self.zoom, self.center)
        if self.frame == len(self.frame_data.frame_data):
            self.frame += 1
        self.update_prev_frames()

    def update_frame(self):
        if self.frame - 1 < len(self.frame_data.frame_data):
            self.log()
            self.frame_data.update_frame(self.frame, self.hurtboxNode, self.hitbox_ids, self.real_center, self.pan, self.zoom, self.center)

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
            self.real_center = self.get_nodes(frame)[2]
            self.pan = self.get_nodes(frame)[3]
            self.zoom = self.get_nodes(frame)[4]
            self.center = self.get_nodes(frame)[5]
            self.selectedNode = None
        self.update_prev_frames()

    def get_nodes(self, frame: int) -> List:
        try:
            return [copy.deepcopy(self.frame_data.frame_data[frame - 1]['hurtboxNode']),
                    copy.deepcopy(self.frame_data.frame_data[frame - 1]['hitbox_ids']),
                    self.frame_data.frame_data[frame - 1].get('center', (640, 720)),
                    self.frame_data.frame_data[frame - 1].get('pan', (0, 0)),
                    self.frame_data.frame_data[frame - 1].get('zoom', 1),
                    self.frame_data.frame_data[frame - 1].get('disp_center', (640, 720))]
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

    def create_hitbox_type(self, pos: Tuple):
        self.log()
        popup = Toplevel()
        Label(popup, text='Hitbox Type', width=20, font='arial 12').grid(row=0, column=0, columnspan=3)
        Button(popup, text='Regular', width=20,
               command=lambda: self.create_regular_hitbox(pos, popup)).grid(row=1, column=0)
        Button(popup, text='Grab', width=20,
               command=lambda: self.create_grab_hitbox(pos, popup)).grid(row=1, column=1)
        Button(popup, text='Projectile', width=20,
               command=lambda: self.create_projectile_hitbox(pos, popup)).grid(row=1, column=2)

    def create_regular_hitbox(self, pos: Tuple, popup):
        popup.destroy()
        node = Node(pos, self.radius, 'line', True)
        idn = simpledialog.askstring('id', 'id Number:')
        damage = simpledialog.askstring('Damage', 'Damage:')
        angle = simpledialog.askstring('Angle', 'Angle:')
        kbg = simpledialog.askstring('KBG', 'Knockback Growth:')
        bkb = simpledialog.askstring('BKB', 'Base Knockback:')
        wbkb = simpledialog.askstring('WBKB', 'Weight-Based Knockback:')
        shield_damage = simpledialog.askstring('Shield Damage', 'Shield Damage:')
        for attribute in (idn, damage, angle, kbg, bkb, wbkb, shield_damage):
            if attribute is None:
                return None
        self.hitbox_ids['id{}'.format(idn)] = {'node': node, 'damage': int(damage), 'angle': int(angle),
                                               'kbg': int(kbg),
                                               'bkb': int(bkb), 'wbkb': int(wbkb), 'shield_damage': int(shield_damage)}
        self.selectedNode = node
        self.clicking = False

    def create_grab_hitbox(self, pos: Tuple, popup):
        popup.destroy()
        node = Node(pos, self.radius, 'line', True)
        idn = simpledialog.askstring('id', 'id Number:')
        if idn is not None and idn != '':
            self.hitbox_ids['id{}'.format(idn)] = {'node': node}
        self.selectedNode = node
        self.clicking = False

    def create_projectile_hitbox(self, pos: Tuple, popup):
        popup.destroy()
        node = Node(pos, self.radius, 'line', True)
        idn = simpledialog.askstring('id', 'id Number:')
        x_inc = simpledialog.askinteger('x increment', 'x increment:')
        y_inc = simpledialog.askinteger('y increment', 'y increment:')
        for attribute in (idn, x_inc, y_inc):
            if attribute is None:
                return None
        self.hitbox_ids['id{}'.format(idn)] = {'node': node, 'increment': [x_inc, y_inc]}
        self.selectedNode = node
        self.clicking = False

    def change_zoom(self, factor, center):
        self.zoom *= factor
        self.scale *= factor
        self.pan = (self.pan[0] / self.zoom, self.pan[1] / self.zoom)
        self.transform(factor, (0, 0), center)

    def change_pan(self, real_pan: Tuple):
        self.pan = (self.pan[0] + (real_pan[0] / self.zoom), self.pan[1] + (real_pan[1] / self.zoom))
        self.center = (self.center[0] + real_pan[0], self.center[1] + real_pan[1])
        self.transform(1, real_pan, self.center)

    def transform(self, factor: float, pan: Tuple, center):
        if self.hurtboxNode is not None:
            self.hurtboxNode = copy.deepcopy(self.hurtboxNode)
            self.hurtboxNode.transform_node(center)
            self.hurtboxNode.scale_node(factor)
            self.hurtboxNode.move_node(pan)
            self.hurtboxNode.transform_node((-center[0], -center[1]))
        for ids in self.hitbox_ids:
            self.hitbox_ids[ids]['node'].transform_node(center)
            self.hitbox_ids[ids]['node'].scale_node(factor)
            self.hitbox_ids[ids]['node'].move_node(pan)
            self.hitbox_ids[ids]['node'].transform_node((center[0], center[1]))
        dc_center = (factor * (self.center[0] - center[0]),
                     factor * (self.center[1] - center[1]))
        self.center = (int(dc_center[0] + center[0]), int(dc_center[1] + center[1]))
        self.selectedNode = None

        bg_transform = (factor * (self.bg_pan[0] - center[0]),
                        factor * (self.bg_pan[1] - center[1]))
        self.background = pygame.transform.scale(self.background,
                                    (int(
                                        self.background.get_width() * factor),
                                     int(
                                         self.background.get_height() * factor)))
        self.bg_pan = (bg_transform[0] + center[0] + pan[0],
                       bg_transform[1] + center[1] + pan[1])

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

    def select_center(self, mouse_pos: Tuple):
        offset = (mouse_pos[0] - self.center[0], mouse_pos[1] - self.center[1])
        real_offset = ((mouse_pos[0] - self.center[0]) / self.zoom,
                       (mouse_pos[1] - self.center[1]) / self.zoom)
        self.real_center = (self.real_center[0] + real_offset[0],
                            self.real_center[1] + real_offset[1])
        self.center = mouse_pos
        if self.hurtboxNode is not None:
            self.hurtboxNode.move_node(offset)
        for ids in self.hitbox_ids:
            self.hitbox_ids[ids]['node'].move_node(offset)

    def load_animation(self, path):
        self.frame = 1
        self.frame_data.load_animation(path)
        self.update_nodes(self.frame)

    def save_animation(self, path):
        self.frame_data.save_animation(path)

    def update_prev_frames(self):
        frames_copy = self.frame_data.transform_per_frame().scale_all(0.25)
        self.frames_screen.fill((102, 204, 255))
        padding = 5
        for frames in range(1, 5):
            pygame.draw.rect(self.frames_screen, (255, 255, 255),
                             (320 * (frames - 1) + padding, padding, 320 - 2 * padding, 180 - 2 * padding))
            pygame.draw.rect(self.frames_screen, (0, 0, 0),
                             (320 * (frames - 1) + padding, padding, 320 - 2 * padding, 180 - 2 * padding), 2)
            if self.frame - frames > 0:
                frame = font.render('Frame {}'.format(str(self.frame - frames)), True, (0, 0, 0))
                self.frames_screen.blit(frame, (320 * (frames - 1) + padding + 5, padding + 5))
                frame_nodes = frames_copy.goto_frame(self.frame - frames)
                if frame_nodes is not None:
                    x_mid = 320 * (frames - 1) + padding + 160
                    y_c = 180 - 2 * padding
                    frame_nodes[0].move_node((x_mid, y_c))
                    frame_nodes[0].draw_nodes(self.frames_screen, (0, 0, 0), ignore=True)
                    for ids in frame_nodes[1]:
                        frame_nodes[1][ids]['node'].move_node((320 * (frames - 1) + padding, -padding))
                        frame_nodes[1][ids]['node'].draw_nodes(self.frames_screen, (0, 0, 0), ignore=True)

    def load_background(self):
        file = filedialog.askopenfilename(initialdir=root_path, title='Select file',
                                          filetypes=(("PNG", "*.png"),
                                                     ("All files", "*.*")))
        image = pygame.image.load(file)
        background = pygame.transform.scale(image, (image.get_width() * self.scale, image.get_height() * self.scale))
        self.bg_pan = (-background.get_width() / 2, -background.get_height() / 2)
        self.background = background

    def draw_background(self):
        self.main_screen.blit(self.background, self.bg_pan)

    def draw_guidance_rulers(self):
        needed_ruler_x = round((1300 - self.ruler_start[0]) / (self.scale * self.ruler_increment))
        needed_rulers_y = round(self.ruler_start[1] / (self.scale * self.ruler_increment))
        for x_ruler in range(needed_ruler_x):
            pygame.draw.line(self.main_screen, (128, 128, 128), (x_ruler * self.scale * self.ruler_increment, 0),
                             (x_ruler * self.scale * self.ruler_increment, self.ruler_start[1]), 2)
        for y_ruler in range(needed_rulers_y):
            pygame.draw.line(self.main_screen, (128, 128, 128),
                             (0, self.ruler_start[1] - (y_ruler * self.scale * self.ruler_increment)),
                             (1300, self.ruler_start[1] - (y_ruler * self.scale * self.ruler_increment)), 2)

    def draw_onions(self):
        for onions in range(self.onions, 0, -1):
            if self.frame - onions > 0:
                frame_nodes = self.get_nodes(self.frame - onions)
                if frame_nodes[0] is not None:
                    frame_nodes[0].transform_node(frame_nodes[5])
                    frame_nodes[0].scale_node(self.zoom / frame_nodes[4])
                    frame_nodes[0].move_node((self.pan[0] - frame_nodes[3][0],
                                              self.pan[1] - frame_nodes[3][1]))
                    frame_nodes[0].transform_node((-frame_nodes[5][0], -frame_nodes[5][1]))
                    if self.onion_follow:
                        frame_nodes[0].move_node((self.center[0] - frame_nodes[5][0],
                                                  self.center[1] - frame_nodes[5][1]))
                for ids in frame_nodes[1]:
                    frame_nodes[1][ids]['node'].transform_node(frame_nodes[5])
                    frame_nodes[1][ids]['node'].scale_node(self.zoom / frame_nodes[4])
                    frame_nodes[1][ids]['node'].move_node((self.pan[0] - frame_nodes[3][0],
                                                   self.pan[1] - frame_nodes[3][1]))
                    frame_nodes[1][ids]['node'].transform_node(
                        (-frame_nodes[5][0], -frame_nodes[5][1]))
                    if self.onion_follow:
                        frame_nodes[1][ids].move_node((self.center[0] - frame_nodes[5][0],
                                                       self.center[1] - frame_nodes[5][1]))

                val = (onions / (self.onions + 1)) * 255
                if frame_nodes[0] is not None:
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

    def draw_prev_frames(self):
        # Draws the frames screen, which updates upon frame change
        self.main_screen.blit(self.frames_screen, (0, 720))

    def play_animation(self, fps: int, root):
        self.playing = True
        self.draw_guidance_rulers()
        self.draw_prev_frames()
        pygame.mouse.set_visible(True)
        frame = 0
        while self.playing:
            frame = (frame + 1) % (len(self.frame_data.frame_data) + 1)
            self.main_screen.fill((255, 255, 255))
            self.draw_guidance_rulers()
            frame_nodes = self.get_nodes(frame)
            if frame_nodes[0] is not None:
                frame_nodes[0].transform_node(frame_nodes[5])
                frame_nodes[0].scale_node(self.zoom / frame_nodes[4])
                frame_nodes[0].move_node((self.pan[0] - frame_nodes[3][0],
                                          self.pan[1] - frame_nodes[3][1]))
                frame_nodes[0].transform_node(
                    (-frame_nodes[5][0], -frame_nodes[5][1]))
                frame_nodes[0].move_node((self.center[0] - frame_nodes[5][0],
                                          self.center[1] - frame_nodes[5][1]))
            for ids in frame_nodes[1]:
                frame_nodes[1][ids]['node'].transform_node(frame_nodes[5])
                frame_nodes[1][ids]['node'].scale_node(self.zoom / frame_nodes[4])
                frame_nodes[1][ids]['node'].move_node((self.pan[0] - frame_nodes[3][0],
                                               self.pan[1] - frame_nodes[3][1]))
                frame_nodes[1][ids]['node'].transform_node(
                    (-frame_nodes[5][0], -frame_nodes[5][1]))
                frame_nodes[1][ids]['node'].move_node(
                    (self.center[0] - frame_nodes[5][0],
                     self.center[1] - frame_nodes[5][1]))
            if frame_nodes is not None:
                frame_nodes[0].draw_nodes(self.main_screen, (0, 0, 0), ignore=True)
                for ids in frame_nodes[1]:
                    frame_nodes[1][ids]['node'].draw_nodes(self.main_screen, (255, 0, 0), ignore=True)
            self.draw_prev_frames()
            pygame.display.update()
            root.update()
            clock.tick(fps)


class AnimatorWindow:

    def __init__(self):
        self.root = Tk()
        self.root.geometry('1600x900+0+0')
        self.root.configure(bg='#66ccff')
        self.setup_UI()
        self.done = False
        self.animatorplay = True

    def setup_UI(self):
        style = ttk.Style()
        style.theme_use('clam')

        self.root.option_add('*Font', 'arial 10')

        embed = Frame(self.root, width=1280, height=900)
        embed.grid(row=0, column=1, sticky=E, rowspan=30)
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        self.mscreen = pygame.display.set_mode((1280, 900))
        self.animator = Animator(self.mscreen)

        menubar = Menu(self.root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Export Polygon", command=self.export_polygon)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=sys.exit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.animator.undo)
        editmenu.add_command(label="Redo")
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        # Special tools
        special_tools = Frame(self.root, width=300, height=100, bg='#99ddff', borderwidth=3, relief=SUNKEN)
        special_tools.grid(row=3, column=0, padx=10, pady=10)

        special_tools_label = Label(special_tools, text='-Special Tools-', bg='#99ddff', font='arial 12')
        special_tools_label.grid(row=0, column=0, columnspan=2, pady=5)

        play_animator = ttk.Button(special_tools, text='Play Animator', width=20, command=self.play_animator)
        play_animator.grid(row=1, column=0, padx=5, pady=5)

        pause_animator = ttk.Button(special_tools, text='Pause Animator', width=20, command=self.pause_animator)
        pause_animator.grid(row=1, column=1, padx=5, pady=5)

        # Animator Editor Tools
        editor_tools = Frame(self.root, width=300, height=100, bg='#99ddff', borderwidth=3, relief=SUNKEN)
        editor_tools.grid(row=1, column=0, padx=10, pady=10)

        editor_tools_label = Label(editor_tools, text='-Editor Tools-', bg='#99ddff', font='arial 12')
        editor_tools_label.grid(row=0, column=0, columnspan=2, pady=5)

        line = ttk.Button(editor_tools, text='Line Mode', width=20, command=lambda: self.animator.change_mode('line'))
        line.grid(row=1, column=0, padx=5, pady=5)

        circle = ttk.Button(editor_tools, text='Circle Mode', width=20, command=lambda: self.animator.change_mode('circle'))
        circle.grid(row=1, column=1, padx=5, pady=5)

        edit = ttk.Button(editor_tools, text='Edit Node', width=20, command=lambda: self.animator.change_mode('edit'))
        edit.grid(row=2, column=0, padx=5, pady=5)

        duplicate = ttk.Button(editor_tools, text='Duplicate Node', width=20,
                               command=lambda: self.animator.change_mode('duplicate'))
        duplicate.grid(row=2, column=1, padx=5, pady=5)

        make_hurtbox = ttk.Button(editor_tools, text='Make Hurtbox', width=20,
                                  command=lambda: self.animator.change_mode('make hurtbox'))
        make_hurtbox.grid(row=3, column=0, padx=5, pady=5)

        add_hitbox = ttk.Button(editor_tools, text='Add Hitbox', width=20,
                                command=lambda: self.animator.change_mode('add hitbox'))
        add_hitbox.grid(row=3, column=1, padx=5, pady=5)

        inc_radius = ttk.Button(editor_tools, text='Radius +', width=20,
                                command=lambda: self.animator.change_radius(self.animator.radius + 1))
        inc_radius.grid(row=4, column=0, padx=5, pady=5)

        dec_radius = ttk.Button(editor_tools, text='Radius -', width=20,
                                command=lambda: self.animator.change_radius(self.animator.radius - 1))
        dec_radius.grid(row=4, column=1, padx=5, pady=5)

        # Animator Tools
        ag_tools = Frame(self.root, width=300, height=100, bg='#99ddff', borderwidth=3, relief=SUNKEN)
        ag_tools.grid(row=2, column=0, padx=10, pady=10)

        ag_tools_label = Label(ag_tools, text='-Animator General Tools-', bg='#99ddff', font='arial 12')
        ag_tools_label.grid(row=0, column=0, columnspan=2, pady=5)

        add_frame = ttk.Button(ag_tools, text='Add Frame', width=20, command=self.animator.insert_frame)
        add_frame.grid(row=1, column=0, padx=5, pady=5)

        update_frame = ttk.Button(ag_tools, text='Update Frame', width=20, command=self.animator.update_frame)
        update_frame.grid(row=1, column=1, padx=5, pady=5)

        delete_frame = ttk.Button(ag_tools, text='Delete Frame', width=20, command=self.animator.delete_frame)
        delete_frame.grid(row=2, column=0, padx=5, pady=5)

        choose_onions = ttk.Button(ag_tools, text='Select Onions', width=20, command=self.select_onions)
        choose_onions.grid(row=2, column=1, padx=5, pady=5)

        select_scale = ttk.Button(ag_tools, text='Select Scale', width=20, command=self.select_scale)
        select_scale.grid(row=3, column=0, padx=5, pady=5)

        select_ruler_inc = ttk.Button(ag_tools, text='Select Ruler Increment', width=20, command=self.select_ruler_inc)
        select_ruler_inc.grid(row=3, column=1, padx=5, pady=5)

        add_img = ttk.Button(ag_tools, text='Add Image To Node', width=20, command=self.add_img)
        add_img.grid(row=4, column=0, padx=5, pady=5)

        move_img = ttk.Button(ag_tools, text='Move Image', width=20,
                              command=lambda: self.animator.change_mode('move image'))
        move_img.grid(row=4, column=1, padx=5, pady=5)

        rotate_img = ttk.Button(ag_tools, text='Rotate Image', width=20,
                                  command=lambda: self.animator.change_mode('rotate image'))
        rotate_img.grid(row=5, column=0, padx=5, pady=5)

        scale_img = ttk.Button(ag_tools, text='Scale Image', width=20,
                               command=self.scale_img)
        scale_img.grid(row=5, column=1, padx=5, pady=5)

        add_background = ttk.Button(ag_tools, text='Load Background', width=20, command=self.animator.load_background)
        add_background.grid(row=6,column=0, padx=5, pady=5)

        self.onion_follow = BooleanVar()
        self.onion_follow.set(False)
        onion_follow = Checkbutton(ag_tools, text='Follow Onions', variable=self.onion_follow,
                                   command=self.change_onion_follow)
        onion_follow.grid(row=6, column=1, padx=5, pady=5)

        move_background = ttk.Button(ag_tools, text='Move Background', width=20,
                                     command=lambda: self.animator.change_mode('move background'))
        move_background.grid(row=7, column=0, padx=5, pady=5)

        play = ttk.Button(ag_tools, text='Play Animation', width=20, command=self.play_animation)
        play.grid(row=8, column=0, padx=5, pady=5)

        stop = ttk.Button(ag_tools, text='Pause Animation', width=20, command=self.stop_animation)
        stop.grid(row=8, column=1, padx=5, pady=5)

        # States
        states = Frame(self.root, width=300, height=100, bg='#99ddff', borderwidth=3, relief=SUNKEN)
        states.grid(row=0, column=0, padx=10, pady=10)

        states_label = Label(states, text='-States-', bg='#99ddff', font='arial 12')
        states_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.frame = StringVar()
        lframe = Label(states, textvariable=self.frame, width=15)
        lframe.grid(row=1, column=0, padx=5, pady=5)

        self.mode = StringVar()
        lmode = Label(states, textvariable=self.mode, width=15)
        lmode.grid(row=1, column=1, padx=5, pady=5)

        self.radius = StringVar()
        lradius = Label(states, textvariable=self.radius, width=15)
        lradius.grid(row=2, column=0, padx=5, pady=5)

        self.onions = StringVar()
        lonions = Label(states, textvariable=self.onions, width=15)
        lonions.grid(row=2, column=1, padx=5, pady=5)

        self.scale = StringVar()
        lscale = Label(states, textvariable=self.scale, width=15)
        lscale.grid(row=3, column=0, padx=5, pady=5)

        self.ruler_inc = StringVar()
        lruler_inc = Label(states, textvariable=self.ruler_inc, width=15)
        lruler_inc.grid(row=3, column=1, padx=5, pady=5)

        self.center = StringVar()
        lcenter = Label(states, textvariable=self.center, width=15)
        lcenter.grid(row=4, column=0)

        self.mouse_pos = StringVar()
        lmouse_pos = Label(states, textvariable=self.mouse_pos, width=15)
        lmouse_pos.grid(row=4, column=1, padx=5, pady=5)


        self.root.config(menu=menubar)

    def open(self):
        file = filedialog.askopenfilename(initialdir=root_path, title='Select file',
                                          filetypes=(('anipk Files', '*.anipk'),
                                                     ('All Files', '*.*')))
        if file != '' and file is not None:
            self.animator.load_animation(file)

    def save(self):
        file = filedialog.asksaveasfilename(initialdir=root_path,
                                            title="Select file",
                                            filetypes=(("anipk Files", "*.anipk"),
                                                       ("All Files", "*.*")))
        if file != '' and file is not None:
            self.animator.save_animation(file)

    def export_polygon(self):
        file = filedialog.asksaveasfilename(initialdir=root_path,
                                            title="Select file",
                                            filetypes=(("plypk Files", "*.plypk"),
                                                       ("All files", "*.*")))
        if file != '' and file is not None:
            self.animator.frame_data.convert(1 / self.animator.scale, file)

    def pause_animator(self):
        self.animatorplay = False

    def play_animator(self):
        self.animatorplay = True

    def play_animation(self):
        fps = simpledialog.askinteger('FPS', 'FPS:')
        self.animator.play_animation(fps, self.root)

    def stop_animation(self):
        self.animator.playing = False

    def goto_frame(self):
        frame = simpledialog.askinteger('Go To Frame', 'Frame:')
        self.animator.goto_frame(frame)

    def select_onions(self):
        onions = simpledialog.askinteger('Choose Onions', 'Onions:')
        self.animator.onions = onions

    def select_scale(self):
        scale = simpledialog.askinteger('Select Scale', 'Scale:')
        self.animator.scale = scale

    def select_ruler_inc(self):
        ruler_inc = simpledialog.askinteger('Select Ruler Increment', 'Ruler Increment:')
        self.animator.ruler_increment = ruler_inc

    def add_img(self):
        image = filedialog.askopenfilename(initialdir=root_path, title='Select file',
                                          filetypes=(("PNG", "*.png"),
                                                     ("All files", "*.*")))
        loaded_image = pygame.image.load(image)
        self.animator.selectedNode.add_image(loaded_image)

    def scale_img(self):
        scale = simpledialog.askfloat('Select Scale', 'Scale:')
        self.animator.selectedNode.scale_image(scale)

    def change_onion_follow(self):
        self.animator.onion_follow = self.onion_follow.get()

    def eventloop(self):
        mouse_pos = pygame.mouse.get_pos()
        self.mscreen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.animator.clicking = True
                if event.button == 4:
                    self.animator.change_zoom(2, mouse_pos)
                elif event.button == 5:
                    self.animator.change_zoom(0.5, mouse_pos)
                elif self.animator.mode == 'move background':
                    global orig_pos
                    orig_pos = mouse_pos
                elif self.animator.mode == 'override':
                    if self.animator.prev_mode == 'line':
                        node = Node(mouse_pos, self.animator.radius, 'line')
                        self.animator.add_node(node)
                        self.animator.selectedNode = node
                    elif self.animator.prev_mode == 'circle':
                        circle_radius = sqrt((mouse_pos[0] - self.animator.selectedNode.pos[0]) ** 2 +
                                             (mouse_pos[1] - self.animator.selectedNode.pos[1]) ** 2)
                        node = Node(mouse_pos, circle_radius, 'circle')
                        self.animator.add_node(node)
                        self.animator.selectedNode = node
                    elif self.animator.prev_mode == 'add hitbox':
                        self.animator.create_hitbox_type(mouse_pos)
                        self.animator.change_mode('line')
                        self.animator.prev_mode = 'line'
                elif pygame.Rect(self.animator.center[0] - 10, self.animator.center[1] - 10, 20, 20).collidepoint(mouse_pos):
                    self.animator.prev_mode = self.animator.mode
                    self.animator.change_mode('select center')
                elif self.animator.mode == 'duplicate' and self.animator.selectedNode is not None:
                    if not self.animator.selectedNode.main:
                        dupe = copy.deepcopy(self.animator.selectedNode)
                        dupe.connect = []
                        self.animator.select_node(mouse_pos)
                        dupe.move_node(Animator.get_offset(self.animator.selectedNode.pos, dupe.parent.pos))
                        self.animator.add_node(dupe)
                    self.animator.change_mode('line')
                elif self.animator.select_node(mouse_pos):
                    pass
                elif self.animator.mode == 'make hurtbox':
                    self.animator.create_hurtbox(mouse_pos)
                    self.animator.change_mode('line')
                    self.animator.mode = 'line'
                elif self.animator.mode == 'add hitbox':
                    self.animator.create_hitbox_type(mouse_pos)
                    self.animator.change_mode('line')
                elif self.animator.mode == 'select center':
                    self.animator.select_center(mouse_pos)
                elif self.animator.selectedNode is not None:
                    if self.animator.mode == 'line':
                        node = Node(mouse_pos, self.animator.radius, 'line')
                        self.animator.add_node(node)
                        self.animator.selectedNode = node
                    elif self.animator.mode == 'circle':
                        circle_radius = sqrt((mouse_pos[0] - self.animator.selectedNode.pos[0]) ** 2 +
                                             (mouse_pos[1] - self.animator.selectedNode.pos[1]) ** 2)
                        node = Node(mouse_pos, circle_radius, 'circle')
                        self.animator.add_node(node)
                        self.animator.selectedNode = node
                    elif self.animator.mode == 'edit':
                        self.animator.selectedNode.move_node(
                            Animator.get_offset(mouse_pos, self.animator.selectedNode.pos))
            elif event.type == pygame.MOUSEMOTION and self.animator.clicking:
                if self.animator.mode == 'select center':
                    self.animator.select_center(mouse_pos)
                elif self.animator.mode == 'move background':
                    self.animator.change_pan((mouse_pos[0] - orig_pos[0], mouse_pos[1] - orig_pos[1]))
                    orig_pos = mouse_pos
                elif self.animator.mode == 'edit' or (
                        self.animator.selectedNode is not None and self.animator.selectedNode.main):
                    self.animator.selectedNode.move_node(Animator.get_offset(mouse_pos, self.animator.selectedNode.pos))
                elif self.animator.mode == 'move image':
                    self.animator.selectedNode.move_image(
                        Animator.get_offset(mouse_pos, self.animator.selectedNode.image_center))
                elif self.animator.mode == 'rotate image':
                    angle = atan2(mouse_pos[1] - self.animator.selectedNode.image_center[1],
                                  mouse_pos[0] - self.animator.selectedNode.image_center[0])
                    self.animator.selectedNode.rotate_image(-angle)
                elif self.animator.selectedNode is not None and not self.animator.selectedNode.main:
                    angle = Animator.get_angle(self.animator.selectedNode.parent.pos, self.animator.selectedNode.pos,
                                               mouse_pos)
                    self.animator.selectedNode.rotate_node(angle, self.animator.selectedNode.parent)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.animator.clicking = False
                if self.animator.mode == 'select center':
                    self.animator.change_mode(self.animator.prev_mode)
                    self.animator.prev_mode = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    if self.animator.select_node(mouse_pos):
                        self.animator.delete_node()

                elif event.key == pygame.K_SPACE:
                    self.animator.insert_frame()
                elif event.key == pygame.K_1:
                    if self.animator.frame not in (0, 1):
                        self.animator.goto_frame(self.animator.frame - 1)
                elif event.key == pygame.K_2:
                    if self.animator.frame < len(self.animator.frame_data.frame_data):
                        self.animator.goto_frame(self.animator.frame + 1)
                    elif self.animator.frame == len(self.animator.frame_data.frame_data):
                        self.animator.frame += 1
                        self.animator.update_prev_frames()

                elif event.key == pygame.K_e:
                    self.animator.prev_mode = self.animator.mode
                    self.animator.change_mode('edit')
                elif event.key == pygame.K_c:
                    self.animator.prev_mode = self.animator.mode
                    self.animator.change_mode('duplicate')

                elif event.key == 306:
                    self.animator.prev_mode = self.animator.mode
                    self.animator.change_mode('override')

                elif event.key == pygame.K_q:
                    self.animator.radius -= 1
                elif event.key == pygame.K_w:
                    self.animator.radius += 1

                elif event.key == pygame.K_r:
                    self.animator.prev_mode = self.animator.mode
                    self.animator.change_mode('select hurtbox')
                elif event.key == pygame.K_t:
                    self.animator.prev_mode = self.animator.mode
                    self.animator.change_mode('select hitbox')

                elif event.key == pygame.K_LEFT:
                    self.animator.change_pan((50, 0))
                elif event.key == pygame.K_RIGHT:
                    self.animator.change_pan((-50, 0))
                elif event.key == pygame.K_UP:
                    self.animator.change_pan((0, 50))
                elif event.key == pygame.K_DOWN:
                    self.animator.change_pan((0, -50))

                elif pygame.KMOD_CTRL and event.key == pygame.K_z:
                    self.animator.undo()

            elif event.type == pygame.KEYUP:
                if self.animator.prev_mode is not None:
                    self.animator.change_mode(self.animator.prev_mode)
                    self.animator.prev_mode = None

    def drawloop(self):
        mouse_pos = pygame.mouse.get_pos()
        self.mscreen.fill((255, 255, 255))
        self.frame.set('Frame: {}'.format(str(self.animator.frame)))
        self.mode.set('Mode: {}'.format(str(self.animator.mode)))
        self.radius.set('Radius: {}'.format(str(self.animator.radius)))
        self.onions.set('Onions: {}'.format(str(self.animator.onions)))
        self.scale.set('Scale: {}'.format(str(self.animator.scale)))
        self.ruler_inc.set('Ruler Increment: {}'.format(str(self.animator.ruler_increment)))
        self.center.set('Center: {}'.format(str(self.animator.center)))
        self.mouse_pos.set('Mouse Pos: {}'.format(str(mouse_pos)))

        self.animator.draw_background()
        self.animator.draw_guidance_rulers()
        self.animator.draw_onions()
        self.animator.draw_nodes()
        pygame.draw.circle(self.animator.main_screen, (255, 0, 255),
                           self.animator.center, 10)
        pygame.draw.rect(self.animator.main_screen, (255, 128, 255), pygame.Rect(self.animator.center[0] - 10, self.animator.center[1] - 10, 20, 20))
        self.animator.draw_prev_frames()
        pygame.display.flip()

    def mainloop(self):
        while not self.done:
            try:
                self.root.update()
                if self.animatorplay:
                    self.eventloop()
                self.drawloop()
                clock.tick(60)
            except Exception as e:
                self.save()
                print(e)
                sys.exit()



# === DECLARATIONS ===
main_win = AnimatorWindow()

clock = pygame.time.Clock()

main_win.mainloop()

sys.exit()
