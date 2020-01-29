from __future__ import annotations
from typing import *
from characters import *
import pygame
pygame.joystick.init()


class CharacterControl:

    def __init__(self, character: Character, controller: Controller)-> None:
        self.Character = character
        self.Controller = controller

    def update_inputs(self) -> None:
        self.Controller.update_inputs()


class ControlMap:

    def __init__(self, name: str, input_maps: Dict):
        """
        input_maps will like something like this:
        {'axes': {'y': 0, 'x': 2, ...}, 'buttons': {'a': 3, 'b': 2, ...}, ...}
        """
        self.name = name
        self.axis_map = input_maps['axes']
        self.button_map = input_maps['buttons']
        self.hat_map = input_maps['hats']

    def get_input_num(self, input_name: str, type_: Union[str, None] = None) \
        -> float:
        """
        Returns the input number corresponding to the correct input type.
        Ex:
        get_input_num('y')
        >>> 0
        get_input_num('dpad_up')
        >>> 3
        """
        if type_ is None:
            if input_name in self.axis_map:
                return self.axis_map[input_name]
            elif input_name in self.button_map:
                return self.button_map[input_name]
            elif input_name in self.hat_map:
                return self.hat_map[input_name]
            return 0
        elif type_ == 'axis':
            return self.axis_map[input_name]
        elif type_ == 'button':
            return self.button_map[input_name]
        elif type_ == 'hat':
            return self.hat_map[input_name]

    def get_input_type(self, input_name: str) -> str:
        if input_name in self.axis_map:
            return 'axis'
        elif input_name in self.button_map:
            return 'button'
        elif input_name in self.hat_map:
            return 'hat'


class Controller:

    def __init__(self, joystick_num: int, control_map: ControlMap) -> None:
        self.joystick = pygame.joystick.Joystick(joystick_num)
        self.joystick.init()
        self.control_map = control_map
        self.input_storage = {'curr': {}, 'prev': {}}

    def get_input_value(self, input_name: str) -> float:
        input_type = self.control_map.get_input_type(input_name)
        input_num = self.control_map.get_input_num(input_name)
        if input_type == 'axis':
            return self.joystick.get_axis(input_num)
        elif input_type == 'button':
            return self.joystick.get_button(input_num)
        elif input_type == 'hat':
            return self.joystick.get_hat(input_num)
        return 0

    def update_inputs(self) -> None:
        """
        Every frame this will be called to update the current and previous
        frame's inputs.
        """
        self.input_storage['prev'] = self.input_storage['curr'].copy()
        axis = {}
        for inputs in self.control_map.axis_map:
            axis[inputs] = self.get_input_value(inputs)

        button = {}
        for inputs in self.control_map.button_map:
            button[inputs] = self.get_input_value(inputs)

        hat = {}
        for inputs in self.control_map.hat_map:
            button[inputs] = self.get_input_value(inputs)

        self.input_storage['curr'] = {'axis': axis,
                                      'button': button,
                                      'hat': hat}

    def c_input(self, input_name: str) -> float:
        """
        Gets current inputs. Why might we want to call this instead of
        get_input_value? Because inputs should only be recorded during the
        update_inputs method and used from that data. The reason for this is
        just for cleaner execution (i.e. no inputs taken in between frame 1-2)
        and in case we ever want to create a replay system, one input record
        per frame is absolutely necessary.
        """
        curr_inputs = self.input_storage['curr']
        if input_name in curr_inputs['axis']:
            return curr_inputs['axis'][input_name]
        elif input_name in curr_inputs['button']:
            return curr_inputs['button'][input_name]
        elif input_name in curr_inputs['hat']:
            return curr_inputs['hat'][input_name]

    def get_button_change(self, button_name: str) -> bool:
        """
        Checks if a given button changed values from the last frame.
        """
        curr = self.input_storage['curr']
        prev = self.input_storage['prev']
        return not curr['button'][button_name] == prev['button'][button_name]

    def get_nonneutral(self) -> Dict:
        """
        Returns inputs that are not in their neutral position.
        """
        pass


class ControlHandler:

    def __init__(self, CharControls: Tuple[CharacterControl]) -> None:
        self.CharControls = CharControls

    def process_inputs(self) -> None:
        """
        P1
        TODO: Finish
        This is going to be what's called every frame
        Must figure out the control structure for this.
        """
        pass

