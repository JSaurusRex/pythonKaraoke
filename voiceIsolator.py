import os
import sys
from spleeter.separator import Separator
import yt_dlp
import shutil
import glob

def filterName(name):
    name = name.replace(' ', '')
    name = name.replace('-', '')
    name = name.replace('|', '')
    name = name.replace('[', '')
    name = name.replace(']', '')
    return name

def download_mp3(youtube_url, output_directory):
    video_opts = {
       'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # Ensure the format is MP4
        'merge_output_format': 'mp4',  # Ensure the final file is in MP4 format
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'verbose': True,
    }

    with yt_dlp.YoutubeDL(video_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        video_title = info_dict.get('title', None)
        
        # Create a directory named after the video title
        folder_name = filterName(video_title)
        output_path = os.path.join(output_directory, folder_name)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Update the output template to include the new folder
        video_opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
        
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([youtube_url])
        
        File = ""
        for file in glob.glob(output_path+"/*.mp4"):
            File = file
        
        os.rename(File, output_path+"/original.mp4")

    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'verbose': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        video_title = info_dict.get('title', None)
        
        # Create a directory named after the video title
        folder_name = filterName(video_title)
        output_path = os.path.join(output_directory, folder_name)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        ydl_opts_audio['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
        
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([youtube_url])
        
        File = ""
        print(output_path+"/*.mp3")
        for file in glob.glob(output_path+"/*.mp3"):
            File = file
        
        os.rename(File, output_path+"/original.mp3")
        return output_path

def isolate_vocals(input_file, output_dir, used_ytdl):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize the Spleeter separator with 2stems (vocals + accompaniment)
    separator = Separator('spleeter:2stems')

    # Perform the separation
    separator.separate_to_file(input_file, output_dir)

    folderName = output_dir + "/" + os.path.splitext(os.path.basename(input_file))[0]

    # if yt_dlp:
        # folderName = output_dir + "/"
    
    # print("folder name ", folderName)
    os.rename(folderName+"/vocals.wav", output_dir+"/vocals.wav")

    print(f"Vocals and accompaniment saved to directory: {output_dir}")


def run(arg1):
    input_file = arg1

    output_dir = "Songs/"

    used_ytdl = False

    if "http" in input_file:
        #is youtube link
        dir = download_mp3(input_file, output_dir)
        input_file = dir + "/original.mp3"
        output_dir = dir
        used_ytdl = True
    else:
        output_dir += os.path.splitext(os.path.basename(input_file))[0] + "Folder"
    
    print("output directory ", output_dir)
    print("input file ", input_file)

    if not os.path.isfile(input_file):
        print(f"Error: The file {input_file} does not exist.")
        sys.exit(1)

    isolate_vocals(input_file, output_dir, used_ytdl)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python isolate_vocals.py <input_mp3_file / http>")
        sys.exit(1)
    
    run(sys.argv[1])

    
