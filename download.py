import requests

def construct_url(year, month, day, station_id, hour, minute, second=0):
    base_url = "https://noaa-nexrad-level2.s3.amazonaws.com/"
    
    # format year, month, day, hour, minute, and second to fit the URL format
    year_str = str(year)
    month_str = str(month).zfill(2)
    day_str = str(day).zfill(2)
    hour_str = str(hour).zfill(2)
    minute_str = str(minute).zfill(2)
    second_str = str(second).zfill(2)

    # determine the file extension
    if year < 2016 or (year == 2016 and month < 6):
        file_ext = ".gz"
    else:
        file_ext = ""

    # for dates after 2015, we add "_V06" before the file extension
    version = "_V06" if year > 2015 else ""

    # construct the full URL
    url = f"{base_url}{year_str}/{month_str}/{day_str}/{station_id}/{station_id}{year_str}{month_str}{day_str}_{hour_str}{minute_str}{second_str}{version}{file_ext}"
    
    return url

def download_nexrad_data(year, month, day, station_id, hour, minute, second=0):
    url = construct_url(year, month, day, station_id, hour, minute, second)
    local_filename = url.split('/')[-1]
    
    # Note: We're using 'requests' here, but in a real-world scenario, you might want to 
    # add error handling or use a more robust method to download large files.
    response = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # Filter out keep-alive new chunks
                f.write(chunk)
                
    print(f"Downloaded {url} to {local_filename}")
    return local_filename

# Test example
download_nexrad_data(2015, 3, 3, 0, 10, 'KABX')
