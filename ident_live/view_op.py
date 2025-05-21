



import sys, requests, re
import csv


import matplotlib
import matplotlib.patches as mpatches
from matplotlib import colormaps
import matplotlib.pyplot as plt
cmap = matplotlib.cm.get_cmap('Spectral')
# -- bot id --
op_id = sys.argv[1]
single = False
if len(sys.argv) > 2:
    single = True
    active_id = sys.argv[2]
# # -- number of decisions --
# number_decisions_reqd = sys.argv[2]
# number_decisions = 0

# model = None
# try:
#     model = sys.argv[3]
# except:
#     print ("No model provided")
# -- from --
op_data_path = f'https://marlin-network.hopto.org/mldata/{op_id}'
# energies_path = f'https://marlin-network.hopto.org/mldata/interesting/energies/{bot_id}.dat'


print ("--- OPTIMISATION DATA ---")

# -- download decisions ---
# r_ = requests.get(op_data_path, allow_redirects=True, stream=True) 
# html = r_.text   
# pattern=r'href=[\'"]?([^\'" >]+)'
# decision_files = re.findall(pattern, html)
# print (decision_files)
# print ("--- OPTIMISATION DATA ---")

gen_number = 0
bot_fitness_data = {}
while True:
    fp = f'dec_data_{op_id}_{gen_number}.txt'
    fitness_profile = []
    iter_profile  = [] 
    
    # r_e = requests.get(energies_path, allow_redirects=True, stream=True)
    try:
        print (f'{op_data_path}/{fp}')
        with requests.get(f'{op_data_path}/{fp}', stream=True) as r:
            # print (r.status_code)
            if r.status_code =='404':
                break
            # print (f'{op_data_path}/{fp}')
            lines = (line.decode('utf-8') for line in r.iter_lines())
            iter_cnt = 0
            for row in csv.reader(lines):
                bot_id = row[0].split(' ')[0]
                # print (bot_id)
                fitness  = float(row[0].split(' ')[3])
                if fitness > 0:
                    if bot_id in bot_fitness_data:
                        bot_fitness_data[bot_id].append({'iter':gen_number, 'fitness' : fitness})
                    else:
                        bot_fitness_data[bot_id] = []
                        bot_fitness_data[bot_id].append({'iter':gen_number, 'fitness' : fitness})
                                
            gen_number += 1
            # print (gen_number)
            if gen_number > 500:
                break
    except:
        break        
    
# print (bot_fitness_data)
# plot successful bots features
fig, ax1 = plt.subplots(figsize=(8, 8))


number_show = 10
number_bots = 0
for bot_id, data in bot_fitness_data.items():
    
    bot_iters = []
    bot_fitness = []
    for pt in data:
        bot_iters.append(pt['iter'])
        bot_fitness.append(pt['fitness'])
        
    rgba = cmap(float(number_bots/number_show))
    if single is True:
        if bot_id == active_id:
            plt.plot(bot_iters, bot_fitness,color=rgba, label=f'{bot_id}')
    else:  
        plt.plot(bot_iters, bot_fitness,color=rgba, label=f'{bot_id}')

    number_bots += 1
    if number_bots > number_show:
        break

plt.title(f'Bot/Feature Performance {op_id}')
plt.legend(loc="upper left")
plt.ylabel('Bot/Feature Performance')
plt.xlabel('Iter #')
plt.savefig(f'bots_profil_e{op_id}.png')
plt.ylim(-10,100)
plt.show()
plt.clf()



fitness_profile = []
iter_profile  = [] 
# r_e = requests.get(energies_path, allow_redirects=True, stream=True)
with requests.get(f'{op_data_path}/gen_out_best_brahma_36016.txt', stream=True) as r:
    lines = (line.decode('utf-8') for line in r.iter_lines())
    iter_cnt = 0
    for row in csv.reader(lines):
        #print (row)
        
        # energy_profile.append(float(row[0]))
        # iter_profile.append(float(iter_cnt))
        # iter_cnt += 1 
        fitness_profile.append(float(row[0].split(' ')[2]))
        iter_profile.append(float(row[0].split(' ')[1]))
        
# print (fitness_profile)
# === plot optimisation energy profile ===
fig, ax1 = plt.subplots(figsize=(8, 8))


    
rgba = cmap(0.999)
plt.plot(iter_profile, fitness_profile,color=rgba)
plt.title(f'Optimisation Performance {op_id}')

plt.ylabel('Performance')
plt.xlabel('Iter #')
plt.savefig(f'p_profil_e{op_id}.png')
plt.ylim(-10,100)
plt.show()
plt.clf()


