import os
import csv
import pandas as pd
from tqdm import tqdm
import time
import re


#################################################
#                                               #
#   Configuration for Dataset Generation BEGIN  #   
#                                               #
#################################################

# Base directory where the folders containing the data are located.
base_directory = "DiskUnit:/path/to/Data's/Folders"

destination_folder = "DiskUnit:/path/to/New/Data/Folder"

# The address of the CSV table with the sensor calibration values for the boards must be within the base_folder.
boards_data_table = "DiskUnit:/path/to/Data/Folder/Table_UIDS.csv"

# Maximum value for X and Y.
boards = 20      # Change this to the maximum value you desire for X (NUM_BOARDS).
algorithms = 5  # Change this to the maximum value you desire for Y (NUM_ALGTH)
iterations = 20  # Change this to the maximum value you desire for Z (NUM_DATOS)

# List with the maximum number of samples per algorithm.
max_samples = [159200, 159200, 200000, 140000, 24000] # number of samples per algorithm, in checking order:
# A1_SIZE = 159200
# A2_SIZE = 159200
# A3_SIZE = 200000
# A4_SIZE = 140000
# A5_SIZE = 24000

#################################################
#                                               #
#   Configuration for Dataset Generation END    #   
#                                               #
#################################################


# Counter to control the decimation.
pair_counter = 0  

# List of discarded algorithms.
discarded_algths = []
# List of discarded boards.
discarded_boards = []

# Name of the unified CSV file.
csv_filename_unified = f"raw_dataset_{boards}_{algorithms}_{iterations}.csv"

# List for storing data from all the files.
data = []

# Define the column labels.
fields = ["Voltage Value", "Temperature Value", "Board Number", "Algorithm", "Iteration"]

# Regular expression to extract numbers: 
pattern = r'\d+'

# "Discard Algorithms" Template
discard_algorithms_template = {
    "label": "Discard Algorithms", 
    "config_option": [], 
    "suboptions": [],
    "type": "multiple",
    "numeric": False
}

# "Discard Boards" Template
discard_boards_template = {
    "label": "Discard Boards", 
    "config_option": [], 
    "suboptions": [],
    "type": "multiple",
    "numeric": False
}

# To generate the "Discard Algorithms" section based on the number of algorithms
for i in range(1, algorithms + 1):
    algorithm = {
        "label": f"Algorithm {i}",
        "selected": False
    }
    discard_algorithms_template["suboptions"].append(algorithm)

# To generate the "Discard Boards" section based on the number of boards
for i in range(1, boards + 1):
    board = {
        "label": f"Board {i}",
        "selected": False
    }
    discard_boards_template["suboptions"].append(board)

#################################################################################################################################
#################################################################################################################################  


operation_accepted = False
config_format_option = []
config_algths_option = []
config_boards_option = []
config_decimation_option = []
config_normalize_option = []

# Create a list for each option and its selected configuration, along with the option type.
menu_options = [
    {"label": "Select Output Format", "config_option": ["Unified"], "suboptions": [
    {"label": "Unified", "selected": False},
    {"label": "Multiple Files", "selected": False}
    ], "type": "single", "numeric": False},
    # {"label": "Discard Algorithms", "config_option": [], "suboptions": [
        # # Comment or add new algoritm labels if needed according your application
        # {"label": "algorithm 1", "selected": False},
        # {"label": "algorithm 2", "selected": False},
        # {"label": "algorithm 3", "selected": False},
        # {"label": "algorithm 4", "selected": False},
        # {"label": "algorithm 5", "selected": False}
    # ], "type": "multiple", "numeric": False},
    # {"label": "Discard Boards", "config_option": [], "suboptions": [
        # # Comment or add new board labels if needed according your application
        # {"label": "Board 1", "selected": False},
        # {"label": "Board 2", "selected": False},
        # {"label": "Board 3", "selected": False},
        # {"label": "Board 4", "selected": False},
        # {"label": "Board 5", "selected": False},
        # {"label": "Board 6", "selected": False},
        # {"label": "Board 7", "selected": False},
        # {"label": "Board 8", "selected": False},
        # {"label": "Board 9", "selected": False},
        # {"label": "Board 10", "selected": False},
        # {"label": "Board 11", "selected": False},
        # {"label": "Board 12", "selected": False},
        # {"label": "Board 13", "selected": False},
        # {"label": "Board 14", "selected": False},
        # {"label": "Board 15", "selected": False},
        # {"label": "Board 16", "selected": False},
        # {"label": "Board 17", "selected": False},
        # {"label": "Board 18", "selected": False},
        # {"label": "Board 19", "selected": False},
        # {"label": "Board 20", "selected": False}
    # ], "type": "multiple", "numeric": False},
    {"label": "Decimation Factor", "config_option": [1], "suboptions": [], "type": "single", "numeric": True},
    {"label": "T-V Normalization", "config_option": [False], "suboptions": [], "type": "normalization", "numeric": False},
    {"label": "Generate File", "config_option": [], "suboptions": [], "type": "verification"}
]

