import pygame
from typing import *


class Character:
    """
    An abstract representation of a Slap City 2 character.
     === PUBLIC ATTRIBUTES ===
    center: A list of the character's x and y coordinates. This is used in reference to the characters hurtboxes/
    hitboxes.
    hurtboxes: A list of pygame rectangles of a character's hurtboxes.
    hitboxes: A list of pygame rectangles of a character's active hitboxes.
    action_state: A list with index 0 containing the action state a character is currently in, as well as what frame
    of that action state they're in. (Some action states may have no frames associated with it, such as walking, in
    which case it will be set to 0)

    === PRIVATE ATTRIBUTES ===
    _attributes: A tuple containing character attributes such as ground speed, air speed, etc.
    _direction: The direction a character is facing. Left will be False and right will be True.

    === REPRESENTATION INVARIANTS ===
    - hitboxes is never None
    - _attributes is never None
    - _direction is never None

    ATTRIBUTE INDEX MAPPING -Note: Will add more as we continue
    0: Max ground speed
    """
    center: List[int]
    hurtboxes: List[pygame.Rect]
    hitboxes: List[pygame.Rect]
    _attributes: Tuple[int]
    action_state: List
    _direction: bool

    def __init__(self, center: List[int], direction: bool, action_state: List) -> None:
        self.center = center
        self._direction = direction
        self.action_state =  action_state
        # self._attributes = []
        # self._direction = False
        # self.hitboxes = []
        # self.hurtboxes = []

    def update(self) -> None:
        raise NotImplementedError

    def ground_actionable(self) -> bool:
        raise NotImplementedError

    def walk(self, tilt) -> None:
        raise NotImplementedError

    def ftilt(self) -> None:
        raise NotImplementedError


class CharOne(Character):

    def __init__(self, center: List[int], direction: bool, action_state: List) -> None:
        super(CharOne, self).__init__(center, direction, action_state)
        width = 30
        self.hurtboxes = [pygame.Rect(self.center[0] - width / 2,
                                     self.center[1] - width, width, width),
                         pygame.Rect(self.center[0] - width / 2, self.center[1],
                                     width, 2 * width)]
        self.hitboxes = []
        self._attributes = [5]

    def update(self) -> None:
        # TODO: If a character is in an unactionable state, continue that unactionable state until actionable
        if self.action_state[0] != "grounded":  # This is going to have to change later too, to be generalized.
            getattr(self, self.action_state[0])() # This is calling the function "self.action_state[0]". For example,
            # if self.action_state is "ftilt", this will call on the function ftilt().

    def ground_actionable(self) -> bool:
        if self.action_state[0] == 'grounded':
            return True
        return False

    def walk(self, tilt) -> None:
        if self.ground_actionable():
            self.center[0] += tilt * self.attributes[0]
            if tilt > 0:
                self._direction = True
            else:
                self._direction = False

    def ftilt(self):
        if self.ground_actionable() or self.action_state[0] == 'ftilt':
            self.action_state[0] = 'ftilt'
            self.action_state[1] += 1
            if self.action_state[1] > 7:
                if self._direction:
                    self.hitboxes = [pygame.Rect(self.center[0] + 30 / 2, self.center[1], 50, 30)]
                    # I hard coded this in, but this is bound to change, along with the one below.
                else:
                    self.hitboxes = [pygame.Rect(self.center[0] - 30 / 2 - 50, self.center[1], 50, 30 -
                                                  int(self.action_state[1] * 3))]
                    # Again, this needs to change.
            if self.action_state[1] > 15:
                self.hitboxes = []
            if self.action_state[1] > 20:
                self.action_state[0] = 'grounded'
                self.action_state[1] = 0
