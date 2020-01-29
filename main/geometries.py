from __future__ import annotations
from typing import *
import math


class Vector:
    """
    This class simplifies some many operations and is specified for 2D vectors
    only.
    """

    def __init__(self, point: Tuple) -> None:
        """
        x and y attributes are valid to use since any vector operations returns
        a new vector, and thus values for a Vector object is never changed.
        """
        self.values = point
        self.x = point[0]
        self.y = point[1]

    def get_values(self) -> Tuple:
        return self.values

    def __add__(self, other: Vector) -> Vector:
        return Vector((self.values[0] + other.values[0],
                       self.values[1] + other.values[1]))

    def __mul__(self, other: Any) -> Union[Vector, float]:
        if isinstance(other, Vector):
            return self.values[0] * other.values[0] + \
                   self.values[1] * other.values[1]
        # For matrix multiplication with precondition that other is of length 4
        # with numerical entries.
        # Note that the vector is written before the matrix with this.
        elif isinstance(other, Tuple):
            row1 = Vector((other[0], other[1]))
            row2 = Vector((other[2], other[3]))
            return Vector((self * row1, self * row2))
        else:
            return Vector((self.values[0] * other, self.values[1] * other))

    def __sub__(self, other: Vector) -> Vector:
        return Vector((self.values[0] - other.values[0],
                       self.values[1] - other.values[1]))

    def __abs__(self) -> float:
        return math.sqrt(self.values[0] ** 2 + self.values[1] ** 2)

    def normalize(self) -> Vector:
        norm = abs(self)
        try:
            return Vector((self.x / norm, self.y / norm))
        except Exception as e:
            print(e)
            return Vector((1, 0))

    def orthogonal(self) -> Vector:
        return Vector((self.y, -self.x))


class Line:

    def __init__(self, points: Tuple) -> None:
        converted = []
        for p in points:
            if isinstance(p, tuple):
                converted.append(Vector(p))
            else:
                converted.append(p)
        self.points = tuple(converted)

    def get_standard(self) -> Dict:
        p1 = self.points[0].get_values()
        p2 = self.points[1].get_values()
        a = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = -1
        c = p1[1] - a * p1[0]
        return {'a': a, 'b': b, 'c': c}

    def vectorize(self) -> Vector:
        return self.points[1] - self.points[0]


class Shape:

    def __init__(self) -> None:
        pass

    def translate_to(self, increment: Vector) -> None:
        """
        Moves this Shape object by some amount.
        """
        raise NotImplementedError

    def translate(self, increment: Vector) -> Shape:
        """
        Returns a new Shape object corresponding to a new origin.
        """
        raise NotImplementedError

    def change_coords_to(self, origin: Vector) -> None:
        raise NotImplementedError

    def change_coords(self, origin: Vector) -> Shape:
        """
        This method changes the shape's position relative to a new origin.
        Ex: Circle is at (5, 5) currently. Setting the origin to (1, 1)
        makes the circle's position then (4, 4). This is really just a fancy
        translate() method.
        """
        return self.translate(origin * -1)

    def scale(self, factor: float, origin: Vector) -> Shape:
        """
        Returns a new Shape object scaled by a factor about an origin.
        """
        raise NotImplementedError

    def collide(self, shape: Shape) -> bool:
        """
        Checks for collision between another shape.
        """
        raise NotImplementedError

    def contain(self, point: Vector) -> bool:
        """
        Checks if a point is contained in this shape.
        """
        raise NotImplementedError


