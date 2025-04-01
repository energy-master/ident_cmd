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


from pathlib import Path


# === Downlod Features ===
#! Update for model
# -- from --
features_path = 'https://marlin-network.hopto.org/ident/bots_repo'

# -- to --
download_path = '/Users/vixen/rs/dev/ident_live/ident_live/bots_repo'

r_ = requests.get(features_path, allow_redirects=True, stream=True)      




html = r_.text

pattern=r'href=[\'"]?([^\'" >]+)'
folder_ids = re.findall(pattern, html)



for folder in folder_ids[5:]:

    print (f'{features_path}{folder}')
    
    f_ = requests.get(f'{features_path}/{folder}', allow_redirects=True, stream=True)      
    html2 = f_.text

    pattern=r'href=[\'"]?([^\'" >]+)'
    feature_ids = re.findall(pattern, html2)

    # print (f'{download_path}/{folder}')
    
    Path(f'{download_path}/{folder}').mkdir(parents=True, exist_ok=True)
    for fid in feature_ids[5:]:
        features_file_path = f'{features_path}/{folder}/{fid}'
        print (f'Downloading ... {fid}')
        
        # features_file_path = f'{features_path}/{fid}'
    
    
        r = requests.get(features_file_path, allow_redirects=True, stream=True)
        total_length = r.headers.get('content-length')
        save_filepath = f'{download_path}/{folder}{fid}'
        # print (save_filepath)
        

    
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
