import os
import sys
import numpy as np

backup = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pyart

sys.stdout = backup
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import warnings
warnings.filterwarnings("ignore")

def visualize_radar_data(filename, image_directory, tornado_lat, tornado_lon, debug_mode=False):
    """
    This function reads the radar data using pyart and creates a visualization for velocity.
    It then saves this visualization to the specified image directory, focused on the tornado's location.
    """

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
        x /= 1000.0    # Convert to km
        y /= 1000.0    # Convert to km

        # Convert Cartesian x and y to latitudes and longitudes
        lon_offset = x / (111.0 * np.cos(np.radians(radar.latitude['data'][0])))
        lat_offset = y / 111.0
        actual_lons = radar.longitude['data'][0] + lon_offset
        actual_lats = radar.latitude['data'][0] + lat_offset

        # Setting up file names for saving
        base_filename = os.path.basename(filename).split('.')[0]
        vel_image_name = f"{base_filename}_velocity.png"

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
        vmin, vmax = -30, 30

        # Plotting the data
        cax = ax.pcolormesh(actual_lons, actual_lats, data, vmin=vmin, vmax=vmax, cmap=pyart.graph.cm.NWSVel)

        # Set the extent around the tornado's location
        buffer_degrees = 1.5  # or any other value that provides the desired zoom level
        ax.set_xlim([tornado_lon - buffer_degrees, tornado_lon + buffer_degrees])
        ax.set_ylim([tornado_lat - buffer_degrees, tornado_lat + buffer_degrees])

        if debug_mode:
            print("Radar Base Location: ", radar.latitude['data'][0], radar.longitude['data'][0])
            ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black', linewidth=0.5)
            ax.gridlines(draw_labels=True)
        else:
            ax.axis('off')

        ax.scatter(tornado_lon, tornado_lat, color='red', s=100)

        # Save the image
        plt.savefig(os.path.join(image_directory, vel_image_name), bbox_inches='tight', pad_inches=0)
        plt.close()

    except Exception as e:
        print(f"Error processing {filename}. Error: {e}")

# Adjust this if your directory is elsewhere
image_directory = 'radar_images'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)
