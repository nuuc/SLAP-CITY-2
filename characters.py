import pygame, numpy, math
from typing import *

JUMPSQUAT_FRAME = 3

class Character:
    """
    An abstract representation of a Slap City 2 character.
     === PUBLIC ATTRIBUTES ===
     action_state: A list containing a character's action state. The first index is its main action state (i.e.
    'airborne'), the second is the frame of its main state (currently this is only used for wavelanding, but it may
    be useful later), the third is its substate, and the fourth is the frame of its substate.
    attributes: A tuple containing character attributes such as ground speed, air speed, etc.
    air_speed: A list of a character's horizontal and vertical air velocity
    center: A list of a character's x and y coordinates. This is used in reference to the characters hurtboxes/
    hitboxes.
    direction: The direction a character is facing. Left will be False and right will be True.
    ground_speed: A character's ground speed
    ecb: A list of a character's edges for interacting with the stage. Its indexes are left, right, top and bottom.
    hurtboxes: A list of pygame rectangles of a character's hurtboxes.
    hitboxes: A list of pygame rectangles of a character's active hitboxes.
    invincible: A list with the first index being True if a character is invincible and the second index is how many
    frames of invincibility it has left.
    jumped: True if a character has jumped in the air, False if they haven't.

    ATTRIBUTE INDEX MAPPING
    'max_gr_speed: max ground speed
    'vair_acc': Vertical air acceleration
    'max_vair_speed': Max vertical air speed
    'hair_acc': Horizontal air acceleration
    'max_hair_speed': Max horizontal air speed
    'traction': A character's traction from wavelanding
    'width': A character's width
    'height': A character's height
    'fullhop_velocity': A character's initial fullhop velocity
    'shorthop_velocity': A character's initial shorthop velocity
    """
    action_state: List
    air_speed: List
    attributes: Dict
    center: List[float]
    direction: bool
    ecb: List
    ground_speed: float
    hitboxes: List[pygame.Rect]
    hurtboxes: List[pygame.Rect]
    invincible: List
    jumped: bool

    def __init__(self, center: List[int], direction: bool, action_state: List) -> None:
        self.action_state = action_state
        self.air_speed = [0, 0]
        self.attributes = {}
        self.center = center
        self.direction = direction
        self.ecb = []
        self.ground_speed = 0
        self.hitboxes = []
        self.hurtboxes = []
        self.invincible = [True, 60]
        self.jumped = False

    def get_attr(self) -> Dict:
        return {'action_state': self.action_state, 'air_speed': self.air_speed, 'attributes': self.attributes,
                'center': self.center, 'direction': self.direction, 'hitboxes': self.hitboxes,
                'hurtboxes': self.hurtboxes, 'jumped': self.jumped, 'ecb': self.ecb, 'invincible': self.invincible}

    def update(self) -> None:
        # TODO: Generalize update to handle all action states
        if self.invincible[0]:
            self.invincible[1] -= 1
            if self.invincible[1] == 0:
                self.invincible = [False, 0]
        if self.action_state[0] == 'grounded':
            self.update_air_speed(0, 0)
            self.jumped = False
            if self.action_state[2] == 'grounded':
                self.update_center(self.center[0] + self.ground_speed, self.center[1])
            elif self.action_state[2] == 'fullhop_jumpsquat':
                self.fullhop()
            elif self.action_state[2] == 'shorthop_jumpsquat':
                self.shorthop()
            elif self.action_state[2] != 'grounded':
                getattr(self, self.action_state[2])()

        elif self.action_state[0] == 'waveland':
            self.action_state[1] += 1
            if abs(self.ground_speed) <= 1:
                self.ground_speed = 0
            else:
                new_speed = self.ground_speed * math.sqrt((self.attributes['max_waveland_duration']
                                                           - self.action_state[1]) * self.attributes['friction'])
                self.ground_speed = new_speed
            self.update_center(self.center[0] + self.ground_speed, self.center[1])
            if self.action_state[2] == 'fullhop_jumpsquat':
                self.fullhop()
            elif self.action_state[2] == 'shorthop_jumpsquat':
                self.shorthop()
            elif self.action_state[2] != 'grounded':
                getattr(self, self.action_state[2])()
            if self.action_state[1] > self.attributes['max_waveland_duration']:
                self.action_state[0] = 'grounded'
                self.action_state[1] = 0

        elif self.action_state[0] == 'airborne':
            self.update_air_speed(self.air_speed[0], self.air_speed[1] - self.attributes['vair_acc'])
            self.update_center(self.center[0] + self.air_speed[0], self.center[1] - self.air_speed[1])
            self.ground_speed = 0
            if not self.action_state[2] == 'airborne' and not self.action_state[2] == 'freefall':
                getattr(self, self.action_state[2])()

        elif self.action_state[0] == 'airdodge':
            self.update_center(self.center[0] + self.air_speed[0], self.center[1] - self.air_speed[1])
            self.airdodge(self.action_state[3])

    def update_center(self, x: int, y: int) -> None:
        raise NotImplementedError

    def update_air_speed(self, x: float, y: float) -> None:
        self.air_speed = [x, y]
        if self.air_speed[0] > self.attributes['max_hair_speed']:
            self.air_speed[0] = self.attributes['max_hair_speed'] * numpy.sign(x)
        if self.air_speed[1] < -self.attributes['max_vair_speed']:
            self.air_speed[1] = -self.attributes['max_vair_speed']

    def ground_actionable(self) -> bool:
        if self.action_state[2] == 'grounded':
            return True
        return False

    def air_actionable(self) -> bool:
        if self.action_state[2] == 'airborne':
            return True
        return False

    def move(self, tilt) -> None:
        if self.ground_actionable() and self.action_state[0] != 'waveland':
            self.ground_speed = self.attributes['max_gr_speed'] * tilt
            if tilt > 0:
                self.direction = True
            elif tilt < 0:
                self.direction = False
        elif self.action_state[0] == 'waveland' and self.action_state[1] > 9 and tilt != 0:
            self.action_state = ['grounded', 0, 'grounded', 0]
            self.ground_speed = self.attributes['max_gr_speed'] * tilt
            if tilt > 0:
                self.direction = True
            elif tilt < 0:
                self.direction = False
        elif self.action_state[0] == 'airborne':
            set_spd = tilt * self.attributes['max_hair_speed']
            if self.air_speed[0] != set_spd:
                if self.air_speed[0] < set_spd:
                    self.update_air_speed(self.air_speed[0] + self.attributes['hair_acc'], self.air_speed[1])
                    if self.air_speed[0] > set_spd:
                        self.update_air_speed(set_spd, self.air_speed[1])
                else:
                    self.update_air_speed(self.air_speed[0] - self.attributes['hair_acc'], self.air_speed[1])
                    if self.air_speed[0] < set_spd:
                        self.update_air_speed(set_spd, self.air_speed[1])

    def fullhop(self) -> None:
        if not self.jumped and self.action_state[0] == 'airborne':
            self.jumped = True
            self.update_air_speed(self.air_speed[0], self.attributes['fullhop_velocity'])
        if self.ground_actionable() or self.action_state[2] == 'fullhop_jumpsquat':
            self.action_state[2] = 'fullhop_jumpsquat'
            self.action_state[3] += 1
            if self.action_state[3] > JUMPSQUAT_FRAME:
                self.action_state = ['airborne', 0, 'airborne', 0]
                self.update_air_speed(self.ground_speed, self.attributes['fullhop_velocity'])

    def shorthop(self) -> None:
        if self.ground_actionable() or self.action_state[2] == 'shorthop_jumpsquat':
            self.action_state[2] = 'shorthop_jumpsquat'
            self.action_state[3] += 1
            if self.action_state[3] > JUMPSQUAT_FRAME:
                self.action_state = ['airborne', 0, 'airborne', 0]
                self.update_air_speed(self.ground_speed * 1, self.attributes['shorthop_velocity'])

    def airdodge(self, angle: List) -> None:
        if self.air_actionable() or self.action_state[0] == 'airdodge':
            self.action_state[0] = 'airdodge'
            self.action_state[1] += 1
            self.action_state[2] = 'airdodge'
            self.action_state[3] = angle
            if self.action_state[1] == 3:
                self.invincible = [True, 29]
            if self.action_state[1] < 42:
                multiplier = 900 / (self.action_state[1] + 7) ** 2
                self.air_speed = [angle[0] * multiplier, angle[1] * multiplier]
            if self.action_state[1] > 42:
                self.action_state = ['airborne', 0, 'freefall', 0]

    def auto_wavedash(self, angle: List) -> None:
        if self.action_state[2] == 'fullhop_jumpsquat' or self.action_state[2] == 'shorthop_jumpsquat':
            self.action_state[2] = 'auto_wavedash'
            self.action_state[3] += 1
            if self.action_state[3] > JUMPSQUAT_FRAME:
                self.action_state = ['airborne', 0, 'airborne', 0]
                self.airdodge(angle)

    def ftilt(self) -> None:
        raise NotImplementedError

    def fair(self) -> None:
        raise NotImplementedError

    def bair(self) -> None:
        raise NotImplementedError

    def upair(self) -> None:
        raise NotImplementedError

    def dair(self) -> None:
        raise NotImplementedError



