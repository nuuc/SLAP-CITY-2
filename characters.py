import pygame, numpy, math
from typing import *
from shapely.geometry import *
from misc_functions import *
from shapely import affinity

JUMPSQUAT_FRAME = 4
WAVELAND_ACTIONABLE = 10


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
    damage: How much damage a character has taken. Higher percentage means higher knockback.
    direction: The direction a character is facing. Left will be False and right will be True.
    ground_speed: A character's ground speed
    ecb: A list of a character's edges for interacting with the stage. Its indexes are left, right, top and bottom.
    hurtboxes: A list of pygame rectangles of a character's hurtboxes.
    hitboxes: A list with the first index being a list of a character's active hitboxes and the second index being
    a dictionary of each hitbox data: 'damage', 'direction', 'KBG', 'BKB'
    invincible: A list with the first index being True if a character is invincible and the second index is how many
    frames of invincibility it has left.
    jumped: True if a character has jumped in the air, False if they haven't.
    misc_data: Miscellaneous data that is used for entering hitlag, airdodging, etc.

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
    'airdodge_conversion': How much a character's horizontal air speed is converted into ground speed
    'max_waveland_duration': How long a character can be in the waveland state

    HITBOX DATA INDEX MAPPING
    'damage': The amount of damage a hitbox deals to a character
    'direction:" An angle between -180 and 180 that determines the direction an attack will send
    'KBG': Short for knockback growth, which determines how well knockback scales off of damage
    'BKB': Short for base knockback, which determines how much knockback an attack will always do.
    """
    action_state: List
    air_speed: List
    attributes: Dict
    center: List[float]
    damage: int
    direction: bool
    ecb: List[Tuple]
    ground_speed: float
    hitboxes: Dict
    hurtboxes: List[Polygon]
    invincible: bool
    jumped: bool
    misc_data: Dict

    def __init__(self, center: List[int], direction: bool, action_state: List) -> None:
        self.action_state = action_state
        self.air_speed = [0, 0]
        self.attributes = {}
        self.center = center
        self.damage = 0
        self.direction = direction
        self.ecb = []
        self.ground_speed = 0
        self.hitboxes = {'regular': [[], [], False], 'projectile': []}
        self.hurtboxes = []
        self.invincible = False
        self.jumped = False
        self.misc_data = {'shield_health': 86, 'invincibility': 60}

    def return_attr(self, attribute: str) -> Any:
        return getattr(self, attribute)

    def update(self) -> None:
        """
        Update the character based on their action state.
        """
        # TODO: Generalize update to handle all action states

        if self.misc_data['invincibility'] > 0:
            self.misc_data['invincibility'] -= 1
            if self.misc_data['invincibility'] == 0:
                self.invincible = False
            else:
                self.invincible = True

        for projectile in self.hitboxes['projectile']:
            if projectile[2]:
                projectile[0] = affinity.translate(projectile[0], 20)
            else:
                projectile[0] = affinity.translate(projectile[0], -20)
            if projectile[0].bounds[2] >= 1280 or projectile[0].bounds[0] <= 0:
                self.hitboxes['projectile'].remove(projectile)

        if self.action_state[0] != 'shielded':
            if self.misc_data['shield_health'] < 86:
                self.misc_data['shield_health'] += 0.1
            elif self.misc_data['shield_health'] > 86:
                self.misc_data['shield_health'] = 86

        if self.action_state[0] == 'grounded' or self.action_state[0] == 'waveland':
            self.update_air_speed(0, 0)
            self.jumped = False
            if self.action_state[0] == 'waveland':
                self.action_state[1] += 1
                if not self.ground_speed == 0:
                    if self.ground_speed > self.attributes['high_traction_speed']:
                        new_speed = self.ground_speed - self.attributes['traction'] * numpy.sign(self.ground_speed) * 2
                    else:
                        new_speed = self.ground_speed - self.attributes['traction'] * numpy.sign(self.ground_speed)
                    if not numpy.sign(new_speed) == numpy.sign(self.ground_speed):
                        self.ground_speed = 0
                    else:
                        self.ground_speed = new_speed
            if self.action_state[2] == 'grounded':
                self.update_center(self.center[0] + self.ground_speed, self.center[1])
            elif self.action_state[2] == 'walk':
                self.update_center(self.center[0] + self.ground_speed, self.center[1])
            elif self.action_state[2] == 'dash':
                self.action_state[3] -= 1
                if self.action_state[3] == 0:
                    self.ground_speed = 0
                    self.action_state = ['grounded', 0, 'grounded', 0]
                else:
                    self.ground_speed = directional_incrementer(self.ground_speed, -self.attributes['traction'] * 10, 0)
                self.update_center(self.center[0] + self.ground_speed, self.center[1])
            elif self.action_state[2] == 'jumpsquat':
                self.update_center(self.center[0] +
                    directional_incrementer(self.ground_speed, -self.attributes['traction'] * 2, 0), self.center[1])
                self.jump(self.action_state[4])
            elif self.action_state[2] == 'auto_wavedash':
                self.auto_wavedash(self.misc_data['angle'])
            elif self.action_state[2] == 'shield_off':
                self.action_state[3] -= 1
                if self.action_state[3] <= 0:
                    self.action_state = ['grounded', 0, 'grounded', 0]
            elif self.action_state[2] == 'shieldstun':
                self.action_state[3] -= 1
                if self.action_state[3] == 0:
                    self.action_state[2] = 'shielded'
            elif self.action_state[2] != 'grounded':
                getattr(self, self.action_state[2])()

        elif self.action_state[0] == 'airborne':
            self.update_air_speed(self.air_speed[0], self.air_speed[1] - self.attributes['vair_acc'])
            self.update_center(self.center[0] + self.air_speed[0], self.center[1] - self.air_speed[1])
            self.ground_speed = 0
            if not self.action_state[2] == 'airborne' and not self.action_state[2] == 'freefall' \
                    and not self.action_state[2] == 'tumble':
                getattr(self, self.action_state[2])()

        elif self.action_state[0] == 'airdodge':
            self.airdodge(self.misc_data['angle'])
            self.update_center(self.center[0] + self.air_speed[0], self.center[1] - self.air_speed[1])

        elif self.action_state[0] == 'freefall':
            self.update_air_speed(self.air_speed[0], self.air_speed[1] - self.attributes['vair_acc'])
            self.update_center(self.center[0] + self.air_speed[0], self.center[1] - self.air_speed[1])
            self.ground_speed = 0

        elif self.action_state[0] == 'shielded':
            if self.action_state[2] == 'shieldstun':
                self.action_state[3] -= 1
                if self.action_state[3] == 0:
                    self.action_state[2] = 'shielded'
                else:
                    if not self.ground_speed == 0:
                        if self.ground_speed > self.attributes['high_traction_speed']:
                            new_speed = self.ground_speed - self.attributes['traction'] * numpy.sign(self.ground_speed) * 2
                        else:
                            new_speed = self.ground_speed - self.attributes['traction'] * numpy.sign(self.ground_speed)
                        if not numpy.sign(new_speed) == numpy.sign(self.ground_speed):
                            self.ground_speed = 0
                        else:
                            self.ground_speed = new_speed
                    self.update_center(self.center[0] + self.ground_speed, self.center[1])
            else:
                self.ground_speed = 0
            self.misc_data['shield_health'] -= 0.2

        elif self.action_state[0] == 'ledge_grab':
            self.invincible = True
            self.jumped = False
            self.action_state[1] -= 1
            if self.action_state[1] == 0:
                self.action_state = ['ledge_wait', 30, 'ledge_wait', 0]
                self.misc_data['invincibility'] = 30

        elif self.action_state[0] == 'hitstun':
            self.update_center(self.center[0] + self.air_speed[0], self.center[1] - self.air_speed[1])
            self.update_air_speed(self.air_speed[0], self.air_speed[1])
            self.action_state[1] -= 1
            if self.action_state[1] == 0:
                self.action_state[1] = 0
                if self.misc_data['KB'] < 80:
                    self.action_state = ['airborne', 0, 'airborne', 0]
                else:
                    self.action_state = ['airborne', 0, 'tumble', 0]

        elif self.action_state[0] == 'hitlag':
            self.action_state[1] -= 1
            if self.action_state[1] == 0:
                self.action_state = self.misc_data['action_state']

        elif self.action_state[0] == 'knockdown':
            if self.action_state[2] == 'kd_bounce':
                self.update_air_speed(directional_incrementer(self.air_speed[0], -self.attributes['air_friction'], 0), 0)
                self.update_center(self.center[0] + self.air_speed[0], self.center[1])
                self.action_state[3] -= 1
                if self.action_state[3] == 0:
                    self.action_state = ['knockdown', 0, 'kd_wait', 0]
            elif self.action_state[2] == 'kd_wait':
                self.update_ecb()

    def character_update(self) -> None:
        raise NotImplementedError

    def update_ecb(self) -> None:
        raise NotImplementedError

    def update_center(self, x: float, y: float) -> None:
        """
        Update the character's center to x and y, ecb, and hitbox. This must be implemented in subclasses of Character
        because the ecb and hitbox should update dynamically based on action state.
        """
        raise NotImplementedError

    def update_air_speed(self, x: float, y: float) -> None:
        """
        Update a character's air speed to x and y and adjust according to max air speeds and action state.
        """
        self.air_speed = [x, y]
        if abs(self.air_speed[0]) > self.attributes['max_hair_speed'] and not self.action_state[0] == 'hitstun':
            self.air_speed[0] -= self.attributes['hair_acc'] / 4 * numpy.sign(x)
        if self.air_speed[1] < -self.attributes['max_vair_speed'] and not self.action_state[0] == 'hitstun':
            self.air_speed[1] = -self.attributes['max_vair_speed']
        elif self.action_state[0] == 'hitstun':
            if self.air_speed[0] > 0:
                self.air_speed[0] -= 0.19
                if self.air_speed[0] < 0:
                    self.air_speed[0] = 0
            elif self.air_speed[0] < 0:
                self.air_speed[0] += 0.19
                if self.air_speed[0] > 0:
                    self.air_speed[0] = 0
            self.air_speed[1] -= 1.3

    def ground_actionable(self) -> bool:
        """
        Return true if a character is on the ground and actionable.
        """
        if self.action_state[2] == 'grounded' or self.action_state[2] == 'walk' or self.action_state[2] == 'dash':
            if self.action_state[0] == 'waveland' and self.action_state[1] > WAVELAND_ACTIONABLE \
                    or self.action_state[0] == 'grounded':
                return True
            return False
        return False

    def air_actionable(self) -> bool:
        """
        Return true if a character is in the air and actionable.
        """
        if self.action_state[2] == 'airborne':
            return True
        return False

    def enter_hitlag(self, frames: int, attack_data: Dict) -> None:
        """
        Enters hitlag for 'frames' frames and stores the data of an attack into the action state to be used when hitstun
        ends and a DI input is recorded
        """
        self.misc_data.update({'action_state': self.action_state.copy(), 'attack_data': attack_data})
        self.action_state = ['hitlag', frames, 'hitlag', 0]

    def shield(self) -> None:
        if self.ground_actionable():
            self.action_state = ['shielded', 0, 'shielded', 0]

    def drop_shield(self) -> None:
        if self.action_state[2] != 'shieldstun':
            self.action_state = ['grounded', 0, 'shield_off', 15]

    def dash(self, direction: bool) -> None:
        if self.ground_actionable():
            self.direction = direction
            self.action_state = ['grounded', 0, 'dash', 22]
            if direction:
                self.ground_speed = self.attributes['max_gr_speed']
            else:
                self.ground_speed = -self.attributes['max_gr_speed']

    def walk(self, tilt) -> None:
        if self.ground_actionable():
            if tilt != 0:
                if self.action_state[0] != 'waveland':
                    self.action_state = ['grounded', 0, 'walk', 0]
                    self.ground_speed = self.attributes['max_gr_speed'] * tilt * 0.7
                elif self.action_state[0] == 'waveland':
                    self.action_state = ['grounded', 0, 'walk', 0]
                    self.ground_speed = self.attributes['max_gr_speed'] * tilt * 0.7
            else:
                if self.action_state[0] != 'waveland':
                    self.ground_speed = 0
                    self.action_state = ['grounded', 0, 'grounded', 0]
            if tilt > 0:
                self.direction = True
            elif tilt < 0:
                self.direction = False
    def drift(self, tilt) -> None:
        if (self.action_state[0] == 'airborne' and self.action_state[2] != 'hitstun') \
                or self.action_state[0] == 'freefall':
            set_spd = tilt * self.attributes['max_hair_speed']
            if set_spd == 0:
                self.update_air_speed(directional_incrementer(self.air_speed[0], -self.attributes['air_friction'], 0),
                                        self.air_speed[1])
            elif self.air_speed[0] != set_spd:
                self.update_air_speed(directional_incrementer(self.air_speed[0], -self.attributes['hair_acc'], set_spd),
                                      self.air_speed[1])

    def jump(self, released: bool) -> None:
        """
        Causes a character to enter jumpsquat animation for JUMPSQUAT_FRAME frames. The character performs a shorthop
        if released is True, and a fullhop otherwise.
        """
        if not self.jumped and self.action_state[0] == 'airborne' and self.action_state[2] != 'hitstun':
            self.jumped = True
            self.update_air_speed(self.air_speed[0], self.attributes['fullhop_velocity'])
        elif self.ground_actionable() or self.action_state[0] == 'shielded' or self.action_state[2] == 'shield_off':
            self.action_state[0] = 'grounded'
            self.action_state[1] = 0
            self.action_state.insert(4, released)
            self.action_state[2] = 'jumpsquat'
            self.action_state[3] = 1
        elif self.action_state[2] == 'jumpsquat':
            self.action_state[3] += 1
            if self.action_state[3] > JUMPSQUAT_FRAME:
                if self.action_state[4]:
                    self.update_air_speed(self.ground_speed,
                                          self.attributes['shorthop_velocity'] - self.attributes['vair_acc'])
                    self.update_center(self.center[0] + self.ground_speed,
                                       self.center[1] - self.attributes['shorthop_velocity'])
                else:
                    self.update_air_speed(self.ground_speed,
                                          self.attributes['fullhop_velocity'] - self.attributes['vair_acc'])
                    self.update_center(self.center[0] + self.ground_speed,
                                       self.center[1] - self.attributes['fullhop_velocity'])
                self.action_state = ['airborne', 0, 'airborne', 0]

    def airdodge(self, angle=None) -> None:
        """
        Causes a character to airdodge at angle 'angle', and then enter a freefall action state after the airdodge
        has completed.
        """
        if self.air_actionable():
            self.action_state = ['airdodge', 0, 'airdodge', 0]
            self.misc_data.update({'angle': angle})
        elif self.action_state[0] == 'airdodge':
            self.action_state[1] += 1
            if self.action_state[1] == 3:
                self.invincible = True
            elif self.action_state[1] < 28:
                multiplier = (605535 / (self.action_state[1] + 29.65) ** 3.24) - 0.25
                if angle is not None:
                    self.update_air_speed(math.cos(angle) * multiplier, math.sin(angle) * multiplier)
                else:
                    self.update_air_speed(0, 0)
            elif self.action_state[1] >= 29:
                self.invincible = False
                self.action_state = ['freefall', 0, 'freefall', 0]


    def auto_wavedash(self, angle=None) -> None:
        """
        Automatically inputs an airdodge after JUMPSQUAT_FRAME at angle 'angle'.
        """
        if self.action_state[2] == 'jumpsquat':
            self.action_state[2] = 'auto_wavedash'
            self.action_state[3] += 1
            self.misc_data.update({'angle': angle})
            if self.action_state[3] > JUMPSQUAT_FRAME:
                self.action_state = ['airborne', 0, 'airborne', 0]
                self.airdodge(self.misc_data['angle'])
        elif self.action_state[2] == 'auto_wavedash':
            self.action_state[3] += 1
            if self.action_state[3] > JUMPSQUAT_FRAME:
                self.action_state = ['airborne', 0, 'airborne', 0]
                self.airdodge(self.misc_data['angle'])

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
        self.hurtboxes = [Polygon(in_relation(self.center, [(-15, -90), (15, -90), (15, -30), (-15, -30)]))]
        self.hitboxes = {'regular': [[], [], False], 'projectile': []}
        self.attributes = {'max_gr_speed': 11.5, 'vair_acc': 1.18, 'max_vair_speed': 14.34, 'hair_acc': 0.41,
                           'max_hair_speed': 4.27, 'fullhop_velocity': 18.84, 'shorthop_velocity': 10.41,
                           'traction': 0.24, 'high_traction_speed': 8.19, 'weight': 30, 'air_friction': 0.1,
                           'edge_link': (80, 30, 30)}
        self.ground_speed = 0
        self.air_speed = [0, 0]
        self.jumped = False
        self.damage = 0
        self.ecb = [(self.center[0], self.center[1]), (self.center[0] - 15, self.center[1] - 30),
                    (self.center[0], self.center[1] - 30), (self.center[0] + 15, self.center[1] - 30)]

    def update_ecb(self) -> None:
        if self.action_state[0] == 'grounded' or self.action_state[0] == 'waveland':
            self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])
        elif self.action_state[0] == 'airborne':
            if 5 < self.air_speed[1]:
                self.ecb = in_relation(self.center, [(0, 10), (-15, -30), (0, -70), (15, -30)])

            elif -5 <= self.air_speed[1] <= 5:
                self.ecb = in_relation(self.center, [(0, self.air_speed[1] * 2), (-15, -30),
                           (0, -60 - self.air_speed[1] * 2), (15, -30)])
            else:
                self.ecb = in_relation(self.center, [(0, -10), (-15, -30), (0, -50), (15, -30)])
        elif self.action_state[0] == 'airdodge':
            if self.action_state[1] <= 3:
                self.ecb = in_relation(self.center, [(0, 10), (-15, -30), (0, -60), (15, -30)])
            else:
                self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])
        elif self.action_state[0] == 'knockdown':
            if self.action_state[2] == 'kd_bounce':
                self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -90), (15, -30)])
            elif self.action_state[2] == 'kd_wait':
                self.ecb = in_relation(self.center, [(0, 0), (-25, -15), (0, -30), (25, -15)])
        else:
            self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])

    def update_center(self, x: float, y: float) -> None:
        self.center = [x, y]
        self.update_ecb()
        self.hurtboxes = [Polygon(in_relation(self.center, [(-15, -90), (15, -90), (15, 0), (-15, 0)])),
                          x_reflect(Polygon(in_relation(self.center, [(15, -15), (30, -15), (30, -30), (15, -30)])),
                                    self.center[0], self.direction)]

    def ftilt(self) -> None:
        """
        A grounded attack.
        """
        if self.ground_actionable():
            self.action_state[2] = 'ftilt'
            self.action_state[3] = 1
            hitbox0 = [(15, -60), (15, -30), (30, -30), (30, -60)]
            hitbox1 = [(50, -60), (50, -30), (110, -30), (110, -60)]
            id0 = hitbox_maker(self.center, hitbox0, self.direction, 12, 70, 70, 60)
            id1 = hitbox_maker(self.center, hitbox1, self.direction, 8, 70, 70, 30)
            self.misc_data.update({'id0': id0, 'id1': id1, 'hitbox0': hitbox0, 'hitbox1': hitbox1})
        elif self.action_state[2] == 'ftilt':
            self.action_state[3] += 1
            if self.action_state[3] == 5:
                self.hitboxes['regular'] = [[self.misc_data['id0'][0]], [self.misc_data['id0'][1]], False]
            elif 10 >= self.action_state[3] >= 7:
                rotation_axis = [self.center[0], self.center[1] - 45]
                self.hitboxes['regular'][0] = [hitbox_rotate(rotation_axis, self.misc_data['id0'][0], self.direction,
                                                             (7 - self.action_state[3]) * 20),
                                               hitbox_rotate(rotation_axis, self.misc_data['id1'][0], self.direction,
                                                             (7 - self.action_state[3]) * 20)]
                self.hitboxes['regular'][1] = [self.misc_data['id0'][1], self.misc_data['id1'][1]]

            elif self.action_state[3] == 11:
                self.hitboxes['regular'] = [[], [], False]
            elif self.action_state[3] == 30:
                self.action_state[2] = 'grounded'
                self.action_state[3] = 0

    def fair(self) -> None:
        if self.air_actionable():
            self.action_state[2] = 'fair'
            self.action_state[3] = 1
            hitbox0 = [(15, -60), (15, -30), (30, -30), (30, -60)]
            hitbox1 = [(50, -60), (50, -30), (110, -30), (110, -60)]
            id0 = hitbox_maker(self.center, hitbox0, self.direction, 12, 45, 70, 60)
            id1 = hitbox_maker(self.center, hitbox1, self.direction, 8, 45, 70, 30)
            self.misc_data.update({'id0': id0, 'id1': id1, 'hitbox0': hitbox0, 'hitbox1': hitbox1})
        elif self.action_state[2] == 'fair':
            self.action_state[3] += 1
            if 4 <= self.action_state[3] <= 7:
                rotation_axis = [self.center[0], self.center[1] - 45]
                self.hitboxes['regular'][0] = [hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox0'], self.direction), self.direction, (self.action_state[3] - 7) * 20),
                                               hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox1'], self.direction), self.direction, (self.action_state[3] - 7) * 20)]
                self.hitboxes['regular'][1] = [self.misc_data['id0'][1], self.misc_data['id1'][1]]
            elif self.action_state[3] == 8:
                self.hitboxes['regular'] = [[], [], False]
            elif self.action_state[3] == 33:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def bair(self) -> None:
        if self.air_actionable():
            self.action_state[2] = 'bair'
            self.action_state[3] = 1
            hitbox0 = [(-15, -60), (-15, -30), (-30, -30), (-30, -60)]
            hitbox1 = [(-50, -60), (-50, -30), (-110, -30), (-110, -60)]
            id0 = hitbox_maker(self.center, hitbox0, self.direction, 12, -45, 70, 60)
            id1 = hitbox_maker(self.center, hitbox1, self.direction, 8, -45, 70, 30)
            self.misc_data.update({'id0': id0, 'id1': id1, 'hitbox0': hitbox0, 'hitbox1': hitbox1})
        elif self.action_state[2] == 'bair':
            self.action_state[3] += 1
            if 4 <= self.action_state[3] <= 7:
                rotation_axis = [self.center[0], self.center[1] - 45]
                self.hitboxes['regular'][0] = [hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox0'], self.direction), self.direction, (self.action_state[3] - 7) * 20),
                                               hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox1'], self.direction), self.direction, (self.action_state[3] - 7) * 20)]
                self.hitboxes['regular'][1] = [self.misc_data['id0'][1], self.misc_data['id1'][1]]
            elif self.action_state[3] == 8:
                self.hitboxes['regular'] = [[], [], False]
            elif self.action_state[3] == 33:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def upair(self) -> None:
        if self.air_actionable():
            self.action_state[2] = 'upair'
            self.action_state[3] = 1
            hitbox0 = [(-15, -60), (-15, -30), (-30, -30), (-30, -60)]
            hitbox1 = [(-50, -60), (-50, -30), (-110, -30), (-110, -60)]
            id0 = hitbox_maker(self.center, hitbox0, self.direction, 12, -45, 70, 60)
            id1 = hitbox_maker(self.center, hitbox1, self.direction, 8, -45, 70, 30)
            self.misc_data.update({'id0': id0, 'id1': id1, 'hitbox0': hitbox0, 'hitbox1': hitbox1})
        elif self.action_state[2] == 'upair':
            self.action_state[3] += 1
            if 4 <= self.action_state[3] <= 7:
                rotation_axis = [self.center[0], self.center[1] - 45]
                self.hitboxes['regular'][0] = [hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox0'], self.direction), self.direction, (self.action_state[3] - 7) * 20),
                                               hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox1'], self.direction), self.direction, (self.action_state[3] - 7) * 20)]
                self.hitboxes['regular'][1] = [self.misc_data['id0'][1], self.misc_data['id1'][1]]
            elif self.action_state[3] == 8:
                self.hitboxes['regular'] = [[], [], False]
            elif self.action_state[3] == 33:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def dair(self) -> None:
        if self.air_actionable():
            self.action_state[2] = 'dair'
            self.action_state[3] = 1
            hitbox0 = [(15, 30), (15, 0), (-15, 0), (-15, 30)]
            hitbox1 = [(15, 70), (15, 40), (-15, 40), (-15, 70)]
            id0 = hitbox_maker(self.center, hitbox0, self.direction, 12, 135, 70, 60)
            id1 = hitbox_maker(self.center, hitbox1, self.direction, 8, -135, 70, 30)
            self.misc_data.update({'id0': id0, 'id1': id1, 'hitbox0': hitbox0, 'hitbox1': hitbox1})
        elif self.action_state[2] == 'dair':
            self.action_state[3] += 1
            if 4 <= self.action_state[3] <= 7:
                rotation_axis = [self.center[0], self.center[1] - 45]
                self.hitboxes['regular'][0] = [hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox0'], self.direction), self.direction, (self.action_state[3] - 7) * 20 + 45),
                                               hitbox_rotate(rotation_axis, hitbox_updater(self.center,
                        self.misc_data['hitbox1'], self.direction), self.direction, (self.action_state[3] - 7) * 20 + 45)]
                self.hitboxes['regular'][1] = [self.misc_data['id0'][1], self.misc_data['id1'][1]]
            elif self.action_state[3] == 8:
                self.hitboxes['regular'] = [[], [], False]
            elif self.action_state[3] == 33:
                self.action_state[2] = 'airborne'
                self.action_state[3] = 0

    def neutral_special(self) -> None:
        if self.ground_actionable() or self.air_actionable() and not self.action_state[2] == 'neutral_special':
            proj0= [(15, -40), (15, -30), (60, -30), (60, -40)]
            self.misc_data.update({'proj0': proj0, 'prev_action_state': self.return_attr('action_state').copy()})
            self.action_state[2] = 'neutral_special'
            self.action_state[3] = 1
        elif self.action_state[2] == 'neutral_special':
            self.action_state[3] += 1
            if self.action_state[3] == 10:
                projid0 = hitbox_maker(self.center, self.misc_data['proj0'], self.direction, 3, 45, 0, 3)
                self.hitboxes['projectile'].append([projid0[0], projid0[1],
                                                    self.direction, False])
            if self.action_state[3] == 30:
                self.action_state = self.misc_data['prev_action_state']
