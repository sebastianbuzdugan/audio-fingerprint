import os
import random
import subprocess
import sys
from glob import glob

# base directories for the samples
base_dirs = [
    r'C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\audio_samples\noisy_samples',
    r'C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\audio_samples\noisy_filtered_samples',
    r'C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\audio_samples\filtered_samples',
    r'C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\audio_samples\clean_samples'
]

# function to gather all sample file paths
def gather_sample_paths(base_dirs):
    sample_paths = []
    for base_dir in base_dirs:
        for i in range(1, 41):  # for each song number from 01 to 40
            song_dir_pattern = os.path.join(base_dir, f"{i:02}_*")
            for song_dir in glob(song_dir_pattern):
                for j in range(5):  # for each sample number from 0 to 4
                    sample_file_pattern = os.path.join(song_dir, f"{i:02}_*_{j}.wav")
                    sample_files = glob(sample_file_pattern)
                    for sample_file in sample_files:
                        if os.path.isfile(sample_file):
                            sample_paths.append(sample_file)
    return sample_paths

# function to select a random sample
def select_random_sample(sample_paths):
    return random.choice(sample_paths)

# function to run the identify script on the selected sample
def run_identify_script(database_file, sample_file):
    command = [sys.executable, 'identify.py', '-d', database_file, '-i', sample_file]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

# main execution
if __name__ == "__main__":
    database_file = r"C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\database.pkl"
    sample_paths = gather_sample_paths(base_dirs)

    if sample_paths:
        random_sample = select_random_sample(sample_paths)
        print(f"Selected sample: {random_sample}")
        run_identify_script(database_file, random_sample)
    else:
        print("No sample files found.")
