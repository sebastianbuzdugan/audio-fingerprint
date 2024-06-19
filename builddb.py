import os
import sys
import scipy.io.wavfile as wavfile
import pickle
import warnings
import time
from matplotlib import mlab
import numpy as np
import hashlib

# constants for fingerprinting
AUDIO_SAMPLE_RATE = 44100  # sample rate of audio files
FFT_WINDOW_SIZE = 2**12  # reduced size of the FFT window
HASH_TARGET_ZONE = 8  # moderate number of points for combinatorial hashing
PEAK_BLOCK_SIZE = 30  # moderate size of blocks to search for peaks


def create_fingerprints(channel):
    """generate fingerprints for an audio channel"""
    window_overlap = int(FFT_WINDOW_SIZE * 0.5)
    spectrogram, freqs, times = mlab.specgram(channel, NFFT=FFT_WINDOW_SIZE, Fs=AUDIO_SAMPLE_RATE, window=mlab.window_hanning, noverlap=window_overlap)
    spectrogram = 10 * np.log10(spectrogram)
    spectrogram[spectrogram == -np.inf] = 0
    peak_points = find_peaks(spectrogram, freqs, times)
    hashes, offsets = hash_peaks(peak_points)
    return hashes, offsets

def find_peaks(spectrogram, freqs, times):
    """find peaks in the spectrogram"""
    peak_points = []
    for i in range(0, len(times), PEAK_BLOCK_SIZE):
        for j in range(0, len(freqs), PEAK_BLOCK_SIZE):
            block_amplitudes = spectrogram[j:j+PEAK_BLOCK_SIZE, i:i+PEAK_BLOCK_SIZE]
            max_amplitude = np.max(block_amplitudes)
            indices = np.where(block_amplitudes == max_amplitude)
            if indices[0].size > 0 and indices[1].size > 0:
                max_freq = freqs[j + indices[0][0]]
                max_time = times[i + indices[1][0]]
                peak_points.append((max_freq, max_time))
    return peak_points

def hash_peaks(peak_points):
    """hash the peak points"""
    hashes = []
    offsets = []
    for i in range(len(peak_points)):
        for j in range(1, HASH_TARGET_ZONE):
            if (i + j) < len(peak_points):
                time1 = peak_points[i][1]
                time2 = peak_points[i + j][1]
                freq1 = peak_points[i][0]
                freq2 = peak_points[i + j][0]
                t_delta = time2 - time1
                string_to_hash = f"{freq1}|{freq2}|{t_delta}"
                offsets.append(time1)
                hashes.append(hashlib.sha256(string_to_hash.encode()).hexdigest())
    return hashes, offsets

# main script execution
if len(sys.argv) != 5:
    print("usage: python builddb.py -i <songs-folder> -o <database-file>")
    sys.exit(1)

input_folder = sys.argv[2]
output_file = sys.argv[4]

print(f'building database from songs in: {input_folder}')
print(f'database will be saved as: {output_file}\n')

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning)

# initialize the database dictionary
database = {}

start_time = time.time()

# get the list of files and the total number of files
files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]
total_files = len(files)

# process each .wav file in the input directory
for index, filename in enumerate(files):
    audio_file = os.path.join(input_folder, filename)
    song_name = filename[4:-4].replace(" ", "_")
    print(f"processing: {song_name} ({index + 1}/{total_files})")
    _, channels = wavfile.read(audio_file)
    hashes_LR = []
    offsets_LR = []
    for chan in range(2):
        hashes, offsets = create_fingerprints(channels[:, chan])
        hashes_LR.extend(hashes)
        offsets_LR.extend(offsets)
    for i in range(len(hashes_LR)):
        if hashes_LR[i] not in database:
            database[hashes_LR[i]] = []
        database[hashes_LR[i]].append((offsets_LR[i], song_name))
    
    # show the progress
    progress = (index + 1) / total_files * 100
    print(f"progress: {progress:.2f}%")

# save the database to a file
with open(output_file, 'wb') as f:
    pickle.dump(database, f)

end_time = time.time()
print(f"database creation completed in {end_time - start_time:.2f} seconds.")
print("all songs have been fingerprinted and stored in the database.")
