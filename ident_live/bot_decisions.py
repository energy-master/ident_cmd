



import sys, requests, re
import csv
import gzip

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
energies_path = f'https://marlin-network.hopto.org/mldata/interesting_beta/energies/{bot_id}.dat'

DUMP_PATH = "/Volumes/MARLIN_1"
GENETIC_DUMP = "/Volumes/MARLIN_1/genetic_dump"
BOT_PATH = "/Users/vixen/rs/dev/ident_live/ident_live/hp_bots"
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





import sys
from dotenv import load_dotenv, dotenv_values
import pickle
import json
import os.path
if model is not None:
    
    
    
    

    bot_fp = f'{BOT_PATH}/{model}/{bot_id}.vixen'

    print (bot_fp)
    try:
        with open(bot_fp,'rb') as bfp:
            bot = pickle.load(bfp)

        bot_structure = (bot.printStr())

        bot_structure_json = json.loads(bot_structure)
        bot_formatted_str = json.dumps(bot_structure_json,indent=10)

        print (bot_formatted_str)
        print ("==================================================================")
        print ("==================================================================")
        print (f'Data acquisition and DM information for {bot_id}')
        try:
            print (bot.training_data_desc)
            print (bot.study_focus)
        except:
            print ("Data not provided")
        print ("==================================================================") 
        print ("==================================================================")
        
    except:
        pass    

attrs = vars(bot)
print(', '.join("%s: %s" % item for item in attrs.items()))

exit()

print ("---LOCAL DATA---")
local_decision_path = f'{DUMP_PATH}/decisions/{bot_id}_decisions.csv'

#r = requests.get(local_decision_path, allow_redirects=True, stream=True)\
decision_frames = []
decision_y = []
try:
    with open(local_decision_path,'r') as fp:
        r = fp.read()



    decisions_list = r.split('\n')
    pretty_decistions = {}
    for d_ in decisions_list:
        d_.strip()
        d_data = d_.split(',')
        
        
        if len(d_data) > 1:
            print (d_data)
            decision_frames.append(float(d_data[20]))
            decision_y.append(50.0)
            # d_id = d_['decision_id']
            # d_time = d_['Time From']
            if d_data[4].strip() == "Idle":
                print (f'{d_data[16]}, {d_data[8]} -> {d_data[12]} {d_data[18]} {d_data[20]}')
except:
    print ("Error with local decision analysis")
    
print ("===LOCAL DEBUG===")
local_debug_path = f'{DUMP_PATH}/debug/{bot_id}.csv'
print (local_debug_path)
# try:
    


# === correct decisions ===


s_frames = []
s_frames_t = []
s_frames_y = []

try:
    with open("successful_frames.csv",'r') as fp:
        r = fp.read()


    s_frames = r.split(',')
    s_frames = s_frames[:-2]
    s_frames =  [float(x) for x in s_frames]
    s_frames_y = [80] * len(s_frames)
    # print (l)
    # exit()
except:
    print ("no local successful frames")


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
triggers = {}
trigger_frames = {}
ratio_v = {}

for d_ in decisions_list:
    d_.strip()
    d_data = d_.split(',')
    
    
    if len(d_data) > 1:
        # t_v.append(d_data[1])
        gene_id = d_data[9].strip()
        # print (d_data)
        condition = d_data[10].strip()
        activity = 0
        if condition == "True":
            activity = 1
            if gene_id in triggers:
                triggers[gene_id].append(float(activity))
                trigger_frames[gene_id].append(float(d_data[1]))
            else:
                triggers[gene_id] = []
                triggers[gene_id].append(float(activity))
                trigger_frames[gene_id] = []
                trigger_frames[gene_id].append(float(d_data[1]))

        
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
        
        if gene_id in ratio_v:
            ratio_v[gene_id].append(float(d_data[11]))
        else:
            ratio_v[gene_id] = []
            ratio_v[gene_id].append(float(d_data[11]))
        
        
        
        
for gid, data in pc_v.items():
    # print (len(data))
    # print (len(t_v[gid]))
    t_vals = t_v[gid]
    upper_vals = u_v[gid]
    lower_vals = l_v[gid]
    
    # -- %
    fig, ax1 = plt.subplots(figsize=(8, 8))
    rgba = cmap(0.999)
    plt.plot(t_vals, data,color=rgba,label=f'{gid}', lw=0.2)
    rgba = cmap(0.2)
    
    plt.plot(t_vals, upper_vals,color=rgba, lw=2.0)
    rgba = cmap(0.6)
    plt.plot(t_vals, lower_vals,color="blue", lw=2.0)
    # print(t_vals)
    # print (decision_frames)
    # print (decision_y)
    rgba = cmap(0.1)
    if gid in trigger_frames:
        plt.plot(trigger_frames[gid], triggers[gid], color=rgba, lw=0.2)
    
    rgba = cmap(0.5)
    plt.plot(decision_frames, decision_y, color=rgba, lw=0.2)
    
    rgba = cmap(0.5)
    plt.plot(s_frames, s_frames_y, color=rgba, lw=0.1)
    
    
    
    plt.ylabel('% Spike')
    plt.xlabel('Iter #')
    plt.ylim(0,100)
    plt.savefig(f'{GENETIC_DUMP}/pc_spike_debug_{gid}.png')
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
    plt.savefig(f'{GENETIC_DUMP}/avg_energy_debug_{gid}.png')
    plt.clf()
    
    # --  e values
    fig, ax1 = plt.subplots(figsize=(8, 8))
    rgba = cmap(0.999)
    plt.plot(t_vals, e_v[gid],color=rgba,label=f'{gid}')
    # rgba = cmap(0.2)
    # plt.plot(t_vals, upper_vals,color=rgba)
    # rgba = cmap(0.6)
    # plt.plot(t_vals, lower_vals,color=rgba)
    plt.ylabel('e')
    plt.xlabel('Iter #')
    plt.savefig(f'{GENETIC_DUMP}/energy_debug_{gid}.png')
    plt.clf()
    
    # --  ratio values
    fig, ax1 = plt.subplots(figsize=(8, 8))
    rgba = cmap(0.999)
    plt.plot(t_vals, ratio_v[gid],color=rgba,label=f'{gid}')
    # rgba = cmap(0.2)
    # plt.plot(t_vals, upper_vals,color=rgba)
    # rgba = cmap(0.6)
    # plt.plot(t_vals, lower_vals,color=rgba)
    plt.ylabel('e')
    plt.xlabel('Iter #')
    
    plt.savefig(f'{GENETIC_DUMP}/ratio_debug_{gid}.png')
    plt.clf()
    
    
        




# # optimisation energy profile
# energy_profile = []
# iter_profile  = [] 
# # print (energies_path)
# # r_e = requests.get(energies_path, allow_redirects=True, stream=True)
# print (energies_path)
# with requests.get(energies_path, stream=True) as r:
#     lines = (line.decode('utf-8') for line in r.iter_lines())
#     iter_cnt = 0
#     for row in csv.reader(lines):
#         energy_profile.append(float(row[0]))
#         iter_profile.append(float(iter_cnt))
#         iter_cnt += 1 
    
        
# # === plot optimisation energy profile ===
# fig, ax1 = plt.subplots(figsize=(8, 8))


    
# rgba = cmap(0.999)
# plt.plot(iter_profile, energy_profile,color=rgba)


# plt.ylabel('Energy')
# plt.xlabel('Iter #')
# plt.savefig(f'op_profile_{bot_id}.png')
# plt.clf()
