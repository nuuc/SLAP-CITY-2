# SUPER SLAM BROTHERS: JAM
## Table of contents

[Changelog](#changelog)

[Task List](#task-list)

## Changelog

### July 06, 2019
  - Created a temporary 'phrog' dbpk file in character_info, accessed through hard-code in characters, to test the ability to access database pickle files.
  - Added squatting to the game, as well as squatting to trigger the check to drop through platforms.
  - Added some animations into the 'phrog' dbpk file, including ftilt, walk, startsquat, airborne, jumpsquat
  - The generic character update is (hopefully) more accessible now, with many action state/env state specific updates being handled within a group of helper functions, keycoded by a '\_h' before the helper handler function name.
  - Update hurtbox now updates hurtbox dynamically based on action state.
  - Partly redesigned controller_handler: five new classes.
   - The InputMapping class provides the functionality to map different buttons, as well as gives a name to the mapping.
   - The Controller class is an abstract superclass meant to abstractify Keyboard and Joystick inputs. Its function is to provide an abstract representation of a controller.
     - It has three class attributes: button_list which contains button inputs from the last ten frames, button_mapping which is an InputMapping object containing information about the button mapping for a Controller object and an unimplemented options attribute, which will contain information regarding tap jump, tilt on cstick, etc.
     - It has three functions: an abstract update method, a get_button method, and get_button_change method.
   - The Joystick class inherits from Controller, meant to be used for Joystick inputs such as Gamecube Controllers, Xbox Controllers, etc.
     - It has three extra class attributes: joystick_id, axis_list, and axis_mapping.
     - It implements the abstract update method and has five new method, with two of them being static. get_angle returns the angle between a point and the origin in radians. axis_mapper takes in a point and dead zone and maps it to five possible different locations. get_axis takes in an axis and returns the value of the axis on the current frame. get_axes takes in either 'control' or 'cstick' and returns a tuple of length two of the values of the axes according to the input. map_axes takes in either 'control' or 'cstick' and maps and returns the axes accordingly.
   - The Keyboard class inherits from Controller, meant to be used for Keyboard inputs.
     - It has two extra class attributes: vaxis_list and vaxis_mapping.
     - It implements the abstract update function and has one new function. get_vaxis takes in an 'axis' and returns the value for that axis on the current frame (only return values are 0 and 1)
   - The ControllerHandler class initializes with a character-control map dictionary of {Controller: Character} and a button-mapping map to map which controller maps to which button mapping.
     - It has one method, which is to handle the controls based on what type of Controller it is, and although unimplemented, it will handle also based on the Controller options

### July 03, 2019
 - Made some minor changes to characters (a full redesign is still needed).
  - character.misc_data -> character.data
  - Attributes such as character.invincible, character.jumped, character.damage were moved into character.data.
  - 'wavedashing' is reformatted as 'sliding'.
 - pklTreeView has new features and a small style update.
    - Buttons added to the right of the treeview, replacing the previous keyboard shortcuts).
    - Hovering over a row and column and pressing 'e' allows you to edit the corresponding key, type, value.
    - Pressing 'r' hard refreshes.
    - Selective select button added.
     - Enter in a keyword to search within the selected item for all occurrences of that keyword as a key.
    - Add entry button added with two features.
     - Regular add adds an item to the selected item.
     - Add to children adds an item to all children of the selected item (might encode positional update information within each frame, so this will be helpful).
    - Special edit button added.
     - Allows user to enter an equation such that the selected items values conform to that equation with values transformed to that equation based on the index (within the selected items) of the value as input. This is the only functionality of special edit currently, however, more will be added if needed.

### July 02, 2019
- Finished pklTreeView to have all intended features-more may be added as needed.
  - Functionality to edit
    - Copy parts of pkl files
    - Move parts of pkl files
    - Open and save pkl files
    - Edit values

## Task list

### Short term
#### July 02, 2019 - July 09 2019
- [x] ~~Finish pklTreeView~~ *Finished July 02, 2019*
- [ ] Redesign/reformat the game
  - [ ] Implement Meter
  - [ ] Reformat character update (with relation to the new pkl files)
  - [ ] Redo controls (keyboard support and better joystick mapping)
  - [ ] Reorganize misc_functions (and functions in general)
- [ ] Think about/create a framework for sprites
- [ ] Fix bugs in animator/make it more accessible

### Long term
- [ ] Implement better environment collision
- [ ] Implement camera
- [ ] Draw and animate characters
- [ ] Optimize runtime
- [ ] Add a menu
- [ ] Add new characters


