import pygame, characters, math, loops, engine
from typing import *

CTRL_STICK_RADIUS = 0.8
pygame.init()
pygame.joystick.init()


class InputMapping:
    mapping: Dict
    name: str

    def __init__(self, mapping: Dict, name: str):
        self.mapping = mapping
        self.name = name

    def get_map(self) -> Dict:
        return self.mapping

    def get_name(self) -> str:
        return self.name


# TODO: Make input a superclass for Keyboard, GC Controller, etc.
class Controller:
    """
    A class containing information and methods of a controller, including previous button presses.

    === PUBLIC ATTRIBUTES ==
    'button_list': A list with the first index containing the current button press, and the second containing the
    button presses on the previous frame.
    'axis_list': A list with the first index containing the current axis input, and the second containing the axis
    input on the previous frame.
    joystick_id: An integer that maps which controller an Input object is connected to.
    """
    button_list: List
    button_mapping: InputMapping
    options: Dict

    def __init__(self, button_mapping: InputMapping, options=None) -> None:
        self.button_list = [[] for i in range(10)]
        self.button_mapping = button_mapping
        self.options = options

    def update(self) -> None:
        """
        Updates the button and axis list to the current frame.
        """
        raise NotImplementedError

    def get_button_change(self, button: str) -> bool:
        """
        Checks if 'button' is pressed this frame, and is not pressed last frame.
        """
        if self.button_list[0][button] and not self.button_list[1][button]:
            return True
        return False

    def get_button(self, button: str) -> bool:
        """
        Returns the button value on this frame.
        """
        try:
            return self.button_list[0][button]
        except:
            return False


class Joystick(Controller):
    joystick_id: int
    axis_list: List
    axis_mapping: InputMapping

    def __init__(self, joystick_id: int, button_mapping: InputMapping, axis_mapping=None) -> None:
        super().__init__(button_mapping)
        self.joystick_id = joystick_id
        joystick = pygame.joystick.Joystick(joystick_id)
        joystick.init()
        if axis_mapping is None:
            self.axis_mapping = InputMapping({'y': 1, 'x': 0, 'cy': 3, 'cx': 2, 'ranalog': 4, 'lanalog': 5},
                                             'default')
        else:
            self.axis_mapping = axis_mapping
        self.axis_list = []

    @staticmethod
    def get_angle(tilt: Tuple) -> float:
        return math.atan2(tilt[1], tilt[0])

    @staticmethod
    def axis_mapper(axis: Tuple, dead_zone: float) -> Tuple:
        x, y = axis
        if math.sqrt(x ** 2 + y ** 2) < dead_zone:
            return tuple((0, 0))
        else:
            if x > abs(y):
                return tuple((1, 0))
            elif x < -abs(y):
                return tuple((-1, 0))
            elif abs(x) < y:
                return tuple((0, 1))
            elif -abs(x) > y:
                return tuple((0, -1))
        return tuple((0, 0))

    def get_axis(self, axis: str) -> float:
        return self.axis_list[0][axis]

    def get_axes(self, axis: str) -> Tuple:
        if axis == 'control':
            return tuple((self.get_axis('x'), self.get_axis('y')))
        elif axis == 'cstick':
            return tuple((self.get_axis('cx'), self.get_axis('cy')))
        return tuple((0, 0))

    def map_axes(self, axis: str, dead_zone=0.15) -> Tuple:
        if axis == 'control':
            x = self.get_axis('x')
            y = self.get_axis('y')
            return Joystick.axis_mapper((x, y), dead_zone)
        elif axis == 'cstick':
            x = self.get_axis('cx')
            y = self.get_axis('cy')
            return Joystick.axis_mapper((x, y), dead_zone)
        return tuple((0, 0))

    def update(self) -> None:
        joystick = pygame.joystick.Joystick(self.joystick_id)

        button_dict = {}
        for button in self.button_mapping.get_map():
            button_dict[button] = joystick.get_button(self.button_mapping.get_map()[button])

        axis_dict = {}
        for axis in self.axis_mapping.get_map():
            axis_dict[axis] = joystick.get_axis(self.axis_mapping.get_map()[axis])
        axis_dict['y'] *= -1
        axis_dict['cy'] *= -1

        if len(self.button_list) > 10:
            del self.button_list[9]
        if len(self.axis_list) > 10:
            del self.axis_list[9]

        self.button_list.insert(0, button_dict)
        self.axis_list.insert(0, axis_dict)


