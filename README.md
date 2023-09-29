# maya-midi-import
This Maya python script imports midi files into Autodesk Maya and converts their note events into keyframes applied to cubes. Each cube represents a note in a particular channel and its Y scale is animated when the note is played and released. Pitch bend events will animate the Y translation of the cubes for an entire channel. All the cubes for a given channel will be placed in their own display layer. The amount the cubes are scaled and translated, as well as the timing of the attack, decay and release of notes, can be customized using a UI.
## Requirements
* Maya 2023 or higher
* Has been tested on Mac OS 13.5.1
## Example Output
Importing the `example/pachelbel.mid` into Maya and playing back the animation along with `example/pachelbel.mp3` yields the following results (turn on sound). 

https://github.com/pnut/maya-midi-import/assets/1393462/d5312608-c43e-451f-bf0f-265b08097b95
## Instructions
1. Install `umidiparser` in your Maya Python environment by running the following command in your Terminal (on Windows the Terminal needs to be run in [admin mode](https://learn.microsoft.com/en-us/windows/terminal/faq#how-do-i-run-a-shell-in-windows-terminal-in-administrator-mode). If you're using a later version than Maya 2023, replace the Maya path to reflect the version you're using:
##### Mac OS
```
/Applications/Autodesk/maya2023/Maya.app/Contents/bin/mayapy -m pip install umidiparser
```
##### Windows
```
"C:\Program Files\Autodesk\Maya2023\bin\mayapy" -m pip install umidiparser
```
You should see the message `Successfully installed umidiparser-1.2`.

2. Open a new instance of Maya and set the the desired frame rate for your scene (Windows->Settings/Preferences->Preferences->Time Slider).

3. Paste the contents of `maya_midi_import.py` into Maya's Script Editor (Python tab).

4. Select all the text of the script and run it by pressing Ctrl+Return (Windows) or Cmd+Return (Mac OS).

5. Using the window that pops up, input your desired options (see `Options` section below) and click on the `Import Midi` button. Larger midi files may take some minutes to finish importing.

6. If you want to run the script again with different options, start with a fresh scene before re-running the script, or click on the `Clear Scene` button to remove all midi-related nodes from your scene.

## Options
<img width="352" alt="Screenshot 2023-09-24 at 9 47 07 PM" src="https://github.com/pnut/maya-midi-import/assets/1393462/709104e2-7ba9-4530-a842-1bac3725b2c7">

* <b>Midi File</b> - a full path to the midi file you want to import.

* <b>Min Velocity Scale</b> - the Y scale a cube should have when its note is completely off

* <b>Max Velocity Scale</b> - the Y scale a cube reaches during the initial "attack" phase of a note is dependent on the velocity with which the note is hit. This value represents the maxiimum scale it can reach, when the note is hit with maximum velocity.

* <b>Attack Frames</b> - the number of frames for a cube to reach its attack scale.

* <b>Decay Frames</b> - the number of frames for a cube to reach its "sustain" scale, after its attack phase.

* <b>Sustain Factor</b> - the Y scale factor that should be applied to a cube while a note is being sustained. This factor will be multiplied with the attack scale, which is dependent on the velocity of the note.

* <b>Release Frames</b> - the number of frames a cube should take to reach `min_velocity_scale` after it is released.

* <b>Max Pitch Translation</b> - the maximum amount of units in the positive or negative Y direction that cubes should be translated when the pitch of their channel is bent up or down.

* <b>Create display layers for midi channels</b> - whether or not to place the cubes for each channel in their own display layer.

## About
`maya-midi-import` developed by Paris Mavroidis

`umidiparser` developed by Hermann Paul von Borries https://github.com/bixb922/umidiparser
