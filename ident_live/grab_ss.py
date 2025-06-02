



import sys,os, pickle, logging
import requests, json

import librosa

from marlin_data.marlin_data import MarlinDerivedData
from marlin_data.marlin_data import MarlinDataStreamer
from marlin_data.marlin_data import MarlinData

print ("Downloading data")

ss_id = sys.argv[1]
location = sys.argv[2]
locations = []
ss_ids  = []

ss_ids.append(f'{ss_id}')
locations.append(location)

print (ss_id)


url = f'https://vixen.hopto.org/rs/api/v1/data/snapshot/serialdata/{ss_id}'

r = requests.get(url)


rj = r.json()
raw_data = json.loads(rj['data'][0]['raw_data'])
sample_rate =  (raw_data['sample_rate'])
wav_source = raw_data['sample_sound_url']
# print (r.json()['data'][0]['raw_data'])

# download url
r = requests.get(wav_source, allow_redirects=True, stream=True)
total_length = r.headers.get('content-length')
# save_filepath = f'{download_path}/{fid}'


f = open(f'{ss_id}.wav', 'wb')
dl = 0
total_length = int(total_length)
for data in r.iter_content(chunk_size=2000):
    dl += len(data)
    f.write(data)
    done = int(50* dl / total_length)
    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
    sys.stdout.flush()

sys.stdout.flush()
