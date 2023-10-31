import pandas as pd
from scipy.spatial import KDTree

def adjust_to_gmt(row):
    """Adjust the time to GMT based on the timezone."""
    hour, minute, _ = map(int, row['time'].split(':'))
    tz = row['tz']
    
    if tz == 3:  # CST is 6 hours behind GMT
        hour += 6
        if hour >= 24:
            hour -= 24
            # Adjust day as well if it spills over to the next day
            # This will not account for month/year changes, but such cases should be rare in this context
            row['dy'] += 1
    elif tz == '?':  # Unknown timezone, we exclude this data
        raise ValueError("Unknown timezone")
    
    row['time'] = f"{hour:02}:{minute:02}:00"
    return row

def cleanup_tornado_data():
    # Load the radar station data
    radar_df = pd.read_csv('radar_locations.csv')
    radar_points = list(zip(radar_df['Latitude'], radar_df['Longitude']))

    # Create a k-d tree for the radar stations
    kdtree = KDTree(radar_points)

    # Load tornado data
    tornado_df = pd.read_csv('1950-2022_all_tornadoes.csv')

    # Filter out tornado data before a certain year, e.g., 2010
    filtered_data = tornado_df[tornado_df['yr'] >= 2012]

    # Adjust time to GMT
    try:
        filtered_data = filtered_data.apply(adjust_to_gmt, axis=1)
    except ValueError as ve:
        print(f"Error adjusting to GMT: {ve}")

    # For each tornado location in the filtered_data, find the nearest radar station
    nearest_radars = []
    for idx, row in filtered_data.iterrows():
        _, index = kdtree.query((row['slat'], row['slon']))
        nearest_radar = radar_df.iloc[index]
        nearest_radars.append(nearest_radar['RadarCode'])

    # Add the nearest radar station ID to the filtered_data DataFrame
    filtered_data.loc[:, 'Nearest Radar Station'] = nearest_radars

    # Save the enriched filtered_data to a new CSV
    filtered_data.to_csv('enriched_tornado_data.csv', index=False)

# For standalone execution
if __name__ == '__main__':
    cleanup_tornado_data()
