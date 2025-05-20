



import sys, requests, re
import csv


import matplotlib
import matplotlib.patches as mpatches
from matplotlib import colormaps
import matplotlib.pyplot as plt
cmap = matplotlib.cm.get_cmap('Spectral')
# -- bot id --
bot_id = sys.argv[1]

# -- number of decisions --
number_decisions_reqd = sys.argv[2]
number_decisions = 0

# -- from --
decisions_path = 'https://marlin-network.hopto.org/mldata/decisions'
energies_path = f'https://marlin-network.hopto.org/mldata/interesting/energies/{bot_id}.dat'

# -- download decisions ---
r_ = requests.get(decisions_path, allow_redirects=True, stream=True) 
html = r_.text   
pattern=r'href=[\'"]?([^\'" >]+)'
decision_files = re.findall(pattern, html)

print ("--- OPTIMISATION DATA ---")

for decision_file in decision_files[5:]:
    
    file_bot_id = '_'.join(decision_file.split('_')[0:3])
    # print (file_bot_id)
    if file_bot_id == bot_id:
        # download csv file
        decision_file_path = f'{decisions_path}/{decision_file}'

        print (decision_file_path)
        r = requests.get(decision_file_path, allow_redirects=True, stream=True)
        decisions_list = r.text.split('\n')
        pretty_decistions = {}
        for d_ in decisions_list:
            d_.strip()
            d_data = d_.split(',')
            if len(d_data) > 1:
                # d_id = d_['decision_id']
                # d_time = d_['Time From']
                if d_data[4].strip() == "Idle":
                    print (f'{d_data[16]}, {d_data[8]} -> {d_data[12]}')

                # for data in d_data:
                #     data.strip()
                
                
                    
            

        
        # <- decision stats ->


energy_profile = []
iter_profile  = [] 
# r_e = requests.get(energies_path, allow_redirects=True, stream=True)
with requests.get(energies_path, stream=True) as r:
    lines = (line.decode('utf-8') for line in r.iter_lines())
    iter_cnt = 0
    for row in csv.reader(lines):
        energy_profile.append(float(row[0]))
        iter_profile.append(float(iter_cnt))
        iter_cnt += 1 
    
        
# === plot optimisation energy profile ===
fig, ax1 = plt.subplots(figsize=(8, 8))


    
rgba = cmap(0.999)
plt.plot(iter_profile, energy_profile,color=rgba)


plt.ylabel('Energy')
plt.xlabel('Iter #')
plt.savefig("profile.png")
plt.clf()


print ("---LOCAL DATA---")
local_decision_path = f'decisions/{bot_id}_decisions.csv'

#r = requests.get(local_decision_path, allow_redirects=True, stream=True)\
with open(local_decision_path,'r') as fp:
    r = fp.read()

decisions_list = r.split('\n')
pretty_decistions = {}
for d_ in decisions_list:
    d_.strip()
    d_data = d_.split(',')
    if len(d_data) > 1:
        # d_id = d_['decision_id']
        # d_time = d_['Time From']
        if d_data[4].strip() == "Idle":
            print (f'{d_data[16]}, {d_data[8]} -> {d_data[12]}')


