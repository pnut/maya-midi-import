import maya.cmds as mc
import os.path as osp
try:
    import umidiparser
except Exception as e:
    mc.confirmDialog(annotation="Error", message="Please follow the instructions in the README to install the umidiparser library.", button="OK")

class MayaMidiImport():
    def __init__(self):
        # set default values for the UI
        self.midi_filepath = ""           # path to midi file
        self.attack_frames = 2            # number of frames for a note-on attack
        self.decay_frames = 1             # number of frames for a note-on decay
        self.sustain_factor = 0.8         # scale factor for a sustained note
        self.release_frames = 2           # number of frames for a note-off release
        self.min_velocity_scale = 0.1     # the scale of a cube when a note is off
        self.max_velocity_scale = 4.0     # the max scale of a cube when a note is hit. actual scale will depend on note-on velocity
        self.pitch_translation = 2.0      # max amount of translation (positive or negative) for pitch bends
        
    def get_note_cube_name(self, channel, note):
        return self.get_channel_group_name(channel) + f"_note{str(note).zfill(3)}"

    def get_channel_group_name(self, channel):
        return f"midiChannel{str(channel).zfill(2)}"

    def get_fps(self):
        "Return Maya scene's current frame rate in frames per second"
        fps_map = { "game": 15.0,
                    "film": 24.0,
                    "pal": 25.0,
                    "ntsc": 30.0,
                    "show": 48.0,
                    "palf": 50.0,
                    "ntscf": 60.0 }
        
        curr_unit = mc.currentUnit(query=True, time=True)
        if curr_unit in fps_map:
            return fps_map[curr_unit]
        else:
            return float(curr_unit.replace("fps", ""))
        
    def create_note_cube(self, channel, note, channel_group, note_index, min_velocity_scale):
        """
        Create a cube to represent a note.

        :param channel: number of the channel the note belongs to
        :param note: number of the note
        :param channel_group: transform node the cube should be parented under
        :param note_index: the index of the note
        :param min_velocity_scale: the scale that should be applied to the cube when the note is off
        """
        cube_name = mc.polyCube(name=self.get_note_cube_name(channel, note), width=1, depth=1, height=1)[0]
        mc.move(0, -0.5, 0, cube_name + ".scalePivot", cube_name + ".rotatePivot", relative=True)
        mc.move(note_index, 0.5, 0, cube_name, absolute=True)
        mc.scale(1, min_velocity_scale, 1, cube_name, absolute=True)
        mc.parent(cube_name, channel_group)

    def delete_midi_nodes(self, *args):
        """
        Delete all transform nodes and display layers that start with 'midiChannel'
        """
        mc.delete(mc.ls("midiChannel*", transforms=True))
        mc.delete(mc.ls("midiChannel*", type="displayLayer"))
        
    def import_midi(self,
                    midi_filepath,
                    attack_frames = 2,
                    decay_frames = 1,
                    sustain_factor = 0.8,
                    release_frames = 2,
                    round_frames=True,
                    min_velocity_scale=0.1,
                    max_velocity_scale=4.0,
                    pitch_translation=2.0,
                    create_display_layers=True):
        """
        Import midi file and create animated cubes
        """
        if not midi_filepath:
            mc.error(f"No Midi file specified!")
            return
        
        if not osp.isfile(midi_filepath):
            mc.error(f"File '{midi_filepath}' not found!")
            return

        fps = self.get_fps()
        try:
            midi_file = umidiparser.MidiFile(midi_filepath)
        except Exception as e:
            mc.error("Error encountered while parsing midi file.")
            print(e)
        channel_notes = {}

        # populate the channel_notes dictionary with lists of notes that are played for each channel
        for event in midi_file:
            if event.status == umidiparser.NOTE_ON or event.status == umidiparser.NOTE_OFF:
                if event.channel not in channel_notes:
                    channel_notes[event.channel] = []
                if event.note not in channel_notes[event.channel]:
                    channel_notes[event.channel].append(event.note)
        
        # create groups and cubes to represent channels and notes
        # if create_display_layers is true, also create a display layer for each channel
        curr_channel_index = 0
        for channel, notes in channel_notes.items():
            if len(notes) > 0:
                notes.sort()
                group_name = mc.group(name=self.get_channel_group_name(channel), empty=True)
                
                for idx, note in enumerate(notes):
                    self.create_note_cube(channel, note, group_name, idx, min_velocity_scale=min_velocity_scale)
                mc.move(0, 0, curr_channel_index, group_name, absolute=True)
                if create_display_layers:
                    mc.select(group_name, replace=True)
                    mc.createDisplayLayer(name=self.get_channel_group_name(channel) + "_displayLayer")
                curr_channel_index += 1
        mc.select(clear=True)
        
        # iterate through all events in the midi file and animate the cubes and groups
        curr_frame = 0.0
        for event in midi_file:
            curr_frame += (event.delta_us / 1000000.0) * fps
            frame_to_use = curr_frame
            if round_frames:
                frame_to_use = round(frame_to_use)
            if event.status == umidiparser.NOTE_ON or event.status == umidiparser.NOTE_OFF:
                cube_node = self.get_note_cube_name(event.channel, event.note)
                mc.currentTime(frame_to_use)
                if event.status == umidiparser.NOTE_ON and event.velocity > 0:
                    attack_scale = (event.velocity / 127.0) * max_velocity_scale
                    sustain_scale = attack_scale * sustain_factor
                    mc.setKeyframe(cube_node, attribute='scaleY', t=frame_to_use)
                    mc.cutKey(cube_node, clear=True, time=(frame_to_use+0.01, None), attribute='scaleY', option="keys")
                    mc.setKeyframe(cube_node, attribute='scaleY', v=attack_scale, t=frame_to_use+attack_frames)
                    mc.setKeyframe(cube_node, attribute='scaleY', v=sustain_scale, t=frame_to_use+attack_frames+decay_frames)
                else:
                    mc.setKeyframe(cube_node, attribute='scaleY', t=frame_to_use)
                    mc.cutKey(cube_node, clear=True, time=(frame_to_use+0.01, None), attribute='scaleY', option="keys")
                    mc.setKeyframe(cube_node, attribute='scaleY', v=min_velocity_scale, t=frame_to_use + release_frames)
            elif event.status == umidiparser.PITCHWHEEL:
                translation = (event.pitch / 8191.0) * pitch_translation
                group_name = self.get_channel_group_name(event.channel)
                mc.currentTime(frame_to_use-1)
                mc.setKeyframe(group_name, attribute='translateY')
                mc.currentTime(frame_to_use)
                mc.setKeyframe(group_name, attribute='translateY', v=translation)

        mc.playbackOptions(minTime=0.0, 
                           maxTime=round(curr_frame))
    
    def get_file_from_dialog(self, *args):
        return_val = mc.fileDialog2(cap='Choose Midi File', fm=1, fileFilter='Midi Files (*.mid *.midi)')
        if return_val != None:
            mc.textField(self.midi_file_field, edit=True, text=return_val[0])
    
    def import_midi_from_ui(self, *args):
        self.import_midi(midi_filepath=mc.textField(self.midi_file_field, query=True, text=True),
                            attack_frames=mc.floatField(self.attack_frames_field, query=True, value=True),
                            decay_frames=mc.floatField(self.decay_frames_field, query=True, value=True),
                            sustain_factor=mc.floatField(self.sustain_factor_field, query=True, value=True),
                            release_frames=mc.floatField(self.release_frames_field, query=True, value=True),
                            min_velocity_scale=mc.floatField(self.min_velocity_scale_field, query=True, value=True),
                            max_velocity_scale=mc.floatField(self.max_velocity_scale_field, query=True, value=True),
                            pitch_translation=mc.floatField(self.max_pitch_translation_field, query=True, value=True),
                            create_display_layers=mc.checkBox(self.display_layers_checkbox, query=True, value=True))
    
    def show_ui(self):
        """
        Create Midi Import UI
        """
        if mc.window("MayaMidiImportWindow", query=True, exists=True):
            mc.deleteUI("MayaMidiImportWindow", window=True)
        self.win = mc.window("MayaMidiImportWindow", title="Midi Import", widthHeight=(350,235), sizeable=False)
        mc.columnLayout()
        mc.rowLayout(numberOfColumns=3)
        mc.text(label="Midi File", width=150, al="right")
        self.midi_file_field = mc.textField(width=100, text=self.midi_filepath)
        mc.button(label="Browse...", command = self.get_file_from_dialog, width=75)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Attack Frames", width=150, al="right")
        self.attack_frames_field = mc.floatField(width=100, annotation="Number of frames for a note-on attack.", value=self.attack_frames, tze=False, step=10)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Decay Frames", width=150, al="right")
        self.decay_frames_field = mc.floatField(width=100, annotation="Number of frames for a note-on decay.", value=self.decay_frames, tze=False, step=10)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Sustain Factor", width=150, al="right")
        self.sustain_factor_field = mc.floatField(width=100, annotation="Scale factor for a sustained note.", value=self.sustain_factor, tze=False, step=0.1)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Release Frames", width=150, al="right")
        self.release_frames_field = mc.floatField(width=100, annotation="Number of frames for a note-off release.", value=self.release_frames, tze=False, step=10)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Min Velocity Scale", width=150, al="right")
        self.min_velocity_scale_field = mc.floatField(width=100, annotation="The scale of a cube when a note is off.", value=self.min_velocity_scale, tze=False, step=0.1)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Max Velocity Scale", width=150, al="right")
        self.max_velocity_scale_field = mc.floatField(width=100, annotation="The max scale of a cube when a note is hit.\nActual scale will depend on note-on velocity.", value=self.max_velocity_scale, tze=False, step=0.1)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        mc.text(label="Max Pitch Translation", width=150, al="right")
        self.max_pitch_translation_field = mc.floatField(width=100, annotation="Max amount of translation (positive or negative) for pitch bends.", value=self.pitch_translation, tze=False, step=0.1)
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=2)
        self.display_layers_checkbox = mc.text(width=50, label="")
        self.display_layers_checkbox = mc.checkBox(label='Create display layers for midi channels', value=1, al="right")
        mc.setParent("..")
        mc.rowLayout(numberOfColumns=3)
        mc.button(label="Import Midi", command=self.import_midi_from_ui, width=115)
        mc.button(label="Clear Scene", command=self.delete_midi_nodes, width=115)
        mc.button(label="Close", command='mc.deleteUI(\"' + self.win + '\", window=True)', width=115)
        mc.setParent("..")
        mc.showWindow(self.win)

midi_importer = MayaMidiImport()
midi_importer.show_ui()
