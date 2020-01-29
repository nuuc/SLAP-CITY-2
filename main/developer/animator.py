from __future__ import annotations
from typing import *
from geometries import *
from math import *
import pygame
import copy

DEFAULT_ATKDATA = {'damage': 0,
                   'angle': 0,
                   'KBG': 0,
                   'BKB': 0,
                   'shield_damage': 0}
SCREEN_SIZE = (1600, 900)
HURTBOX_CLR = (0, 0, 0)
HITBOX_CLR = (255, 0, 0)


class Node:

    def __init__(self, circle: Circle, name: str = None, parent: Node = None) \
            -> None:
        self.parent = parent
        self.children = []
        self.circle = circle
        self.name = name

    def connect(self, node: Node) -> Shape:
        return self.circle.connect(node.circle)

    def add_node(self, node: Node) -> None:
        self.children.append(node)
        node.parent = self

    def delete(self) -> None:
        if self.parent is not None:
            self.parent.children.remove(self)
        del self

    def rotate(self, angle: float, node: Node) -> None:
        """
        Rotates this node as well the children nodes around a node.
        """
        origin = node.circle.pos
        # Transform the circle s.t. the node is at the origin.
        self.circle.change_coords_to(origin)
        # Transform the circle by the CCW rotation matrix.
        self.circle.pos = self.circle.pos * (cos(angle), -sin(angle),
                                             sin(angle), cos(angle))
        # Transform the circle back to the base origin.
        self.circle.translate_to(origin)
        # Recursively repeat for all children.
        for child in self.children:
            child.rotate(angle, node)

    def translate(self, translation: Vector) -> None:
        """
        This can only be called on the root Node! Moves this tree of nodes by
        a translation vector.
        """
        self.circle.translate_to(translation)
        for child in self.children:
            child.translate_to(translation)

    def search_for(self, pos: Vector) -> Union[Node, None]:
        """
        Recursively search for the node within the children of this node and
        return it if possible.
        """
        if self.circle.contain(pos):
            return self
        for child in self.children:
            ret = child.search_for(pos)
            if ret is not None:
                return ret
        return None

    def create_hbox(self, type_: str, **kwargs) -> Union[Hitbox, Hurtbox]:
        if type_ == 'hurtbox':
            return Hurtbox(self.circle)
        elif type_ == 'hitbox':
            attack_data = kwargs['attack_data']
            # Unfinished
            return Hitbox(self.circle, attack_data)


