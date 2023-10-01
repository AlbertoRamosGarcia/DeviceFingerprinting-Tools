# Stimulated Microcontroller Dataset for New IoT Device Identification Schemes through On-Chip Sensor Monitoring

En this repository, the scripts are provided for manipulating the dataset (available on **Zenodo**) to construct subsets in multiple formats and options. These subsets are generated from readings collected from on-chip sensors of various electronic devices during the execution of different workloads. The aim is to train models capable of uniquely identifying these devices based on their behavior.

Access to the dataset at [Zenodo](https://doi.org/tobe.fulfilled/zenodo.tbd).

Additionally, the requirements for utilizing these scripts, the specifics of their functionalities, and recommended practices for adapting the employed workflow and extending its usage are detailed here.

 All materials, including the dataset, have been published for open access and free use under the GNU GPL v3 software license.
 
## Dataset and Data shape

The MOSID (Microcontroller On-chip Sensor IDentification) dataset consists of 5 acquired data subsets, each collected during different experiments and periods using various equipment (HMP4040, DF1731SB & HM305) and acquisition strategies. These subsets contain readings from the temperature and voltage sensors embedded in 20 STM32L-DISCOVERY devices. The data was captured during the execution of 5 different workloads as stimuli, repeated over 20 iterations. The stimuli employed are as follows:

1. 20x20 Long-type matrix product.
2. 20x20 Float-type matrix product.
3. Algorithm for ascending sorting, Bubble Sort.
4. Algorithm for 2D-point clustering, Convex Hull.
5. Encryption algorithm AES 128-bit

The subsets are structured according to the folder format "X_Y," where X is the manually assigned number to the board, and Y is the corresponding number for the executed algorithm. Within each of these folders, files are present in the format "data_Z.txt," where Z represents the iteration number to which the file belongs. In total, the dataset comprises 9600 files with a final size of approximately 7 GB. The different presented subsets are as follows:

- **ACQ1**: Derived from the experiment named "Automatic Acquisition 1 (HMP4040)" conducted from 24/10/22 (ending on 26/10/22), using a daisy-chain topology (20 out of 20 boards, 2000 files). 
- **ACQ2**: Derived from the experiment named "Automatic Acquisition 2 (HMP4040)" conducted from 27/10/22 (ending on 29/10/22), using a daisy-chain topology (20 out of 20 boards, 2000 files). 
- **ACQ3**: Derived from the experiment named "Individual Acquisitions (HMP4040)" conducted on 30/06/23 (ending on 13/07/23), performed board by board from idle conditions (20 out of 20 boards, 2000 files). 
- **ACQ4**: Derived from the experiment named "GOLD SOURCE DF1731SB Acquisitions" conducted from 13/07/23 (ending on 27/09/23), using a partial daisy-chain setup (2 devices at a time, 18 out of 20 boards, 1800 files). 
- **ACQ5**: Derived from the experiment named "HANMATEK HM305 Acquisitions" conducted from 13/07/23 (ending on 27/09/23), using a partial daisy-chain setup (2 devices at a time, 18 out of 20 boards, 1800 files).

In each "data_Z.txt" file, starting from the 5th line, temperature and voltage values are provided, captured during the execution of the stimulus in successive lines. Additionally, a table (Table_UIDS.csv) with metadata for each of the boards used in the experiments is included, which is of great relevance for their use and study.

|BOARD_NUM|BITS [95:64]|BITS [63:32]|BITS [31: 0]|T_CAL_1|T_CAL_2|VREFINT_CAL|
|--|--|--|--|--|--|--|

## Requirements

As mentioned in the initial description of this repository, it is a necessary condition to adhere to the specified format:

-   The directories for the data of the devices under test must be organized in the "X_Y" format, where X is the manually assigned board number, and Y corresponds to the number assigned to a specific stimulus under which the data was collected.
    
-   The generated data files should be in the .txt format, with temperature and voltage sensor data appearing on each line. The files should be named "data_Z.txt," where Z represents the iteration number of the stimulus for which the data was collected.
    
-   Additionally, if normalization is required (in the case where the sensor ADC conversions are acquired without conversion), it is possible as long as the values are present in a "Table_UIDs.csv" table with headers matching the fields:
	- `BOARD_NUM`, which contains the manually assigned board number.
	- `T_CAL_1`, which holds the calibration value of the board's temperature sensor at 30ºC.
	- `T_CAL_2`, which holds the calibration value of the board's temperature sensor at 100ºC.
	- `VREFINT_CAL`, which contains the calibration value of the board's voltage sensor.

In case of needing to adapt the scripts for a greater or lesser number of sensors or a different format, they can be easily modified according to the new requirements. It is crucial to consider (if applicable) the new dimensions of the "Table_UIDs.csv" and modify or add the conversion equations for values obtained from the sensors, as well as the labels defined in the `fields` variable.

	fields = ["Voltage Value", "Temperature Value", "Board Number", "Algorithm", "Iteration"]

Prior to running the scripts, it will be necessary to import the following libraries:
 - pandas
 - tqdm
 - numpy
 - h5py

#	SCRIPT #1 : DataBuilder	
To handle the dataset and adapt it for subsequent machine learning studies and projects, this script has been developed, encompassing the following options:

1. Select the output CSV file(s) format (Unified/Multiple).
2. Choose which algorithm to discard in the generated file.
3. Choose which board to discard in the generated file.
4. Select a downsampling factor to apply to the data (disabled by default).
5. Conversion of acquired values into Temperature (ºC) and Voltage (V).
6. Generate File(s).

The chosen configuration will be displayed to the right of each option in the selection menu.

The user should modify the variables `boards`, `algorithms`, and `iterations` with the maximum values desired to use for these elements. Similarly, the paths for the base directory (where the folders with the data are located) and the destination directory for the output files must be specified.

#	SCRIPT #2 : Sequencer

This script allows the construction of sequences of pairs of Temperature-Voltage values of a desired length along with their corresponding board label to facilitate the study of using fixed sequences for the identification of devices based on their electronic activity and through the use of artificial intelligence.

The script explores CSV files *which should have been generated in a multiple format* located in the directory specified in `folder` and will generate sequences with the length specified in the `sequence_length` variable as it iterates through all the files it finds. As a result, an HDF5 file is generated for each board, containing the generated sequences and their respective labels for later use.

It is worth noting that since the main objective of the script is to generate training/validation/test sets for various models, as an intermediate step before creating .hdf5 files, Z-score Data Normalization is performed on the temperature and voltage values. If this is not desired, it is recommended to comment out the indicated part of the `save_sequences_to_hdf5` function where these operations are performed and replace the `normalized_data` variable with `data_array` in the lines of that same function.

