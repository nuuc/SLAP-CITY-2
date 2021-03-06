# SUPER SLAM BROTHERS: JAM
## Table of contents

[Changelog](#changelog)

[Task List](#task-list)

## Changelog

## January 29, 2019
  I got lazy with finishing up the animator over the winter break, and I lost all momentum from doing that, so I've made more or less zero changes since the last time... On the other hand, while I was messing around with trying to mod Getting Over It, specifically understanding how the code structure works in Unity, I realized that I should just use a game engine to make this game so much easier. It was really dumb to try to create my own engine and handle all of the responsibilities that come with it. So, from now on, the updates will be in Unity, and as a promise to myself, I will at least try to make progress by spending at least an hour a week on the game, whether it be testing new mechanics out in Unity, or actually developing the game. I've created a Unity branch instead of just deleting/resetting this repository because I feel sentimental to all the code I've written, despite the oldest code being literal trash. For the time being, I'm messing around with understanding how Unity works so I can exactly implement my vision of Super Slam Brothers Jam in the future.

## December 06, 2019
  I forgot to update this for a while, but I have been working on updates. There's quite a lot of updates this time and I don't remember what was actually changed since last time, so I'll go over what I've been working on. I've mostly dedicated my work to the animator these days because that's necessary for pretty much everything in the game. Since I want to NOT spaghetti code it this time, it has taken quite a while to write, but I'd say it's about 60-70% complete, in terms of just functionality. Apart from that, I've worked a bit on character and environment, patching things up here and there. Additionally, I've since fixed the geometries file so that the SAT and MTV work correctly now, and I've even tested it a little bit using the geometries_debug file. So far, it seems to be fine, and even tunnelling should be accounted for with max speeds, but there is still a subcase of tunneling where an ECB can tunnel through the corner of a polygon. I'm aware that this can happen, but I'm too lazy to fix it, since at the end of the day, it causes very little issues and is a very isolated edge case. Anyways, I hope to finish animator and maybe even the data manager (previously named pklTreeView) by the end of this year. Progress is steady and what I expected it to be, but since I started late, we're still slightly behind.

## November 10, 2019
  First weekly update is here (in the experimental branch). I've actually managed to finish about 80% or so of what was in the game previously, but like I said before, restructured it in a much more robust manner. There are only a couple of things left to do, a lot of which can be considered 'grunt work' or something that's still undecided. The big things that have yet to be implemented are the control handler (specifically the control structure of the update loop) and the character action method (also to do with the control structure). Some other things left unfinished are the environment handler and the fact that the separating axis theorem and its minimum translation vector does not detect collision at high velocities. For example, if a character is travelling extremely fast, on one frame, they may be above the stage, and the next, they may be below the stage. Since there is no in-between frame for the SAT/MTV to detect, they'll fall right through the stage. This is a problem, albeit a small one that we'll have to address and fix in the future. For now though, I'll just leave it as a TODO.
  
  Anyways, progress is steady and although I can't work on this as much in the coming weeks since reading week is over for me, I can reasonably expect that I'll be finished the main structure of the game code by the end of November. I worked about 5 hours per day during the reading week, accomplishing (let's round down) 70%. Then, I'd need about 10 more hours to finish the rest of the code, which I can do with a consistent, steady commitment to finishing it.

## November 03, 2019
  Finally, updates have started coming out again. The reason for the extended break was mainly because the code we had written was not robust enough to support the features we wanted to implement. Now that we have a better idea of what the game is going to look like, we're rewriting pretty much everything as well as adding much, much more documentation for a better collaborative process. Additionally, I have created a partially finished design draft for the game in order to avoid the same mistakes as last time: spaghetti code. Admittedly, I'm working on the code even though the draft isn't finished, which may lead to problems, but I plan to work in parallel on the code and draft, sketching out what I want to do before I implement it. Currently, I'm still in the process of rebuilding the old code in a robust, well-documented manner, but I expect to be finished before December. Ideally, I would like to have a working development environment by then too, but no guarantees on that. 
  
  Additionally, although we plan to work on the code in Python, we plan on porting it over to C or C++ eventually because Python is easy to write and create prototypes in, but doesn't have the extensive features and control of other languages. Knowing that, it's important to consider Python specific features and if it would be easy to implement them in another language. I'm thinking specifically about data storage by pickling in Python and how (or if) that would be transferred to another language. I'm looking into serialization in C++ right now, but the method for data storage is still currently undecided.
  
   Anyways, I'll try to push out updates weekly and document what changes or features I've added, but for the most part, I probably won't go into detail too much about the changes I make for a while, since most of these updates will just be on reimplementing old features, and the design draft should cover all the features that will be in the game anyways (I'll add the draft to this page once it's almost done).


### July 09, 2019
  - Reimplemented engine's hit handler within the new framework.
  - Renamed a couple of functions to better reflect what they do.
  - Removed constructor parameters from Character and its inheritor's init.
  - Platform dropping now checks for an input on the last frame of initiating the squat animation.
    - Allows for squatting on platforms much more easily.

#### July 09, 2019 Notes
  - Did not meet this week's short term goals, however I plan on catching up next week, in addition to implementing all basic features.
  - Attempting to finish all of next week's shert term goals before I go on vacation.


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

### January 29, 2020
- [ ] Understand Unity mechanics better
  - [ ] Figure out components, their methods, properties, etc.
  - [ ] Learn tips and tricks to improve workflow
- [ ] Create an environmental handler
  - [ ] Make ECB scripts
  - [ ] Make ground/edge collision scripts


## Task list (Old)

I'm going to archive this within the README for sentimental purposes.

### Short term

#### July 09, 2019 - July 16, 2019
- [ ] Redesign/reformat the game
  - [ ] Implement Meter
  - [ ] Reformat character update (with relation to the new pkl files)
  - [ ] Redo controls (keyboard support and better joystick mapping)
  - [ ] Reorganize misc_functions (and functions in general)
- [ ] Think about/create a framework for sprites
- [ ] Fix bugs in animator/make it more accessible
- [ ] Implement all basic features in Dummy (ledge options, knockdown options, etc.)

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