class Circle(Shape):
    """
    This will be used in the animator tool, replacing the Shapely polygons.
    """

    def __init__(self, vector: Vector, radius: float) -> None:
        super().__init__()
        if isinstance(vector, tuple):
            self.pos = Vector(vector)
        else:
            self.pos = vector
        self.radius = radius

    def get_pos(self) -> Tuple:
        return self.pos.get_values()

    def get_radius(self) -> float:
        return self.radius

    def modify_pos(self, **kwargs) -> None:
        if 'pos' in kwargs:
            self.pos = Vector(kwargs['pos'])
        elif 'vector' in kwargs:
            self.pos = kwargs['vector']

    def increment_pos(self, increment: Vector) -> None:
        self.pos = self.pos + increment

    def modify_radius(self, new_radius: float) -> None:
        self.radius = new_radius

    def increment_radius(self, increment: float) -> None:
        self.radius += increment

    def translate_to(self, increment: Vector) -> None:
        """
        Translates this Circle.
        """
        self.pos = self.pos + increment

    def translate(self, increment: Vector) -> Circle:
        """
        This method returns a transformed circle relative to a new origin.
        Ex. Circle is at (5, 5) currently. Essentially, you can imagine this
        method moving the entire coordinate system from (0, 0) to position,
        dragging the circle with it.
        """
        return Circle(self.pos + increment, self.radius)

    def change_coords(self, origin: Vector) -> Circle:
        """
        Same thing as the other function, but returns a new Circle.
        """
        return Circle(self.pos - origin, self.radius)

    def change_coords_to(self, origin: Vector):
        self.pos = self.pos - origin

    def scale(self, factor: float, origin: Vector) -> Circle:
        """
        This method is used to scale the circle by a factor about an origin.
        This is very useful in the animator tool.
        """
        translated = self.change_coords(origin)
        translated.modify_pos(vector=translated.pos * factor)
        translated.modify_radius(translated.radius * factor)

        translated.translate_to(origin)

        return translated

    def collide(self, shape: Shape) -> bool:
        """
        Checks for collision between circle or rectangle
        """
        if isinstance(shape, Circle):
            return (shape.get_pos()[0] - self.get_pos()[0]) ** 2 + \
                   (shape.get_pos()[1] - self.get_pos()[1]) ** 2 <= \
                   (shape.get_radius() + self.get_radius()) ** 2
        elif isinstance(shape, Rectangle):
            edges = shape.edges()
            for edge in edges:
                if self.line_intersect(edge):
                    return True
            return shape.contain(self.pos)

        # Safety measure
        return False

    def line_intersect(self, line: Line) -> bool:
        vector = self.pos
        standard = line.get_standard()
        a = standard['a']
        b = standard['b']
        c = standard['c']
        return abs(a * vector.x + b * vector.y + c) / \
               math.sqrt(a **2 + b ** 2) < self.radius

    def contain(self, point: Vector) -> bool:
        return abs(point - self.pos) <= self.radius

    def connect(self, circle: Circle) -> Shape:
        """
        If the circles are not on the same position, it will return a polygon
        connecting the two circles. Otherwise, it will return a circle with
        the lower radius.

        Eventually, I want to get this to check if circle_a is fully contained
        in circle_b, or vice versa, because for our purposes, we would never
        need to use this function in that case.
        """
        a_pos = self.pos
        b_pos = circle.pos
        a_rad = self.get_radius()
        b_rad = circle.get_radius()
        if a_pos.get_values() == b_pos.get_values():
            return Circle(self.pos, min(a_rad, b_rad))

        line_ab = a_pos - b_pos
        orthogonal = line_ab.orthogonal().normalize()
        vert_a1 = a_pos + (orthogonal * a_rad)
        vert_a2 = a_pos - (orthogonal * a_rad)
        vert_b1 = b_pos + (orthogonal * b_rad)
        vert_b2 = b_pos - (orthogonal * b_rad)
        return Polygon((vert_a1, vert_a2, vert_b2, vert_b1))


class Polygon(Shape):
    """
    This is ONLY meant for convex polygons.
    """

    def __init__(self, vertices: Tuple) -> None:
        super().__init__()
        converted = []
        for p in vertices:
            if isinstance(p, tuple):
                converted.append(Vector(p))
            else:
                converted.append(p)
        self.vertices = tuple(converted)

    def translate_to(self, increment: Vector) -> None:
        self.vertices = tuple(vert + increment for vert in self.vertices)

    def translate(self, increment: Vector) -> Shape:
        return Polygon(tuple(vert + increment for vert in self.vertices))

    def change_coords(self, origin: Vector) -> Polygon:
        new_vert = tuple((vert - origin for vert in self.vertices))
        return Polygon(new_vert)

    def change_coords_to(self, origin: Vector) -> None:
        self.vertices = tuple((vert - origin for vert in self.vertices))

    def scale(self, factor: float, origin: Vector) -> Shape:
        translated = self.change_coords_to(origin)
        scaled_vert = tuple([vert * factor for vert in translated.vertices])

        retr = Polygon(scaled_vert)
        retr.translate_to(origin)

        return retr

    def collide(self, polygon: Shape) -> bool:
        """
        Note this will only return True iff the polygon is CONTAINED within
        this polygon, not when only the edge is touching.
        """
        if isinstance(polygon, Polygon):
            return SAT.SAT(self, polygon)

    def get_MTV(self, polygon: Polygon) -> Vector:
        """
        Gets the minimum translation vector for this polygon to move out of the
        argument 'polygon.'
        Note that this should ONLY be called if collision is already detected,
        otherwise it may return rubbish.
        """
        return SAT.MTV(self, polygon)

    def contain(self, point: Vector) -> bool:
        """
        Might leave this unimplemented since we probably will never deal with
        any polygons other than a rectangle, so there's no need to generalize.
        """
        raise NotImplementedError

    def edges(self) -> Tuple(Line):
        """
        Connects each consecutive point into a line and returns them as in a
        tuple.
        """
        return tuple(Line((self.vertices[i],
                           self.vertices[(i + 1) % len(self.vertices)]))
                     for i in range(len(self.vertices)))


