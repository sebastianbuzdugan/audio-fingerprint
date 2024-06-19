import sys
import warnings
import scipy.io.wavfile as wavfile
import pickle
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
    """Find peaks in the spectrogram"""
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

def load_database(filename):
    """load the fingerprint database from a file"""
    with open(filename, 'rb') as f:
        database = pickle.load(f)
    return database

def search_matches(database, hashes):
    """search for song matches in the database based on hashes"""
    matches = []
    for hash_value in hashes:
        if hash_value in database:
            matches.extend(database[hash_value])
    return matches

# main script is executed
if len(sys.argv) != 5:
    print("usage: python identify.py -d <database-file> -i <sample>")
    sys.exit(1)

db_file = sys.argv[2]
input_file = sys.argv[4]

print(f'database file: {db_file}')
print(f'input file: {input_file}')

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning)

start_time = time.time()

# load the database
database = load_database(db_file)

# read the input audio file and generate fingerprints
_, channels = wavfile.read(input_file)

hashes_LR = []
offsets_LR = []

print(f"\ncreating fingerprint for: {input_file}...")
for chan in range(2):
    hashes, offsets = create_fingerprints(channels[:, chan])
    hashes_LR.extend(hashes)
    offsets_LR.extend(offsets)

print("searching for matches...")
matches = search_matches(database, hashes_LR)

# to calculate relative offsets
hashes_dict = {hash_value: offsets_LR[i] for i, hash_value in enumerate(hashes_LR)}
relative_offsets = [(song_name, offset - hashes_dict[hash_value]) for hash_value, (offset, song_name) in zip(hashes_LR, matches) if hash_value in hashes_dict]
print(f"possible hash matches: {len(relative_offsets)}")

# find the best match
candidates = {}
for song_name, offset in relative_offsets:
    if song_name not in candidates:
        candidates[song_name] = {}
    if offset not in candidates[song_name]:
        candidates[song_name][offset] = 0
    candidates[song_name][offset] += 1

max_count = 0
best_match = None
for song_name, offsets in candidates.items():
    for offset, count in offsets.items():
        if count > max_count:
            max_count = count
            best_match = song_name

end_time = time.time()
elapsed_time = end_time - start_time

print(f"\nbest match: {best_match} with {max_count} matches")
print(f"recognition time: {elapsed_time:.2f} seconds")

if best_match and input_file.__contains__(best_match):
    print("\ncorrect identification of the sample!")
else:
    print("\nincorrect identification! :-(")
