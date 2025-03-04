#!/usr/local/bin/python3

""" 

Sample script to run a target against MARLIN acoustic data and view results. Documentation for installation
and execution can be found at https://vixen.hopto.org/rs/marlin/docs/ident/site. 

"""


""" 

Import modules. Python modules required for application.

"""

import json, requests

# === MARLIN DATA MODULE ===
# Import the marlin_data module. This can be found at pypi.org

from marlin_data.marlin_data import *


# Read command line parameters
target = sys.argv[1]
run_id = sys.argv[2]
location = sys.argv[3]
user_uid = sys.argv[4]
start_time = sys.argv[5]
end_time = sys.argv[6]
number_features = int(sys.argv[7])

my_name = "Rahul Tandon"
my_position = "ML Engineer"

# ============== GET SNAPSHOT IDS FROM MARLIN DATA ===================
limit = 100

data_adapter = MarlinData(load_args={'limit': 10})
location_parm = [f'{location}']

print (f'Downloading acoustic data for [{start_time}] -> [{end_time}]')
snapshot_id_list_rtn = data_adapter.download_simulation_snapshots(load_args={"snapshot_type": "simulation", "limit": limit, "location":location_parm, "time_start" : f'{start_time}', "time_end" : f'{end_time}'}, id_only=True)
snapshot_id_list = []
print ("Snaphots downloaded")

for data in snapshot_id_list_rtn:
    snapshot_id_list.append(data['id'])
    print (data['start_time'])
      
snapshot_id_list = snapshot_id_list[:5]
snapshot_list_str = " ".join(snapshot_id_list)


# ============== SEND JOB TO IDent ===================

url = "https://vixen.hopto.org/rs/api/v1/data/forward_sim"
data = {
    'target' : target,
    'run_id' : run_id,
    'number_features' : number_features,
    'location' : location,
    'user_uid' : user_uid,
    'sim_ids' : snapshot_list_str
    
}


print ("sending run request")
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print ("Run complete. Downloading results.")

html_root = f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out'
spec_path = f'{html_root}/spec/{user_uid}_{run_id}.png'
decision_path = f'{html_root}/decisions_{user_uid}_{run_id}.json'

# === spectrogram ===
r = requests.get(spec_path, allow_redirects=True, stream=True)
total_length = r.headers.get('content-length')
filepath = f'{run_id}_spec.png'
f = open(filepath, 'wb')
dl = 0
total_length = int(total_length)

for data in r.iter_content(chunk_size=2000):
    dl += len(data)
    f.write(data)
    done = int(50* dl / total_length)
    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
    sys.stdout.flush()

sys.stdout.flush()

with open(filepath, 'rb') as fr:
    c = fr.read()
    
# === decisions ===

r = requests.get(decision_path, allow_redirects=True, stream=True)
total_length = r.headers.get('content-length')
filepath = f'{run_id}_decisions.png'
f = open(filepath, 'wb')
dl = 0
total_length = int(total_length)

for data in r.iter_content(chunk_size=2000):
    dl += len(data)
    f.write(data)
    done = int(50* dl / total_length)
    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
    sys.stdout.flush()

sys.stdout.flush()

with open(filepath, 'rb') as fr:
    c = fr.read()
    


