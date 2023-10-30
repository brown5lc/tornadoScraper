import os
import tarfile
import requests
import gzip
import shutil

def construct_url(year, month, day, hour, minute, seconds, radar_code):
    base_url = "https://noaa-nexrad-level2.s3.amazonaws.com"
    
    if year < 2016:
        filename = f"{radar_code}{year}{month:02}{day:02}_{hour:02}{minute:02}{seconds:02}_V06.gz"
    else:
        filename = f"{radar_code}{year}{month:02}{day:02}_{hour:02}{minute:02}{seconds:02}_V06"
    
    return f"{base_url}/{year}/{month:02}/{day:02}/{radar_code}/{filename}"

def download_nexrad_data(year, month, day, hour, minute, seconds, radar_code, compressed_dir, uncompressed_dir):
    url = construct_url(year, month, day, hour, minute, seconds, radar_code)
    
    timestamp = f"{year}{month:02}{day:02}_{hour:02}{minute:02}{seconds:02}"
    compressed_filename = f"{radar_code}{timestamp}_V06.gz" if year < 2016 else f"{radar_code}{timestamp}_V06"
    
    response = requests.get(url, stream=True)
    compressed_path = os.path.join(compressed_dir, compressed_filename)
    
    with open(compressed_path, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
    
    uncompressed_path = os.path.join(uncompressed_dir, compressed_filename.rstrip('.gz'))
    
    # Adjusting extraction based on file extension
    if year < 2016:
        with gzip.open(compressed_path, 'rb') as f_in:
            with open(uncompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        os.rename(compressed_path, uncompressed_path)

    return uncompressed_path

# Make sure to create directories if they don't exist
compressed_dir = 'compressed_files'
uncompressed_dir = 'uncompressed_files'

if not os.path.exists(compressed_dir):
    os.makedirs(compressed_dir)

if not os.path.exists(uncompressed_dir):
    os.makedirs(uncompressed_dir)

# You can now use the function specifying the directories where you want the files
# For example:
download_nexrad_data(2015, 3, 3, 0, 10, 50, 'KABX', compressed_dir, uncompressed_dir)


