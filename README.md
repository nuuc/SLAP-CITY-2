# SLAP-CITY-2
## Table of contents

[Changelog](#changelog)

[Task List](#task-list)

## Changelog

 ### July 02, 2019
- Finished pklTreeView to have all intended features-more may be added as needed.
  - Functionality to edit
    - Copy parts of pkl files
    - Move parts of pkl files
    - Open and save pkl files
    - Edit values
    
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
     

## Task list

### Short term
#### July 02, 2019 - July 07 2019
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


