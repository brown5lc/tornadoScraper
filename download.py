import os
import gzip
import shutil
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime
import re
import pandas as pd

bucket_name = 'noaa-nexrad-level2'
compressed_dir = "./compressed_files"
uncompressed_dir = "./uncompressed_files"

def list_files(bucket_name, prefix):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    results = []
    paginator = s3.get_paginator('list_objects_v2')
    
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for content in page.get('Contents', []):
            results.append(content['Key'])
    
    return results

def extract_datetime_from_filename(filename):
    base_filename = os.path.basename(filename)
    pattern = r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})'

    match = re.search(pattern, base_filename)
    if not match:
        raise ValueError(f"Failed to extract datetime from filename {filename}")

    year, month, day, hour, minute, second = map(int, match.groups())

    # Validate datetime components
    if not (1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
        raise ValueError(f"Invalid datetime components in filename {filename}")

    return datetime(year, month, day, hour, minute, second)

    
def filter_files_based_on_time(files, start_time, end_time):
    """
    Filters the list of files based on the tornado's start and end time.
    Currently only returns the first file that matches the time range.
    """
    # filtered_files = []
    for file in files:
        if file.endswith('.tar'):  # Skip tar files
            continue
        timestamp = extract_datetime_from_filename(file)
        if timestamp and start_time <= timestamp <= end_time:
            # filtered_files.append(file)
            return [file]
    #return filtered_files
    return []

def download_selected_files(files, bucket_name, compressed_dir, uncompressed_dir):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    downloaded_files_list = []

    for file in files:
        actual_file = os.path.basename(file)  # Get the filename from the S3 key
        
        compressed_path = os.path.join(compressed_dir, actual_file)
        
        # Ensure the directory for the compressed file exists
        os.makedirs(compressed_dir, exist_ok=True)

        try:
            # Download the file
            s3.download_file(bucket_name, file, compressed_path)
            
            # If the file is a gzip, uncompress it and store in uncompressed_dir
            if actual_file.endswith(".gz"):
                uncompressed_file = actual_file.rstrip('.gz')
                uncompressed_path = os.path.join(uncompressed_dir, uncompressed_file)
                
                with gzip.open(compressed_path, 'rb') as f_in:
                    with open(uncompressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(compressed_path)  # Remove the gz file after decompressing
                downloaded_files_list.append(uncompressed_path)
            else:
                # If not a gzip, simply move it to the uncompressed_dir
                shutil.move(compressed_path, os.path.join(uncompressed_dir, actual_file))
                downloaded_files_list.append(os.path.join(uncompressed_dir, actual_file))
        except Exception as e:
            print(f"Failed to download and process file {file}. Error: {e}")

    return downloaded_files_list

def main_download_proccess(year, month, day, radar_code, start_time, end_time, compressed_dir='compressed_files', uncompressed_dir='uncompressed_files'):
    # Ensure the output directories exist
    try:
        if not os.path.exists(compressed_dir):
            os.makedirs(compressed_dir)
        if not os.path.exists(uncompressed_dir):
            os.makedirs(uncompressed_dir)
    except OSError as e:
        if e.errno != 17:
            raise
        
    prefix = f'{year}/{month:02}/{day:02}/{radar_code}'

    files = list_files(bucket_name, prefix)

    if not files:
        print(f"No files found for {radar_code} on {year}-{month:02}-{day:02}.")
        return []
    
    selected_files = filter_files_based_on_time(files, start_time, end_time)

    downloaded_files = download_selected_files(selected_files, bucket_name, compressed_dir, uncompressed_dir)

    return downloaded_files or []
