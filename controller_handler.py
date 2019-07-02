import pygame, characters, math, game_loop, engine
from typing import *

CTRL_STICK_RADIUS = 0.8
pygame.init()
pygame.joystick.init()


# TODO: Make input a superclass for Keyboard, GC Controller, etc.
class Input:
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
    axis_list: List
    joystick_id: int

    def __init__(self, joystick_id: int) -> None:
        inputs = [[], []]
        joystick = pygame.joystick.Joystick(joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs[0].insert(i, joystick.get_button(i))
        for i in range(joystick.get_numaxes()):
            inputs[1].insert(i, joystick.get_axis(i))
        self.button_list = [inputs[0], inputs[0]]
        self.axis_list = [inputs[1], inputs[1]]
        self.joystick_id = joystick_id

    def update(self) -> None:
        """
        Updates the button and axis list to the current frame.
        """
        self.button_list = [self.get_input()[0], self.button_list[0]]
        self.axis_list = [self.get_input()[1], self.axis_list[0]]

    @staticmethod
    def controller_mapping(x: float, y: float, dead_zone: float) -> List:
        """
        Takes an input of the axis position and maps the controller into five regions: Left, right, up, down, and a
        dead zone region, according to 'dead_zone'.
        """
        if math.sqrt(x ** 2 + y ** 2) < dead_zone:
            return [0, 0]
        else:
            if x > abs(y):
                return [1, 0]
            elif x < -1 * abs(y):
                return [-1, 0]
            elif abs(x) < y:
                return [0, 1]
            elif -1 * abs(x) > y:
                return [0, -1]
        return [0, 0]

    @staticmethod
    def get_angle(tilt: List) -> float:
        """
        Gets the angle of tilt in radians.
        """
        return math.atan2(tilt[1], tilt[0])

    def get_button_change(self, button: int) -> bool:
        """
        Checks if 'button' is pressed this frame, and is not pressed last frame.
        """
        if self.button_list[0][button] and not self.button_list[1][button]:
            return True
        return False

    def get_axis_change(self, axis: int, prev_dead_zone: float, curr_dead_zone: float) -> bool:
        """
        Checks if axis was within 'prev_dead_zone' last frame and is not within curr_dead_zone this frame.
        """
        if axis < 2:
            prev = self.controller_mapping(self.axis_list[1][0], self.axis_list[1][1], prev_dead_zone)
            curr = self.controller_mapping(self.axis_list[0][0], self.axis_list[0][1], curr_dead_zone)
            if prev == [0, 0] and curr[axis]:
                return True
            return False
        else:
            prev = self.controller_mapping(self.axis_list[1][3], self.axis_list[1][2], prev_dead_zone)
            curr = self.controller_mapping(self.axis_list[0][3], self.axis_list[0][2], curr_dead_zone)
            if prev == [0, 0] and curr[axis - 2]:
                return True
            return False

    def get_flick(self, axis: int, curr_dead_zone: float) -> bool:
        prev = self.controller_mapping(self.axis_list[1][0], self.axis_list[1][1], curr_dead_zone)
        curr = self.controller_mapping(self.axis_list[0][0], self.axis_list[0][1], curr_dead_zone)
        if (prev[axis] == -1 and curr[axis] == 1) or (prev[axis] == 1 and curr[axis] == -1):
            return True
        return False
        # prev = self.controller_mapping(self.axis_list[1][0], self.axis_list[1][1], prev_dead_zone)
        # curr = self.controller_mapping(self.axis_list[0][0], self.axis_list[0][1], curr_dead_zone)
        # if prev == [0, 0] and curr[axis] or :
        #     return True
        # return False

    def get_input(self) -> List:
        """
        A helper function that records the input to be used in the update function.
        """
        inputs = [[], []]
        joystick = pygame.joystick.Joystick(self.joystick_id)
        for i in range(joystick.get_numbuttons()):
            inputs[0].insert(i, joystick.get_button(i))
        for i in range(joystick.get_numaxes()):
            inputs[1].insert(i, joystick.get_axis(i))
        inputs[1][1] *= -1
        inputs[1][2] *= -1
        return inputs

    def get_axis(self, axis: int) -> float:
        """
        Returns the axis value on this frame.
        """
        return self.axis_list[0][axis]

    def get_button(self, button: int) -> bool:
        """
        Returns the button value on this frame.
        """
        return self.button_list[0][button]


controller_input = []
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()
    controller_input.append(Input(i))


def handle(char_control_map: Dict) -> None:
    """
    Handles character inputs according to which controller they are mapped to.
    """
    for character in char_control_map:
        controller = controller_input[char_control_map[character]]
        controller.update()
        ctrl_stick = [controller.get_axis(0), controller.get_axis(1)]
        cstick = [controller.get_axis(3), controller.get_axis(2)]
        ctrl_stick_mapping = controller.controller_mapping(ctrl_stick[0], ctrl_stick[1], 0.15)
        cstick_mapping = controller.controller_mapping(cstick[0], cstick[1], 0.15)
        action_state = character.action_state
        env_state = character.env_state

        if controller.get_button(12):
            character.update_center(500, 100)
            character.action_state = ['jump', 0]
            character.damage = 0
            character.update_speed(0, 0)
            character.env_state = 'airborne'
        if controller.get_button(13):
            print(character.direction, character.action_state, character.env_state, character.center, character.ecb, character.invincible, character.misc_data['invincibility'])

        if controller.get_button(14):
            print(character.hitboxes)

        if character.misc_data['need_input'] == 0:
            character.misc_data.update({'need_input': controller.get_angle(ctrl_stick)})

        if env_state == 'grounded':
            if action_state[0] in ('wait', 'start_dash', 'full_dash', 'walk', 'turnaround'):
                if controller.get_axis(4) >= 0:
                    character.action('shielded')

                elif ctrl_stick_mapping[0] != 0 and controller.get_button_change(1):
                    character.action('ftilt')

                elif controller.get_button(2):
                    character.action('neutral_special')

                elif controller.get_button_change(3):
                    character.action('jumpsquat', False)

                elif controller.get_button_change(0):
                    character.action('jumpsquat', True)

                elif controller.get_button_change(7):
                    character.action('grab')

                if controller.get_button(4):
                    character.action('dash', ctrl_stick_mapping[0])
                elif ctrl_stick_mapping[0] != 0:
                    character.action('walk', ctrl_stick[0])
                elif ctrl_stick_mapping[0] == 0 and action_state[0] == 'start_dash':
                    pass
                    # super spaghetti, but it's gonna be fixed when the input for dash is implemented anyways
                else:
                    character.action('walk', 0)

            elif action_state[0] == 'jumpsquat':
                if controller.get_button(5) and ctrl_stick_mapping != [0, 0]:
                    character.action('auto_wavedash', controller.get_angle(ctrl_stick))
                elif ctrl_stick_mapping[0] == 1:
                    character.misc_data.update({'jump_speed': character.attributes['max_gr_speed'] / 3})
                elif ctrl_stick_mapping[0] == -1:
                    character.misc_data.update({'jump_speed': -character.attributes['max_gr_speed'] / 3})
                else:
                    character.misc_data.update({'jump_speed': 0})

            elif action_state[0] == 'shielded':
                if controller.get_button_change(3):
                    character.action('jumpsquat', False)
                elif controller.get_button_change(0):
                    character.action('jumpsquat', True)
                elif controller.get_axis(4) < 0:
                    character.action('shield_off', 15)
                elif ctrl_stick_mapping[0] != 0:
                    character.action('roll', ctrl_stick_mapping[0])
                elif controller.get_axis(4) >= 0:
                    character.action('shield')

            elif action_state[0] == 'grabbing':
                if ctrl_stick_mapping[1] == 1:
                    character.action_state = ['upthrow', 0]

            elif action_state[0] == 'shield_off':
                if controller.get_button_change(3):
                    character.action('jumpsquat', False)
                elif controller.get_button_change(0):
                    character.action('jumpsquat', True)

            elif action_state[0] == 'kd_wait':
                if ctrl_stick_mapping[0] != 0:
                    character.action('kd_roll', ctrl_stick_mapping[0])
                elif ctrl_stick_mapping[1] == 1:
                    character.action('kd_getup')

        elif env_state == 'airborne':
            if ctrl_stick_mapping[0] != 0 and character.action_state[0] != 'hitstun':
                character.drift(ctrl_stick[0])
            else:
                character.drift(0)

            if controller.get_button_change(5):
                if ctrl_stick_mapping != [0, 0]:
                    character.action('airdodge', controller.get_angle(ctrl_stick))
                else:
                    character.action('airdodge', False)

            if controller.get_axis_change(1, 0.25, 0.3) and character.speed[1] <= 0 and ctrl_stick_mapping[1] == -1:
                character.update_speed(0, -character.attributes['max_vair_speed'])

            elif controller.get_button_change(1):
                if character.direction:
                    if ctrl_stick_mapping[0] == 1:
                        character.action('fair')
                    elif ctrl_stick_mapping[0] == -1:
                        character.action('bair')
                elif not character.direction:
                    if ctrl_stick_mapping[0] == 1:
                        character.action('bair')
                    elif ctrl_stick_mapping[0] == -1:
                        character.action('fair')
                if ctrl_stick_mapping[1] == 1:
                    character.action('upair')
                elif ctrl_stick_mapping[1] == -1:
                    character.action('dair')

            elif controller.get_axis_change(2, 0.15, 0.2) or controller.get_axis_change(3, 0.15, 0.2):
                if character.direction:
                    if cstick_mapping[0] == 1:
                        character.action('fair')
                    elif cstick_mapping[0] == -1:
                        character.action('bair')
                elif not character.direction:
                    if cstick_mapping[0] == 1:
                        character.action('bair')
                    elif cstick_mapping[0] == -1:
                        character.action('fair')
                if cstick_mapping[1] == 1:
                    character.upair()
                elif cstick_mapping[1] == -1:
                    character.dair()

            elif controller.get_button(2):
                if ctrl_stick_mapping[1] == 1:
                    character.action('up_special')
                else:
                    character.action('neutral_special')

            elif controller.get_button_change(3) or controller.get_button_change(0):
                character.action('aerial_jump', ctrl_stick_mapping[0])

            elif action_state[0] in ('hitstun', 'tumble'):
                if controller.get_axis(4) >= 0:
                    character.misc_data.update({'tech': 40})

        if action_state[0] == 'hitlag' and action_state[1] == 1 and character.misc_data['attack_data'] is not None:
            if ctrl_stick_mapping != [0, 0]:
                engine.handle_hit(character, character.misc_data['attack_data'], controller.get_angle(ctrl_stick))
                character.misc_data.update({'ASDI': controller.get_angle(ctrl_stick)})
            else:
                engine.handle_hit(character, character.misc_data['attack_data'])

        elif action_state[0] == 'ledge_wait':
            if ctrl_stick_mapping[1] == -1:
                character.action_state = ['jump', 0]
                character.env_state = 'airborne'
                character.update_speed(0, -character.attributes['max_vair_speed'])
            elif ctrl_stick_mapping[0] == -1:
                if character.direction:
                    character.action_state = ['jump', 0]
                    character.env_state = 'airborne'
                    character.update_speed(0, 0)
                else:
                    character.action('ledge_getup')
            elif ctrl_stick_mapping[0] == 1:
                if not character.direction:
                    character.action_state = ['jump', 0]
                    character.env_state = 'airborne'
                    character.update_speed(0, 0)
                else:
                    character.action('ledge_getup')
            elif controller.get_button(3) or controller.get_button(0):
                character.action_state = ['ledge_jump', 0]

            elif controller.get_button(5):
                character.action_state = ['ledge_roll', 0]



