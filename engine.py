from typing import *
from characters import Character, CharacterHelper
import controller, environment, pygame
import misc_functions as mf


class GameEngine:

    def __init__(self, CharControls: Tuple[controller.CharacterControl],
                 Stage: environment.Stage, Screen: pygame.Surface):
        self.CharControls = CharControls
        self.Stage = Stage
        self.Screen = Screen
        self.ControlHandler = controller.ControlHandler(CharControls)

    @staticmethod
    def pop_tuple(item: Any, tup: Tuple) -> Tuple:
        return tuple((obj for obj in tup if obj is not item))

    def process(self) -> None:
        # First, process inputs
        self.process_inputs()

        # Second, process environment
        self.process_env()

        # Then, draw before any collision detection occurs.
        self.draw()

        # Lastly, process collision.
        self.process_collision()

    def process_inputs(self) -> None:
        """
        Processes inputs for each character. This is just a wrapper method
        to keep everything clean.
        """
        self.ControlHandler.process_inputs()

    def process_env(self) -> None:
        """
        Processes environment for each character.
        """
        for CharControl in self.CharControls:
            self.Stage.process(CharControl)

    def draw(self) -> None:
        """
        P3
        TODO: Finish
        Draws everything on the screen. This will probably be handled in a draw
        class.
        """
        pass

    def process_collision(self) -> None:
        for CharControl in self.CharControls:
            character = CharControl.Character
            others = self.pop_tuple(CharControl, self.CharControls)
            for other_CharControl in others:
                other_character = other_CharControl.Character
                self.handle_collision(character, other_character)

    def ECB_collision(self) -> None:
        """
        P2
        TODO: Finish
        This method is used to move the character's ECB outside of one another.
        """
        pass

    @staticmethod
    def hit_dir(dealt_char: Character, hit_char: Character) -> None:
        """
        Makes the character that got hit change direction to face the character
        who dealt the hit.
        """
        dir = mf.sign(hit_char.pos('x') - dealt_char.pos('x'))
        hit_char.modify_int_data('direction', dir)


    @staticmethod
    def handle_collision(char_a: Character, char_b: Character) -> bool:
        """
        A helper method for process collision that checks for character_a
        hitting character_b and handles it accordingly.
        """
        hitbox_a = char_a.hitboxes
        hurtbox_b = char_b.hurtbox

        if char_b.int_data('invincible'):
            return False

        collide_reg = hitbox_a.collide_reg(hurtbox_b)
        collide_proj = hitbox_a.collide_proj(hurtbox_b)
        collide_grab = hitbox_a.collide_grab(hurtbox_b)

        # Looks a little spaghetti, I know. However, this is actually intended.
        # For example, say a character_a shoots a projectile while character_b
        # is shielding. On the frame the projectile hits character_b's shield,
        # it breaks and character_a grabs on that frame. Then, it make sense
        # that character_a would grab character_b.
        if collide_reg is not None:
            GameEngine.hit_dir(char_a, char_b)
            char_a.deal_hit(char_b, collide_reg)
        if collide_proj is not None:
            GameEngine.hit_dir(char_a, char_b)
            char_a.deal_hit(char_b, collide_proj)
        if collide_grab is not None:
            char_a.deal_hit(char_b, collide_grab)
        return True
