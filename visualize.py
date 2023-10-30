import pyart
import matplotlib.pyplot as plt
import os

def create_directory(directory_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def visualize_radar_data(file_path, output_directory):
    # Ensure the output directory exists
    create_directory(output_directory)
    
    # Create an output path for the image using the filename
    output_img_path = os.path.join(output_directory, os.path.basename(file_path) + '.png')
    
    # 1. Read the radar data
    radar = pyart.io.read_nexrad_archive(file_path)
    
    # 2. Display the velocity field
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=(10, 10))
    display.plot('reflectivity', 0, title='Doppler Velocity', colorbar_label='', axislabels=('', 'North South distance from radar (km)'))
    display.set_limits((-150, 150), (-150, 150))
    
    # 3. Save the display as an image
    plt.savefig(output_img_path)
    plt.close(fig)

# Directory to save the radar images
image_directory = './radar_images'

# Path to your NEXRAD file
file_path = './uncompressed_files/KABX20150303_001050_V06'  # Adjust as per your file

radar = pyart.io.read_nexrad_archive(file_path)
print(radar.fields.keys())
print(radar.fields['velocity']['data'])

visualize_radar_data(file_path, image_directory)
