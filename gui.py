import tkinter as tk
from tkinter import ttk
import os

import voiceIsolator
import karaoke_game
import test
import signal
import sys
import threading

# Sample data for files and their information

def load_songs():
    songs = {}
    dirs = os.listdir("Songs/")
    for dir in dirs:
        print(dir)
    
        score = -999
        file = "Songs/"+dir+"/score.txt"
        if os.path.isfile(file):
            with open(file) as f:
                score = float(f.readline())

        songs[dir] = score
    return songs


def execute_function_with_filename(filename):
    print(f"Function executed with: {filename}")
    karaoke_game.select_mic_and_play("Songs/"+filename+"/original.mp4")
    
    if not os.path.isfile("Songs/"+filename+"/original.mp4.do"):
        return
    print("begining with judgement")
    score = test.plot_spectrogram("Songs/"+filename+"/vocals.wav", "Songs/"+filename+"/user_sang.mp3")
    if files_data[filename] >= score:
        return
    f = open("Songs/"+filename+"/score.txt", "a")
    f.write(str(score))
    f.close()
    files_data[filename] = score

def download_function(url):
    print(f"Downloading from: {url}")
    voiceIsolator.run(url)
    global files_data
    files_data = load_songs()

def update_file_list(filter_text=""):
    listbox.delete(0, tk.END)
    for file in files_data:
        if filter_text.lower() in file.lower():
            listbox.insert(tk.END, file)

def on_file_select(event):
    selected_file = listbox.get(listbox.curselection())
    info_label.config(text=files_data[selected_file])
    execute_function_with_filename(selected_file)

def on_filter_change(*args):
    filter_text = filter_var.get()
    update_file_list(filter_text)

def on_download_button_click():
    url = download_entry.get()
    threading.Thread(target=download_function, args=(url,)).start()

signal.signal(signal.SIGINT, signal.SIG_DFL)


if __name__ == "__main__":
    print("name of thread ", __name__)
    files_data = load_songs()
    # Create the main window
    root = tk.Tk()
    root.title("File Selector")

    # Create a frame for the listbox and scrollbar
    listbox_frame = ttk.Frame(root)
    listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create the listbox
    listbox = tk.Listbox(listbox_frame, height=10)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar for the listbox
    scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    # Display extra information label
    info_label = ttk.Label(root, text="Select a file to see more information", wraplength=300)
    info_label.pack(padx=10, pady=5)

    # Create a text bar for filtering files
    filter_var = tk.StringVar()
    filter_var.trace_add("write", on_filter_change)
    filter_entry = ttk.Entry(root, textvariable=filter_var)
    filter_entry.pack(fill=tk.X, padx=10, pady=5)
    filter_entry.insert(0, "Filter files")

    # Create a frame for the download section
    download_frame = ttk.Frame(root)
    download_frame.pack(fill=tk.X, padx=10, pady=10)

    # Create a text bar for download URL
    download_entry = ttk.Entry(download_frame)
    download_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Create a download button
    download_button = ttk.Button(download_frame, text="Download", command=on_download_button_click)
    download_button.pack(side=tk.LEFT, padx=5)

    # Populate the listbox with initial data
    update_file_list()

    # Bind the listbox selection event
    listbox.bind("<<ListboxSelect>>", on_file_select)

    # Run the application
    root.mainloop()
