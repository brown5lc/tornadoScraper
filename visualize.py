import os
import sys
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from PIL import Image

backup = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pyart
sys.stdout = backup

def visualize_radar_data(filename, image_directory, tornado_lat, tornado_lon, debug_mode=False):
    # This function reads the radar data using pyart and creates a visualization for velocity.
    # It will then randomly offset the tornado's location by up to 25 miles in any direction.
    # It then saves this visualization to the specified image directory, focused on the tornado's location.
    # Finally, it crops the image to a square and resizes it to 224x224.

    try:
        # Reading the radar data
        radar = pyart.io.read_nexrad_archive(filename)

        # Check if the velocity field is present in the radar data
        if 'velocity' not in radar.fields:
            print(f"Error processing {filename}. Velocity data is missing.")
            return

        # Extracting the data from radar object
        sweep = 3
        data = radar.get_field(sweep, 'velocity')
        x, y, _ = radar.get_gate_x_y_z(sweep)
        x /= 1000.0  # Convert to km
        y /= 1000.0  # Convert to km

        # Convert Cartesian x and y to latitudes and longitudes
        lon_offset = x / (111.0 * np.cos(np.radians(radar.latitude['data'][0])))
        lat_offset = y / 111.0
        actual_lons = radar.longitude['data'][0] + lon_offset
        actual_lats = radar.latitude['data'][0] + lat_offset

        # Randomly offset the tornado's location by up to 25 miles
        max_offset_miles = 20
        lat_offset_degrees = max_offset_miles / 69.0
        lon_offset_degrees = max_offset_miles / (69.0 * np.cos(np.radians(tornado_lat)))

        random_lat_offset = np.random.uniform(-lat_offset_degrees, lat_offset_degrees)
        random_lon_offset = np.random.uniform(-lon_offset_degrees, lon_offset_degrees)

        random_tornado_lat = tornado_lat + random_lat_offset
        random_tornado_lon = tornado_lon + random_lon_offset

        # Setting up file names for saving
        base_filename = os.path.basename(filename).split('.')[0]
        vel_image_name = f"{base_filename}_velocity.png"

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
        vmin, vmax = -30, 30

        cax = ax.pcolormesh(actual_lons, actual_lats, data, vmin=vmin, vmax=vmax, cmap=pyart.graph.cm.NWSVel)

        # Calculate the buffer in degrees for a 50x50 mile square around the tornado's location
        miles_per_degree = 69.0
        buffer_in_degrees_lat = 30.0 / miles_per_degree
        buffer_in_degrees_lon = 30.0 / (miles_per_degree * np.cos(np.radians(tornado_lat)))

        # Set the extent around the tornado's location
        ax.set_xlim([random_tornado_lon - buffer_in_degrees_lon, random_tornado_lon + buffer_in_degrees_lon])
        ax.set_ylim([random_tornado_lat - buffer_in_degrees_lat, random_tornado_lat + buffer_in_degrees_lat])

        if debug_mode:
            ax.axis('off')
            #print("Radar Base Location: ", radar.latitude['data'][0], radar.longitude['data'][0])
            #ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black', linewidth=0.5)
            #ax.gridlines(draw_labels=True)
            #ax.scatter(tornado_lon, tornado_lat, color='yellow', s=100)
        else:
            ax.axis('off')

        # Save the image
        plt.savefig(os.path.join(image_directory, vel_image_name), bbox_inches='tight', pad_inches=0)
        plt.close()

        image_path = os.path.join(image_directory, vel_image_name)
        with Image.open(image_path) as img:
            width, height = img.size
            new_size = min(width, height)

            left = (width - new_size)/2
            top = (height - new_size)/2
            right = (width + new_size)/2
            bottom = (height + new_size)/2

            img_cropped = img.crop((left, top, right, bottom))

            img_resized = img_cropped.resize((224, 224), Image.ANTIALIAS)

            img_resized.save(image_path)

    except Exception as e:
        print(f"Error processing {filename}. Error: {e}")

# Adjust this if your directory is elsewhere
image_directory = 'radar_images'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)
