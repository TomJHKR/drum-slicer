# Drum Slicer Application

## Overview
The Drum Slicer Application allows users to load a `.wav` file, slice it into smaller audio segments, and play those segments in a loop. 

The application provides a GUI where users can interact with the slices, play or stop the audio, and shuffle the slices randomly or arrange the slices using a set of radio buttons in the interface.

This application is built using Python with `Tkinter` for the GUI, `pyaudio` for audio playback, and `wave` for handling audio files.

## Features
- **Slice control**: The audio file is sliced into 16 smaller segments. Each slice can be played in a loop.
- **Play/Stop**: Play or stop the audio loop with a single click.
- **Randomize**: Randomize the order of the slices.
- **Interactive GUI**: Select slices using a grid of radio buttons.
  
## Requirements
- Python 3.x
- `pyaudio`: Used for playing audio.
- `wave`: Used for processing `.wav` files.
- `ttkbootstrap`: Provides advanced styling for Tkinter widgets.

You can install the required dependencies using the following command:

```bash
pip install pyaudio ttkbootstrap
```

## Usage

1. **Run the Application**: The application is run by executing the Python script `main.py`.

2. **Play the Audio**: Click on the **Play** button in the GUI to start the audio playback. The slices will be played in a loop until stopped.

3. **Stop the Audio**: Click on the **Stop** button to stop the audio playback at any time.

4. **Randomize the Slices**: Click on the **Random** button to randomize the order of the slices. The slices are shuffled and can be played in the randomized order.

5. **Slice Selection**: The radio buttons in the GUI allow you to control the order of the slices. You can select which slice will be played using these buttons.

## How It Works

The main component of the application is the `WavePlayerLoop` class, which is responsible for:
- Slicing the `.wav` file into smaller segments based on the number of slices.
- Playing the slices in a loop with the option to randomize the order.
- Handling playback in a separate thread so that the application can continue to run while the audio is playing.

The `GUIObject` class is responsible for rendering the graphical user interface, handling user interactions like button presses, and controlling the audio playback via the `WavePlayerLoop`.

## Future Enhancements
- Add support for more audio formats (e.g., MP3, FLAC).
- Visualize the waveform of the audio.
- Implement additional audio effects like pitch-shifting or tempo-changing.
- Selecting amount of slices/beats

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
