import tkinter as tk
from tkinter import filedialog
import pyaudio
import wave
import threading
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os
import pygame

# Function to list available microphones
def list_microphones():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []
    for i in range(0, num_devices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            devices.append((i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
    p.terminate()
    return devices

# Function to record audio
def record_audio(mic_index, filename, stop_event, delay_ms):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    input_device_index=mic_index,
                    frames_per_buffer=1024)
    
    frames = []
    while not stop_event.is_set():
        data = stream.read(1024)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    # Convert WAV to MP3
    sound = AudioSegment.from_wav(filename)

    # Remove the first x ms
    if delay_ms > 0:
        print("applying ", delay_ms, "ms delay")
        sound = sound[int(delay_ms*44100/1000):]
    
    sound.export(filename.replace('.wav', '.mp3'), format="mp3")
    print("done exporting")

# Function to play video and record audio
def play_and_record(video_path, mic_index, delay_ms):
    print("video path: ", video_path)
    stop_event = threading.Event()
    
    # Start recording in a separate thread
    audio_filename = os.path.join(os.path.dirname(video_path), "user_sang.wav")
    record_thread = threading.Thread(target=record_audio, args=(mic_index, audio_filename, stop_event, delay_ms))
    
    # Play video
    video = VideoFileClip(video_path)

    record_thread.start()
    video.preview(fps=30, fullscreen=True)
    video.close()
    pygame.quit()
    
    # Stop recording
    stop_event.set()
    record_thread.join()
    f = open(video_path+".do", "a")
    f.write("please judge")
    f.close()

    print("recording and playback done")

# GUI for selecting the microphone and video file
def select_mic_and_play(video_path):
    devices = list_microphones()
    
    def start_recording():
        selected_mic = mic_listbox.curselection()
        delay_ms = int(delay_entry.get())
        if selected_mic:
            mic_index = devices[selected_mic[0]][0]
            # video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
            if video_path:
                play_and_record(video_path, mic_index, delay_ms)
                root.quit()
                root.destroy()
    
    root = tk.Tk()
    root.title("Select Microphone")
    
    mic_listbox = tk.Listbox(root)
    for i, device in enumerate(devices):
        mic_listbox.insert(i, device[1])
    mic_listbox.pack()

    delay_label = tk.Label(root, text="Input delay (ms):")
    delay_label.pack()
    
    delay_entry = tk.Entry(root)
    delay_entry.pack()
    delay_entry.insert(0, "0")  # Default delay is 0 ms
    
    start_button = tk.Button(root, text="Start Recording", command=start_recording)
    start_button.pack()
    
    root.mainloop()

# Run the GUI
# select_mic_and_play()
