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
        self.floor = [[400, 600, 375], [550, 700, 300], [800, 1000, 350], [300, 900, 500]]
        self.walls = [[500, 700, 300], [500, 700, 900], [100, 500, 400]]
        self.ceiling = [[(300, 700), (900, 700)]]