class Rectangle(Polygon):

    def __init__(self, vertices: Tuple):
        """
        Vertices must be defined in a way s.t. index 0 is perpendicular with
        index 1 and index 0 is perpendicular to index 3.
        """
        super().__init__(vertices)

    def collide(self, polygon: Shape) -> bool:
        """
        Checks for collision between circle or rectangle
        """
        if isinstance(polygon, Rectangle):
            return super().collide(polygon)

        elif isinstance(polygon, Circle):
            # Use the Circle collide.
            return polygon.collide(self)

        # Safety measure
        return False

    def contain(self, point: Vector) -> bool:
        """
        Check if a point is in the rectangle.
        """
        AM = point - self.vertices[0]
        AB = self.vertices[1] - self.vertices[0]
        AD = self.vertices[3] - self.vertices[1]
        return (0 <= AM * AB <= AB * AB) and (0 <= AM * AD <= AD * AD)


class SAT:
    """
    An implementation of the separating axis theorem in 2D. Just accept that it
    works.

    In the future, we may come back to optimize this:
    https://gamedevelopment.tutsplus.com/tutorials/collision-detection-using-the-separating-axis-theorem--gamedev-169

    For example, we may only need to check two axes since the other two are
    already parallel. Or there may be some shortcut to these computations.

    """

    @staticmethod
    def SAT(a: Polygon, b: Polygon) -> bool:
        """
        Returns True if there is intersection.
        """
        vert_a = a.vertices
        vert_b = b.vertices

        edges_a = SAT.edge_vectors(vert_a)
        edges_b = SAT.edge_vectors(vert_b)

        edges = edges_a + edges_b

        axes = SAT.orthonormal_axes(edges)

        for i in range(len(axes)):
            proj_a = SAT.projection_range(vert_a, axes[i])
            proj_b = SAT.projection_range(vert_b, axes[i])
            if not SAT.overlap(proj_a, proj_b):
                return False
        return True

    @staticmethod
    def MTV(a: Polygon, b: Polygon) -> Vector:
        """
        Gets the minimum translation vector for polygon b to move out of a.

        Currently, there is a bug where it will not process correctly if one
        polygon is wholly contained in the other. If we decide not to fix it,
        we can work around it by limiting speeds such that an object will never
        update into another.
        P2
        TODO: Bugfix
        """
        vert_a = a.vertices
        vert_b = b.vertices

        # Necessary to iterate over both shapes, then account for reversed order
        MTV_a = SAT.iterate_over(vert_a, vert_b)
        MTV_b = SAT.iterate_over(vert_b, vert_a) * -1

        if abs(MTV_a) < abs(MTV_b):
            return MTV_a
        return MTV_b

    @staticmethod
    def iterate_over(vert_a, vert_b) -> Vector:
        """
        Gets MTV for projections of b on a.
        """
        edges_a = SAT.edge_vectors(vert_a)
        edges_b = SAT.edge_vectors(vert_b)

        edges = edges_a + edges_b

        axes = SAT.orthonormal_axes(edges)

        # Not spaghetti if there's no sauce
        min_overlap = 5000
        final_axis = Vector((0, 0))

        for axis in axes:
            proj_a = SAT.projection_range(vert_a, axis)
            proj_b = SAT.projection_range(vert_b, axis)
            overlap = SAT.overlap_value(proj_a, proj_b)
            if 0 < abs(overlap) < abs(min_overlap):
                min_overlap = overlap
                final_axis = axis
        return final_axis * min_overlap

    @staticmethod
    def edge_vectors(vertices: Tuple) -> Tuple:
        return tuple((
            vertices[(i + 1) % len(vertices)] - vertices[i]
            for i in range(len(vertices))
        ))

    @staticmethod
    def orthonormal_axes(edges: Tuple) -> Tuple:
        axes = []
        for edge in edges:
            orthonormal = edge.orthogonal().normalize().get_values()
            if orthonormal not in axes:
                axes.append(orthonormal)
        return tuple((Vector(axis) for axis in axes))

    @staticmethod
    def projection_range(vectors: Tuple, axis: Vector) -> Tuple:
        """
        Returns the minimum and maximum projection of a tuple of vectors onto
        an axis.
        """
        dots = [vect * axis for vect in vectors]
        return tuple((min(dots), max(dots)))

    @staticmethod
    def in_range(n: float, range_: Tuple) -> bool:
        """
        Checks if n is inclusively in the range.
        """
        a = range_[0]
        b = range_[1]
        if b < a:
            a = range_[1]
            b = range_[0]
        return (n > a) and (n < b)

    @staticmethod
    def overlap(proj_a: Tuple, proj_b: Tuple) -> bool:
        """
        Returns False if none of the values in a are in range of b and none of
        the values of b are in range of a, otherwise returns True.
        """
        if SAT.in_range(proj_a[0], proj_b):
            return True
        if SAT.in_range(proj_a[1], proj_b):
            return True
        if SAT.in_range(proj_b[0], proj_a):
            return True
        if SAT.in_range(proj_b[1], proj_a):
            return True
        return False

    @staticmethod
    def overlap_value(proj_a: Tuple, proj_b: Tuple) -> float:
        if proj_a[0] < proj_b[0]:
            return -max(proj_a) + min(proj_b)
        elif proj_a[0] > proj_b[0]:
            return max(proj_a) - min(proj_b)
        else:
            return -max(proj_a) + min(proj_b)