# Add the generated parts in a specific location of the menu_options list
menu_options.insert(1, discard_algorithms_template)     # Insert "Discard Algorithms" at position 2 (Option 1 starts at 0)
menu_options.insert(2, discard_boards_template)         # Insert "Discard Boards" at position 3 (Option 1 starts at 0)

# Custom function to extract the number "Z" from the file name
def get_Z_number(file):
    try:
        number_Z = int(file.split("_")[1].split(".")[0])
        return number_Z
    except ValueError:
        return float('inf')  # Return infinity to handle files without a Z number


# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_main_menu():
    clear_screen()
    print("\n***********************************")
    print("**                               **")
    print("**     Raw Data Builder Menu     **")
    print("**                               **")
    print("***********************************\n")
    for index, option in enumerate(menu_options, start=1):
        label = option["label"]
        configuration = option["config_option"]
        type = option["type"]
        if type == "single":
            if configuration:
                value = configuration[0]
                if "numeric" in option:
                    print(f"{index}. {label} ({value})")
                else:
                    print(f"{index}. {label} ({value})")
            else:
                print(f"{index}. {label}")
        elif type == "multiple":
            suboptions = option["suboptions"]
            selected_sublabels = [suboption["label"] for suboption in suboptions if suboption['selected']] 
            if selected_sublabels:
            
                if(option == menu_options[1]):
                    config_algths_option.clear()
                    for element in selected_sublabels:
                        # Search for matches in the current element
                        match = re.search(pattern, element)
                        if match:
                            # Retrieve the found number and add it to the list
                            number = int(match.group())
                            config_algths_option.append(number)
                            
                if(option == menu_options[2]):
                    config_boards_option.clear()
                    for element in selected_sublabels:
                        # Search for matches in the current element
                        match = re.search(pattern, element)
                        if match:
                            # Obtain the found number and add it to the list
                            number = int(match.group())
                            config_boards_option.append(number)
                   
                sublabels_str = ", ".join(selected_sublabels)
                print(f"{index}. {label} ({sublabels_str})")
            else:
                print(f"{index}. {label}")
        elif type == "normalization":
            current_value = "Yes" if configuration[0] else "No"
            print(f"{index}. {label} ({current_value})")
        elif type == "verification":
            if all(configuration):
                print(f"{index}. {label} (Available)")
            else:
                print(f"{index}. {label} (Blocked)")

    print("0. Salir")
    
def check_option_6_available():
    option_6 = menu_options[5]  # "Option 6" is located at position 5 in the list
    return all(option_6["config_option"])

