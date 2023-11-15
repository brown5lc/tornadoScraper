import pandas as pd
import cleanup
import download
import visualize
import datetime
import os
import sys
from tqdm import tqdm
import gc  # Garbage Collector interface

def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        if e.errno != 2:  # errno 2 is "No such file or directory"
            raise

def process_batch(batch_df, debug=False):
    downloaded_files_info = []

    for _, row in tqdm(batch_df.iterrows(), desc="Downloading data", total=batch_df.shape[0]):
        year, month, day = row['yr'], row['mo'], row['dy']
        hour, minute, seconds = map(int, row['time'].split(':'))
        radar_code = row['Nearest Radar Station']
        
        start_time = datetime.datetime(year, month, day, hour, minute, seconds)

        try:
            downloaded_files = download.main_download_proccess(year, month, day, radar_code, start_time, download.compressed_dir, download.uncompressed_dir)
            downloaded_files_info.extend([(file_path, radar_code, year, month, day, hour, minute, seconds, row['slat'], row['slon']) for file_path in downloaded_files])
        except Exception as e:
            print(f"Error downloading data for {radar_code} on {year}-{month:02}-{day:02}. Error: {e}")

    # After all files in the batch are downloaded, we visualize them
    print("\n")
    for file_info in tqdm(downloaded_files_info, desc="Visualizing data", total=len(downloaded_files_info)):
        file_path, radar_code, year, month, day, hour, minute, seconds, slat, slon = file_info
        try:
            visualize.visualize_radar_data(file_path, visualize.image_directory, slat, slon, debug)
            delete_file(file_path)
        except Exception as e:
            print(f"Error visualizing data for {radar_code} on {year}-{month:02}-{day:02}. Error: {e}")

    # Clear the list to free up memory
    downloaded_files_info.clear()
    gc.collect()  # Run garbage collector to free up unreferenced memory

def main_process(debug=False, debug_idx=None, batch_size=100):
    # 1. Cleanup and Prepare enriched_tornado_data.csv
    cleanup.cleanup_tornado_data()

    # 2. Load enriched tornado data
    enriched_df = pd.read_csv('enriched_tornado_data.csv')

    # 3. Ask the user how they want the sampling to be
    if debug:
        enriched_df = enriched_df.iloc[[debug_idx]]
    else:
        sampling_choice = input("Do you want the sampling to be random? (y/n): ").strip().lower()

        if sampling_choice == 'n':
            start_idx = int(input(f"Please enter the starting index (between 0 and {len(enriched_df)-1}): "))
            enriched_df = enriched_df.iloc[start_idx:]

        sample_size = int(input("How many samples would you like to produce? "))
        enriched_df = enriched_df.sample(sample_size) if sampling_choice == 'y' else enriched_df.iloc[:sample_size]

    # 4. Process the data in batches to avoid memory issues
    for start_idx in range(0, len(enriched_df), batch_size):
        end_idx = min(start_idx + batch_size, len(enriched_df))
        batch_df = enriched_df.iloc[start_idx:end_idx]

        print(f"\nProcessing batch {start_idx // batch_size + 1}/{(len(enriched_df) - 1) // batch_size + 1}")
        process_batch(batch_df, debug)

        # Clear memory
        del batch_df
        gc.collect()

# Call the main process function
if __name__ == "__main__":
    if '--debug' in sys.argv:
        try:
            idx = int(sys.argv[sys.argv.index('--debug') + 1])
            idx -= 2  # Adjust for the first 4 lines in enriched_tornado_data.csv
            main_process(debug=True, debug_idx=idx)
        except (IndexError, ValueError):
            print("Please specify the index for debug mode. Usage: --debug [index]")
    else:
        main_process()