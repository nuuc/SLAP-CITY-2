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

with open('assets/character_info/phrog.dbpk', 'rb') as file:
    dummy_data = pickle.load(file)


# noinspection SpellCheckingInspection
class Character:
    """
    An abstract representation of a Slap City 2 character.
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
    data: Dict
    moves: Dict
    meter: int

    def __init__(self) -> None:
        self.action_state = ['jump', 0]
        self.speed = [0, 0]
        self.attributes = {}
        self.center = [0, 0]
        self.direction = False
        self.ecb = []
        self.env_state = 'airborne'
        self.hitboxes = {'regular': {'hitboxPolys': {}, 'hit': False}, 'projectile': []}
        self.data = {'shield_health': 86, 'invincible': False, 'invincibility': 0, 'need_input': -1, 'on_ledge': 0,
                     'sliding': False, 'landing_lag': UNIV_LANDING_LAG, 'dash_dir': 0, 'ASDI': 0,
                     'meter': 0, 'jumped': False, 'damage': 0, 'needed_input': 0, 'tech': 0, 'kb': 0, 'jump_speed': 0}
        self.moves = {}

    def _hinvincibility(self) -> None:
        if self.data['invincibility'] >= 0:
            self.data['invincibility'] -= 1
            if self.data['invincibility'] <= 0:
                self.data['invincible'] = False
            else:
                self.data['invincible'] = True

    def _htech(self) -> None:
        if self.data['tech'] >= 0:
            self.data['tech'] -= 1

    def _hprojectile(self) -> None:
        pass

    def _hshield(self) -> None:
        if self.action_state[0] != 'shielded':
            if self.data['shield_health'] < 86:
                self.data['shield_health'] += 0.1
            elif self.data['shield_health'] > 86:
                self.data['shield_health'] = 86

    def _hASDI(self) -> None:
        if self.action_state[0] == 'hitlag':
            self.action_state[1] -= 1
            if self.action_state[1] == 0:
                if self.data['ASDI'] != 0:
                    self.increment_center(math.cos(self.data['ASDI']) * ASDI_MULTI,
                                          -math.sin(self.data['ASDI']) * ASDI_MULTI)
                self.action_state = self.data['action_state']

    def _hsliding(self) -> None:
        if self.data['sliding']:
            if not self.speed[0] == 0:
                if abs(self.speed[0]) > self.attributes['high_traction_speed']:
                    self.speed[0] = dir_inc(self.speed[0], -2 * self.attributes['traction'], 0)
                else:
                    self.speed[0] = dir_inc(self.speed[0], -self.attributes['traction'], 0)
                self.increment_center(self.speed[0])

    def _hwalk(self) -> None:
        tilt = self.data['walk_tilt']
        if tilt != 0:
            self.data.update({'sliding': False})
            self.update_speed(self.attributes['max_gr_speed'] * tilt * 0.7)
            self.increment_center(self.speed[0])
            self.action_state[1] += 1
            if self.action_state[1] > len(dummy_data['animations']['walk']) - 1:
                self.action_state[1] = 0
        elif self.data['sliding'] and tilt == 0:
            self.action_state = ['wait', 0]
        elif not self.data['sliding'] and tilt == 0:
            self.action_state = ['wait', 0]
            self.update_speed(0)
        if tilt > 0:
            self.direction = True
        elif tilt < 0:
            self.direction = False

    def _hdash(self) -> None:
        if self.action_state[0] == 'start_dash':
            self.data.update({'sliding': False})
            self.action_state[1] += 1
            if self.action_state[1] == self.attributes['dash_frames']:
                self.action_state = ['full_dash', 0]
            if self.data['dash_dir'] < 0:
                self.direction = False
            elif self.data['dash_dir'] > 0:
                self.direction = True
            self.speed[0] = self.attributes['max_gr_speed'] * self.data['dash_dir']
            self.increment_center(self.speed[0])

        elif self.action_state[0] == 'full_dash':
            self.increment_center(self.speed[0])
            if self.data['dash_dir'] < 0:
                self.direction = False
            elif self.data['dash_dir'] > 0:
                self.direction = True
        elif self.action_state[0] == 'turnaround':
            self.action_state[1] += 1
            if self.action_state[1] == 1:
                self.data.update({'turnaround_initial': numpy.sign(self.speed.copy()[0])})
            if self.data['turnaround_initial'] > 0:
                self.speed[0] -= self.attributes['traction']
            else:
                self.speed[0] += self.attributes['traction']

            if self.action_state[1] < self.attributes['turnaround_frames']:
                self.data.update({'dash_dir': 0})
            elif self.data['dash_dir'] != 0:
                self.action_state = ['start_dash', 0]
            else:
                self.action_state = ['wait', 0]
            self.increment_center(self.speed[0])

    def _hwaveland(self) -> None:
        self.action_state[1] += 1
        if self.action_state[1] > 10:
            self.action_state = ['wait', 0]

    def _hlag(self) -> None:
        self.action_state[1] -= 1
        if self.action_state[1] == 0:
            self.action_state = ['wait', 0]

    def _hjump(self) -> None:
        self.action_state[1] += 1
        self.increment_center(dir_inc(self.speed[0], -2 * self.attributes['traction'], 0))
        if self.action_state[1] > JUMPSQUAT_FRAME:
            self.env_state = 'airborne'
            if self.data['released']:
                self.update_speed(self.data['jump_speed'],
                                  self.attributes['shorthop_velocity'] - self.attributes['vair_acc'])
                self.increment_center(self.speed[0], -self.attributes['shorthop_velocity'])
            else:
                self.update_speed(self.data['jump_speed'],
                                  self.attributes['fullhop_velocity'] - self.attributes['vair_acc'])
                self.increment_center(self.speed[0], -self.attributes['fullhop_velocity'])
            self.action_state = ['jump', 0]

    def _hauto_wavedash(self) -> None:
        self.action_state[1] += 1
        if self.action_state[1] > JUMPSQUAT_FRAME:
            self.env_state = 'airborne'
            self.action_state = ['jump', 0]
            self.action('airdodge', self.data['angle'])

    def _hshield_off(self) -> None:
        self.action_state[1] -= 1
        if self.action_state[1] <= 0:
            self.action_state = ['wait', 0]

    def _hshieldstun(self) -> None:
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

    def _hkd_bounce(self) -> None:
        self.data.update({'wavelanding': False})
        self.update_speed(dir_inc(self.speed[0], -self.attributes['air_friction'], 0))
        self.increment_center(self.speed[0])
        self.action_state[1] -= 1
        if self.action_state[1] == 0:
            self.action_state = ['kd_wait', 0]

    def _hgroundmove(self) -> None:
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
        if self.action_state[0] in self.moves:
            self.action_state[1] += 1
            move = self.moves[self.action_state[0]]
            frame_data = move['frame data']
            if self.action_state[1] > len(frame_data) - 1:
                self.action_state = ['wait', 0]
                self.hitboxes['regular'] = {'hitboxPolys': {}, 'hit': False}
            else:
                if move['type'] == 'regular hitbox':
                    self.hitboxes['regular']['hitboxPolys'] = \
                        copy.deepcopy(frame_data[self.action_state[1]]['hitboxPolys'])
                    for ids in frame_data[self.action_state[1]]['hitboxPolys']:
                        hitboxPoly = frame_data[self.action_state[1]]['hitboxPolys'][ids]['polygon']
                        self.hitboxes['regular']['hitboxPolys'][ids]['polygon'] = auto_transform(hitboxPoly,
                                                                                                 self.direction,
                                                                                                 tuple(self.center))

    def _hairdodge(self) -> None:
        self.action_state[1] += 1
        if self.action_state[1] == 3:
            self.data.update({'invincibility': 27})
        elif self.action_state[1] < 28:
            multiplier = (605535 / (self.action_state[1] + 29.65) ** 3.24) - 0.25
            angle = self.data['angle']
            if angle:
                self.update_speed(math.cos(angle) * multiplier, math.sin(angle) * multiplier)
                self.increment_center(self.speed[0], -self.speed[1])
            else:
                self.update_speed(0, 0)
                self.increment_center(self.speed[0], -self.speed[1])
        elif self.action_state[1] > 28:
            self.action_state = ['freefall', 0]

    def _hhitstun(self) -> None:
        self.speed = [dir_inc(self.speed[0], 0.19, 0), dir_inc(self.speed[1], -self.attributes['vair_acc'],
                                                               -self.attributes['max_vair_speed'])]
        self.increment_center(self.speed[0], -self.speed[1])
        self.action_state[1] -= 1
        if self.action_state[1] == 0:
            if self.data['kb'] < 80:
                self.action_state = ['jump', 0]
            else:
                self.action_state = ['tumble', 0]

    def _hairmove(self) -> None:
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
        self.action_state[1] += 1
        self.handle_airborne_speed()

    def _hledge_grab(self) -> None:
        self.jumped = False
        self.action_state[1] -= 1
        if self.action_state[1] == 0:
            self.action_state = ['ledge_wait', 0]

    def _hledge_maneuver(self) -> None:
        # TODO: Make this handle ledges according to new framework
        self.action_state[1] += 1
        if self.moves[self.action_state[0]]['type'] == 'maneuver':
            if self.env_state == 'grounded':
                if self.action_state[1] == self.moves[self.action_state[0]]['invincible'][0]:
                    self.data.update({'invincibility': self.moves[self.action_state[0]]['invincible'][1]})
                if self.action_state[1] == self.moves[self.action_state[0]]['end']:
                    if self.action_state[0] == 'rollf':
                        self.direction = not self.direction
                    elif self.action_state[0] == 'techrolll':
                        self.direction = True
                    elif self.action_state[0] == 'techrollr':
                        self.direction = False
                    self.update_ecb()
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
                    self.data.update({'invincibility': self.moves[self.action_state[0]]['invincible'][1]})
                if self.action_state[1] <= 10:
                    self.increment_center(0, -9)
                else:
                    self.env_state = 'grounded'
                    self.data.update({'sliding': False})

    def _hstartsquat(self) -> None:
        self.action_state[1] += 1
        if self.action_state[1] > 4:
            self.action_state = ['squat', 0]

    def update(self) -> None:
        """
        Update the character based on their action state.
        """
        self._hinvincibility()
        self._htech()
        self._hprojectile()
        self._hshield()
        self._hASDI()

        if self.env_state == 'grounded':
            self._hsliding()
            if self.action_state[0] == 'walk':
                self._hwalk()

            elif self.action_state[0] in ('start_dash', 'full_dash'):
                self._hdash()

            elif self.action_state[0] == 'startsquat':
                self._hstartsquat()

            elif self.action_state[0] == 'waveland':
                self._hwaveland()

            elif self.action_state[0] == 'lag':
                self._hlag()

            elif self.action_state[0] == 'jumpsquat':
                self._hjump()

            elif self.action_state[0] == 'auto_wavedash':
                self._hauto_wavedash()

            elif self.action_state[0] == 'shielded':
                self.data['shield_health'] -= 0.2

            elif self.action_state[0] == 'shield_off':
                self._hshield_off()

            elif self.action_state[0] == 'shieldstun':
                self._hshieldstun()

            elif self.action_state[0] == 'kd_bounce':
                self._hkd_bounce()

            elif self.action_state[0] == 'kd_wait':
                self.update_ecb()

            else:
                self._hgroundmove()

        elif self.env_state == 'airborne':
            if self.action_state[0] == 'airdodge':
                self._hairdodge()

            elif self.action_state[0] == 'hitstun':
                self._hhitstun()

            elif self.action_state[0] in ('tumble', 'jump', 'freefall'):
                self.handle_airborne_speed()

            elif self.action_state[0] in self.moves:
                self._hairmove()

        elif self.env_state == 'ledge':
            if self.action_state[0] == 'ledge_grab':
                self._hledge_grab()

            elif self.action_state[0] in self.moves:
                self._hledge_maneuver()

        self.update_hurtbox()

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
        if self.action_state[0] in ('wait', 'jump', 'walk', 'full_dash', 'start_dash', 'tumble', 'ledge_wait', 'squat'):
            return True
        return False

    def enter_hitlag(self, frames: int, attack_data: Dict) -> None:
        """
        Enters hitlag for 'frames' frames and stores the data of an attack into the action state to be used when hitstun
        ends and a DI input is recorded
        """
        self.data.update({'action_state': self.action_state.copy(), 'attack_data': attack_data})
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
            self.action_state[0] = 'walk'
            self.data.update({'walk_tilt': extra})
        elif self.action_state[0] == 'full_dash' and action == 'dash':
            if numpy.sign(self.speed[0]) != numpy.sign(extra):
                if extra != 0:
                    self.direction = not self.direction
                self.action_state = ['turnaround', 0]
        elif self.actionable() and action == 'dash':
            if self.action_state[1] < self.attributes['dash_frames'] and extra != self.data['dash_dir']:
                self.action_state = ['start_dash', 0]
            self.data.update({'dash_dir': extra})
        elif self.action_state[0] == 'turnaround' and action == 'dash':
            self.data.update({'dash_dir': extra})
        elif action == 'shield_off':
            self.action_state = ['shield_off', extra]
        elif self.actionable() and action == 'airdodge':
            self.action_state = ['airdodge', 0]
            self.data.update({'angle': extra})
        elif action == 'auto_wavedash':
            self.action_state[0] = 'auto_wavedash'
            self.data.update({'angle': extra})
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
            self.data.update({'released': extra})
        elif self.actionable() and action == 'aerial_jump':
            if not self.jumped:
                self.update_speed(extra * self.attributes['max_hair_speed'], self.attributes['fullhop_velocity'])
                self.action_state = ['jump', 0]
                self.jumped = True


class Dummy(Character):

    def __init__(self, center: List[int], direction: bool, action_state: List, env_state: str) -> None:
        super(Dummy, self).__init__()
        self.hurtboxes = Polygon([(-30, 0), (30, 0), (30, -60), (-30, -60)])
        self.hitboxes = {'regular': {'hit': True, 'ids': {}}, 'grab': {}, 'projectiles': []}
        self.attributes = char_data['Phrog']['attributes']
        self.speed = [0, 0]
        self.jumped = False
        self.damage = 0
        self.ecb = [(self.center[0], self.center[1]), (self.center[0] - 15, self.center[1] - 30),
                    (self.center[0], self.center[1] - 30), (self.center[0] + 15, self.center[1] - 30)]
        self.moves = dummy_data['moves']

    def update(self) -> None:
        super().update()
        if self.action_state[0] == 'up_special':
            self.env_state = 'suspended'
            self.action_state[1] += 1
            if self.action_state[1] == self.moves[self.action_state[0]]['need_input']:
                self.data.update({'need_input': 0})
            elif self.action_state[1] == self.moves[self.action_state[0]]['need_input'] + 1:
                direction = self.data['need_input']
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
                    self.data.update({'prev_action_state': self.action_state.copy()})
            elif self.moves[self.action_state[0]]['type'] == 'projectile':
                for id in self.moves[self.action_state[0]]['ids']:
                    if self.action_state[1] == self.moves[self.action_state[0]]['ids'][id]['start'][0]:
                        # Adds the hitbox
                        pos1 = in_relation_point(self.center, x_reflect_point(self.moves[self.action_state[0]]['ids']
                                                                    [id]['hitbox']['position'], 0, self.direction))
                        radius = self.moves[self.action_state[0]]['ids'][id]['hitbox']['radius']
                        self.hitboxes['projectile'].append([pos1, pos1, radius, self.direction])

            # When they reach the end of the move, return them to action state based on the env_state or if
            # env_state is 'any', return them to the previous action state
            if self.action_state[1] == self.moves[self.action_state[0]]['end']:
                if self.moves[self.action_state[0]]['env_state'] == 'any':
                    self.action_state = self.data['prev_action_state']
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
        '''
        Set hurtboxes equal to some polygon defined in %character data%
        '''
        if self.env_state == 'grounded':
            if self.action_state[0] == 'walk':
                hurtboxPoly = dummy_data['animations']['walk'][self.action_state[1]]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
            elif self.action_state[0] == 'jumpsquat':
                hurtboxPoly = dummy_data['animations']['jump'][self.action_state[1] - 1]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
            elif self.action_state[0] == 'startsquat':
                hurtboxPoly = dummy_data['animations']['startsquat'][self.action_state[1] - 1]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
            elif self.action_state[0] == 'squat':
                hurtboxPoly = dummy_data['animations']['startsquat'][3]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
            elif self.action_state[0] in self.moves:
                hurtboxPoly = self.moves[self.action_state[0]]['frame data'][self.action_state[1]]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
            else:
                hurtboxPoly = dummy_data['animations']['walk'][0]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
        elif self.env_state == 'airborne':
            if self.action_state[0] == 'jump':
                hurtboxPoly = dummy_data['animations']['airborne'][0]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
            else:
                hurtboxPoly = dummy_data['animations']['walk'][0]['hurtboxPoly']
                self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))
        else:
            hurtboxPoly = dummy_data['animations']['walk'][0]['hurtboxPoly']
            self.hurtboxes = auto_transform(hurtboxPoly, self.direction, tuple(self.center))



