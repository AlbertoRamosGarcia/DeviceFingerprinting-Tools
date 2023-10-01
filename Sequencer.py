import os
import csv
import pandas as pd
from tqdm import tqdm
import time
import re
import numpy as np
import h5py


###########################################################
#                                                         #
#   Configuration for the Generation of Sequences BEGIN   #   
#                                                         #
###########################################################

# Base directory where the folder containing the data(in Multiple .CSV format) are located.
folder = "DiskUnit:/path/to/Data's/Folder"

# List with the maximum number of pairs of T-V samples per algorithm.
max_pair_samples = [79600, 79600, 100000, 70000, 12000] # number of pairs of samples per algorithm, in checking order:
# A1_SIZE = 159200
# A2_SIZE = 159200
# A3_SIZE = 200000
# A4_SIZE = 140000
# A5_SIZE = 24000

# Define the sequence length
sequence_length = 100

###########################################################
#                                                         #
#   Configuration for the Generation of Sequences END     #   
#                                                         #
###########################################################


# Initialize the global sequences list
sequences = []

current_board = 1

# Define a regular expression pattern to extract the X, Y, and Z values
pattern = r'(\d+)_(\d+)_(\d+)\.csv'

# Function to read and process a CSV file
def process_csv_file(file_path, max_samples):
    global sequences
    
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')  # Specify the delimiter
        sequence = []
        sample_count = 0  # Initialize a counter for the samples processed
        for row in csv_reader:
            voltage = float(row['Voltage Value'])
            temperature = float(row['Temperature Value'])
            pair = [voltage, temperature]
            sequence.append(pair)
            sample_count += 1  # Increment the sample count
            
            if len(sequence) == sequence_length:
                sequences.append(sequence)
                sequence = []
                
            # Check if we have reached max_samples
            if sample_count >= max_samples:
                break

# Function to normalize (Z-score normalization) save sequences to an HDF5 file for a specific board
def save_sequences_to_hdf5(board, data):
    file_name = f'board_{board}_sequences.h5'
    with h5py.File(file_name, 'w') as hdf_file:
        data_array = np.array(data)
        
        # Z-score Data Normalization BEGIN
        voltages = data_array[:, :, 0]
        temperatures = data_array[:, :, 1]

        mean_volt = np.mean(voltages)
        std_volt = np.std(voltages)
        mean_temp = np.mean(temperatures)
        std_temp = np.std(temperatures)
        
        normalized_voltages = (voltages - mean_volt) / std_volt
        normalized_temperatures = (temperatures - mean_temp) / std_temp

        normalized_data = np.dstack((normalized_voltages, normalized_temperatures))
        # Z-score Data Normalization  END
        
        # Create Indexes for training dataset
        indexes = [board] * len(normalized_data)
        # Include in hdf5 file
        hdf_file.create_dataset('sequences', data = normalized_data)
        hdf_file.create_dataset('indexes', data = indexes)
        
        print(f"\nFile {file_name} has been created\n")


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Get the list of files in the folder
files = os.listdir(folder)

# Sort the list of files based on the X_Y_Z criteria
sorted_files = sorted(files, key=lambda x: tuple(map(int, re.search(pattern, x).groups())))

# Iterate through the sorted files and get the Y value
for file in sorted_files:
    x, y, z = map(int, re.search(pattern, file).groups())
    max_samples = max_pair_samples[y - 1]  # Adjust for 0-based indexing
    
    if x != current_board:
        save_sequences_to_hdf5(current_board, sequences)
        sequences = []
    
    file_path = os.path.join(folder, file)
    print(f"\nFilepath: {file_path}")
    process_csv_file(file_path, max_samples)
    
    current_board = x

# Ensure Last Board sequence file is generated
if(sequences):
    save_sequences_to_hdf5(current_board, sequences)
    sequences = []