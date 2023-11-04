import pandas as pd
import cleanup  
import download
import visualize
import datetime
import os
import sys
from tqdm import tqdm

def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        if e.errno != 2:
            raise

def recover_process():
    uncompressed_files_dir = download.uncompressed_dir  # Make sure this points to your uncompressed files directory
    uncompressed_files = os.listdir(uncompressed_files_dir)

    if not uncompressed_files:
        print("The uncompressed_files directory is empty.")
        return

    for file_name in tqdm(uncompressed_files, desc="Recovering visualizations"):
        file_path = os.path.join(uncompressed_files_dir, file_name)
        try:
            # Extract metadata from file name or path if necessary
            # Assuming file name contains necessary metadata for visualization
            # Example: 'radar_KTLX_20200520_1345.png'
            # You might need to adjust parsing according to your file naming convention
            parts = file_name.split('_')
            radar_code = parts[1]
            year, month, day = int(parts[2][:4]), int(parts[2][4:6]), int(parts[2][6:8])
            hour, minute = int(parts[3][:2]), int(parts[3][2:4])

            # Dummy values for slat and slon, replace with actual values extracted from file name if available
            slat, slon = 0, 0

            visualize.visualize_radar_data(file_path, visualize.image_directory, slat, slon, debug=False)
            print(f"Visualization recovered for {file_name} successfully!")
            delete_file(file_path)
        except Exception as e:
            print(f"Error recovering visualization for {file_name}. Error: {e}")

def main_process(debug = False, debug_idx = None):
    # 1. Cleanup and Prepare enriched_tornado_data.csv
    cleanup.cleanup_tornado_data()
    
    # 2. Load enriched tornado data
    enriched_df = pd.read_csv('enriched_tornado_data.csv')

    # 3. Ask the user how they want the sampling to be
    if debug:
        # Only use one sample for debugging purposes
        enriched_df = enriched_df.iloc[[debug_idx]]
        
    else:
        sampling_choice = input("Do you want the sampling to be random? (y/n): ").strip().lower()
        
        if sampling_choice == 'n':
            start_idx = int(input(f"Please enter the starting index (between 0 and {len(enriched_df)-1}): "))
            
            while start_idx < 0 or start_idx >= len(enriched_df):
                print("Invalid index. Please try again.")
                start_idx = int(input(f"Please enter the starting index (between 0 and {len(enriched_df)-1}): "))
                
            enriched_df = enriched_df.iloc[start_idx:]
        
        # 4. Ask the user how many samples they'd like
        sample_size = int(input("How many samples would you like to produce? "))
        
        while sample_size <= 0 or sample_size > len(enriched_df):
            print(f"Invalid number of samples. Please enter a value between 1 and {len(enriched_df)}.")
            sample_size = int(input("How many samples would you like to produce? "))

        if sampling_choice == 'y':
            enriched_df = enriched_df.sample(sample_size)

        enriched_df = enriched_df.iloc[:sample_size]

    # 5. Download, decompress, and visualize each tornado radar data
    downloaded_files_info = []
    for _, row in tqdm(enriched_df.iterrows(), desc="Downloading data", total=enriched_df.shape[0]):
        year, month, day = row['yr'], row['mo'], row['dy']
        hour, minute, seconds = map(int, row['time'].split(':'))
        radar_code = row['Nearest Radar Station']
        
        #print(f"Preparing to download data for {radar_code} on {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{seconds:02}...")
        start_time = datetime.datetime(year, month, day, hour, minute, seconds)

        try:
            downloaded_files = download.main_download_proccess(year, month, day, radar_code, start_time, download.compressed_dir, download.uncompressed_dir)
            downloaded_files_info.extend([(file_path, radar_code, year, month, day, hour, minute, seconds, row['slat'], row['slon']) for file_path in downloaded_files])
            #print(f"Data for {radar_code} on {year}-{month:02}-{day:02} downloaded successfully!")
        except Exception as e:
            print(f"Error downloading data for {radar_code} on {year}-{month:02}-{day:02}. Error: {e}")

    # After all files are downloaded, we visualize them
    print("\n")
    for file_info in tqdm(downloaded_files_info, desc="Visualizing data", total=len(downloaded_files_info)):
        file_path, radar_code, year, month, day, hour, minute, seconds, slat, slon = file_info
        try:
            #print(f"Visualizing data for {radar_code} on {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{seconds:02}...")
            visualize.visualize_radar_data(file_path, visualize.image_directory, slat, slon, debug)
            #print(f"Visualization for {radar_code} on {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{seconds:02} created successfully!\n")
            # Assuming we want to delete the file after visualization
            delete_file(file_path)
        except Exception as e:
            print(f"Error visualizing data for {radar_code} on {year}-{month:02}-{day:02}. Error: {e}")
    
# Call the main process function
if __name__ == "__main__":
    if '--debug' in sys.argv:
        try:
            idx = int(sys.argv[sys.argv.index('--debug')+1])
            idx -= 2 # Adjust for the first 4 lines in enriched_tornado_data.csv 
            main_process(debug=True, debug_idx=idx)
        except (IndexError, ValueError):
            print("Please specify the index for debug mode. Usage: --debug [index]")
    else:    
        main_process()