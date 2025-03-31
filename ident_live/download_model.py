#!/usr/local/bin/python3


""" 
1.0
Sample script to run a local data file against MARLIN IDent Live features. Documentation for installation
and execution can be found at https://vixen.hopto.org/rs/marlin/docs/ident/site. 

"""

import os           # import os module
import requests     # import requests module
import re           # import regex module
import sys

# === Downlod Features ===
#! Update for model
# -- from --
features_path = 'https://marlin-network.hopto.org/ident/bots_repo/sonar_n_2_p'

# -- to --
download_path = '/Users/vixen/rs/dev/ident_live/ident_live/bots/sonar_sentropy_1'

r_ = requests.get(features_path, allow_redirects=True, stream=True)      

html = r_.text
pattern=r'href=[\'"]?([^\'" >]+)'
feature_ids = re.findall(pattern, html)


for fid in feature_ids[5:]:
   
    print (f'Downloading ... {fid}')
    features_file_path = f'{features_path}/{fid}'
   
  
    r = requests.get(features_file_path, allow_redirects=True, stream=True)
    total_length = r.headers.get('content-length')
    save_filepath = f'{download_path}/{fid}'
   
   
    f = open(save_filepath, 'wb')
    dl = 0
    total_length = int(total_length)
    for data in r.iter_content(chunk_size=2000):
        dl += len(data)
        f.write(data)
        done = int(50* dl / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
        sys.stdout.flush()

    sys.stdout.flush()


# exit()

# === Downlod Feature Frameworks ===
#! Update for model
# --- from ---
features_path = 'https://marlin-network.hopto.org/ident/features'
# --- to ---
download_path = '/Users/vixen/rs/dev/ident_live/ident_live/custom_genes'

r_ = requests.get(features_path, allow_redirects=True, stream=True)      

html = r_.text


pattern=r'href=[\'"]?([^\'" >]+)'
feature_ids = re.findall(pattern, html)


# print (type(feature_ids))



for fid in feature_ids[5:]:
    print (f'Downloading ... {fid}')
    
    features_file_path = f'{features_path}/{fid}'
   
  
    r = requests.get(features_file_path, allow_redirects=True, stream=True)
    total_length = r.headers.get('content-length')
    save_filepath = f'{download_path}/{fid}'
   
   
    f = open(save_filepath, 'wb')
    dl = 0
    total_length = int(total_length)
    for data in r.iter_content(chunk_size=2000):
        dl += len(data)
        f.write(data)
        done = int(50* dl / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
        sys.stdout.flush()

    sys.stdout.flush()
