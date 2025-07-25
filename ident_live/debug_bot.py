


import sys, requests, re
import csv


import matplotlib
import matplotlib.patches as mpatches
from matplotlib import colormaps
import matplotlib.pyplot as plt
cmap = matplotlib.cm.get_cmap('Spectral')

bot_id = sys.argv[1]
print ("---LOCAL DATA---")
local_decision_path = f'decisions/{bot_id}_decisions.csv'

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
            decision_frames.append(float(d_data[20]))
            decision_y.append(50.0)
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
    


# === correct decisions ===

with open("successful_frames.csv",'r') as fp:
    r = fp.read()



s_frames = r.split(',')
s_frames = s_frames[:-2]
s_frames =  [float(x) for x in s_frames]
s_frames_y = [80] * len(s_frames)
# print (l)
# exit()


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
    print (gid)
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
    if gid in triggers:
        plt.plot(trigger_frames[gid], triggers[gid], 'go', color=rgba, lw=0.2)
    
    rgba = cmap(0.5)
    plt.plot(decision_frames, decision_y, 'go', color=rgba, lw=0.2)
    
    rgba = cmap(0.5)
    plt.plot(s_frames, s_frames_y, 'go', color=rgba, lw=0.1)
    
    
    
    plt.ylabel('% Spike')
    plt.xlabel('Iter #')
    plt.ylim(0,100)
    plt.savefig(f'pc_spike_debug_{gid}.png')
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
    plt.savefig(f'energy_debug_{gid}.png')
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
    plt.savefig(f'ratio_debug_{gid}.png')
    plt.clf()
        


# except:
#     print ("Error with local debug analysis")
