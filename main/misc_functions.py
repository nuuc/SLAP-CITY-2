from typing import *
import math


def sign(value: float) -> int:
    """
    Gets the sign of a value.
    """
    if value > 0:
        return 1
    elif value < 0:
        return -1
    elif value == 0:
        return 0


def cross_inc(value: float, increment: float, cross: float = 0) \
        -> float:
    """
    This static function does the following:
    Increments value if value is higher than cross. If value is then lower
    than cross, it will return cross, otherwise it will return value.
    Decrements value if value is lower than cross. If value is then higher
    than cross, it will return cross, otherwise it will return value.

    In practise, what this is used for is when you want to increment
    directionally. For example, if you want to lower speed, it's trivial
    when the speed is positive. However, when it is negative, this function
    comes in handy, since you can set a negative increment, and this
    function will handle both when speed is negative or when it is positive.

    Additionally, since most of the time, when you increment directionally,
    you don't want to increment PAST a certain "cross," this function
    handles that.

    Example:
        cross_inc(10, -5, 0)
        >>> 5
        cross_inc(-10, -5, 0)
        >>> -5
        cross_inc(-3, -5, 0)
        >>> 0

        These are strange examples, but it shows how a special way this
        method can be used.
        cross_inc(3, -5, 6)
        >>> 6
        cross_inc(-3, -5, -6)
        >>> -6
        cross_inc(3, 5, 6)
        >>> -2
    """
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


def angle(pos: Tuple) -> float:
    """
    Returns the angle between pos and the x-axis.
    """
    return math.atan2(pos[1], pos[0])


def reflect_angle(angle_: float, axis: str) -> float:
    """
    Reflects the angle about an axis.

    As an aside, there are really interesting symmetries about these
    transformations that I discovered while finding the optimal way to compute
    this.
    """
    deg_angle = math.degrees(angle_)

    if axis == 'y':
        if 0 <= deg_angle <= 180:
            return math.radians(-deg_angle % 180)
        else:
            return math.radians(180 + (-deg_angle % 360))

    if axis == 'x':
        if 0 <= deg_angle <= 180:
            return math.radians(-deg_angle % 360)
        else:
            return math.radians(-deg_angle % 180)


def std_angle(angle_: float) -> float:
    """
    angle_ is in radians.
    """
    return math.radians(math.degrees(angle_) % 360)


def delta_angle(angle_a: float, angle_b: float) -> float:
    """
    Gets the difference between two angles. Input is in radians, output is in
    radians.
    """
    return math.radians(min(std_angle(angle_a - angle_b),
                            std_angle(angle_b - angle_a)))