class Keyboard(Controller):
    vaxis_list: List
    vaxis_mapping: InputMapping

    def __init__(self, button_mapping: InputMapping, vaxis_mapping=None) -> None:
        super().__init__(button_mapping)
        if vaxis_mapping is None:
            self.vaxis_mapping = InputMapping({'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a,
                                               'right': pygame.K_d}, 'default')

    def get_vaxis(self, axis: str) -> float:
        return self.vaxis_list[0][axis]

    def update(self) -> None:
        button_dict = {}
        for button in self.button_mapping.get_map():
            button_dict[button] = pygame.key.get_pressed()[self.button_mapping.get_map()[button]]

        vaxis_dict = {}
        for vaxis in self.vaxis_mapping.get_map():
            vaxis_dict[vaxis] = pygame.key.get_pressed()[self.vaxis_mapping.get_map()[vaxis]]

        if len(self.button_list) > 10:
            del self.button_list[9]
        if len(self.vaxis_list) > 10:
            del self.vaxis_list[9]

        self.button_list.insert(0, button_dict)
        self.vaxis_list.insert(0, vaxis_dict)


class ControllerHandler:
    char_control_map: Dict[Controller, characters.Character]

    def __init__(self, char_control_map: Dict, button_mapping_map: Dict) -> None:
        self.char_control_map = {}
        for controller in char_control_map:
            if isinstance(controller, int):
                self.char_control_map[Joystick(controller, button_mapping_map[controller])] = \
                    char_control_map[controller]
            elif controller == 'keyboard':
                self.char_control_map[Keyboard(button_mapping_map[controller])] = char_control_map[controller]

    def handle_controls(self) -> None:
        for controller in self.char_control_map:
            controller.update()
            character = self.char_control_map[controller]
            action_state = character.action_state
            env_state = character.env_state
            if isinstance(controller, Joystick):
                ctrl_stick = controller.get_axes('control')
                cstick = controller.get_axes('cstick')
                dctrl_stick_map = controller.map_axes('control')
                dcstick_map = controller.map_axes('cstick')

                if controller.get_button('dpadup'):
                    character.update_center(500, 100)
                    character.action_state = ['jump', 0]
                    character.damage = 0
                    character.update_speed(0, 0)
                    character.env_state = 'airborne'

                if character.data['need_input'] == 0:
                    character.data['needed_input'] = controller.get_axes('control')

                if env_state == 'grounded':
                    if action_state[0] in ('wait', 'start_dash', 'full_dash', 'walk', 'turnaround', 'squat'):
                        if controller.get_axis('ranalog') >= 0:
                            character.action('shielded')

                        elif dctrl_stick_map[0] != 0 and controller.get_button_change('a'):
                            character.action('ftilt')

                        elif controller.get_button('b'):
                            character.action('neutral_special')

                        elif controller.get_button_change('y'):
                            character.action('jumpsquat', False)

                        elif controller.get_button_change('x'):
                            character.action('jumpsquat', True)

                        elif controller.get_button_change('z'):
                            character.action('grab')
                        elif dctrl_stick_map[1] == -1:
                            if character.action_state[0] != 'squat':
                                character.action('startsquat')
                        elif dctrl_stick_map[0] != 0:
                            character.action('walk', ctrl_stick[0])
                        else:
                            character.action('walk', 0)

                    elif action_state[0] == 'jumpsquat':
                        if controller.get_button('ltrigger') and dctrl_stick_map != [0, 0]:
                            character.action('auto_wavedash', controller.get_angle(ctrl_stick))
                        elif dctrl_stick_map[0] == 1:
                            character.data['jump_speed'] = character.attributes['max_gr_speed'] / 3
                        elif dctrl_stick_map[0] == -1:
                            character.data['jump_speed'] = -character.attributes['max_gr_speed'] / 3
                        else:
                            character.data['jump_speed'] = 0

                    elif action_state[0] == 'shielded':
                        if controller.get_button_change('y'):
                            character.action('jumpsquat', False)
                        elif controller.get_button_change('x'):
                            character.action('jumpsquat', True)
                        elif controller.get_axis('ranalog') < 0:
                            character.action('shield_off', 15)
                        elif dctrl_stick_map[0] != 0:
                            character.action('roll', dctrl_stick_map[0])
                        elif controller.get_axis('ranalog') >= 0:
                            character.action('shield')

                    elif action_state[0] == 'grabbing':
                        if dctrl_stick_map[1] == 1:
                            character.action_state = ['upthrow', 0]

                    elif action_state[0] == 'shield_off':
                        if controller.get_button_change('y'):
                            character.action('jumpsquat', False)
                        elif controller.get_button_change('x'):
                            character.action('jumpsquat', True)

                    elif action_state[0] == 'kd_wait':
                        if dctrl_stick_map[0] != 0:
                            character.action('kd_roll', dctrl_stick_map[0])
                        elif dctrl_stick_map[1] == 1:
                            character.action('kd_getup')

                elif env_state == 'airborne':
                    if dctrl_stick_map[0] != 0 and character.action_state[0] != 'hitstun':
                        character.drift(ctrl_stick[0])
                    else:
                        character.drift(0)

                    if controller.get_button_change('ltrigger'):
                        if dctrl_stick_map != [0, 0]:
                            character.action('airdodge', controller.get_angle(ctrl_stick))
                        else:
                            character.action('airdodge', False)

                    elif controller.get_button_change('a'):
                        if character.direction:
                            if dctrl_stick_map[0] == 1:
                                character.action('fair')
                            elif dctrl_stick_map[0] == -1:
                                character.action('bair')
                        elif not character.direction:
                            if dctrl_stick_map[0] == 1:
                                character.action('bair')
                            elif dctrl_stick_map[0] == -1:
                                character.action('fair')
                        if dctrl_stick_map[1] == 1:
                            character.action('upair')
                        elif dctrl_stick_map[1] == -1:
                            character.action('dair')
                        elif dctrl_stick_map == (0, 0):
                            character.action('nair')

                    # Check for cstick input

                    elif controller.get_button('b'):
                        if dctrl_stick_map[1] == 1:
                            character.action('up_special')
                        else:
                            character.action('neutral_special')

                    elif controller.get_button_change('y') or controller.get_button_change('x'):
                        character.action('aerial_jump', dctrl_stick_map[0])

                    elif action_state[0] in ('hitstun', 'tumble'):
                        if controller.get_axis('ltrigger') >= 0 and character.data['tech'] == 0:
                            character.data['tech'] = 40

                if action_state[0] == 'hitlag' and action_state[1] == 1 and character.data['attack_data'] is not None:
                    if dctrl_stick_map != [0, 0]:
                        engine.handle_hit(character, character.data['attack_data'], Joystick.get_angle(ctrl_stick))
                        character.data['ASDI'] = controller.get_angle(ctrl_stick)
                    else:
                        engine.handle_hit(character, character.data['attack_data'])

                elif action_state[0] == 'ledge_wait':
                    if dctrl_stick_map[1] == -1:
                        character.action_state = ['jump', 0]
                        character.env_state = 'airborne'
                        character.update_speed(0, -character.attributes['max_vair_speed'])
                    elif dctrl_stick_map[0] == -1:
                        if character.direction:
                            character.action_state = ['jump', 0]
                            character.env_state = 'airborne'
                            character.update_speed(0, 0)
                        else:
                            character.action('ledge_getup')
                    elif dctrl_stick_map[0] == 1:
                        if not character.direction:
                            character.action_state = ['jump', 0]
                            character.env_state = 'airborne'
                            character.update_speed(0, 0)
                        else:
                            character.action('ledge_getup')
                    elif controller.get_button('y') or controller.get_button('x'):
                        character.action_state = ['ledge_jump', 0]

                    elif controller.get_button('rtrigger') or controller.get_button('ltrigger'):
                        character.action_state = ['ledge_roll', 0]




