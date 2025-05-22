



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

model = None
try:
    model = sys.argv[3]
except:
    print ("No model provided")
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
                    print (f'{d_data[16]}, {d_data[8]} -> {d_data[12]} {d_data[18]}')

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




import sys
from dotenv import load_dotenv, dotenv_values
import pickle
import json
import os.path
if model is not None:
    
    
    
    
    save_filepath = f'{bot_id}.vixen'
    if not os.path.isfile(save_filepath):
        
        features_file_path = f'https://marlin-network.hopto.org/ident/bots_repo/{model}/{bot_id}.vixen'
    
    
        r_ = requests.get(features_file_path, allow_redirects=True, stream=True)
        total_length = r_.headers.get('content-length')
    
    
        f = open(save_filepath, 'wb')
        dl = 0
        total_length = int(total_length)
    
        for data in r_.iter_content(chunk_size=2000):
            dl += len(data)
            f.write(data)
            done = int(50* dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
            sys.stdout.flush()

        sys.stdout.flush()
    
    else:
      # load bot

    # import time as t
    # t.sleep(2)


        bot_fp = f'{bot_id}.vixen'

        # print (bot_fp)
        with open(bot_fp,'rb') as bfp:
            bot = pickle.load(bfp)

        bot_structure = (bot.printStr())

        bot_structure_json = json.loads(bot_structure)
        bot_formatted_str = json.dumps(bot_structure_json,indent=10)

        print (bot_formatted_str)



print ("---LOCAL DATA---")
local_decision_path = f'decisions/{bot_id}_decisions.csv'

#r = requests.get(local_decision_path, allow_redirects=True, stream=True)\
try:
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
                print (f'{d_data[16]}, {d_data[8]} -> {d_data[12]} {d_data[18]} {d_data[20]}')
except:
    print ("Error with local decision analysis")
    
print ("===LOCAL DEBUG===")
local_debug_path = f'debug/{bot_id}.csv'
print (local_debug_path)
# try:
    


with open(local_debug_path,'r') as fp:
    r = fp.read()



decisions_list = r.split('\n')
gene_ids = []
ae_v = {}
e_v = {}
pc_v = {}
u_v = {}
l_v = {}
t_v = {}
for d_ in decisions_list:
    d_.strip()
    d_data = d_.split(',')
    
    
    if len(d_data) > 1:
        # t_v.append(d_data[1])
        gene_id = d_data[9].strip()
        if gene_id in ae_v:
            ae_v[gene_id].append(float(d_data[2]))
        else:
            ae_v[gene_id] = []
            ae_v[gene_id].append(float(d_data[2]))
        
        if gene_id in pc_v:
            pc_v[gene_id].append(float(d_data[4]))
        else:
            pc_v[gene_id] = []
            pc_v[gene_id].append(float(d_data[4]))
        if gene_id in e_v:
            e_v[gene_id].append(float(d_data[3]))
        else:
            e_v[gene_id] = []
            e_v[gene_id].append(float(d_data[3]))
        
        if gene_id in l_v:
            l_v[gene_id].append(float(d_data[7]))
        else:
            l_v[gene_id] = []
            l_v[gene_id].append(float(d_data[7]))
            
        
        if gene_id in u_v:
            u_v[gene_id].append(float(d_data[8]))
        else:
            u_v[gene_id] = []
            u_v[gene_id].append(float(d_data[8]))
            
        if gene_id in t_v:
            t_v[gene_id].append(float(d_data[1]))
        else:
            t_v[gene_id] = []
            t_v[gene_id].append(float(d_data[1]))
        
        
        
        
for gid, data in pc_v.items():
    # print (len(data))
    # print (len(t_v[gid]))
    t_vals = t_v[gid]
    upper_vals = u_v[gid]
    lower_vals = l_v[gid]
    
    
    # -- %
    fig, ax1 = plt.subplots(figsize=(8, 8))
    rgba = cmap(0.999)
    plt.plot(t_vals, data,color=rgba,label=f'{gid}')
    rgba = cmap(0.2)
    plt.plot(t_vals, upper_vals,color=rgba)
    rgba = cmap(0.6)
    plt.plot(t_vals, lower_vals,color=rgba)
    plt.ylabel('% Spike')
    plt.xlabel('Iter #')
    plt.savefig(f'debug_{gid}.png')
    plt.clf()
    
    # -- averge e
    fig, ax1 = plt.subplots(figsize=(8, 8))
    rgba = cmap(0.999)
    plt.plot(t_vals, ae_v[gid],color=rgba,label=f'{gid}')
    # rgba = cmap(0.2)
    # plt.plot(t_vals, upper_vals,color=rgba)
    # rgba = cmap(0.6)
    # plt.plot(t_vals, lower_vals,color=rgba)
    # plt.ylabel('[E]')
    plt.xlabel('Iter #')
    plt.savefig(f'avg_energy_debug_{gid}.png')
    plt.clf()
    
    


# except:
    # print ("Error with local debug analysis")
    
