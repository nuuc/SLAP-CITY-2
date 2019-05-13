from typing import *


class Stage:
    """

    """
    floor: List
    walls: List
    ceiling: List
    platform: List

    def __init__(self) -> None:
        raise NotImplementedError


class FD(Stage):

    def __init__(self) -> None:
        super(Stage, self).__init__()
        self.floor = [[(300, 500), (900, 500)]]
        self.walls = [[(300, 500), (300, 700)], [(900, 500), (900, 700)]]
        self.ceiling = [[(300, 700), (900, 700)]]