def submenu(option):
    current_option = menu_options[option]
    suboptions = current_option["suboptions"]
    type = current_option["type"]
    numeric = current_option["numeric"]
    
    while True:
        clear_screen()
        print(f"\n{current_option['label']} Submenu")
        print("\n--- Submenu ---\n")
        if type == "single":
            if numeric:
                print("Enter a value for the Decimation Factor:")
                print(f"Current Value: {current_option['config_option'][0]}")
            else:
                print("1. Unified")
                print("2. Multiple Files")
        elif type == "multiple":
            for index, suboption in enumerate(suboptions, start=1):
                marker = "[X]" if suboption["selected"] else "[ ]"
                print(f"{index}. {marker} {suboption['label']}")
        elif type == "normalization":
            current_value = "Yes" if current_option["config_option"][0] else "No"
            print(f"Current Value: {current_value}")
            print("1. Yes")
            print("2. No")
        print("0. Back to the main menu")
        
        if type == "single" and numeric:
            selection = input("\nNew value for the Decimation Factor: ")
            if selection == "0":
                clear_screen()
                print("Canceling the Decimation Factor modification...")
                break
            elif selection.isdigit():
                new_value = int(selection)
                if new_value >= 1:
                    current_option["config_option"] = [new_value]
                else:
                    clear_screen()
                    print("Invalid value. It must be greater than or equal to 1. Please try again.")
            else:
                clear_screen()
                print("Invalid input. It must be an integer.")
        elif type == "single" and not numeric:
            selection = input("\nSelect an option (1-2), 0 to go back): ")
            if selection == "0":
                break
            elif selection == "1":
                current_option["config_option"] = ["Unified"]
                break
            elif selection == "2":
                current_option["config_option"] = ["Multiple Files"]
                break
            else:
                clear_screen()
                print("Invalid option. Please select a valid option.")
        elif type == "normalization":
            selection = input("\nSelect an option for T-V Normalization (1:Yes, 2:No, 0 to go back): ")
            if selection == "0":
                break
            elif selection == "1":
                current_option["config_option"] = [True]
                break
            elif selection == "2":
                current_option["config_option"] = [False]
                break
            else:
                clear_screen()
                print("Invalid option. Please select 'Yes' or 'No'.")
        else:
            selection = input("\nSelect a Suboption: ")

            if selection == "0":
                clear_screen()
                print("Returning to the main menu...")
                break
            elif selection.isdigit():
                number_selection = int(selection)
                if 1 <= number_selection <= len(suboptions):
                    current_suboption = suboptions[number_selection - 1]
                    current_suboption["selected"] = not current_suboption["selected"]
                else:
                    clear_screen()
                    print("Invalid sub-option. Please select a valid sub-option.")
            else:
                clear_screen()
                print("Invalid sub-option. Please select a valid sub-option.")

#################################################################################################################################
#################################################################################################################################

while True:
    show_main_menu()
    main_selection = input("\nSelect an option (0-6): ")

    if main_selection == "0":
        clear_screen()
        print("Exiting the program...")
        break
    elif main_selection.isdigit():
        number_selection = int(main_selection)
        if 1 <= number_selection <= len(menu_options):
            if number_selection == 6:  # If selected "Option 6"
                if check_option_6_available():
                    clear_screen()
                    
                    config_format_option = menu_options[0]["config_option"]
                    config_decimation_option = menu_options[3]["config_option"]
                    config_normalize_option = menu_options[4]["config_option"]
                    
                    print("Configuration Preview:")
                    chain_elements = ', '.join(map(str, config_format_option))
                    print(f"\nOutput format of the .csv file: {chain_elements}")
                    chain_elements = None
                    
                    chain_elements = ', '.join(map(str, config_algths_option))
                    print(f"Discarded Algorithms: {chain_elements}")
                    chain_elements = None
                    
                    chain_elements = ', '.join(map(str, config_boards_option))
                    print(f"Discarded Boards: {chain_elements}")
                    chain_elements = None
                    
                    chain_elements = ', '.join(map(str, config_decimation_option))
                    print(f"Decimation Factor: {chain_elements}")
                    chain_elements = None
                    
                    chain_elements = ', '.join(map(str, config_normalize_option))
                    print(f"T-V Normalization: {chain_elements}\n")
                    chain_elements = None
                    
                    confirmation = input("Do you want to generate the file? (y/n): ")
                    
                    if confirmation.lower() == "y":
                        operation_accepted = True             
                        time.sleep(2)
                        clear_screen()
                        print("Generating File...")                      
                        break
                    else:
                        clear_screen()
                        print("Operation canceled. Returning to the main menu...")
                        time.sleep(1)
                else:
                    clear_screen()
                    print("Option 6 is locked due to incomplete configurations.")
                    input("Press Enter to continue...")
            else:
                submenu(number_selection - 1)
        else:
            clear_screen()
            print("Invalid option. Please select a valid option.")
    else:
        clear_screen()
        print("Invalid option. Please select a valid option.")

#################################################################################################################################
#################################################################################################################################
   
