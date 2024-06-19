# Installation and Setup
Download and install Python 3.x from python.org. (I use Python 3.8.10)
Use pip to install the necessary packages:

```
pip install scipy numpy matplotlib
```

## Commands and Usage

### Building the Database

To build the database, use the following command:

```
python builddb.py -i <path_to_audio_library> -o <database_file>
```

Example:
```
python builddb.py -i C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\audio_library -o database.pkl
```

This command processes each .wav file in the specified folder (audio_library), generates fingerprints, and stores them in a database file (database.pkl).

### Identifying Audio Samples

To identify a sample, use the following command:

```
python identify.py -d <database_file> -i <sample_file>
```

Example:
```
python identify.py -d database.pkl -i C:\Users\sbuzdugan\Desktop\me\audioFingerprinting\audio_samples\clean_samples\01_Bourgade_samples\01_Bourgade_4.wav
```

This command reads the sample audio file, generates fingerprints, and matches them against the fingerprints stored in the database to identify the song.

### Testing a Random Sample

```
python random_test.py
```

The random_test.py script selects a random sample from the available audio samples and runs the identify script on it

### Calculating Accuracy

```
python accuracy_test.py
```

The accuracy_test.py script tests all samples in the specified directories, compares the identified song with the expected song, and calculates the accuracy of the system. It outputs the accuracy for each category of samples and stores the results in a file.
