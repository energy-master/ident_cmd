

"""
Gene : Energy Spike gene. Return 1 if True. True if f domain is in range of gene.
Peristent version. 


"""

version = 1.0
print (f"VectorEnergySpikeReject [{version}]")
from marlin_data import *
from marlin_brahma.genes.gene_root import *
import random, json, math
from datetime import timedelta
import statistics

from numba import jit, njit, vectorize
import numpy as np
import time as t
   
from marlin_utils import *
    
# --- optimisation ----

DUMP_PATH = "/Volumes/MARLIN_1"

@njit(nopython=True, cache=True)
def query_stats_freq_index_hyped(frequency_index : int = 0, _time : int = None, data_arr = None ):
    
    #v3.2
    idx_value = np.argmin(np.abs(data_arr[frequency_index] - _time))
    return (idx_value)
    

@njit(nopython=True, cache=True)
def query_closest_idx( value : float = None, data_arr = None ):
    
    #v3.2
    idx_value = np.argmin(np.abs(data_arr - value))
    return (idx_value)
      
# --- end optimisation ----

class VectorEnergySpikeReject(ConditionalRoot):
  
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    #print (gene_args)
    super().__init__(condition='VectorEnergySpikeReject', env=env)
    
    
    max_memory = gene_args['max_memory']
    
    
    min_freq = gene_args['f_min']
    max_freq = gene_args['f_max']
    min_threshold = gene_args['spike_energy_min']
    max_threshold = gene_args['spike_energy_max']
    center_threshold_bound = float(min_threshold + ((max_threshold-min_threshold)/2))
    
    self.memory = random.uniform(500 , max_memory) # ms
    self.memory_ref =  random.uniform(500 , max_memory) # ms
    self.frequency = math.floor(random.uniform(min_freq , max_freq))   
    # self.frequency = 130000
    # print (min_freq, max_freq, self.frequency)
    # self.energy_threshold = random.uniform(0.01, 0.15)  
    self.energy_threshold_lower = random.uniform(min_threshold,center_threshold_bound) 
    self.energy_threshold_upper = random.uniform(center_threshold_bound,max_threshold)
    # self.energy_threshold_lower = 7
    # self.energy_threshold_upper = self.energy_threshold_lower + 5
    # self.memory = 2000
    # self.memory_ref = 500
    self.energy_tracker = []
    self.energy_tracker_ref = []
    self.ratio_threshold = 1.05
    
    
  def __str__(self):
    description = {}
    overview = super().__str__()
    
    data = {
        "decision type" : "VectorEnergySpikeReject",
        "frequency index" : self.frequency,
        "energy_threshold_lower" : self.energy_threshold_lower,
       
        "memory_ref" : self.memory_ref,
        "memory" : self.memory
    }
    
    description['overview'] = overview
    description['data'] = data
    
    return ((description))
    
    
  def GetMemory(self):
    return self.memory
  
  def Reset(self):
    self.energy_tracker = []
    self.energy_tracker_ref = []

  def run(self, data = {}):
    
    
    import math
    
    avg_energy = 0
    timings_on = data['timings']
    owner_id = data['bot_id']
    # get f at timestamps
    derived_data = data['derived_model_data']
    
    iter_start_time = data['iter_end_time']
    stats = None
    geneInit = False
    
    # get frequency index of derived data
    # frequency_index = derived_data.get_index_from_f(self.frequency)
   
    # check init state
    sample_rate = data['sample_rate']
    current_data_index = data['data_index'] 
    current_data_delta_time = (current_data_index/sample_rate) * 1000 # ms
    current_data_delta_time_s = current_data_delta_time / 1000
    self.Start()
    self.state = 0
    
    if ((current_data_delta_time) > self.memory):
        geneInit = True
    
    number_indices_memory = math.floor(self.memory/(data['sim_delta_t']*1000))
    number_indices_ref = math.floor(self.memory_ref/(data['sim_delta_t']*1000))
    
    # get energy and add to tracker
    fourier_e_pivot = 0.0
    fourier_f_idx = query_closest_idx(self.frequency, derived_data.librosa_f_bins)
    fourier_t_idx = query_closest_idx(current_data_delta_time_s, derived_data.librosa_time_bins)
    fourier_e_pivot = derived_data.fourier[fourier_f_idx,fourier_t_idx]
    # print (current_data_delta_time_s)
    # print (fourier_e_pivot)
    if not geneInit:
      self.energy_tracker.append(fourier_e_pivot)
      self.energy_tracker_ref.append(fourier_e_pivot)
      
    # print (self.energy_tracker)
    if geneInit:
        self.Safe()
        
        if self.frequency > derived_data.librosa_f_bins[-1]:
          return 0.0
        
        if timings_on:
          startt(name="mean_attack")
          
        # get average of energy vector
        # print (number_indices_memory,number_indices_ref)
        # print (len(self.energy_tracker), len(self.energy_tracker_ref))
        # print ((len(self.energy_tracker)-number_indices_memory),(len(self.energy_tracker_ref)-number_indices_ref))
        # exit()
        avg_energy = statistics.mean(self.energy_tracker[(len(self.energy_tracker)-number_indices_memory): ])
        avg_energy_ref = statistics.mean(self.energy_tracker_ref[(len(self.energy_tracker_ref)-number_indices_ref): ])
        
        if timings_on:
          stopt(desc="mean_attack", out=0)
        
        self.energy_tracker.append(fourier_e_pivot)
        self.energy_tracker_ref.append(fourier_e_pivot)
        # remove first energy
        self.energy_tracker.pop(0)
        self.energy_tracker_ref.pop(0)
        
        # --- USING MARLIN-DATA Frequency Indexing ----       
        delta_f = 0
        # delta_f = abs(fourier_e_pivot - avg_energy)
        delta_f = abs(avg_energy_ref - avg_energy)
        delta_f_pc = (delta_f / (avg_energy))  * 100
        ratio = avg_energy_ref/avg_energy
        #--- debg out --
        file_out = True
        condition = False
        if delta_f_pc < self.energy_threshold_lower:
        # if ratio > self.ratio_threshold:
          condition = True
        
        if file_out:
            outfile_name = f'{owner_id}.csv'
            with open(f'/Users/vixen/rs/dev/ident_live/ident_live/debug/{outfile_name}', 'a+') as f:
                f.write(f'{iter_start_time},{data['global_iter_count']},{avg_energy},{fourier_e_pivot},{delta_f_pc}, {self.frequency}, {self.memory}, {self.energy_threshold_lower},{self.energy_threshold_upper}, {self.i_D}, {condition}, {ratio} \n')
            
        # print (fourier_e_pivot, avg_energy,avg_energy_ref, delta_f_pc, data['global_iter_count'], ratio)
        #--- debg out --
        # print (f'{delta_f_pc} <> {self.energy_threshold_lower}')
        if delta_f_pc < self.energy_threshold_lower:
        # if ratio > self.ratio_threshold:
            # print (f'trigger {delta_f_pc} > {self.energy_threshold_lower}')
            # self.energy_tracker = []
            # self.last_decision = current_data_delta_time
            return 1

        return 0
    
    return 0
  
  def mutate(self, data = {}):
    print ("mutating")
    
    factor = 1
    creep_rate = data['pc_threshold_creep_rate']
    dice = random.uniform(0,1)
    if dice > 0.5:
      self.energy_threshold_lower = self.energy_threshold_lower + (creep_rate*factor)
    else:
      self.energy_threshold_lower = self.energy_threshold_lower - (creep_rate*factor)
    
    dice = random.uniform(0,1)
    if dice > 0.5:
      self.energy_threshold_upper = self.energy_threshold_upper + (creep_rate*factor)
    else:
      self.energy_threshold_upper = self.energy_threshold_upper - (creep_rate*factor)
    
    dice = random.uniform(0,1)
    
    if dice > 0.5:
      self.frequency = self.frequency + (creep_rate*factor)
    else:
      self.frequency = self.frequency - (creep_rate*factor)
      

