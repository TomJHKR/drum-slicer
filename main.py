import os
import time
import wave
import shutil
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

    ## Class Init
    # filepath = filepath of sample
    # loop = loop boolean wether to loop or not
    def __init__(self,filepath,gui,loop=True,num_slices=16):
        super(WavePlayerLoop, self).__init__()
        self.gui = gui
        self.filepath = os.path.abspath(filepath)
        self.loop = loop
        self.num_slices = num_slices
        self.audio_length = self.get_audio_length()
        self.slice_duration = self.audio_length / self.num_slices
        self.current_order = list(range(self.num_slices))
        self.running = threading.Event()
        self.running.set()
        self.default_order = [i for i in range(self.num_slices)]

    ## Function to aid in the math for slicing
    def get_audio_length(self):
        # Open the wave file
        with wave.open(self.filepath, 'rb') as wf:
            num_frames = wf.getnframes()
            frame_rate = wf.getframerate()
            return num_frames / float(frame_rate)


    def run(self):
        print("Running")
        print(self.gui)
        with wave.open(self.filepath, 'rb') as wf:
            player = pyaudio.PyAudio()
            stream = player.open(
                format=player.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            while self.loop:
                for col,slice_index in enumerate(self.current_order):
                    if self.gui:
                        self.gui.highlight_current(col)
                    if not self.running.is_set():
                        break
                    start_time = slice_index * self.slice_duration
                    start_frame = int(start_time * wf.getframerate())
                    wf.setpos(start_frame)
                    frames_to_read = int(self.slice_duration * wf.getframerate())
                    self.play_slice(wf, stream, frames_to_read)
                    if not self.loop:
                        break
            stream.stop_stream()
            stream.close()
            player.terminate()

    def play_slice(self, wf, stream, frames_to_read):
        while frames_to_read > 0 and self.running.is_set():
            data = wf.readframes(min(self.CHUNK, frames_to_read))
            if not data:
                break
            stream.write(data)
            frames_to_read -= self.CHUNK

    ## Play 
    def play(self):
        self.start()

    ## Stop - removes tempdir if exits
    def stop(self):
        self.running.clear()
        self.loop = False
        if self.is_alive():
            self.join()
    

    ## Randomise the slice order
    def random(self,gui):
        random_array = [random.randint(0, self.num_slices - 1) for _ in range(self.num_slices)]
        self.current_order = random_array
        gui.update_slice_order(self.current_order)

        


## Tkinter class for the GUI
class GUIObject:
    

    def __init__(self, tkObject):
        self.master = tkObject  # Store Tk instance for later use
        #self.setup_styles()
        self.player = WavePlayerLoop("bassport_amen.wav", self,loop=True)
        self.master.style = ttk.Style()
        self.master.style.theme_use("superhero")

        ##
        self.num_slices = self.player.num_slices
        

        # Label to show GUI content
        self.label = ttk.Label(self.master, text="Slice Control")
        self.label.pack(pady=10)

        self.slice_boxes = ttk.Entry(self.master)
        self.slice_boxes.insert(0, str(self.num_slices))  # Pre-fill with the default value
        self.slice_boxes.pack(pady=10)

        # Button to update the number of slices
        self.update_button = ttk.Button(self.master, text="Update Slices", command=self.update_slices)
        self.update_button.pack(pady=10)

        # Play button will call the 'play' method of master (WavePlayerLoop)
        self.play_button = ttk.Button(self.master, text="Play", command=self.play, bootstyle="success")
        self.play_button.pack(pady=10)

        # Stop button will call the 'stop' method of master (WavePlayerLoop)
        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop, bootstyle="danger")
        self.stop_button.pack(pady=10)

        # Randomise button
        self.random_button = ttk.Button(self.master, text="Random",command=self.random, bootstyle="primary")
        self.random_button.pack(pady=10)

        # Create the grid of radio buttons
        self.radio_vars = [
            IntVar(value=(col % self.num_slices) + 1) for col in range(self.num_slices)
        ]
        self.create_radio_grid()

        # Store the current player instance
        self.player = None

    def update_slices(self):
        # Get the new number of slices from the Entry widget
        try:
            new_num_slices = int(self.slice_boxes.get())
            if new_num_slices != self.num_slices:
                self.num_slices = new_num_slices
                #self.player.num_slices = self.num_slices
                self.radio_vars = [
                    IntVar(value=(col % self.num_slices) + 1) for col in range(self.num_slices)
                ]
                self.create_radio_grid()
                self.play(new_num_slices)

        except ValueError:
            print("Please enter a valid number.")

    def setup_styles(self):
        # Configure the style for the selected state of the radio buttons
        self.master.style.configure("TRadiobutton", background="#D1D8E0")
        self.master.style.configure("TRadioutton.selected", background="#6D9EC1", foreground="white")
        self.master.style.configure("TRadiobutton.highlighted", background="#FFFF99", foreground="white") 
    ## Play button for GUI to call play method in song
    # Will also create new song object
    def play(self,num_slices=16):
        if self.player is None or not self.player.is_alive():
            self.player = WavePlayerLoop("bassport_amen.wav",self, loop=True,num_slices=num_slices)
            self.player.play()
            self.update_slice_order(self.player.default_order)
        else:
            print("Already playing.")
    ## As above
    def stop(self):
        if self.player:
            self.player.stop()
            print("Audio stopped.")

    ## As above
    def random(self):
        self.player.random(self)


    def rand_helper(self,grid):
        for i, rad in enumerate(self.radio_vars):
            rad.set(grid[i]) 

    def create_radio_grid(self):
        if hasattr(self, 'grid_frame'):
            self.grid_frame.destroy()

        grid_frame = ttk.LabelFrame(self.master, text="Select Slices:", padding=10)
        grid_frame.pack(pady=10)
        self.radio_buttons = []

        for col in range(self.num_slices):
            
            # Add a label for each column
            Label(grid_frame, text=f"{col + 1}").grid(row=0, column=col)
            #separator = ttk.Separator(grid_frame, orient=VERTICAL)
            #separator.grid(row=0, column=col, rowspan=self.num_slices, sticky="nsw", padx=5)
     
            # Create radio buttons for each row in the column
            for row in range(self.num_slices, 0, -1):
                rb = ttk.Radiobutton(
                    grid_frame,
                    variable=self.radio_vars[col],
                    value=row,
                    #indicatoron=True,
                    #borderwidth=0,
                    #relief="flat",
                    command=lambda c=col: self.update_slice_order_from_gui(c),
                )
                rb.grid(row=self.num_slices - row + 1, column=col, sticky="w",pady=1,padx=5)
                self.radio_buttons.append(rb)
                  # Add a separator after each column except the last one
            self.grid_frame = grid_frame

    def on_radio_select(self, col):
        selected_row = self.radio_vars[col].get()
        self.player.slices[col] = selected_row

    def update_slice_order_from_gui(self, col):
        self.player.current_order = [var.get() - 1 for var in self.radio_vars]

    def update_slice_order(self, new_order):
        for i, new_val in enumerate(new_order):
            self.radio_vars[i].set(new_val + 1)

    def highlight_current(self,col):
        label = self.grid_frame.grid_slaves(row=0,column=col)[0]
        label.config(fg="black",bg="#FFFF99")
        prev = 0
        if col < self.num_slices and col > 0:
            prev = col - 1
        elif col == 0:
            prev = self.num_slices-1
        elif col == self.num_slices:
            prev = 0
        label2 = self.grid_frame.grid_slaves(row=0,column=prev)[0]
        label2.config(fg="white",bg="#2b3e50")
     
        

def main():
    #player = WavePlayerLoop("bassport_amen.wav", loop=True)
    root = Tk()
    gui = GUIObject(root)
    root.mainloop()


if __name__ == "__main__":
    main()
