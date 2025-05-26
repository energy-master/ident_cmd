
#!/usr/local/bin/python3

import marlin_brahma.world.population as pop

# from custom_decisions import *
from custom_genes import *
from custom_bots import *

from gene_limits import *

# Define location of bespoke genes
GENETIC_DATA_FOLDER_USR = os.path.join('/','Users','vixen', 'rs','dev', 'ident_live','ident_live','custom_genes','')
os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])

# bot save path
bot_path = "bots_test/hc/"

population_size = 1

args = {
        'population_size' : population_size,
        'env' : 'custom_hp',
        'min_number_dna' : 1,
        'max_number_dna' : 1,
        'min_number_genes' : 1,
        'max_number_genes' : 1,
        'max_dna_data_delay' : 10
        
        }


logging.basicConfig(level=logging.DEBUG)
try:
    logging.critical('Building population ')
    population = pop.Population(parms=args, name="synthetic_custom_hc", gene_args = gene_limits)

    logging.critical('Populating')
    population.Populate(species="AcousticBot", args=None)
except Exception as err:
    logging.critical(f'Error building population {err} {type(err)}')


for bot_id, bot_str in population.species.items():
    bot_str.save(save_folder=bot_path)

