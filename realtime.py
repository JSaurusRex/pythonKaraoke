import numpy as np
import sounddevice as sd
import librosa
import pygame
import threading
import queue
from scipy.signal import spectrogram
import os

# Constants
SAMPLE_RATE = int(44100/1)
FRAME_SIZE = 1024*(2^6)
DURATION = 30  # Total duration to display in seconds
DISPLAY_DURATION = 5  
BUFFER_SIZE = SAMPLE_RATE * DISPLAY_DURATION

# Queue for handling audio data
audio_queue_play = queue.Queue()
audio_queue_rec = queue.Queue()

# Circular buffers for audio data
played_buffer = np.zeros(BUFFER_SIZE)
recorded_buffer = np.zeros(BUFFER_SIZE)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Real-time Spectrogram")
font = pygame.font.SysFont("Arial", 24)

# Function to play MP3 audio using librosa
def play_audio(file_path):
    audio_data, _ = librosa.load(file_path, sr=SAMPLE_RATE)
    sd.play(audio_data, samplerate=SAMPLE_RATE, device=16)

    data_length = len(audio_data)

    for start in range(0, data_length, FRAME_SIZE):
        end = start + FRAME_SIZE
        if end > data_length:
            end = data_length
        chunk = audio_data[start:end]
        audio_queue_rec.put(chunk)
        sd.sleep(int(1000 * len(chunk) / SAMPLE_RATE))  # Wait for the duration of the chunk


    sd.wait()  # Wait for the playback to finish

# Function to record audio from the microphone
def record_audio():
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_queue_play.put(indata.copy())

    with sd.InputStream(callback=callback, device=16, channels=1, samplerate=SAMPLE_RATE, blocksize=FRAME_SIZE):
        sd.sleep(DURATION * 1000)

# Function to calculate and return the spectrogram as a surface
def create_spectrogram_surface(data, sample_rate):
    dataCopy = np.copy(data)[len(data)-BUFFER_SIZE:]
    freqs, times, Sxx = spectrogram(dataCopy, fs=sample_rate, nperseg=1024, noverlap=512)
    Sxx = np.log(Sxx + 1e-10)  # Log scale
    Sxx = np.divide(Sxx, 80.0)
    Sxx = np.add(Sxx, 1)
    Sxx = np.pow(Sxx, 2)
    Sxx = np.multiply(Sxx, 80.0)

    # Sxx = np.flipud(Sxx)  # Flip to display lower frequencies at the bottom
    # Sxx = np.rot90(Sxx)
    surface = pygame.surfarray.make_surface(Sxx)
    surface = pygame.transform.rotate(surface, 90)
    surface = pygame.transform.flip(surface, True, False)
    return surface

# Function to update and display the spectrograms
def display_spectrogram():
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not audio_queue_rec.empty():
            new_data_rec = audio_queue_rec.get().flatten()
            n_rec = len(new_data_rec)

            new_data_play = audio_queue_play.get().flatten()
            n_play = len(new_data_play)

            # Update played buffer with simulated data (replace with actual playback data if needed)
            played_buffer[:] = np.roll(played_buffer, -n_play)
            played_buffer[-n_play:] = new_data_play

            # Update recorded buffer
            recorded_buffer[:] = np.roll(recorded_buffer, -n_rec)
            recorded_buffer[-n_rec:] = new_data_rec

            # Create and display spectrogram surfaces
            played_surf = create_spectrogram_surface(played_buffer, SAMPLE_RATE)
            recorded_surf = create_spectrogram_surface(recorded_buffer, SAMPLE_RATE)

            screen.blit(pygame.transform.scale(played_surf, (800, 300)), (0, 0))
            screen.blit(pygame.transform.scale(recorded_surf, (800, 300)), (0, 300))

            pygame.display.flip()
        
        pygame.time.wait(10)  # Wait for 10 milliseconds to reduce CPU usage

    pygame.quit()

# Main function
def main(mp3_file):
    # Start audio playback in a separate thread
    audio_thread = threading.Thread(target=play_audio, args=(mp3_file,))
    audio_thread.start()

    # Start recording in a separate thread
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

    # Start the spectrogram display
    display_spectrogram()

    print("sys exit")
    if os.name == 'nt':
        os._exit()
    else:
        os.kill(os.getpid(), 9)

    # audio_thread.join()
    # record_thread.join()

if __name__ == "__main__":
    mp3_file = 'unravel/original.mp3'  # Replace with the path to your MP3 file
    main(mp3_file)
