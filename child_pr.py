# Importing necessary libraries
import os
import io
import sys
import gzip
import shutil
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

backup = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pyart
sys.stdout = backup

# Constants
bucket_name = 'noaa-nexrad-level2'
compressed_dir = "./compressed_files"
uncompressed_dir = "./uncompressed_files"
image_directory = "./radar_images"

radar_df = pd.read_csv('radar_locations.csv')
radar_points = list(zip(radar_df['Latitude'], radar_df['Longitude']))
kdtree = KDTree(radar_points)

def find_nearest_radar_site(lat, lon):
    # Find the nearest radar site to the provided latitude and longitude
    radar_site = kdtree.query([lat, lon])[1]
    return radar_df.iloc[radar_site]['RadarCode']

def list_files(bucket_name, prefix):
    # List all files in the provided S3 bucket and prefix
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    results = []
    paginator = s3.get_paginator('list_objects_v2')
    
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for content in page.get('Contents', []):
            results.append(content['Key'])
     
    return results


def find_most_recent_file(bucket_name, radar_site):
    # Find the most recent radar file for the provided radar site
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    files = list_files(bucket_name, radar_site)
    # return the most recent file from the list
    print("File Path: " + files[-1])
    return files[-1]

# Download the most recent radar file for the provided radar site
def download_and_decompress(filename):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    # Using BytesIO to handle the file content in memory
    compressed_file_obj = io.BytesIO()

    try:
        # Download the file directly into memory
        s3.download_fileobj(bucket_name, filename, compressed_file_obj)

        # If the file is a gzip, decompress it
        if filename.endswith(".gz"):
            compressed_file_obj.seek(0)  # Go to the beginning of the file
            with gzip.GzipFile(fileobj=compressed_file_obj, mode='rb') as f_in:
                decompressed_data = io.BytesIO(f_in.read())
            return decompressed_data
        else:
            # If not a gzip, simply return the BytesIO object
            compressed_file_obj.seek(0)  # Go to the beginning of the file
            return compressed_file_obj

    except Exception as e:
        print(f"Failed to download and process file {filename}. Error: {e}")
        return None


# Visualizing the radar data
def visualize_radar_data(filename, user_lat, user_lon):

    # Read in the file
    radar = pyart.io.read_nexrad_archive(filename)

    # Create a plot
    display = pyart.graph.RadarDisplay(radar)

    # Set up the figure
    fig = plt.figure(figsize=(10, 10))

    # Plot reflectivity
    ax = fig.add_subplot(221)
    display.plot('reflectivity', 0, ax=ax, title='Reflectivity', colorbar_label='', vmin=-32, vmax=64)
    display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
    display.set_limits(xlim=(-150, 150), ylim=(-150, 150), ax=ax)

    # Plot velocity
    ax = fig.add_subplot(222)
    display.plot('velocity', 0, ax=ax, title='Velocity', colorbar_label='', vmin=-32, vmax=32)
    display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
    display.set_limits(xlim=(-150, 150), ylim=(-150, 150), ax=ax)

    # Show the plot
    plt.show()

    return

# Completing the main function
def main(lat, lon):
    # Take the users latitude and longitude and find the nearest radar
    radar_site = find_nearest_radar_site(lat, lon)
    print("Radar Site: " + radar_site)

    # Create a prefix with the radar site using the current date time
    now = datetime.utcnow() # Using UTC because that's what NEXRAD expects

    prefix = f'{now.year}/{now.month:02}/{now.day:02}/{radar_site}'

    filename = find_most_recent_file(bucket_name, prefix)

    # Download the radar file
    decompressed_data = download_and_decompress(filename)

    # Visualize the radar file
    visualize_radar_data(decompressed_data, lat, lon)
 
    return 
"""
if __name__ == "__main__":
    # Example latitude and longitude
    lat = 35.0
    lon = -97.0

    main(lat, lon)
"""

main(39.176252, -84.483565)