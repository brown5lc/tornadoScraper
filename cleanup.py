import pandas as pd
from scipy.spatial import KDTree

from datetime import datetime, timedelta

def adjust_to_gmt(row):
    """Adjust the time to GMT based on the timezone."""
    hour, minute, _ = map(int, row['time'].split(':'))
    tz = row['tz']
    # Assume dy, mo, yr represent day, month, year respectively in `row`
    day = row['dy']
    month = row['mo']
    year = row['yr']

    # Create a datetime object with the local time
    local_time = datetime(year, month, day, hour, minute)

    if tz == 3:  # CST is 6 hours behind GMT
        # Use timedelta to adjust the time
        adjusted_time = local_time + timedelta(hours=6)
    elif tz == '?':  # Unknown timezone, we exclude this data
        raise ValueError("Unknown timezone")
    else:
        # If there are other time zones, you would handle them here
        adjusted_time = local_time

    # Update the row with the adjusted time values
    row['dy'] = adjusted_time.day
    row['mo'] = adjusted_time.month
    row['yr'] = adjusted_time.year
    row['time'] = adjusted_time.strftime("%H:%M:%S")

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

    # Filter out tornadoes with magnitude less than 1
    filtered_data = filtered_data[filtered_data['mag'] > 1]

    # Save the enriched filtered_data to a new CSV
    filtered_data.to_csv('enriched_tornado_data.csv', index=False)

# For standalone execution
if __name__ == '__main__':
    cleanup_tornado_data()
