import pygame, numpy, math, json, time, pickle, copy
from typing import *
from misc_functions import *

JUMPSQUAT_FRAME = 4
WAVELAND_ACTIONABLE = 10
UNIV_LANDING_LAG = 2
ASDI_MULTI = 10

total_elapsed = 0
t = 0

with open('assets/character_info/json_zimmerman.json') as json_file:
    char_data = json.load(json_file)['characters']



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
    """
    action_state: List
    speed: List
    attributes: Dict
    center: List[float]
    damage: int
    direction: bool
    ecb: List[Tuple]
    env_state: str
    hitboxes: Dict
    hurtboxes: Polygon
    invincible: bool
    jumped: bool
    misc_data: Dict
    moves: Dict
    meter: int

    def __init__(self, center: List[int], direction: bool, action_state: List, env_state: str) -> None:
        self.action_state = action_state
        self.speed = [0, 0]
        self.attributes = {}
        self.center = center
        self.damage = 0
        self.direction = direction
        self.ecb = []
        self.env_state = env_state
        self.hitboxes = {'regular': [[], [], False], 'projectile': []}
        self.hurtboxes = None
        self.invincible = False
        self.jumped = False
        self.misc_data = {'shield_health': 86, 'invincibility': 60, 'need_input': -1, 'on_ledge': 0,
                          'wavelanding': False, 'landing_lag': UNIV_LANDING_LAG, 'dash_dir': 0, 'tech': 0, 'ASDI': 0,
                          'super_meter': 0}
        self.moves = {}
        self.meter = 0

    def update(self) -> None:
        """
        Update the character based on their action state.
        """
        # TODO: Generalize update to handle all action states
        if self.misc_data['invincibility'] >= 0:
            self.misc_data['invincibility'] -= 1
            if self.misc_data['invincibility'] <= 0:
                self.invincible = False
            else:
                self.invincible = True

        if self.misc_data['tech'] >= 0:
            self.misc_data['tech'] -= 1

        # for projectile in self.hitboxes['projectile']:
        #     if projectile[2]:
        #         projectile[0] = affinity.translate(projectile[0], 20)
        #     else:
        #         projectile[0] = affinity.translate(projectile[0], -20)
        #     if projectile[0].bounds[2] >= 1280 or projectile[0].bounds[0] <= 0:
        #         self.hitboxes['projectile'].remove(projectile)

        if self.action_state[0] != 'shielded':
            if self.misc_data['shield_health'] < 86:
                self.misc_data['shield_health'] += 0.1
            elif self.misc_data['shield_health'] > 86:
                self.misc_data['shield_health'] = 86

        if self.action_state[0] == 'hitlag':
            self.action_state[1] -= 1
            if self.action_state[1] == 0:
                if self.misc_data['ASDI'] != 0:
                    self.increment_center(math.cos(self.misc_data['ASDI']) * ASDI_MULTI,
                                          -math.sin(self.misc_data['ASDI']) * ASDI_MULTI)
                self.action_state = self.misc_data['action_state']

        elif self.env_state == 'grounded':
            if self.misc_data['wavelanding']:
                if not self.speed[0] == 0:
                    if abs(self.speed[0]) > self.attributes['high_traction_speed']:
                        self.speed[0] = dir_inc(self.speed[0], -2 * self.attributes['traction'], 0)
                    else:
                        self.speed[0] = dir_inc(self.speed[0], -self.attributes['traction'], 0)
                    self.increment_center(self.speed[0])

            if self.action_state[0] == 'walk':
                tilt = self.misc_data['walk_tilt']
                if tilt != 0:
                    self.misc_data.update({'wavelanding': False})
                    self.update_speed(self.attributes['max_gr_speed'] * tilt * 0.7)
                    self.increment_center(self.speed[0])
                elif self.misc_data['wavelanding'] and tilt == 0:
                    self.action_state = ['wait', 0]
                elif not self.misc_data['wavelanding'] and tilt == 0:
                    self.action_state = ['wait', 0]
                    self.update_speed(0)
                if tilt > 0:
                    self.direction = True
                elif tilt < 0:
                    self.direction = False
            elif self.action_state[0] == 'start_dash':
                self.misc_data.update({'wavelanding': False})
                self.action_state[1] += 1
                if self.action_state[1] == self.attributes['dash_frames']:
                    self.action_state = ['full_dash', 0]
                if self.misc_data['dash_dir'] < 0:
                    self.direction = False
                elif self.misc_data['dash_dir'] > 0:
                    self.direction = True
                self.speed[0] = self.attributes['max_gr_speed'] * self.misc_data['dash_dir']
                self.increment_center(self.speed[0])

            elif self.action_state[0] == 'full_dash':
                self.increment_center(self.speed[0])
                if self.misc_data['dash_dir'] < 0:
                    self.direction = False
                elif self.misc_data['dash_dir'] > 0:
                    self.direction = True

            elif self.action_state[0] == 'turnaround':
                self.action_state[1] += 1
                if self.action_state[1] == 1:
                    self.misc_data.update({'turnaround_initial': numpy.sign(self.speed.copy()[0])})
                if self.misc_data['turnaround_initial'] > 0:
                    self.speed[0] -= self.attributes['traction']
                else:
                    self.speed[0] += self.attributes['traction']

                if self.action_state[1] < self.attributes['turnaround_frames']:
                    self.misc_data.update({'dash_dir': 0})
                elif self.misc_data['dash_dir'] != 0:
                    self.action_state = ['start_dash', 0]
                else:
                    self.action_state = ['wait', 0]
                self.increment_center(self.speed[0])

            elif self.action_state[0] == 'waveland':
                self.action_state[1] += 1
                if self.action_state[1] > 10:
                    self.action_state = ['wait', 0]

            elif self.action_state[0] == 'lag':
                self.action_state[1] -= 1
                if self.action_state[1] == 0:
                    self.action_state = ['wait', 0]

            elif self.action_state[0] == 'jumpsquat':
                self.action_state[1] += 1
                self.increment_center(dir_inc(self.speed[0], -2 * self.attributes['traction'], 0))
                if self.action_state[1] > JUMPSQUAT_FRAME:
                    self.env_state = 'airborne'
                    if self.misc_data['released']:
                        self.update_speed(self.misc_data['jump_speed'],
                                          self.attributes['shorthop_velocity'] - self.attributes['vair_acc'])
                        self.increment_center(self.speed[0], -self.attributes['shorthop_velocity'])
                    else:
                        self.update_speed(self.misc_data['jump_speed'],
                                          self.attributes['fullhop_velocity'] - self.attributes['vair_acc'])
                        self.increment_center(self.speed[0], -self.attributes['fullhop_velocity'])
                    self.action_state = ['jump', 0]

            elif self.action_state[0] == 'auto_wavedash':
                self.action_state[1] += 1
                if self.action_state[1] > JUMPSQUAT_FRAME:
                    self.env_state = 'airborne'
                    self.action_state = ['jump', 0]
                    self.action('airdodge', self.misc_data['angle'])

            elif self.action_state[0] == 'shielded':
                self.misc_data['shield_health'] -= 0.2

            elif self.action_state[0] == 'shield_off':
                self.action_state[1] -= 1
                if self.action_state[1] <= 0:
                    self.action_state = ['wait', 0]

            elif self.action_state[0] == 'shieldstun':
                self.action_state[1] -= 1
                if self.action_state[1] == 0:
                    self.action_state[0] = 'shielded'
                    self.speed[0] = 0
                else:
                    if self.speed[0] >= self.attributes['high_traction_speed']:
                        self.update_speed(dir_inc(self.speed[0], -2 * self.attributes['traction'], 0))
                    else:
                        self.update_speed(dir_inc(self.speed[0], -self.attributes['traction'], 0))
                    self.increment_center(self.speed[0])
            elif self.action_state[0] == 'kd_bounce':
                self.misc_data.update({'wavelanding': False})
                self.update_speed(dir_inc(self.speed[0], -self.attributes['air_friction'], 0))
                self.increment_center(self.speed[0])
                self.action_state[1] -= 1
                if self.action_state[1] == 0:
                    self.action_state = ['kd_wait', 0]
            elif self.action_state[0] == 'kd_wait':
                self.update_ecb()
            else:
                self.action_state[1] += 1
                '''
                ~~ If this code is reached, this implies that the action state should be handled by information from
                   %character data%
                
                - Check if self.action_state[1] > len(%corresponding action in character data%)
                    - Update action state accordingly
        
                - Check if this move is considered an attack
                    - If so, update the hit value in hitboxes to False
                    
                - Check for type of move (regular, maneuver, throw, etc.)
                    - Update hurtboxes to corresponding action state hurtbox polygon in %character data%
                    - Update hitboxes to corresponding action state hitbox polygons in %character data%
                '''

        elif self.env_state == 'airborne':
            if self.action_state[0] == 'airdodge':
                self.action_state[1] += 1
                if self.action_state[1] == 3:
                    self.misc_data.update({'invincibility': 27})
                elif self.action_state[1] < 28:
                    multiplier = (605535 / (self.action_state[1] + 29.65) ** 3.24) - 0.25
                    angle = self.misc_data['angle']
                    if angle:
                        self.update_speed(math.cos(angle) * multiplier, math.sin(angle) * multiplier)
                        self.increment_center(self.speed[0], -self.speed[1])
                    else:
                        self.update_speed(0, 0)
                        self.increment_center(self.speed[0], -self.speed[1])
                elif self.action_state[1] > 28:
                    self.action_state = ['freefall', 0]
            elif self.action_state[0] == 'hitstun':
                self.speed = [dir_inc(self.speed[0], 0.19, 0), dir_inc(self.speed[1], -self.attributes['vair_acc'],
                                                                       -self.attributes['max_vair_speed'])]
                self.increment_center(self.speed[0], -self.speed[1])
                self.action_state[1] -= 1
                if self.action_state[1] == 0:
                    if self.misc_data['kb'] < 80:
                        self.action_state = ['jump', 0]
                    else:
                        self.action_state = ['tumble', 0]

            elif self.action_state[0] in ('tumble', 'jump', 'freefall'):
                self.handle_airborne_speed()

            elif self.action_state[0] in self.moves:
                self.action_state[1] += 1
                '''
                ~~ If this code is reached, this implies that the action state should be handled by information from
                   %character data%
                   
                - Check if self.action_state[1] > len(%corresponding action in character data%)
                    - Update action state accordingly
        
                - Check if this move is considered an attack
                    - If so, update the hit value in hitboxes to False
                    
                - Check if self.action_state[1] > autocancel frame
                    - If not, landing lag is set to a value in %character data%
                    - If so, landing lag is set to UNIV_LANDING_LAG
                
                - Check for type of move
                    - Update hurtboxes to corresponding action state hurtbox polygon in %character data%
                    - Update hitboxes to corresponding action state hitbox polygons in %character data%
                '''
                self.handle_airborne_speed()

        elif self.env_state == 'ledge':
            if self.action_state[0] == 'ledge_grab':
                self.jumped = False
                self.action_state[1] -= 1
                if self.action_state[1] == 0:
                    self.action_state = ['ledge_wait', 0]

            elif self.action_state[0] in self.moves:
                self.action_state[1] += 1
                if self.moves[self.action_state[0]]['type'] == 'maneuver':
                    if self.env_state == 'grounded':
                        if self.action_state[1] == self.moves[self.action_state[0]]['invincible'][0]:
                            self.misc_data.update({'invincibility': self.moves[self.action_state[0]]['invincible'][1]})
                        if self.action_state[1] == self.moves[self.action_state[0]]['end']:
                            if self.action_state[0] == 'rollf':
                                self.direction = not self.direction
                            elif self.action_state[0] == 'techrolll':
                                self.direction = True
                            elif self.action_state[0] == 'techrollr':
                                self.direction = False
                            self.update_ecb()
                            self.update_hurtbox()
                        if self.moves[self.action_state[0]]['end'] > self.action_state[1] \
                                >= self.moves[self.action_state[0]]['start']:
                            if self.action_state[0] in ('rollf', 'rollb', 'ledge_getup'):
                                if self.direction:
                                    self.increment_center(eval(self.moves[self.action_state[0]]['increment']))
                                else:
                                    self.increment_center(-eval(self.moves[self.action_state[0]]['increment']))
                            elif self.action_state[0] == 'ledge_jump':
                                if self.direction:
                                    self.update_speed(self.attributes['max_hair_speed'],
                                                      self.attributes['fullhop_velocity'])
                                else:
                                    self.update_speed(-self.attributes['max_hair_speed'],
                                                      self.attributes['fullhop_velocity'])
                                self.env_state = 'airborne'
                            else:
                                self.increment_center(eval(self.moves[self.action_state[0]]['increment']))
                    elif self.env_state == 'ledge':
                        if self.action_state[1] == self.moves[self.action_state[0]]['invincible'][0]:
                            self.misc_data.update({'invincibility': self.moves[self.action_state[0]]['invincible'][1]})
                        if self.action_state[1] <= 10:
                            self.increment_center(0, -9)
                        else:
                            self.env_state = 'grounded'
                            self.misc_data.update({'wavelanding': False})

    def update_ecb(self) -> None:
        raise NotImplementedError

    def update_hurtbox(self) -> None:
        raise NotImplementedError

    def update_center(self, x: float, y: float) -> None:
        """
        Update the character's center to x and y, ecb, and hitbox. This must be implemented in subclasses of Character
        because the ecb and hitbox should update dynamically based on action state.
        """
        self.center = [x, y]
        self.update_ecb()
        self.update_hurtbox()

    def increment_center(self, x=0.0, y=0.0) -> None:
        self.center = [self.center[0] + x, self.center[1] + y]
        self.update_ecb()
        self.update_hurtbox()

    def update_speed(self, x=None, y=None) -> None:
        """
        Update a character's air speed to x and y and adjust according to max air speeds and action state.
        """
        if x is not None and y is not None:
            self.speed = [x, y]
        elif x is None and y is not None:
            self.speed[1] = y
        elif y is None and x is not None:
            self.speed[0] = x
        else:
            self.speed = [0, 0]

    def increment_speed(self, x=0.0, y=0.0) -> None:
        self.speed = [self.speed[0] + x, self.speed[1] + y]

    def handle_airborne_speed(self):
        self.increment_speed(0, -self.attributes['vair_acc'])
        if abs(self.speed[0]) > self.attributes['max_hair_speed']:
            self.speed[0] = dir_inc(self.speed[0], -self.attributes['hair_acc'] / 4, 0)
        if self.speed[1] < -self.attributes['max_vair_speed']:
            self.speed[1] = -self.attributes['max_vair_speed']
        self.increment_center(self.speed[0], -self.speed[1])

    def actionable(self) -> bool:
        if self.action_state[0] in ('wait', 'jump', 'walk', 'full_dash', 'start_dash', 'tumble', 'ledge_wait'):
            return True
        return False

    def enter_hitlag(self, frames: int, attack_data: Dict) -> None:
        """
        Enters hitlag for 'frames' frames and stores the data of an attack into the action state to be used when hitstun
        ends and a DI input is recorded
        """
        self.misc_data.update({'action_state': self.action_state.copy(), 'attack_data': attack_data})
        self.action_state = ['hitlag', frames]

    def drift(self, tilt) -> None:
        set_spd = tilt * self.attributes['max_hair_speed']
        if set_spd == 0:
            self.update_speed(dir_inc(self.speed[0], -self.attributes['air_friction'], 0))
        elif self.speed[0] != set_spd:
            self.update_speed(dir_inc(self.speed[0], -self.attributes['hair_acc'], set_spd))

    def action(self, action: str, extra=None) -> None:
        if self.actionable() and extra is None:
            self.action_state = [action, 0]
        elif self.actionable() and action == 'walk':
            self.action_state = ['walk', 0]
            self.misc_data.update({'walk_tilt': extra})
        elif self.action_state[0] == 'full_dash' and action == 'dash':
            if numpy.sign(self.speed[0]) != numpy.sign(extra):
                if extra != 0:
                    self.direction = not self.direction
                self.action_state = ['turnaround', 0]
        elif self.actionable() and action == 'dash':
            if self.action_state[1] < self.attributes['dash_frames'] and extra != self.misc_data['dash_dir']:
                self.action_state = ['start_dash', 0]
            self.misc_data.update({'dash_dir': extra})
        elif self.action_state[0] == 'turnaround' and action == 'dash':
            self.misc_data.update({'dash_dir': extra})
        elif action == 'shield_off':
            self.action_state = ['shield_off', extra]
        elif self.actionable() and action == 'airdodge':
            self.action_state = ['airdodge', 0]
            self.misc_data.update({'angle': extra})
        elif action == 'auto_wavedash':
            self.action_state[0] = 'auto_wavedash'
            self.misc_data.update({'angle': extra})
        elif action == 'roll' and self.action_state[0] == 'shielded':
            if self.direction and extra == 1:
                self.action_state = ['rollf', 0]
            elif self.direction and extra == -1:
                self.action_state = ['rollb', 0]
            elif not self.direction and extra == -1:
                self.action_state = ['rollf', 0]
            elif not self.direction and extra == 1:
                self.action_state = ['rollb', 0]
        elif action == 'techroll':
            if extra != 0:
                if extra == 1:
                    self.action_state = ['techrollr', 0]
                    self.direction = False
                elif extra == -1:
                    self.action_state = ['techrolll', 0]
                    self.direction = True
            else:
                self.action_state = ['tech', 0]
        elif self.action_state[0] == 'kd_wait':
            if action == 'kd_roll':
                if extra == 1:
                    self.action_state = ['kd_rollr', 0]
                    self.direction = False
                elif extra == -1:
                    self.action_state = ['kd_rolll', 0]
                    self.direction = True
            elif action == 'kd_getup':
                self.action_state = ['kd_getup', 0]
        elif (self.actionable() and action == 'jumpsquat') or \
                (self.action_state[0] in ('shielded', 'shield_off', 'turnaround') and action == 'jumpsquat'):
            self.action_state = ['jumpsquat', 0]
            self.misc_data.update({'released': extra})
        elif self.actionable() and action == 'aerial_jump':
            if not self.jumped:
                self.update_speed(extra * self.attributes['max_hair_speed'], self.attributes['fullhop_velocity'])
                self.action_state = ['jump', 0]
                self.jumped = True


class Phrog(Character):

    def __init__(self, center: List[int], direction: bool, action_state: List, env_state: str) -> None:
        super(Phrog, self).__init__(center, direction, action_state, env_state)
        self.hurtboxes = Polygon([(-30, 0), (30, 0), (30, -60), (-30, -60)])
        self.hitboxes = {'regular': {'hit': True, 'ids': {}}, 'grab': {}, 'projectiles': []}
        self.attributes = char_data['Phrog']['attributes']
        self.speed = [0, 0]
        self.jumped = False
        self.damage = 0
        self.ecb = [(self.center[0], self.center[1]), (self.center[0] - 15, self.center[1] - 30),
                    (self.center[0], self.center[1] - 30), (self.center[0] + 15, self.center[1] - 30)]
        self.moves = char_data['Phrog']['moves']

    def update(self) -> None:
        super().update()
        if self.action_state[0] == 'up_special':
            self.env_state = 'suspended'
            self.action_state[1] += 1
            if self.action_state[1] == self.moves[self.action_state[0]]['need_input']:
                self.misc_data.update({'need_input': 0})
            elif self.action_state[1] == self.moves[self.action_state[0]]['need_input'] + 1:
                direction = self.misc_data['need_input']
                self.update_speed(15 * math.cos(direction), 15 * math.sin(direction))
            elif self.moves[self.action_state[0]]['end']> self.action_state[1] >= self.moves[self.action_state[0]]['start']:
                self.increment_center(self.speed[0], -self.speed[1])
            elif self.action_state[1] == self.moves[self.action_state[0]]['end']:
                self.update_speed(0, 0)
                self.env_state = 'airborne'
                self.action_state = ['freefall', 0]
        elif self.action_state[0] in self.moves and self.moves[self.action_state[0]]['type'] == 'other':
            self.action_state[1] += 1
            if self.action_state[1] == 1:
                if self.moves[self.action_state[0]]['env_state'] == 'any':
                    self.misc_data.update({'prev_action_state': self.action_state.copy()})
            elif self.moves[self.action_state[0]]['type'] == 'projectile':
                for id in self.moves[self.action_state[0]]['ids']:
                    if self.action_state[1] == self.moves[self.action_state[0]]['ids'][id]['start'][0]:
                        # Adds the hitbox
                        pos1 = in_relation_point(self.center, x_reflect_point(self.moves[self.action_state[0]]['ids']
                                                                    [id]['hitbox']['position'],  0, self.direction))
                        radius = self.moves[self.action_state[0]]['ids'][id]['hitbox']['radius']
                        self.hitboxes['projectile'].append([pos1, pos1, radius, self.direction])

            # When they reach the end of the move, return them to action state based on the env_state or if
            # env_state is 'any', return them to the previous action state
            if self.action_state[1] == self.moves[self.action_state[0]]['end']:
                if self.moves[self.action_state[0]]['env_state'] == 'any':
                    self.action_state = self.misc_data['prev_action_state']
                elif self.moves[self.action_state[0]]['env_state'] == 'airborne':
                    self.action_state = ['jump', 0]
                elif self.moves[self.action_state[0]]['env_state'] == 'grounded':
                    self.action_state = ['wait', 0]

    def update_ecb(self) -> None:
        if self.env_state == 'grounded':
            self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])
        elif self.env_state == 'airborne':
            if self.action_state[0] in ('jump', 'freefall'):
                if 5 < self.speed[1]:
                    self.ecb = in_relation(self.center, [(0, 10), (-15, -30), (0, -70), (15, -30)])
                elif -5 <= self.speed[1] <= 5:
                    self.ecb = in_relation(self.center, [(0, self.speed[1] * 2), (-15, -30),
                               (0, -60 - self.speed[1] * 2), (15, -30)])
                else:
                    self.ecb = in_relation(self.center, [(0, -10), (-15, -30), (0, -50), (15, -30)])
            elif self.action_state[0] == 'airdodge':
                if self.action_state[1] <= 3:
                    self.ecb = in_relation(self.center, [(0, 10), (-15, -30), (0, -60), (15, -30)])
                else:
                    self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])
            else:
                self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])
        elif self.env_state == 'ledge':
            self.ecb = in_relation(self.center, [(0, 0), (-8, -45), (0, -90), (8, -45)])
        else:
            self.ecb = in_relation(self.center, [(0, 0), (-15, -30), (0, -60), (15, -30)])

    def update_hurtbox(self) -> None:
        self.hurtboxes = in_relation_poly(Polygon([(-15, 0), (15, 0), (15, -60), (-15, -60)]), self.center)
        '''
        Set hurtboxes equal to some polygon defined in %character data%
        '''






