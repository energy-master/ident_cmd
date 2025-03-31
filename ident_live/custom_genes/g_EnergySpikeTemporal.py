

"""
Gene : Energy Spike gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergySpikeTemporal [{version}]")
from marlin_data import *
from marlin_brahma.genes.gene_root import *
import random, json, math
from datetime import timedelta

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

class EnergySpikeTemporal(ConditionalRoot):
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
    

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "EnergySpikeTemporal",
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
        
    if geneInit:
        
        # if frequency_index < 0:
        #   return (0.0)
       
        self.Safe()
        
        if self.frequency > derived_data.librosa_f_bins[-1]:
          return 0.0
        
        if timings_on:
          startt(name="fourier_attack")
        fourier_e_pivot = 0.0
        fourier_f_idx = query_closest_idx(self.frequency, derived_data.librosa_f_bins)
        fourier_t_idx = query_closest_idx(current_data_delta_time_s, derived_data.librosa_time_bins)
        fourier_e_pivot = derived_data.fourier[fourier_f_idx,fourier_t_idx]
        
        
        fourier_e_ref = 0.0
        ref_time_s = current_data_delta_time_s-(self.memory/1000)
        fourier_t_idx = query_closest_idx(ref_time_s, derived_data.librosa_time_bins)
        fourier_e_ref = derived_data.fourier[fourier_f_idx,fourier_t_idx]
        
        if timings_on:
          stopt(desc="fourier_attack", out=0)
        
          
        # --- USING MARLIN-DATA Frequency Indexing ---
        # if timings_on:
        #   startt(name="time_vector_selection")
        # # time_v_dim = len(list(derived_data.fast_index_energy_stats[2].keys()))
        # if timings_on:
        #   stopt(desc="time_vector_selection")
        # stats_pivot = None
        # if timings_on:
        #   startt(name="frequency_index_from_value")
        # frequency_index = derived_data.get_index_from_f(self.frequency)
        # if timings_on:
        #   stopt(desc="frequency_index_from_value")
        # iter_start_time_ms = iter_start_time.timestamp() * 1000
        
       
        # if timings_on:
        #   startt(name="main_marlin_data_stat_query")
        
        
        # if timings_on:       
        #   startt(name="get_time_idx_from_vector")
        # time_idx = query_stats_freq_index_hyped(frequency_index, iter_start_time_ms, derived_data.f_index_numpy)
        # if timings_on:
        #   stopt(desc="get_time_idx_from_vector")
        
        # if timings_on:
        #   startt(name="get_search_key_from_time_idx_vector")
        # search_key = derived_data.time_idx_lookup[time_idx]
        # if timings_on:
        #   stopt(desc="get_search_key_from_time_idx_vector")
        # if timings_on:
        #   startt(name="get_stats_from_index_vector")
        # hyped_stats = derived_data.fast_index_energy_stats[frequency_index][search_key]
        # if timings_on:
        #   stopt(desc="get_stats_from_index_vector")
        
        # # Stats 1  
        # stats_pivot = hyped_stats.stats
        
      
        # if timings_on:
        #   stopt(desc="main_marlin_data_stat_query")
        # h_time_start = t.time()
        
        # stats_ref = None
        # memory_ref_time = (iter_start_time - timedelta(milliseconds=self.memory))
        # memory_ref_time_ms = memory_ref_time.timestamp() * 1000
        
        
        # time_idx = query_stats_freq_index_hyped(frequency_index, memory_ref_time_ms, derived_data.f_index_numpy)
        # search_key = derived_data.time_idx_lookup[time_idx]
        # hyped_stats = derived_data.fast_index_energy_stats[frequency_index][search_key]
        # h_time_end = t.time()
        # h_time = h_time_end - h_time_start
        # # Stats 2  
        # stats_ref = hyped_stats.stats
       
        # if 'max_energy' not in stats_ref:
        #   print ('no ref')
        #   return 0
        
        # if 'max_energy' not in stats_pivot:
        #   print ('no pivot')
        #   return 0

        # if stats_pivot == None or stats_ref == None:
        #   print (f'Critical error in index time bounds DM.')
        #   exit()
        #   pass

        # --- USING MARLIN-DATA Frequency Indexing ----
               
        delta_f = 0
        delta_f = abs(fourier_e_pivot - fourier_e_ref)
        delta_f_pc = (delta_f / max(fourier_e_pivot,fourier_e_ref))  * 100
        
        # print (delta_f_pc)
        
        
        # print (avg_energy)
        
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
    
    
      

