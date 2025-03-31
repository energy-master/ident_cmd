

"""
Gene : Energy Spike gene. Return 1 if True. True if f domain is in range of gene.
Peristent version. 


"""

version = 1.1
print (f"EnergySpikeTemporalPersistent [{version}]")
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

class EnergySpikeTemporalPersistent(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    #print (gene_args)
    super().__init__(condition='energy_spike_temporal', env=env)
    
    
    max_memory = gene_args['max_memory']
    min_freq = gene_args['f_min']
    max_freq = gene_args['f_max']
    min_threshold = gene_args['spike_energy_min']
    max_threshold = gene_args['spike_energy_max']
    
    self.memory = random.uniform(0 , max_memory) # ms
    self.frequency = math.floor(random.uniform(min_freq , max_freq))   
    
    # self.energy_threshold = random.uniform(0.01, 0.15)  
    self.energy_threshold = random.uniform(min_threshold,max_threshold)  
    
    
    self.energy_tracker = []

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "EnergySpikeTemporalPersistent",
        "frequency index" : self.frequency,
        "energy_threshold" : self.energy_threshold,
        "memory" : self.memory
    }
    
    description['overview'] = overview
    description['data'] = data
    
    return ((description))
    


  def run(self, data = {}):
    import math
    avg_energy = 0
    timings_on = data['timings']
    
    
  
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
    
    if current_data_delta_time > self.memory:
        geneInit = True
    
    # get energy and add to tracker
    
    
    
    fourier_e_pivot = 0.0
    fourier_f_idx = query_closest_idx(self.frequency, derived_data.librosa_f_bins)
    fourier_t_idx = query_closest_idx(current_data_delta_time_s, derived_data.librosa_time_bins)
    fourier_e_pivot = derived_data.fourier[fourier_f_idx,fourier_t_idx]
    
    self.energy_tracker.append(fourier_e_pivot)
    
    if geneInit:
        self.Safe()
        
        if self.frequency > derived_data.librosa_f_bins[-1]:
          return 0.0
        
        if timings_on:
          startt(name="mean_attack")
          
        # get average of energy vector
        avg_energy = statistics.mean(self.energy_tracker)
       
        if timings_on:
          stopt(desc="mean_attack", out=0)
        
          
       
        # remove first energy
        self.energy_tracker.pop(0)
        # --- USING MARLIN-DATA Frequency Indexing ----
               
        delta_f = 0
        delta_f = abs(fourier_e_pivot - avg_energy)
        delta_f_pc = (delta_f / max(fourier_e_pivot,avg_energy))  * 100
   
        
        file_out = False
        if file_out:
            outfile_name = f'{frequency_index}_{self.memory}__deltapower.txt'
            with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
                f.write(f'{iter_start_time} {avg_energy}\n')
            self.Safe()
        
        if delta_f_pc > self.energy_threshold:
            # print (f'trigger {delta_f_pc} > {self.energy_threshold}')
            return 1

        return 0
    
    return 0
  
  def mutate(self, data = {}):
    
    
    factor = 1
    creep_rate = data['pc_threshold_creep_rate']
    
    self.energy_threshold = self.energy_threshold + (creep_rate*factor)
    
    
      

