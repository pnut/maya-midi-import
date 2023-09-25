# maya-midi-import
This Maya python script imports midi files into Autodesk Maya and converts their note events into keyframes applied to cubes. Each cube represents a note in a particular channel and its Y scale is animated when the note is played and released. Pitch bend events will animate the Y translation of the cubes for an entire channel. All the cubes for a given channel will be placed in their own display layer.
## Requirements
* Maya 2022 or higher
* Has been tested on Mac OS 13.5.1
## Instructions
1. Install `umidiparser` into your Maya Python environment by running the following command in your terminal or console. If you're not using Maya 2022, replace the Maya path to reflect the version you're using:
##### Mac OS
```
/Applications/Autodesk/maya2022/Maya.app/Contents/bin/mayapy -m pip install umidiparser
```
##### Windows
```
"C:\Program Files\Autodesk\Maya2022\bin\mayapy" -m pip install umidiparser
```
You should see the message `Successfully installed umidiparser-1.2`.

2. Open a new instance of Maya and set the the desired frame rate for your scene (Windows->Settings/Preferences->Preferences->Time Slider).

3. Paste the contents of `maya_midi_import.py` into Maya's Script Editor (Python tab).

4. Select all the text of the script and run it by pressing Ctrl+Return (Windows) or Cmd+Return (Mac OS).

5. Using the window that pops up, input your desired options (see `Options` section below) and click on the `Import Midi` button. Larger midi files may take some minutes to finish importing.

6. If you want to run the script again with different options, start with a fresh scene before re-running the script, or click on the `Clear Scene` button to remove all midi-related nodes from your scene.

## Options
* <b>Midi File</b> - a full path to the midi file you want to import.

* <b>Min Velocity Scale</b> - the Y scale a cube should have when its note is completely off

* <b>Max Velocity Scale</b> - the Y scale a cube reaches during the initial "attack" phase of a note is dependent on the velocity with which the note is hit. This value represents the maxiimum scale it can reach, when the note is hit with maximum velocity.

* <b>Attack Frames</b> - the number of frames for a cube to reach its attack scale.

* <b>Decay Frames</b> - the number of frames for a cube to reach its "sustain" scale, after its attack phase.

* <b>Sustain Factor</b> - the Y scale factor that should be applied to a cube while a note is being sustained. This factor will be multiplied with the attack scale, which is dependent on the velocity of the note.

* <b>Release Frames</b> - the number of frames a cube should take to reach `min_velocity_scale` after it is released.

* <b>Max Pitch Translation</b> - the maximum amount of units in the positive or negative Y direction that cubes should be translated when the pitch of their channel is bent up or down.

## About
`maya-midi-import` developed by Paris Mavroidis

`umidiparser` developed by Hermann Paul von Borries https://github.com/bixb922/umidiparser