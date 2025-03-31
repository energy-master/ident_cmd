

"""
Gene : Energy Spike gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"FrequencyRank [{version}]")
from marlin_data import *
from marlin_brahma.genes.gene_root import *
import random, json, math
from datetime import timedelta

from numba import jit, njit, vectorize
import numpy as np
import time as t
import math
   
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

class FrequencyRank(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
   
    #print (gene_args)
    super().__init__(condition='frequency_rank', env=env)
    
    
    # Get the gene parameters
    min_freq = gene_args['f_min']
    max_freq = gene_args['f_max']
    print (min_freq, max_freq)
    best_rank = gene_args['best_rank']
    worst_rank = gene_args['worst_rank']
   
    # Default memory for feature. (requires warm up)
    self.memory = 2 # ms
    # Get the active frequency
    self.frequency = math.floor(random.uniform(min_freq , max_freq))   
    print (self.frequency)
    # Get the rank threshold ( < is better )
    self.rank_threshold = math.floor(random.uniform(best_rank, worst_rank))

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "FrequencyRank",
        "frequency index" : self.frequency,
        "energy_threshold" : self.rank_threshold,
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
        rank_index = math.inf
        self.Safe()
        
        
        # =================================== LOGIC ===================================
        
        # get time index for discretised data in derived data object

        t_index_arr = np.array(derived_data.discretised_time_index, dtype='float32')
        discrete_data_idx = query_closest_idx(current_data_delta_time_s, t_index_arr)
        
        
        # get sorted frequencies for time step
        sorted_frequencies = derived_data.sorted_frequencies[discrete_data_idx]
       
        # determine rank of feature frequency
        rank_index = query_closest_idx(self.frequency, sorted_frequencies)
      
        
        
        
        
        
        
        
        
        
        
        
        
        
        # =================================== LOGIC ===================================
        
        file_out = False
        if file_out:
            outfile_name = f'{frequency_index}_{self.memory}__deltapower.txt'
            with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
                f.write(f'{iter_start_time} {avg_energy}\n')
            self.Safe()
        
        if rank_index < self.rank_threshold:
            # print (f'trigger {rank_index} < {self.rank_threshold}')
            return 1

        return 0
    # print ("not init")
    return 0
  
  def mutate(self, data = {}):
    
    
    factor = 1
    creep_rate = data['pc_threshold_creep_rate']
    
    self.rank_threshold = self.rank_threshold + (creep_rate*factor)
    
    
      