class NodeFrame:

    selNode: Node
    map: Dict[Node, List[Union[Hurtbox, Hitbox]]]

    def __init__(self) -> None:
        self.selNode = None

        self.HurtboxNode = None
        self.HitboxNodes = []

        self.Hurtboxes = []
        self.Hitboxes = []

        self.AffineTransform = {'matrix': (1, 0,
                                           0, 1),
                                'translation': Vector((0, 0))}

        self.CharPos = Vector((0, 0))

        self.map = {}

    def untransform_point(self, point: Vector) -> Vector:
        """
        Takes a displayed point and transforms it back to the hidden coordinate
        system.
        """
        aff_inv = self.get_affine_inv()
        return (point + aff_inv['translation']) * aff_inv['matrix']

    def add_node(self, pos: Vector, radius: float, type_: str) -> None:
        """
        Takes in a DISPLAYED position. Radius is an absolute value.
        """
        untrans = self.untransform_point(pos)
        node = Node(Circle(untrans, radius))

        if self.selNode is not None:
            self.selNode.add_node(node)

        node_map = []
        if type_ == 'hurtbox':
            if self.selNode is not None:
                connect = Hurtbox(node.connect(self.selNode))
                node_map.append(connect)
                self.Hurtboxes.append(connect)
            if self.HurtboxNode is None:
                self.HurtboxNode = node
            hurtbox = node.create_hbox('hurtbox')
            node_map.append(hurtbox)
            self.Hurtboxes.append(hurtbox)
        elif type_ == 'hitbox':
            if self.selNode is not None:
                connect = Hitbox(node.connect(self.selNode),
                                 attack_data=DEFAULT_ATKDATA)
                node_map.append(connect)
                self.Hurtboxes.append(connect)

            self.HitboxNodes.append(node)

            hitbox = node.create_hbox('hitbox', attack_data=DEFAULT_ATKDATA)
            node_map.append(hitbox)
            self.Hitboxes.append(hitbox)

        self.selNode = node
        self.map[node] = node_map

    def search_node(self, pos: Vector, type_: str = None) -> Union[Node, None]:
        """
        Searches from the root node of the hurtbox node and each hitbox node.
        """
        untrans = self.untransform_point(pos)
        hurtbox_search = self.HurtboxNode.search_for(untrans)
        hitbox_search = None
        for node in self.HitboxNodes:
            hitbox_search = node.search_for(untrans)
            if hitbox_search is not None:
                break
        if type_ == 'hitbox':
            return hitbox_search
        elif type_ == 'hurtbox':
            return hurtbox_search

        if hurtbox_search is not None:
            return hurtbox_search
        return hitbox_search

    def select_node_pos(self, pos: Vector, type_: str = None) -> bool:
        node = self.search_node(pos, type_)
        if node is not None:
            self.selNode = node
            return True
        return False

    def select_node(self, node: Node):
        self.selNode = node

    def zoom(self, scale: float) -> None:
        curr_scale = self.AffineTransform['matrix']
        self.AffineTransform['matrix'] = \
            tuple((entry * scale for entry in curr_scale))

    def set_zoom(self, scale: float) -> None:
        matrix = self.AffineTransform['matrix']
        normalized = (Vector((matrix[0], matrix[2])).normalize(),
                      Vector((matrix[1], matrix[3])).normalize())
        norm_matrix = (normalized[0].x, normalized[1].x,
                       normalized[0].y, normalized[1].y)
        self.AffineTransform['matrix'] = tuple(
            (scale * entry for entry in norm_matrix)
        )

    def pan(self, pan: Vector) -> None:
        """
        The pan argument is how much the actual display is supposed to move.
        Precondition that the matrix is invertible (which it always should be)
        """
        aff_inv = self.get_affine_inv()
        accounted_pan = pan * aff_inv['matrix']
        self.AffineTransform['translation'] += accounted_pan

    def set_pan(self, pan: Vector) -> None:
        self.AffineTransform['translation'] = pan

    def set_matrix(self, matrix: Tuple) -> None:
        self.AffineTransform['matrix'] = matrix

    def get_affine_inv(self) -> Dict:
        """
        Gets the inverse affine transformation. Inverse is used when a point on
        the displayed screen is meant to be transformed to the hidden coordinate
        system in FrameData.
        """
        matrix = self.AffineTransform['matrix']
        det = self.det()
        inv_matrix = (matrix[3] / det, -matrix[1] / det,
                      -matrix[2] / det, matrix[0] / det)

        inv_trans = self.AffineTransform['translation'] * -1
        return {'matrix': inv_matrix, 'translation': inv_trans}

    def det(self) -> float:
        matrix = self.AffineTransform['matrix']
        return matrix[0] * matrix[3] - matrix[1] * matrix[2]

    def set_pos(self, pos: Vector):
        self.CharPos = pos

    def move_node(self, node: Node, pos: Vector) -> None:
        untrans = self.untransform_point(pos)
        mapped_hbox = self.map.get(node, None)
        distance = untrans - node.circle.pos
        if mapped_hbox is not None:
            node.circle.translate_to(distance)
            for hbox in mapped_hbox:
                hbox.get_geom().translate_to(distance)
        # For debugging purposes.
        else:
            print('Mapped hit/hurtbox not found.')

    def transform_geom(self, geom: Shape) -> Shape:
        """
        Returns the transformed geometry according to the affine transformation.
        """
        affine = self.AffineTransform
        if isinstance(geom, Circle):
            # Determinant scales a square by det after a transformation, so it
            # scales a line by sqrt(det) after transformation.
            transformed = Circle(geom.pos * affine['matrix'],
                                 geom.get_radius() * math.sqrt(abs(self.det())))
            translated = transformed.translate(affine['translation'])
            return translated
        elif isinstance(geom, Polygon):
            transformed_vert = tuple((vert * affine['matrix']
                                      for vert in geom.vertices))
            transformed = Polygon(transformed_vert)
            translated = transformed.translate(affine['translation'])
            return translated

    @staticmethod
    def draw_geom(screen: pygame.Surface, geom: Shape, color: Tuple) \
            -> None:
        if isinstance(geom, Circle):
            radius = round(geom.get_radius())
            rounded_pos = tuple((round(value) for value in geom.get_pos()))
            pygame.draw.circle(screen, color,
                               rounded_pos,
                               radius)
        elif isinstance(geom, Polygon):
            vertices = tuple((vert.get_values()
                              for vert in geom.vertices))
            pygame.draw.polygon(screen, color, vertices)

    def draw(self, screen: pygame.Surface, **kwargs) -> None:
        """
        Draws onto the screen. Takes in keyworded arguments that can have any
        value, but for convention, will be set to true. For example:
        draw(screen, hitbox=True)
        draw(screen, all=True)
        """
        screen.fill((255, 255, 255))

        if 'hurtbox' in kwargs:
            for hurtbox in self.Hurtboxes:
                geom = self.transform_geom(hurtbox.get_geom())
                self.draw_geom(screen, geom, HURTBOX_CLR)
        if 'hitbox' in kwargs:
            for hitbox in self.Hitboxes:
                geom = self.transform_geom(hitbox.get_geom())
                self.draw_geom(screen, geom, HITBOX_CLR)
        if 'all' in kwargs:
            for hurtbox in self.Hurtboxes:
                geom = self.transform_geom(hurtbox.get_geom())
                self.draw_geom(screen, geom, HURTBOX_CLR)
            for hitbox in self.Hitboxes:
                geom = self.transform_geom(hitbox.get_geom())
                self.draw_geom(screen, geom, HITBOX_CLR)

        # TODO: Fix messiness
        # Draw the selected node.
        selNode_h = self.map.get(self.selNode, [])
        for hbox in selNode_h:
            geom = self.transform_geom(hbox.get_geom())
            if isinstance(geom, Circle):
                self.draw_geom(screen, geom, (0, 128, 255))
        pygame.display.flip()

    def convert(self) -> Dict:
        pass


