import os
import sys

backup = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pyart

sys.stdout = backup
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import warnings
warnings.filterwarnings("ignore")

def visualize_radar_data(filename, image_directory, tornado_lat, tornado_lon):
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

        # Setting up file names for saving
        base_filename = os.path.basename(filename).split('.')[0]
        vel_image_name = f"{base_filename}_velocity.png"

        # Plotting velocity with map overlay
        display_map = pyart.graph.RadarMapDisplay(radar)
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
        vmin, vmax = -30, 30
        
        # Set the extent around the tornado's location
        ax.set_extent([tornado_lon - 1.5, tornado_lon + 1.5, tornado_lat - 1.5, tornado_lat + 1.5])
        
        display_map.plot_ppi_map('velocity', sweep=3, vmin=vmin, vmax=vmax, ax=ax, cmap=pyart.graph.cm.NWSVel)
        ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black', linewidth=0.5)
        plt.savefig(os.path.join(image_directory, vel_image_name))
        plt.close()

    except Exception as e:
        print(f"Error processing {filename}. Error: {e}")

# Adjust this if your directory is elsewhere
image_directory = 'radar_images'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)
