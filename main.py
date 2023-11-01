import pandas as pd
import cleanup  
import download
import visualize
import datetime
import os
import sys
import time
import threading

class Spinner:
    def __init__(self, message="Working"):
        self.spinner_cycle = ['-', '\\', '|', '/']
        self.running = False
        self.message = message

    def start(self):
        self.running = True
        threading.Thread(target=self._spin).start()

    def stop(self):
        self.running = False

    def _spin(self):
        write, flush = sys.stdout.write, sys.stdout.flush
        pos = 0
        while self.running:
            write(f'\r{self.message}... {self.spinner_cycle[pos]}')
            flush()
            time.sleep(0.1)
            pos = (pos + 1) % 4
        write('\r')  # Clear line

def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        if e.errno != 2:
            raise

def main_process(debug = False, debug_idx = None):
    spinner_down = Spinner("Downloading data")
    spinner_vis = Spinner("Visualizing data")

    # 1. Cleanup and Prepare enriched_tornado_data.csv
    cleanup.cleanup_tornado_data()
    
    # 2. Load enriched tornado data
    enriched_df = pd.read_csv('enriched_tornado_data.csv')

    # 3. Ask the user how they want the sampling to be
    if debug:
        # Only use one sample for debugging purposes
        enriched_df = enriched_df.iloc[[debug_idx]]
        
    else:
        sampling_choice = input("Do you want the sampling to be random? (yes/no): ").strip().lower()
        
        if sampling_choice == 'no':
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

        if sampling_choice == 'yes':
            enriched_df = enriched_df.sample(sample_size)

    # 5. Download, decompress, and visualize each tornado radar data
    for _, row in enriched_df.iterrows():
        year, month, day = row['yr'], row['mo'], row['dy']
        hour, minute, seconds = map(int, row['time'].split(':'))
        radar_code = row['Nearest Radar Station']

        # Extract start and end times of tornado for filtering
        start_time = datetime.datetime(year, month, day, hour, minute, seconds)
        end_hour, end_minute, end_seconds = hour, minute + 10, seconds

        if end_minute >= 60:
            end_hour += 1
            end_minute -= 60

        end_time = datetime.datetime(year, month, day, end_hour, end_minute, end_seconds)

        # 5a. List available files for the given day and radar station
        try:
            spinner_down.start()
            downloaded_files = download.main_download_proccess(year, month, day, radar_code, start_time, end_time, download.compressed_dir, download.uncompressed_dir)
            spinner_down.stop()
            print(f"Data for {radar_code} on {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{seconds:02} downloaded successfully!\n")
            spinner_vis.start()

            # 5d. Visualize each downloaded file
            for file_path in downloaded_files:
                print(f"Tornado Location: {row['slat']}, {row['slon']}")
                visualize.visualize_radar_data(file_path, visualize.image_directory, row['slat'], row['slon'], True)
                spinner_vis.stop()
                print(f"Visualization for {radar_code} on {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{seconds:02} created successfully!\n")
                print(year, month, day, end_hour, end_minute, end_seconds)
                end_time = datetime.datetime(year, month, day, end_hour, end_minute, end_seconds)
                delete_file(file_path)

        except Exception as e:
            print(f"Error processing data for {radar_code} on {year}-{month:02}-{day:02} {hour:02}:{minute:02}:{seconds:02}. Error: {e}")

    
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