import os
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
            song_dirs = glob(song_dir_pattern)
            for song_dir in song_dirs:
                sample_files = glob(os.path.join(song_dir, "*.wav"))
                sample_paths.extend(sample_files)
    return sample_paths

# function to run the identify script on the selected sample and return the result
def run_identify_script(database_file, sample_file):
    command = [sys.executable, 'identify.py', '-d', database_file, '-i', sample_file]
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    if result.stderr:
        output += result.stderr
    return output

# function to extract the identified song name from the script output
def extract_song_name(output):
    print("Output from identify.py:", output) 
    for line in output.split('\n'):
        if "best match:" in line.lower():
            return line.split(":")[1].strip().split()[0]
    return None

# function to extract the expected song name from the file path
def extract_expected_song_name(sample_file):
    base_name = os.path.basename(sample_file)
    return '_'.join(base_name.split('_')[1:-2])

# function to calculate accuracy for a given directory
def calculate_accuracy(base_dir, database_file, results_file):
    sample_paths = gather_sample_paths([base_dir])
    if sample_paths:
        total_samples = len(sample_paths)
        correct_identifications = 0
        for sample in sample_paths:
            print(f"testing sample: {sample}")
            output = run_identify_script(database_file, sample)
            identified_song = extract_song_name(output)
            expected_song = extract_expected_song_name(sample)
            print(f"expected: {expected_song}, identified: {identified_song}") 
            if identified_song and expected_song in identified_song:
                correct_identifications += 1
            else:
                print(f"incorrect identification! expected: {expected_song}, got: {identified_song}")
        accuracy = (correct_identifications / total_samples) * 100
        accuracy_result = f"accuracy for {base_dir}: {accuracy:.2f}%\n"
        print(accuracy_result)
        
        with open(results_file, 'a') as f:
            f.write(accuracy_result)
    else:
        no_samples_message = f"no sample files found in {base_dir}.\n"
        print(no_samples_message)
        with open(results_file, 'a') as f:
            f.write(no_samples_message)

# main execution
database_file = "database.pkl"
results_file = "accuracy_results.txt"

# clear previous results file content
with open(results_file, 'w') as f:
    f.write("")

for base_dir in base_dirs:
    calculate_accuracy(base_dir, database_file, results_file)