if(operation_accepted == True):
    
    # Load T-V Normalization Table if selected
    if(config_normalize_option[0] == True):
        # Read the CSV file into a pandas DataFrame, be careful with the path, which should contain the table name with its extension.
        df = pd.read_csv(boards_data_table, sep = ';')
    
    # Progress Bar parametrization
    total = 100
    unit = float(100/((boards - len(config_boards_option))*(algorithms - len(config_algths_option))*iterations))

    if(config_format_option[0] == "Unified"):
        # Take actions for the unified option.
        print("... creating the unified .csv file.")
        progress_bar_uni = tqdm(total=total, desc="Procesing")
        
        # Loop to iterate through the folders within the specified range.
        for board in range(1, boards + 1):  #** Boards are scanned.
            # If board has been discarded, skip
            if board in config_boards_option:
                continue
            if(config_normalize_option[0] == True):
                # Filter the DataFrame to obtain the rows where 'BOARD_NUM' matches
                selected_row = df[df['BOARD_NUM'] == board]
                # Access the values of the other columns
                t_cal_1 = selected_row['T_CAL_1'].values[0]
                t_cal_2 = selected_row['T_CAL_2'].values[0]
                vrefint_cal = selected_row['VREFINT_CAL'].values[0]
            
            for algorithm in range(1, algorithms + 1):  #** Evaluated algorithms for each board are scanned.
                # If algorithm has been discarded, skip
                if algorithm in config_algths_option:
                    continue
                folder = f"{board}_{algorithm}"
                complete_folder = os.path.join(base_directory, folder)

                # Check if the folder exists.
                if os.path.exists(complete_folder):
                    # Get the list of files in the current folder.
                    files = os.listdir(complete_folder)
                    
                    # Filter the files that match the format "datos_Z.txt"
                    files_data = [file for file in files if file.startswith("datos_") and file.endswith(".txt")]
                    
                    # Sort the files using the custom function.
                    files_data.sort(key=get_Z_number)
                    
                    # Iterate through the data files in the current folder.
                    for file in files_data: #** The created files from each iteration of the evaluated algorithm on each board are processed.                                                                          
                        iteration = get_Z_number(file)
                        if(iteration > iterations):
                            break
                        complete_file = os.path.join(complete_folder, file)
                        
                        # Perform data reading from the file.
                        with open(complete_file, "r") as opened_file:
                            lines = opened_file.readlines()
                            num_samples = len(lines) - 6
                            EOD = max_samples[algorithm - 1] + 4
                            
                            # Initialize variables for temperature and voltage.
                            temperature = None
                            voltage = None
                            
                            for i in range(4, EOD):

                                if i % 2 == 0:  # If it's an even line, it's temperature.
                                    temperature = int(lines[i])
                                else:  # If it's an odd line, it's voltage.
                                    voltage = int(lines[i])
                                    
                                    if (pair_counter % config_decimation_option[0]) == 0:
                                        if temperature is not None and voltage is not None:
                                            # In case normalization is desired, perform it and save the resulting data in its corresponding format.
                                            if(config_normalize_option[0] == True):
                                                data.append({
                                                    "Voltage Value": float( 3 * (vrefint_cal / voltage) ),
                                                    "Temperature Value": float( (( 80 / (t_cal_2 - t_cal_1) ) * ( temperature - t_cal_1 )) + 30 ),
                                                    "Board Number": board,
                                                    "Algorithm": algorithm,
                                                    "Iteration": iteration
                                                })
                                            else:
                                                data.append({
                                                    "Voltage Value": voltage,
                                                    "Temperature Value": temperature,
                                                    "Board Number": board,
                                                    "Algorithm": algorithm,
                                                    "Iteration": iteration
                                                })
                                            temperature = None
                                            voltage = None
                                    pair_counter += 1
                                    if pair_counter == config_decimation_option[0]:
                                        pair_counter = 0
                       
                        print(f"ID Board: {board}, Algorithm: {algorithm}, Iteration File: {file}, Total Samples: {num_samples}")
                        progress_bar_uni.update(int(unit))
                        
        # Write the data to the CSV file with a semicolon (;) as the delimiter.
        with open(csv_filename_unified, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields, delimiter=';')
            
            # Write the column labels.
            writer.writeheader()
            
            # Write the data for each row.
            for row in data:
                writer.writerow(row)

        print(f"The CSV file '{csv_filename_unified}' has been successfully created.")
        progress_bar_uni.close()
        print("\nProcess complete")    


    if(config_format_option[0] == "Multiple Files"):
        # Take actions for the multiple option.
        print("... creating the multiples .csv files.")
        progress_bar_uni = tqdm(total=total, desc="Procesing")
        
        # Loop to iterate through the folders within the specified range.
        for board in range(1, boards + 1):  #** Boards are scanned.
            # If board has been discarded, skip
            if board in config_boards_option:
                continue
            if(config_normalize_option[0] == True):
                # Filter the DataFrame to obtain the rows where 'BOARD_NUM' matches
                selected_row = df[df['BOARD_NUM'] == board]
                # Access the values of the other columns
                t_cal_1 = selected_row['T_CAL_1'].values[0]
                t_cal_2 = selected_row['T_CAL_2'].values[0]
                vrefint_cal = selected_row['VREFINT_CAL'].values[0]
                
            for algorithm in range(1, algorithms + 1):  #** Evaluated algorithms for each board are scanned.
                # If algorithm has been discarded, skip
                if algorithm in config_algths_option:
                    continue
                folder = f"{board}_{algorithm}"
                complete_folder = os.path.join(base_directory, folder)

                # Check if the folder exists.
                if os.path.exists(complete_folder):
                    # Get the list of files in the current folder.
                    files = os.listdir(complete_folder)
                    
                    # Filter the files that match the format "datos_Z.txt"
                    files_data = [file for file in files if file.startswith("datos_") and file.endswith(".txt")]
                    
                    # Sort the files using the custom function.
                    files_data.sort(key=get_Z_number)
                    
                    # Iterate through the data files in the current folder.
                    for file in files_data: #** The created files from each iteration of the evaluated algorithm on each board are processed.                                                                          
                        iteration = get_Z_number(file)
                        if(iteration > iterations):
                            break
                        complete_file = os.path.join(complete_folder, file)
                        
                        # Perform data reading from the file.
                        with open(complete_file, "r") as opened_file:
                            lines = opened_file.readlines()
                            num_samples = len(lines) - 6
                            EOD = max_samples[algorithm - 1] + 4
                            
                            # Initialize variables for temperature and voltage.
                            temperature = None
                            voltage = None
                            
                            for i in range(4, EOD ):

                                if i % 2 == 0:  # If it's an even line, it's temperature.
                                    temperature = int(lines[i])
                                else:  # If it's an odd line, it's voltage.
                                    voltage = int(lines[i])
             
                                    if (pair_counter % config_decimation_option[0]) == 0:
                                        if temperature is not None and voltage is not None:
                                            # In case normalization is desired, perform it and save the resulting data in its corresponding format.
                                            if(config_normalize_option[0] == True):
                                                data.append({
                                                    "Voltage Value": float( 3 * (vrefint_cal / voltage) ),
                                                    "Temperature Value": float( (( 80 / (t_cal_2 - t_cal_1) ) * ( temperature - t_cal_1 )) + 30 ),
                                                    "Board Number": board,
                                                    "Algorithm": algorithm,
                                                    "Iteration": iteration
                                                })
                                            else:
                                                data.append({
                                                    "Voltage Value": voltage,
                                                    "Temperature Value": temperature,
                                                    "Board Number": board,
                                                    "Algorithm": algorithm,
                                                    "Iteration": iteration
                                                })
                                            temperature = None
                                            voltage = None
                                    pair_counter += 1
                                    if pair_counter == config_decimation_option[0]:
                                        pair_counter = 0
                       
                        print(f"ID Board: {board}, Algorithm: {algorithm}, Iteration File: {file}, Total Samples: {num_samples}")
                        
                        csv_filename_multiple = f"{board}_{algorithm}_{iteration}.csv"
                        if not os.path.exists(destination_folder):
                            # If it doesn't exist, create it
                            os.makedirs(destination_folder)
                        csv_filename_multiple_destination = os.path.join(destination_folder, csv_filename_multiple)
                        # Write the data to the CSV file with a semicolon (;) as the delimiter.
                        with open(csv_filename_multiple_destination, mode='w', newline='') as csv_file:
                            writer = csv.DictWriter(csv_file, fieldnames=fields, delimiter=';')
                            
                            # Write the column labels.
                            writer.writeheader()
                            
                            # Write the data for each row.
                            for row in data:
                                writer.writerow(row)
                                
                            data.clear()
                        print(f"The CSV file '{csv_filename_multiple}' has been successfully created.")
                        progress_bar_uni.update(int(unit))
                        
        progress_bar_uni.close()
        print("\nProcess complete")    
        
        