class ECB:

    def __init__(self, point_dict: Dict[str, Vector]) -> None:
        """
        Make sure point_dict is entered...
        """
        self.point_dict = point_dict
        self.line_dict = self.convert_lines()
        self.polygon = Polygon(tuple(point_dict[i] for i in point_dict))

    def get_point(self, point: str) -> Vector:
        return self.point_dict[point]

    def convert_lines(self) -> Dict:
        return {'UL': Line((self.get_point('U'), self.get_point('L'))),
                'UR': Line((self.get_point('U'), self.get_point('R'))),
                'DL': Line((self.get_point('D'), self.get_point('L'))),
                'DR': Line((self.get_point('D'), self.get_point('R')))}

    def get_line(self, line: str) -> Tuple:
        return self.line_dict[line]

    def transform_to(self, origin: Vector) -> ECB:
        """
        This function returns a transformed ECB relative to a new origin.
        """
        new_point_dict = {}
        for points in self.point_dict:
            point = self.get_point(points)
            new_point_dict[points] = point + origin
        return ECB(new_point_dict)

    def get_MTV(self, environment: Polygon) -> Vector:
        """
        Returns MTV for the ECB to to move out of the environment.
        """
        return self.polygon.get_MTV(environment)


class CharHurtboxes:

    def __init__(self, hurtbox_list: List) -> None:
        self.hurtbox_list = hurtbox_list

    def collide(self, hitbox: Hitbox) -> bool:
        """
        Testing for collision between every hurtbox and a single Hitbox.
        """
        for hurtbox in self.hurtbox_list:
            if hurtbox.collide(hitbox.get_geom()):
                return True
        return False


class CharHitboxes:

    def __init__(self) -> None:
        self.reg_hitboxes = {}
        self.proj_hitboxes = {}
        self.grab_hitboxes = {}
        self.reg_valid = False
        self.grab_valid = False

    def collide_reg(self, hurtbox: CharHurtboxes) -> Union[Hitbox, None]:
        if not self.reg_valid:
            return None

        for ids in self.reg_hitboxes:
            if hurtbox.collide(self.reg_hitboxes[ids]):
                self.reg_valid = False
                return self.reg_hitboxes[ids]
        return None

    def collide_proj(self, hurtbox: CharHurtboxes) -> Union[Hitbox, None]:
        for ids in self.proj_hitboxes:
            if hurtbox.collide(self.proj_hitboxes[ids]):
                return self.proj_hitboxes[ids]
        return None

    def collide_grab(self, hurtbox: CharHurtboxes) -> Union[Hitbox, None]:
        if not self.grab_valid:
            return None

        for ids in self.proj_hitboxes:
            if hurtbox.collide(self.reg_hitboxes[ids]):
                self.grab_valid = False
                return self.grab_hitboxes[ids]
        return None


class Hurtbox:
    """
    Yes, there really isn't much need for this class, but it's to keep the
    animator tidy.
    """

    def __init__(self, geom: Shape) -> None:
        self.geom = geom

    def get_geom(self) -> Shape:
        return self.geom

    def collide(self, geom: Shape) -> bool:
        return geom.collide(self.geom)


class Hitbox:

    def __init__(self, geom: Shape, attack_data: Dict) -> None:
        self.geom = geom
        self.data = attack_data

    def get_geom(self) -> Shape:
        return self.geom

    def get_data(self) -> Dict:
        # Not sure if it needs .copy() for this, but leave it for now for safety
        return self.data.copy()


class GrabHitbox(Hitbox):

    def __init__(self, geom: Shape, attack_data: Dict) -> None:
        # Grab hitbox data will have an extra entry: "name." If name is "regular"
        # then it's the regular grab. Otherwise, the game will execute a special
        # type of grab upon hit.
        super().__init__(geom, attack_data)


class Projectile(Hitbox):

    def __init__(self, geom: Shape, attack_data: Dict) -> None:
        # Projectile hitbox data will have an extra entry: "name." This will
        # Denote what type of projectile it is and how the game should update it.
        super().__init__(geom, attack_data)


class Bullet(Projectile):

    def __init__(self, geom: Shape, attack_data: Dict) -> None:
        super().__init__(geom, attack_data)
