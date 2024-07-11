import os
import sys
from spleeter.separator import Separator

def isolate_vocals(input_file, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize the Spleeter separator with 2stems (vocals + accompaniment)
    separator = Separator('spleeter:2stems')

    # Perform the separation
    separator.separate_to_file(input_file, output_dir)

    print(f"Vocals and accompaniment saved to directory: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python isolate_vocals.py <input_mp3_file> <output_directory>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: The file {input_file} does not exist.")
        sys.exit(1)

    isolate_vocals(input_file, output_dir)