class CharOne(Character):

    def __init__(self, center: List[int], direction: bool, action_state: List) -> None:
        super(CharOne, self).__init__(center, direction, action_state)
        width = 30
        self.hurtboxes = [pygame.Rect(self.center[0] - width / 2,
                                     self.center[1] - width, width, width * 3)]
        self.hitboxes = []
        self.attributes = {'max_gr_speed': 10, 'vair_acc': 2, 'max_vair_speed': 10, 'hair_acc': 2, 'max_hair_speed':
                            10, 'width': width, 'height': width * 2, 'fullhop_velocity': 25, 'shorthop_velocity': 20,
                           'airdodge_conversion': 2, 'friction': 0.025, 'max_waveland_duration': 30}
        self.ground_speed = 0
        self.air_speed = [0, 0]
        self.jumped = False
        self.ecb = [self.center[0] - width / 2, self.center[0] + width / 2,
                    self.center[1] - width, self.center[1] + width * 3]

    def update_center(self, x: float, y: float) -> None:
        self.center[0] = x
        self.center[1] = y
        width = 30
        self.ecb = [self.center[0] - width / 2, self.center[0] + width / 2,
                    self.center[1] - width, self.center[1] + width * 2]
        if self.direction:
            self.hurtboxes = [pygame.Rect(self.center[0] - width / 2,
                                          self.center[1] - width, width, width * 3),
                              pygame.Rect(self.center[0],
                                          self.center[1] + 20, width, 15)]
        else:
            self.hurtboxes = [pygame.Rect(self.center[0] - width / 2,
                                          self.center[1] - width, width, width * 3),
                              pygame.Rect(self.center[0],
                                          self.center[1] + 20, -width, 15)]

    def ftilt(self) -> None:
        if self.ground_actionable() or self.action_state[2] == 'ftilt':
            self.action_state[2] = 'ftilt'
            self.action_state[3] += 1
            if self.action_state[3] > 7:
                if self.direction:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
                else:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
            if self.action_state[3] > 15:
                self.hitboxes = []
            if self.action_state[3] > 20:
                self.action_state[2] = 'grounded'
                self.action_state[3] = 0
        # if self.ground_actionable():
        #     self.action_state[0] = 'ftilt'
        #     self.action_state[1] = 1
        # elif self.action_state[0] == 'ftilt'
        #     self.action_state[1] += 1
        #     if self.action_state[1] > 7:
        #         if self.direction:
        #             # UPDATE HITBOXES
        #         else:
        #             # UPDATE HITBOXES
        #     if self.action_state[1] > 15:
        #         self.hitboxes = []
        #     if self.action_state[1] > 20:
        #         self.action_state[0] = 'grounded'
        #         self.action_state[1] = 0
        # This is an alternate version of the code earlier, where the action state is set only at the startup, not
        # every frame. Currently, there should be no difference, except a tiny bit in runtime, but it may be useful
        # to use this later to account for something.

    def fair(self) -> None:
        if self.air_actionable() or self.action_state[2] == 'fair':
            self.action_state[2] = 'fair'
            self.action_state[3] += 1
            if self.action_state[3] > 8:
                if self.direction:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
                else:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
            if self.action_state[3] > 16:
                self.hitboxes = []
            if self.action_state[3] > 20:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def bair(self) -> None:
        if self.air_actionable() or self.action_state[2] == 'bair':
            self.action_state[2] = 'bair'
            self.action_state[3] += 1
            if self.action_state[3] > 8:
                if self.direction:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
                else:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
            if self.action_state[3] > 16:
                self.hitboxes = []
            if self.action_state[3] > 20:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def upair(self) -> None:
        if self.air_actionable() or self.action_state[2] == 'upair':
            self.action_state[2] = 'upair'
            self.action_state[3] += 1
            if self.action_state[3] > 8:
                if self.direction:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
                else:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
            if self.action_state[3] > 16:
                self.hitboxes = []
            if self.action_state[3] > 20:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def dair(self) -> None:
        if self.air_actionable() or self.action_state[2] == 'upair':
            self.action_state[2] = 'upair'
            self.action_state[3] += 1
            if self.action_state[3] > 8:
                if self.direction:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
                else:
                    self.hitboxes = [pygame.Rect(self.center[0], self.center[1], 10, 10)]
            if self.action_state[3] > 16:
                self.hitboxes = []
            if self.action_state[3] > 20:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0


