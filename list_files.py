import boto3
import botocore

def list_files_for_day(year, month, day, radar_code):
    s3 = boto3.client('s3', region_name='us-east-1', 
                      config=botocore.config.Config(signature_version=botocore.UNSIGNED))  # Note the change here
    
    bucket_name = 'noaa-nexrad-level2'
    prefix = f"{year}/{month:02d}/{day:02d}/{radar_code}/"
    
    result = []
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    for content in response.get('Contents', []):
        result.append(content['Key'])
        
    return result

# Call the function for 2013 Moore, Oklahoma tornado
files = list_files_for_day(2013, 5, 20, 'KTLX')
for file in files:
    print(file)
