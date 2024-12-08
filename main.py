import os
import time
import wave
import shutil
import tempfile
import threading
import sys

import pyaudio
import random

from tkinter import Tk, Label, Button,Radiobutton, IntVar, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
  
"""
  A simple class based on PyAudio to play wave loop.
  It's a threading class. You can play audio while your application
  continues to do its stuff. :)
"""
class WavePlayerLoop(threading.Thread):


    CHUNK = 8192

    def __init__(self,filepath,loop=True):
        super(WavePlayerLoop, self).__init__()
        self.filepath = os.path.abspath(filepath)
        self.loop = loop
        self.temp_dir = tempfile.mkdtemp()
        self.slices = self.slice_audio(16)
        self.beats = len(self.slices)

    def slice_audio(self, num_slices):
        """
        Slice the audio into `num_slices` parts and save them in a temporary directory.
        """
        slices = []
        with wave.open(self.filepath, 'rb') as wf:
            # Get audio properties
            num_frames = wf.getnframes()
            framerate = wf.getframerate()
            duration = num_frames / float(framerate)

            slice_duration = duration / num_slices
            slice_frames = int(slice_duration * framerate)

            # Split the audio into slices
            for i in range(num_slices):
                # Set the start and end frames for each slice
                start_frame = i * slice_frames
                end_frame = (i + 1) * slice_frames if i < num_slices - 1 else num_frames

                # Create a new wave file for this slice
                slice_filepath = os.path.join(self.temp_dir, f"{i+1}.wav")
                wf.setpos(start_frame)
                frames = wf.readframes(end_frame - start_frame)

                with wave.open(slice_filepath, 'wb') as slice_wf:
                    slice_wf.setnchannels(wf.getnchannels())
                    slice_wf.setsampwidth(wf.getsampwidth())
                    slice_wf.setframerate(wf.getframerate())
                    slice_wf.writeframes(frames)
                print(i+1)
                slices.append(i+1)

        return slices

    def run(self):
        """
        Play the audio slices in sequence, looping if self.loop is True.
        """
        player = pyaudio.PyAudio()

        while self.loop:  # Infinite loop if self.loop is True
            for slice in self.slices:
                if not self.loop:
                    break

                path = os.path.join(self.temp_dir, f"{slice}.wav")
                if not os.path.exists(path):  # Check if slice exists
                    print(f"Slice file missing: {path}")
                    continue


                wf = wave.open(path, 'rb')

                # Open Output Stream
                stream = player.open(format=player.get_format_from_width(wf.getsampwidth()),
                                     channels=wf.getnchannels(),
                                     rate=wf.getframerate(),
                                     output=True)

                try:
                    # Read and play the frames
                    data = wf.readframes(self.CHUNK)
                    while data and self.loop:
                        stream.write(data)
                        data = wf.readframes(self.CHUNK)
                finally:
                    # Ensure proper cleanup of resources
                    stream.stop_stream()
                    stream.close()
                    wf.close()

        player.terminate()

    def play(self):
        print("playing")
        self.start()

    def stop(self):
        self.loop = False
        if self.is_alive():
            self.join()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def random(self,mast):
        random.shuffle(self.slices)
        mast.rand_helper(self.slices)

        

    def get_audio_length(self):
        # Open the wave file
        with wave.open(self.filepath, 'rb') as wf:
            # Get the number of frames and the frame rate
            num_frames = wf.getnframes()
            frame_rate = wf.getframerate()
            
            # Calculate the duration of the audio in seconds
            duration = num_frames / float(frame_rate)
            
            return duration
    
class GUIObject:
    def __init__(self, tkObject, master):
        self.master = master  # Assign master to access methods like play/stop
        self.master.tk = tkObject  # Store Tk instance for later use
        self.num_slices = 16
        self.num_slicers = 16
        
        self.master.tk.style = ttk.Style()
        self.master.tk.style.theme_use("superhero")

        # Label to show GUI content
        self.label = ttk.Label(self.master.tk, text="Slice Control")
        self.label.pack(pady=10)



        # Play button will call the 'play' method of master (WavePlayerLoop)
        self.play_button = ttk.Button(self.master.tk, text="Play", command=self.play, bootstyle="success")
        self.play_button.pack(pady=10)

        # Stop button will call the 'stop' method of master (WavePlayerLoop)
        self.stop_button = ttk.Button(self.master.tk, text="Stop", command=self.stop, bootstyle="danger")
        self.stop_button.pack(pady=10)

        # Randomise button
        self.random_button = ttk.Button(self.master.tk, text="Random",command=self.random, bootstyle="primary")
        self.random_button.pack(pady=10)

         # Create the grid of radio buttons
        self.radio_vars = [
            IntVar(value=(col % self.num_slicers) + 1) for col in range(self.num_slices)
        ]
        self.create_radio_grid()

        # Store the current player instance
        self.player = None
    def setup_styles(self):
        # Configure the style for the selected state of the radio buttons
        self.master.tk.style.configure("TButton", background="#D1D8E0")
        self.master.tk.style.configure("TButton.selected", background="#6D9EC1", foreground="white")

    def play(self):
        if self.player is None or not self.player.is_alive():
            self.player = WavePlayerLoop("bassport_amen.wav", loop=True)
            self.player.play()
        else:
            print("Already playing.")

    def stop(self):
        if self.player:
            self.player.stop()
            print("Audio stopped.")

    def random(self):
        self.player.random(self)

    def rand_helper(self,grid):
        print(self.radio_vars)
        for i, rad in enumerate(self.radio_vars):
            rad.set(grid[i]) 

    def create_radio_grid(self):
        """Create a grid of radio buttons."""
        grid_frame = ttk.LabelFrame(self.master.tk, text="Select Slices:", padding=10)
        grid_frame.pack(pady=10)

        for col in range(self.num_slices):
            # Add a label for each column
            Label(grid_frame, text=f"{col + 1}").grid(row=0, column=col)

            # Create radio buttons for each row in the column
            for row in range(self.num_slicers, 0, -1):
                rb = Radiobutton(
                    grid_frame,
                    variable=self.radio_vars[col],
                    value=row,
                    indicatoron=True,
                    command=lambda c=col: self.on_radio_select(c),
                )
                rb.grid(row=self.num_slicers - row + 1, column=col, sticky="w",pady=2)

    def on_radio_select(self, col):
        selected_row = self.radio_vars[col].get()
        self.player.slices[col] = selected_row
        print(f"Column {col + 1}, selected Row: {selected_row}")


def main():
    player = WavePlayerLoop("bassport_amen.wav", loop=True)
    print(player.get_audio_length())
    root = Tk()
    gui = GUIObject(root, player)
    player.tk.mainloop()


if __name__ == "__main__":
    main()
