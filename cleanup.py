import pandas as pd
from scipy.spatial import KDTree

# Load the radar station data
radar_df = pd.read_csv('radar_locations.csv')
radar_points = list(zip(radar_df['Latitude'], radar_df['Longitude']))

# Create a k-d tree for the radar stations
kdtree = KDTree(radar_points)

# Load tornado data
tornado_df = pd.read_csv('1950-2022_all_tornadoes.csv')

# Filter out tornado data before a certain year, e.g., 2000
filtered_data = tornado_df[tornado_df['yr'] >= 2010]

# For each tornado location in the filtered_data, find the nearest radar station
nearest_radars = []
for idx, row in filtered_data.iterrows():
    _, index = kdtree.query((row['slat'], row['slon']))
    nearest_radar = radar_df.iloc[index]
    nearest_radars.append(nearest_radar['RadarCode'])

# Add the nearest radar station ID to the filtered_data DataFrame
filtered_data['Nearest Radar Station'] = nearest_radars

# Save the enriched filtered_data to a new CSV
filtered_data.to_csv('enriched_tornado_data.csv', index=False)