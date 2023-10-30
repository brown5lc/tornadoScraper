import pandas as pd

# Load NOAA CSV data
data = pd.read_csv('./1950-2022_all_tornadoes')
radar_df = pd.read_csv('./radar_locations.csv')

# Filter out tornadoes before 1990
filteredData = data[data['yr'] >= 1990]

# Function to determine the closest radar sire based on tornado latitude and longitude
def getClosestRadarSite(lat, long):
    # TODO: impliment the logic to find the closest radar site
    # I'll need a list of all the radar sites with the lat and long, preferabbly sorted so I can binary search
    # return the four letter station identifier
    
    pass

# Apply the function to each tornado event
filteredData['radar_site'] = filteredData.apply(lambda x: getClosestRadarSite(x['slat'], x['slon']), axis=1)

# Save the data to a new CSV file
filteredData.to_csv('./processedTornadoData', index=False)