class FrameData:

    def __init__(self) -> None:
        self.frame_data = []

    def add_frame(self, frame: NodeFrame) -> None:
        self.frame_data.append(frame)

    def insert_frame(self, frame_num: int, frame: NodeFrame) -> None:
        try:
            self.frame_data.insert(frame_num, frame)
        except Exception as e:
            print(f'Error: {e}')

    def delete_frame(self, frame_num: int) -> None:
        try:
            del self.frame_data[frame_num]
        except Exception as e:
            print(f'Error: {e}')

    def curr_frame_index(self, frame: NodeFrame) -> int:
        if frame in self.frame_data:
            return self.frame_data.index(frame)
        length = len(self.frame_data)
        return length + 1

    def select_frame(self, index: int) -> NodeFrame:
        try:
            return self.frame_data[index]
        except Exception as e:
            print(f'Error: {e}')

    def convert_shapes(self, output: str) -> None:
        pass


class Animator:

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.FrameData = FrameData()
        self.onFrame = NodeFrame()
        self.tool = 'create hurtbox'
        self.settings = {'radius': 10,
                         'onions': 0,
                         'ruler': False,
                         'ruler increment': 50}
        self.background = None

    @staticmethod
    def transform_point(point: Vector, affine: Dict) -> Vector:
        """
        Takes a point from the hidden coordinate system and transforms it
        to the displayed coordinate system.
        """
        matrix = affine['matrix']
        translation = affine['translation']

        point = point * matrix
        point = point + translation

        return point

    def add_frame(self) -> None:
        self.FrameData.add_frame(self.onFrame)
        new_frame = copy.deepcopy(self.onFrame)
        self.onFrame = new_frame

    def insert_frame(self) -> None:
        """
        Should be right, but this method is flagged for debugging.
        """
        index = self.FrameData.curr_frame_index(self.onFrame)
        self.FrameData.insert_frame(index, self.onFrame)

    def select_frame(self, index: int) -> None:
        if index <= len(self.FrameData.frame_data):
            self.onFrame = self.FrameData.select_frame(index)
        else:
            new_frame = copy.deepcopy(self.FrameData.frame_data[-1])
            self.onFrame = new_frame

    def get_frame_num(self) -> int:
        return self.FrameData.curr_frame_index(self.onFrame)

    def add_node(self, pos: Tuple, type_: str = 'hurtbox'):
        """
        NodeFrame accounts for transformation from displayed to hidden.
        """
        self.onFrame.add_node(Vector(pos), self.settings['radius'], type_)

    def delete_node(self) -> None:
        parent = self.onFrame.selNode.parent
        self.onFrame.selNode.delete()
        self.onFrame.select_node(parent)

    def select_node(self, pos: Tuple) -> None:
        self.onFrame.select_node_pos(Vector(pos))

    def zoom(self, initial_pos: Tuple) -> None:
        """
        When this is called, the user clicks down and the initial_pos is entered
        as a Vector. Then, when they move their mouse out of the dead zone, the
        matrix will start getting scaled according to the projection on the axis
        corresponding to where they left the dead zone.

        May end up removing this for a simpler zoom function.
        Super buggy atm, don't use it.
        """
        initial_pos = Vector(initial_pos)
        release = False
        dead_zone = Circle(initial_pos, 30)
        cross = False
        axis = Vector((1, 0))
        scale = 1

        while not release:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    release = True
                elif initial_pos and event.type == pygame.MOUSEMOTION:
                    pos = Vector(pygame.mouse.get_pos())
                    if not cross and not dead_zone.contain(pos):
                        cross = True
                        axis = pos - initial_pos
                    else:
                        transformed = pos - initial_pos
                        scale = (transformed * axis) / abs(axis)

            # Will change this
            self.onFrame.set_zoom(scale)
            self.draw_nodes()

    def pan(self, initial_pos: Tuple) -> None:
        """
        Similar to zoom.
        """
        initial_pos = Vector(initial_pos)
        release = False
        last_pos = initial_pos
        while not release:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    release = True
                elif event.type == pygame.MOUSEMOTION:
                    pos = Vector(pygame.mouse.get_pos())
                    pan = pos - last_pos
                    last_pos = pos
                    self.onFrame.pan(pan)
            self.draw_nodes()

    def set_background(self, file: str) -> None:
        self.background = pygame.image.load(file)

    def draw_background(self) -> None:
        affine = self.onFrame.AffineTransform
        det = self.onFrame.det()
        size = self.background.get_size()
        scaled = tuple((abs(det) * dim for dim in size))
        bg = pygame.transform.scale(self.background.copy(), scaled)

        self.screen.blit(bg, dest=(affine['translation'].get_values()))

    def draw_nodes(self) -> None:
        self.onFrame.draw(self.screen, all=True)

    def run(self) -> None:
        """
        Debug mode right now. Just testing things out.
        """
        while True:
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.add_node(mouse_pos, 'hurtbox')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.onFrame.zoom(2)
                    elif event.key == pygame.K_w:
                        self.onFrame.zoom(1/2)
                    elif event.key == pygame.K_s:
                        self.pan(mouse_pos)
                    elif event.key == pygame.K_e:
                        self.select_node(mouse_pos)
                    elif event.key == pygame.K_a:
                        self.onFrame.pan(Vector((-30, 0)))
                    elif event.key == pygame.K_d:
                        self.onFrame.pan(Vector((30, 0)))
            self.draw_nodes()


clock = pygame.time.Clock()
display = pygame.display.set_mode(SCREEN_SIZE)
anim = Animator(display)
anim.run()
