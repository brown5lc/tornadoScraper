import requests
from bs4 import BeautifulSoup
import pandas as pd

# Helper function to convert DMS (Degrees, Minutes, Seconds) to Decimal
def dms_to_decimal(dms_str):
    # Check if the DMS string is numeric before parsing
    if not dms_str.isdigit():
        return None
    
    degrees = int(dms_str[:2])
    minutes = int(dms_str[2:4])
    seconds = int(dms_str[4:])
    return degrees + minutes/60 + seconds/3600

# URL of the webpage containing radar locations
URL = 'https://apollo.nvu.vsc.edu/classes/remote/lecture_notes/radar/88d/88D_locations.html'

response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# Fetch table rows
table_rows = soup.find_all('tr')  

radar_data = []

for row in table_rows:
    columns = row.find_all('td')
    
    # Fetch radar code from the second column
    radar_code = columns[1].text.strip()
    
    # Split the combined latitude and longitude column
    lat_lon = columns[3].text.strip().split(' / ')
    if len(lat_lon) != 2:  # Safeguard against potential unexpected formats
        continue
    
    lat_dms, lon_dms = lat_lon
    
    latitude = dms_to_decimal(lat_dms)

    # Convert longitude to decimal and account for '0' prefix indicating negative
    if lon_dms.startswith('0'):
        longitude = -dms_to_decimal(lon_dms[1:])
    else:
        longitude = dms_to_decimal(lon_dms)

    # Check if latitude and longitude are both successfully parsed
    if latitude is not None and longitude is not None:
        radar_data.append([radar_code, latitude, longitude])

# Convert to DataFrame and save to CSV
df = pd.DataFrame(radar_data, columns=['RadarCode', 'Latitude', 'Longitude'])
df.to_csv('radar_locations.csv', index=False)
