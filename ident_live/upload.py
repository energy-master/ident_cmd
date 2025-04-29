#!/usr/bin/env python3

import requests, json, sys

# API URL
api_url = f'https://marlin-network.hopto.org/cgi-bin/upload_acoustic.php'

# Parameters required for the API
# filename and location values are read in from the command line and allows for batch runs

filename    =   sys.argv[1] #must be full path (e.g. /home/user/data/_YYYYMMDD_HHMMSS_000.wav) Also note format of acoustic file
location    =   sys.argv[2]
user_uid    =   '0001vixen'
api_key     =   '_marlin_ellen_001'

# open the file stream
file_stream = open(filename,'rb')

# not required - standard headers
headers = {}

# declare post data
post_data = {
    'filename' : filename, 
    'location' : location,
    'api_key' : api_key,
    'user_uid' : user_uid  
}



# create the file upload structure
file_data = {
    'upload_file' : file_stream
}

# send request
r = requests.post(api_url,(post_data), headers, files=file_data)

# read and print the response
if r.json()['error'] == True:
    print (r.json()['error-message'])
else:
    print (r.json()['log'])
    




