
#current


import os, sys
import librosa
import random, json
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta, timezone
import pickle
from dotenv import load_dotenv, dotenv_values

from benchmark_config import *
print ('importing io')
from io_custom import *

s_interval = 5

load_dotenv()
config = dotenv_values("/home/vixen/rs/dev/marlin_hp/marlin_hp/marlin_hp.env")

# print (config)

# file paths and BRAHMA -- CUSTOM --\

# add application root to path
app_path = config['APP_DIR']
sys.path.insert(0, app_path)

# add brahma to system path
brahma_path = config['BRAHMA_DIR']
sys.path.insert(0, brahma_path)

# Define location of bespoke genes
GENETIC_DATA_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_genes', '')
os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])

# Define location of bespoke bots
BOT_DATA_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_bots', '')
os.environ['CUSTOM_BOT_FOLDER_USR'] = BOT_DATA_FOLDER_USR
sys.path.insert(0, os.environ['CUSTOM_BOT_FOLDER_USR'])

# Define bespoke decision logic
DECISION_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])

NUMBA_CACHE_DIR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'cache')
os.environ['NUMBA_CACHE_DIR'] = NUMBA_CACHE_DIR
# IMPORT BRAHMA 
# import evolutionary procedures
import marlin_brahma.bots.bot_root as bots
import marlin_brahma.world.population as pop
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.fitness.performance as performance

#import app 
# from marlin_hp.custom_bots.mybots import *
from custom_bots import *
from custom_genes import *
from custom_decisions import *


from game import *





# --------------------------------------------------------------
# --- Setup Class ---                                          |
# --------------------------------------------------------------

class AlgorithmSetup(object):
    """Class to control optimisation algorithm.

    Args:
        object (): root class object
    """     
    def __init__(self, config_file_path : str = "config.json"):
        
        self.args = {}
        
        #load config file
        run_config = None
        with open(config_file_path, 'r') as config_f:
            run_config = json.load(config_f)
            
        if run_config is not None:
           self.args = run_config
      
      
      
def load_bot(bot_path):
    # print ("loading...")
    # print (bot_path)
    file_ptr = open(bot_path, 'rb')
    bot = pickle.load(file_ptr)
    # print(bot)
    return bot     
# --------------------------------------------------------------
# --- Main Application Class ---                               |
# --------------------------------------------------------------

class SpeciesIdent(object):
    """_summary_

    Args:
        object (_type_): _description_
    """    
    def __init__(self, setup : AlgorithmSetup = None):
        self.algo_setup = setup
        id =  random.randint(0,99999)
        self.batch_id = f'brahma_{id}'
        self.population = None
        self.data_feed = None
        self.derived_data = None
        # performance and evaluation
        self.performance = None
        self.algo_setup.args['run_id'] = self.batch_id
        self.loaded_bots = {}
        self.mode = 0
        self.bulk = 0
        self.ss_ids = []
        self.multiple_derived_data = None
        self.multiple_data = -1
    
    def generation_reset(self):
        self.performance = performance.Performance()

    def load_bots(self, filter_data, version="1_0_0", version_time_from="",version_time_to=""):
        # print (filter_data)
        
        url = 'https://vixen.hopto.org/rs/api/v1/data/features'
        post_data = {'market': filter_data, 'version_time_from' : version_time_from, 'version_time_to' : version_time_to}
        
        
        # print (url)
        # print (post_data)
        
        x = requests.post(url, json = post_data)
        data  = x.json()
        number_loaded = 0
        number_read = 0
        
        versions_list  = version.split('/')
        
        
        for key in data["data"]:
            number_read+=1
            bot_id = key['botID']
            
            bot_dir = "/home/vixen/rs/dev/marlin_hp/marlin_hp/bots"
            bot_path = f'{bot_dir}/{bot_id}.vixen'
            # print (bot_path)
            error = False
            # print (f'loading {version}')
            
            

            try:
                bot = load_bot(bot_path)
                # print (bot)
                # exit()
                
                add = True
                    
                for k,v in bot.dNA.items():
                    for kg,vg in v.genome.items():
                        for kgg, vgg in vg.genome.items():
                            if vgg.condition == 'EnergyProfileFluxIndexPersistent':
                                # print (vgg.condition)
                                # add = False
                                continue
                            
                
                
                if hasattr(bot, 'version'):
                    
                    # print (bot)
                    if bot.version not in versions_list:
                        add = False
                        continue
                    else:
                        print (f' hit : v: {bot.version} | {versions_list}')
                        
                
                else:
                    if "1_0_0" != version:
                        add = False
                        continue
                
                if add:
                    print ('adding bot to game')
                    self.loaded_bots[bot_id] = bot
                    number_loaded+=1
                    if number_loaded > float(number_features):
                        break
            except Exception as e:
                error = True
                # print (f'error loading {bot_id} {type(e).__name__}')
                
            if  error == False:
                pass
                # print (f'success loading {bot_id}')
            
            
        
        self.mode = 1
        self.bulk = 1
        print (f'number loaded : {number_loaded}')
        print (f'number read : {number_read}')
        shell_config['number_working_features'] = number_loaded
        
    
    def run(self):
        pass
    
    def build_world(self):
        """Build the population of bots using brahma_marlin. Genes are present in ../genes
        """
        
        try:
            logging.critical('Building population')
            self.population = pop.Population(parms=self.algo_setup.args, name="hp_classifier")
            logging.critical('Building... ')
            self.population.Populate(species="AcousticBot", args = None)
            logging.debug("Population built")
        except Exception as err:
            logging.critical(f"Error building population {err=} {type(err)=}")
        
    def evolve_world(self):
        pass
    
    def output_world(self):
        pass
  

batch_file_names = []
batch_run_ids = []

#from marlin_bot_run import AlgorithmSetup, SpeciesIdent
#import marlin_bot_run
# import marlin data adapter
sys.path.append('/home/vixen/rs/dev/marlin_data/marlin_data')
from marlin_data import *

filename    =   sys.argv[1]
target      =   sys.argv[2]
location    =   sys.argv[3]
user_uid    =   sys.argv[4]
user_activation_level = sys.argv[5]
user_threshold_above_e = sys.argv[6]
number_features = sys.argv[7]
user_similarity_threshold = sys.argv[8]
feature_version = sys.argv[9]
time_version_from = ""
time_version_to = ""
if len(sys.argv) >= 11:
    time_version_from = f'{sys.argv[10]} {sys.argv[11]}'
if len(sys.argv) >= 12:
    time_version_to = f'{sys.argv[12]} {sys.argv[13]}'


filename_ss_id = ""
batch_id = ""
print (sys.argv)
print (len(sys.argv))
if len(sys.argv) >= 15:
    batch_run_number = sys.argv[14]
    

    for i in range(0,batch_run_number):
        filename_ss_id = sys.argv[14+i].split('_')[0]
        batch_file_names.append(filename_ss_id)
        # batch_id = sys.argv[14+i].split('_')[1]
        batch_run_ids.append(sys.argv[14+i])
        
else:
    filename_ss_id = filename.split('_')[0]
    batch_file_names.append(filename_ss_id)
    batch_run_ids.append(filename)
    


for filename in batch_run_ids:
    
    filename_ss_id = filename.split('_')[0]

    shell_config = {}
    shell_config['filename']    = sys.argv[1]
    shell_config['target']      = sys.argv[2]
    shell_config['location']    = sys.argv[3]
    shell_config['user_uid']    = sys.argv[4]
    shell_config['user_activation_level'] = sys.argv[5]
    shell_config['user_threshold_above_e'] = sys.argv[6]
    shell_config['number_features'] = sys.argv[7]
    shell_config['similarity_threshold'] = sys.argv[8]
    shell_config['feature_version'] = sys.argv[9]
    shell_config['time_version_from'] = time_version_from
    shell_config['time_version_to'] = time_version_to




    # print (shell_config)

    # sample_rate =   sys.argv[4]

    # get raw_data and sample_rate
    # target file for raw data

    # create new run in db
    send_new_run(filename, target, user_uid, location, json.dumps(shell_config))

    update_run(filename,1.1)
    file_path = f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_data/{filename_ss_id}.wav'
    raw_data, sample_rate = librosa.load(file_path,  sr=int(sample_rate))

    # -- META DATA
    # get sample end time
    # start_time = "140822_155229.000000"
    start_time = "010101_000000.000000"
    start_t_dt = dt.strptime(start_time, '%y%m%d_%H%M%S.%f')
    duration_s = len(raw_data)/sample_rate
    start_t_ms = int(start_t_dt.timestamp()) * 1000
    end_t_dt = start_t_dt + timedelta(seconds=duration_s)
    end_t_ms = int(end_t_dt.timestamp()) * 1000
    end_t_f = end_t_dt.strftime('%y%m%d_%H%M%S.%f')

    print (f'Sample Rate : {sample_rate}')
    print (f'Number of seconds : {duration_s}')
    print (start_t_dt, end_t_dt)
    print (start_t_ms, end_t_ms)
    print (end_t_f)



    meta_data = {
        "snapshot_id":filename_ss_id,
        "data_frame_start": start_time,
        "data_frame_end": end_t_f,
        "listener_location": {"latitude": 0, "longitude": 0}, "location_name"
            : "67149847", "frame_delta_t": 10, "sample_rate": sample_rate, "marlin_start_time": 1408719149000,
        "marlin_end_time": 1408719159000
    }


    # --- now we have the raw data, we need to build the derived data object using marlin_data

    # write the file to the tmp folder

    tmp_stream = f'streamedfile_{filename_ss_id}.dat'
    tmp_meta = f'metadata_{filename_ss_id}.json'

    raw_data.tofile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{tmp_stream}')
    with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{tmp_meta}', 'w') as f:
        json.dump(meta_data, f)



    # split file into x second intervals
    wav_data_idx_start = 0
    wav_data_idx_end = 0

    print (f'sr : {sample_rate}')
    print (f'{filename}')

    src_data_id = filename_ss_id
    cnt = 0
    print (f'{len(raw_data)}')
    delta_f_idx = (sample_rate * s_interval)
    print (delta_f_idx)
    f_start_time = start_time
    f_start_time_dt = start_t_dt
    sim_ids = []

    update_run(filename,1.2)
    while wav_data_idx_end < len(raw_data):
        
        f_end_time_dt = f_start_time_dt +  timedelta(seconds=s_interval)
        f_end_time = f_end_time_dt.strftime('%y%m%d_%H%M%S.%f')
        f_start_time = f_start_time_dt.strftime('%y%m%d_%H%M%S.%f')
        
        wav_data_idx_end = wav_data_idx_start + (sample_rate * s_interval)
        tmp_stream = f'streamedfile_{src_data_id}{cnt}.dat'
        tmp_meta = f'metadata_{filename_ss_id}{cnt}.json'
        
        print (f' {wav_data_idx_start} - > {wav_data_idx_end}')
        print (f'{f_start_time} -> {f_end_time}')
        meta_data = {
            "snapshot_id":f'{src_data_id}{cnt}',
            "data_frame_start": f_start_time,
            "data_frame_end": f_end_time,
            "listener_location": {"latitude": 0, "longitude": 0}, "location_name"
                : "67149847", "frame_delta_t": 10, "sample_rate": sample_rate, "marlin_start_time": 1408719149000,
            "marlin_end_time": 1408719159000
        }

        
        
        raw_data[wav_data_idx_start : wav_data_idx_end ].tofile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{tmp_stream}')
        with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{tmp_meta}', 'w') as f:
            json.dump(meta_data, f)
            
        wav_data_idx_start = wav_data_idx_end
        f_start_time_dt = f_end_time_dt
        sim_ids.append(f'{src_data_id}{cnt}')
        
        cnt+=1
        
    

    print (sim_ids)


    # create the data adapter
    simulation_data_path = f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp'
    data_adapter = MarlinData(load_args={'limit' : 100})

    # # load uploaded data
    # sim_ids = []
    # sim_ids = [filename_ss_id]
    limit = 200


    r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", "limit" : limit,  'ss_ids' : sim_ids})

    data_feed = MarlinDataStreamer()
    data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)


    print ("sim")
    print (data_adapter.simulation_index)







    data_avail = False

    derived_data_use = None
    update_run(filename,1.3)
    if not os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{src_data_id}0.da'):


        s_id = filename_ss_id
        # data_adapter.build_derived_data(n_fft=8192)

        for snapshot in data_feed:
            snapshot_derived_data = None
            # print (snapshot.meta_data)
            s_id = snapshot.meta_data['snapshot_id']
            # print (f'{snapshot.meta_data}')
            if not os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da'):
                update_run(filename,1)
                print (f'Building derived data feed structure {s_id}')
                data_adapter.derived_data = None
                data_adapter.build_derived_data(n_fft=8192)
                snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot,  f_min = 115000, f_max = 145000)
                #add to existing derived data
                
                data_adapter.derived_data.ft_build_band_energy_profile(sample_delta_t=0.01, simulation_data=snapshot,discrete_size = 500)
                #add to multiple derived data holder, too
                data_adapter.multiple_derived_data[s_id] = data_adapter.derived_data
                if derived_data_use == None:
                    derived_data_use = data_adapter.derived_data
                with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'wb') as f:  # open a text file
                    pickle.dump(data_adapter.derived_data, f) # serialize the list

            else:
                update_run(filename,2)
                data_avail = True
                print ("Derived data already available.")
            # # with open(f'{s_id}_.der', 'wb') as f:  # open a text file
            # #     pickle.dump(snapshot_derived_data, f) # serialize the list





        if not data_avail:
            update_run(filename,3)
            print ('saving')
            with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{src_data_id}.da', 'wb') as f:  # open a text file
                pickle.dump(data_adapter.derived_data, f) # serialize the list

    else:
        data_avail = True


    # -- old single file derived data - proved to computationally expensive

    # if data_avail:
    #     update_run(filename,4)
    #     print ("Loading data as saved data available.")
    #     data_adapter.derived_data = None
    #     with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{src_data_id}.da', 'rb') as f:  # open a text file
    #         tmp_derived_data = pickle.load(f) 
    #         data_adapter.derived_data = tmp_derived_data


    # Load saved derived data objects

    max_frequency_index = 0

    tmp_derived_data = None
    if data_avail:
        
        for active_ssid in sim_ids:
        
            with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{active_ssid}.da', 'rb') as f:  # open a text file
                print (f'Building derived data : {active_ssid}')
                data_adapter.derived_data = None
                tmp_derived_data = pickle.load(f)
                #tmp_derived_data.get_max_f_index()
                data_adapter.derived_data = tmp_derived_data
                #print(tmp_derived_data.fast_index_energy_stats)
                
                max_frequency_index = 0
                for f_index, value in tmp_derived_data.fast_index_energy_stats.items():
                    max_frequency_index = max(f_index, max_frequency_index)
                data_adapter.multiple_derived_data[active_ssid] = tmp_derived_data
                
                if derived_data_use == None:
                    derived_data_use = tmp_derived_data
                
                print (f'max frequency index : {max_frequency_index}')
                print (f'{data_adapter.derived_data.fourier_delta_t}')
                # if max_frequency_index != 59:
                #     print (f'{active_ssid} has incorrect number of frequency indices')
                #     exit()

    for feed in data_feed:
        print (feed.start_time)
        print (feed.end_time)
        env_pressure_length = feed.frequency_ts_np.shape[0]
        print (f'l : {env_pressure_length}')
        
    # exit()
        
    # _f = 136000
    # _t  = dt.strptime('20010101_000002.000', '%Y%m%d_%H%M%S.%f')

    # print ('---')
    # print (_t)
    # print ('---')
    # e , t = data_adapter.derived_data.ft_query_energy_frame(_t, _f)
    # print (f'[1] ft energy frame query at t and f : {e} @ {t}')
    # print ('---')
    # e = data_adapter.derived_data.query_stats_freq_index(40, _t)
    # print (f'[1] stats for f and t : {e}')
    # print ('---')





    # ---- Data has been initialised -----

    # print (data_adapter.derived_data.index_delta_f)
    # print (data_adapter.derived_data.min_freq)
    # print (data_adapter.derived_data.min_freq + (12 * (data_adapter.derived_data.index_delta_f)))




    algo_setup = AlgorithmSetup(config_file_path="/home/vixen/rs/dev/marlin_hp/marlin_hp/config.json")

    application = SpeciesIdent(algo_setup)
    application.ss_ids = sim_ids
    # for env_pressure in marlin_game.game.data_feed:
    application.derived_data = data_adapter.derived_data 
    
    application.data_feed = data_feed
    application.multiple_derived_data = data_adapter.multiple_derived_data
    # ------------------------------------------------------------------
    #
    #   Bot(s) download for forward testing
    #
    # ------------------------------------------------------------------
    update_run(filename,4.5)
    application.load_bots(target, version=feature_version, version_time_from = time_version_from,  version_time_to = time_version_to)
    # exit()
    application.mode = 1
    application.multiple_data = 1
    # create new run in db
    # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))


    #------------------------------------------------------------------
    #
    # World and Data Initialised. Let's play the game.
    #
    #------------------------------------------------------------------

    marlin_game = IdentGame(application, None, activation_level = user_activation_level)
    marlin_game.game_id = filename


    from layer_three import *
    from utils import *

    if application.mode == 1:
        
        update_run(filename,5)
        print("*** START BOT ***")
        
        
        
            
        # show init f dist
        frequency_activity = []
        for feature in list(application.loaded_bots.values()):
            # print (feature.dNA[0].genome)
            for k,v in feature.dNA.items():
                for kg,vg in v.genome.items():
                    for kgg, vgg in vg.genome.items():
                        # if 'frequency_index' in vgg:
                        idx = vgg.frequency_index
                        f = application.derived_data.min_freq + (idx *  (application.derived_data.index_delta_f))
                        frequency_activity.append(f)
        
        
        filename_ = f'/home/vixen/html/rs/ident_app/ident/brahma/out/f_d_{marlin_game.game_id}_init_all.png'
        plot_hist(frequency_activity, filename_)
        # print (filename)
        
        #get total time:
        s_interval = duration_s
        number_runs = math.floor(duration_s / s_interval)
        delta_idx = s_interval * sample_rate
        
        # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))
        end_idx = 0
        
        all_decisions = {}
        
        combined_bulk_energies = {}    
        combined_bulk_times = {}
        combined_active_features = {}
        
        print (f'number_runs {number_runs}')
        # number_runs = 1
        bot_run_time_start = t.time()
        for run_i in range(0,number_runs):
            
        
            
            if run_i == number_runs:
                break
            sub_filename = f'{filename}_{run_i}'
            #send_new_run(sub_filename, target, user_uid, location, json.dumps(shell_config))
            
            start_idx = end_idx
            end_idx = start_idx+delta_idx
            
            marlin_game.active_features = {}
            marlin_game.run_bot_mt(sub_filename=sub_filename, filename=filename) #, start_idx=start_idx, end_idx=end_idx
            
            bot_run_time_end = t.time()
            
            # print (marlin_game.bulk_energies)
            # print (len(marlin_game.bulk_times))
            # print (marlin_game.number_run_idx)
            bots_run_time = bot_run_time_end - bot_run_time_start
            
            for k,v in marlin_game.bulk_energies.items():
                energies_d = v
                for ke, ve in v.items():
                    if k not in combined_bulk_energies:
                        combined_bulk_energies[k] = {}
                        
                    combined_bulk_energies[k][ke+(run_i*(marlin_game.number_run_idx+1))] = ve            

            for k,v in marlin_game.bulk_times.items():
                combined_bulk_times[k+(run_i*(marlin_game.number_run_idx+1))] = v
                
            for k,v in marlin_game.active_features.items():
                combined_active_features[k+(run_i*(marlin_game.number_run_idx+1))] = v
            
            # print (marlin_game.bulk_times)
            for k,v in combined_bulk_energies.items():
                print (f'le : {len(v)}')
                break
        
            for k,v in marlin_game.bulk_energies.items():
                print (f'mge : {len(v)}')
                break
            
            # marlin_game.run_bot()
            
            # save game
            # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{sub_filename}.game', 'wb') as f:
            #     pickle.dump(marlin_game, f)
            
            
            #write all decisions to json
            update_run(sub_filename,11)
            # print (marlin_game.active_features)
            # print (marlin_game.bulk_times)
            # layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
            layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
            
            
            freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times,active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()) )
            
            
            
            
            
            # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{sub_filename}.json', 'w') as fp:
            #     json.dump(layer_3.decisions, fp)
            
            # update_run(sub_filename,12)

            hits = []
            decisions = layer_3.decisions
            a_ratio = layer_3.ratio_active
            print (f't: {len(marlin_game.bulk_times)}')
            print (f'd: {len(layer_3.ratio_active)}')
            print (f'c_t :{len(combined_bulk_times)}')
            print (f'avg: {len(layer_3.avg_energies)}')
            # print (f'c_d :{len(combined_bulk_energies)}')
            
            # for env_pressure in marlin_game.game.data_feed:
            #     # print (env_pressure)

            #     build_spec_upload(env_pressure, sub_filename, hits = hits, decisions = decisions, peak=a_ratio, avg=layer_3.avg_energies, times=marlin_game.bulk_times, pc_above_e = layer_3.pc_above_tracker, f = freq)
                    
            
            
            
            
            # update_run(sub_filename,13)
        
        
        update_run(filename,12)
        update_run(filename,12.1)
        
        # print (combined_bulk_energies)
        
        for k,v in combined_bulk_energies.items():
            print (len(v))
            break
            
        # print (combined_bulk_times)
        # print (len(combined_bulk_times))
        
        marlin_game.bulk_times = combined_bulk_times
        marlin_game.bulk_energies = combined_bulk_energies
        marlin_game.active_features = combined_active_features
        # print (marlin_game.active_features)
        
        
        # ---
        # layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
        # freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times, active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()) )
        
        
        # -----
        # print (len(layer_3.ratio_active))
        # save game
        update_run(filename,12.2)
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{filename}.game', 'wb') as f:
            pickle.dump(marlin_game, f)
        
        
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{filename}.json', 'w') as fp:
        #         json.dump(layer_3.decisions, fp)
                
        # for env_pressure in marlin_game.game.data_feed:
        update_run(filename,12.3)
        print (f'len of t = {len(marlin_game.bulk_times)}')
        build_spec_upload(sample_rate, filename, hits = hits, decisions = layer_3.decisions, peak=layer_3.ratio_active, avg=layer_3.avg_energies, times=marlin_game.bulk_times, pc_above_e = layer_3.pc_above_tracker, f = freq, full_raw_data=raw_data)
                
        update_run(filename,12.4)
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{filename}.json', 'w') as fp:
                json.dump(layer_3.decisions, fp)
        
        
        
        update_run(filename,13)
        print (f'time to run : {bots_run_time}')    
        
        
            
            
    break









---

#!/usr/bin/env/pyhton3

"""
Marlin acoustic dataclasses, data adapter, and streamer. 
c. Rahul Tandon, R.S. Aqua, 2024
E: r.tandon@rsaqua.co.uk

Sumamry of classes: 
============================================

---SignatureData--- : 
A DataClass that defines the labelled data downloaded. Labelled data is defined as data that has been analysed and annotated. The process of
annotating data is performed using Marlin Ident. SignatureData represents s an acoustic snapshot that has been identified as a legitimate member of a validation dateset.

---SimulationData--- : 
A DataClass that defines all the acoustic data held in the acoustic database. SignatureData represents an acoustic snapshot.

---MarlinData--- :
Responsible for connecting to and downloading data from the acoustic database. 

---MarlinDataStreamer--- :
Initialised with pointer to SimulationData downloaded data and provides the iterable allowing to easily iterate over the downloaded data.


v2.0 - live one
"""

API_VERSION = 1
API_SERVER = "https://vixen.hopto.org"
CONTACT_EMAIL = "r.tandon@rsaqua.co.uk"



# --- module imports ---
import re
import glob
import numpy as np
import pandas as pd
import requests, json
import logging
import time as t
from dotenv import load_dotenv, dotenv_values
import os, sys
from dataclasses import dataclass
import random
from tqdm import tqdm as tq
import scipy
from scipy.stats import norm, kurtosis, entropy
# import antropy as ent
# import ms_entropy as me
import librosa
from datetime import datetime as dt
from datetime import timedelta, timezone
# --- environment setup ---
load_dotenv()
config = dotenv_values("data.env")
# --- logging setup ---
logging.basicConfig(level=logging.CRITICAL)
import pickle
# --- define custom parms ---
api_server = API_SERVER
api_version = API_VERSION
contact_email = CONTACT_EMAIL
import math
import statistics



import threading


from itertools import islice

# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

'''
Define data classes. 
'''



@dataclass
class SubDomainFrame:
    """
    Sub domain analysis frame
    - energy profile and stats
   
    """
    frequency_bounds : list[float]
    time_frame : list[dt]
    
    stats : {}
    energy_profile : []


@dataclass
class EnergyFrame:
    """
    Energy data frame. 
   
    """
    
    frequency_bounds : list[float]
    time_frame : list[dt]
    energy_measure : float
    db_measure : float
    id : int
    delta_frequency : float
   
    def __str__(self):
        return (f'{self.frequency_bounds} | {self.time_frame} | {self.energy_measure}')
       
   
   
@dataclass
class SignatureData:
    """
    Signature dataclass. Define acoustic waveform as a numpy array and pandas dataframe. Dataclass defines a acoustic
    snapshot. meta_data defines snapshot.
    """    

    frequency_ts_np : np.array                  # waveform as numpy array
    frequency_ts_pd : pd.DataFrame              # waveform as dataframe
    meta_data : None                            # snapshot definition
    snapshot : bool = True  
    energy_data : list[EnergyFrame]  = None
    start_time : dt = None
    end_time : dt = None
    
    
@dataclass
class SimulationData:
    """
    Signature dataclass. Define acoustic waveform as a numpy array and pandas dataframe. Dataclass defines a acoustic
    snapshot. meta_data defines snapshot.
    """   
     
    frequency_ts_np : np.array                  # waveform as numpy array
    frequency_ts_pd : pd.DataFrame              # waveform as dataframe
    meta_data : None                             # snapshot definition
    snapshot : bool = True
    energy_data : list[EnergyFrame]  = None
    start_time : dt = None
    end_time : dt = None
    

@dataclass
class Multithread:
    """
    Multithread dataclass. Defines data required for multithread compatibility.

  
    """
    mt_snapshot_ids : {}
    number_threads  : int
    
    

'''
Define Classes
'''


class MarlinData(object):
    
    """
    Class to connect and download data from acoustic database.
    """    
    
    def __init__(self, load_args : {} = {}):
        """
        Initialise class object.

        Args:
            load_args (dict, optional): Initialisation arguments : 'limit' | max number of downloads . Defaults to {}.
        """          
    
        self.snapshot_ids = []              # list of signature snapshot ids
        self.sim_snapshot_ids = []          # list of sim snapshot ids
        self.run_ids = []                   # list of run ids
        self.signature_ids = []             # list of signature ids
        self.number_runs = 0                # number of runs in signature data
        self.number_signatures = 0          # number of signatures in data set
        self.number_snapshots = 0           # number of sig snapshots      
        self.number_sim_snapshots = 0       # number of sim snapshots

        self.signature_data = {}            # signature data. Dictionary of SignatureData.
        self.signature_index = []           # index of signature id required as keys
        self.simulation_data = {}           # simulation data. Dictionary of SimulationData.
        self.simulation_index = []          # index of simulation id require as keys
        
        # define default limit
        
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        else:
            self.limit_sig = 5
    
        self.derived_data = None
        self.multiple_derived_data = {}
    
    def init_multithread(self, number_threads, load_args):
        """
        Initialise multithread data. Returns array of snapshot ids discretised into number of threads which can 
        be loaded for download.

        Args:
            number_threads (_type_): _description_
            load_args (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        snapshot_endpoint = "data/snapshot/data/all"
        api_url = f"{api_server}/rs/api/v{api_version}/{snapshot_endpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']
            # number_r = len(request_json_data_signature)
            
        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} | {ex}")

        
        # download_limit = number_r // number_threads
        download_cnt = 0
        thread_counter = 0
        snapshot_id_holder = {}
        snapshot_id_list = []
        number_r = 0
        for snapshot in request_json_data_signature:
            
           
            if 'location' in load_args:
                if snapshot['data_receiver_location_name'] in load_args['location']:
                    number_r += 1
                    snapshot_id_list.append(snapshot['ss_id'])
                    
        
        download_limit = number_r // number_threads
        snapshot_id_list_mt = []
        for snapshot_id in snapshot_id_list:   
            snapshot_id_list_mt.append(snapshot_id)
            download_cnt += 1
            if download_cnt >= download_limit:
                download_cnt = 0
                snapshot_id_holder[thread_counter] = snapshot_id_list_mt
                thread_counter += 1
                
        return_data = Multithread(snapshot_id_holder, thread_counter)
        return return_data
             
    def download_signature_snapshots(self, load_args : {} = {}) -> ({}):
        
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        """Load binary data from RSA server and load into corresponding dataclasses.

        Args:
            load_args (dict, optional): Load arguments. E.g.location contraints. Defaults to {}.

        Returns:
            {}, [] | {key : snapshot_id , value : signature dataclass} , [snapshot_id]
        """   
        
        signature_enpoint = "data/signature"
        api_url = f"{api_server}/rs/api/v{api_version}/{signature_enpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']

        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} | {ex}")

        for signature in request_json_data_signature:
            
             
          
            if signature['snapshot_id'] not in self.snapshot_ids:
                self.snapshot_ids.append(signature['snapshot_id'])
                
            if signature['run_id'] not in self.run_ids:
                self.run_ids.append(signature['run_id'])
                
            if signature['signature_id'] not in self.signature_ids:
                self.signature_ids.append(signature['signature_id'])
            
        
       
        # limit_sig = 5
        limit_sig_cnt = 1
        
        for snapshot_id in self.snapshot_ids:
            
            if limit_sig_cnt > self.limit_sig:
                break
            # -- 
            # We have the signature id now and require snapshot data in order to build metadata, e.g. delta t, time and location id.
            # We now grab all the meta data for the signature
            # --
           
            
            # get the snapshot id of the snapshot xr with signature
            # snapshot_id = signature['snapshot_id']
            snapshot_id = snapshot_id            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/data"
            snapshot_data_signature_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            # print (snapshot_data_signature_url)
            
            
            # make api request
            try:
                
                r_ss = requests.get(snapshot_data_signature_url) 
                request_json_data_snapshot = r_ss.json()['data'][0]
                
                #---
                # Filter Snapshots
                #---
                
                if 'ss_ids' in load_args:
                    if request_json_data_snapshot['ss_id'] not in load_args['ss_ids']:
                        continue
                
                if 'location' in load_args:
                    # print (signature)
                    
                    #print (request_json_data_snapshot['data_receiver_location_name'], load_args['location'])
                    if request_json_data_snapshot['data_receiver_location_name'] not in load_args['location']:
                        
                        continue
            
               
                
                # print (request_json_data_snapshot)
                meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
                
                
            
                
            except Exception as ex:
                logging.debug(f"[marlin_data.py - 2] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    
            # --
            # Get serial data : meta data complete, download and convert the stored serial data
            # --
            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/serialdata"
            snapshot_serial_data_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            # make api request & load
            try:
                
                r_serial = requests.get(snapshot_serial_data_url) 
                
                request_json_serial_data = r_serial.json()['data'][0]
                
                if 'signature_path' not in load_args.keys():
                    
                    load_args['signature_path'] = ""
                
                domain_data_np, domain_data_pd = self.deserial_data(raw_data = request_json_serial_data['json_raw'], path=load_args['signature_path'], meta_data = meta_data)
                # meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
                
                
                sim_data = SignatureData(frequency_ts_np = domain_data_np, frequency_ts_pd = domain_data_pd, meta_data = meta_data)
                
                
              
                self.signature_data[snapshot_id] = sim_data
                
                self.signature_index.append(snapshot_id)
                limit_sig_cnt += 1
                
                
                
                # if domain_data_np or domain_data_pd == None:
                #     logging.debug(f"[marlin_data.py -3] {snapshot_id} Empty serial data file for snapshot raw data.Email {contact_email} ")
                    
                
            except Exception as ex:
                logging.debug(f"[marlin_data.py - 5] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    
            

        # set length parameters
        self.number_runs = len(self.run_ids)
        self.number_snapshots = len(self.snapshot_ids)
        self.number_signatures = len(self.signature_index)
        
        return self.signature_data, self.signature_index
             
    def download_simulation_snapshots(self, load_args = {}) -> ({}):
        """Load binary data from RSA server and load into corresponding dataclasses.

        Args:
            load_args (dict, optional): _description_. Defaults to {}.

        Returns:
            {}, []: {key : snapshot_id , value : simulation dataclass} , [snapshot_id]
        """   
        
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        
        # print ('downloadng')
        # print (load_args)
        
        
        for location in load_args['location']:
            # print (location)
            snapshot_endpoint = f"data/snapshot/data/all/{location}"
            api_url = f"{api_server}/rs/api/v{api_version}/{snapshot_endpoint}"
            # print (api_url)
            request_json_data_snapshots = None
            try:
                r = requests.get(api_url) 
                
                request_json_data_snapshots = r.json()['data']

            except Exception as error:
                logging.critical(f"{error}")
                logging.critical(f"[marlin_data.py] Unable to run all snapshots retrieval api request. Email {contact_email}")
            
            
            if request_json_data_snapshots == None:
                return {0 : "No Data"}
            
            limit_sig_cnt = 1
            for snapshot in request_json_data_snapshots:
                if limit_sig_cnt > self.limit_sig:
                
                    break
                # --
                # Build tag and id trackers for data object
                # --
                # logging.debug(load_args['ss_ids'])
                
                # logging.debug(f'ss_id{snaphsot['ss_id']}')
                # Filter---
            
                if 'ss_ids' in load_args:
                    if snapshot['ss_id'] not in load_args['ss_ids']:
                        
                        continue
                if 'location' in load_args:
                    
                    if snapshot['data_receiver_location_name'] not in load_args['location']:
                        
                        continue
                # ----
                
                if snapshot['ss_id'] not in self.sim_snapshot_ids:
                    self.sim_snapshot_ids.append(snapshot['ss_id'])
                    limit_sig_cnt += 1
                # if snapshot['run_id'] not in self.run_ids:
                #     self.sim_run_ids.append(signature['run_id'])
                    
            
            
        
        for snapshot_id in self.sim_snapshot_ids:
           
            # -- 
            # We have the signature id now and require snapshot data in order to build metadata, e.g. delta t, time and location id.
            # We now grab all the meta data for the signature
            # --
            
            
            
            # get the snapshot id of the snapshot xr with signature
            # snapshot_id = signature['snapshot_id']
            snapshot_id = snapshot_id            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/data"
            snapshot_data_signature_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            
            # make api request
            try:
                r_ss = requests.get(snapshot_data_signature_url) 
                request_json_data_snapshot = r_ss.json()['data'][0]
                
                #filter location
                
                    
                
                meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
               
            except Exception as ex:
                logging.critical(f"[marlin_data.py - 2] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    
            # --
            # Get serial data : meta data complete, download and convert the stored serial data
            # --
            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/serialdata"
            snapshot_serial_data_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            # make api request
            try:
                
                r_serial = requests.get(snapshot_serial_data_url)
                try: 
                    request_json_serial_data = r_serial.json()['data'][0]
                    
                except Exception as ex:
                    logging.critical(f'Exception raised: {ex}')
                    continue
                
                if "success" in r_serial.json()['data'][0]:
                    continue
                    
                if 'simulation_path' not in load_args.keys():
                    load_args['simulation_path'] = ""
                
                domain_data_np, domain_data_pd = self.deserial_data(raw_data = request_json_serial_data['json_raw'], path=load_args['simulation_path'],meta_data= meta_data)
                
                signature_frame_start_dt = dt.strptime(meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
                signature_frame_end_dt = dt.strptime(meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
               
                sig_data = SimulationData(frequency_ts_np = domain_data_np, frequency_ts_pd = domain_data_pd, meta_data = meta_data)
                sig_data.start_time = signature_frame_start_dt
                sig_data.end_time = signature_frame_end_dt
                self.simulation_data[snapshot_id] = sig_data
                self.simulation_index.append(snapshot_id)
                # if domain_data_np or domain_data_pd == None:
                #     logging.debug(f"[marlin_data.py -3] {snapshot_id} Empty serial data file for snapshot raw data.Email {contact_email} ")
                    
                
            except Exception as ex:
                logging.critical(f"[marlin_data.py - 5] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    

        # set lenght parameters
        self.number_sim_snapshots = len(self.sim_snapshot_ids)
        
        return self.simulation_data, self.simulation_index
    
    def get_track_data(self, mmsi : int = 0, lander_loc : str = "", approach_radius : float =0.0, start_time : str = "", end_time : str = ""):
        '''
            Get a list of snapshot ids from mmsi of vessel. approaches. Check validity and XR with existing data. Use Marlin API
        '''
        
        self.approaches = []
        
        lander_pos = {}
        lander_pos['netley'] = {'lat' : 50.871, 'long' : -1.373}
        lander_lat = lander_pos[lander_loc]['lat']
        lander_long = lander_pos[lander_loc]['long']
        
        url = f'https://vixen.hopto.org/rs/api/v1/data/ships/tracks/{mmsi}/target_known/{lander_lat}/{lander_long}/{approach_radius}'
        
        track_data = None
        try:
            r = requests.get(url) 
            track_data = r.json()
            number_approaches = track_data['number_of_approaches']
            number_tracks = track_data['number_tracks']

        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} : {ex}")

        # for each approach create a vector of snapshot ids.
        for approach_id in range(0,number_approaches):
            
            start_time = track_data['approach_profiles'][approach_id][0]['time']
            end_time = track_data['approach_profiles'][approach_id][len(track_data['approach_profiles'][approach_id])-1]['time']
            
            session_id = random.randrange(0,99999)
            
            post_data = {
                "start_time": start_time,
                "end_time": end_time,
                "location": lander_loc,
                "session_id": session_id,
                "track": "true"
            };
           
            
        
            valid_url =url = "https://vixen.hopto.org/rs/api/v1/data/valid/"
            valid_r = requests.post(valid_url, json.dumps(post_data)) 
            valid_data = valid_r.json()
            snapshot_ids = valid_data['snapshot_ids']
            percent_cover = min(valid_data['percentage_complete'], 100)
            
            # build approach profile data
            approach_profile = track_data['approach_profiles'][approach_id]
            
            
            
            self.approaches.append({'snapshot_ids' : snapshot_ids, 'percent_cover' : percent_cover, 'mmsi' : mmsi, 'approach_profile' : approach_profile})

        return self.approaches
    
    def parse_meta(self, snapshot_data : {} = None) -> {}:
        
        """
        Parse query return of snapshot data into metadata

        Returns:
            {}: MetaData of snapshot.
        """        
        
        meta_data = {}
        meta_data['snapshot_id '] = snapshot_data['ss_id']
        meta_data['snapshot_id'] = snapshot_data['ss_id']
        meta_data['data_frame_start'] = snapshot_data['data_frame_start']
        meta_data['data_frame_end'] = snapshot_data['data_frame_end']
        meta_data['listener_location'] = snapshot_data['data_receiver_location']
        meta_data['location_name'] = snapshot_data['data_receiver_location_name']
        meta_data['frame_delta_t'] = snapshot_data['data_delta_time']
        meta_data['sample_rate'] =  snapshot_data['sample_rate']
        
        start_t_dt = dt.strptime(meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        marlin_start_time = start_t_dt.timestamp()
        
        end_t_dt = dt.strptime(meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_end_time = end_t_dt.timestamp()
        
        meta_data['marlin_start_time'] =  int(start_t_dt.timestamp()) * 1000
        meta_data['marlin_end_time'] =  int(end_t_dt.timestamp()) * 1000
        
        #meta_data['marlin_end_time'] = 
        #print (meta_data['data_frame_start'])
        return meta_data
    
    def load_from_path(self, load_args : {} = None):
        # print (load_args)
        load_limit = 5
        load_cnt = 1
        sim_ids = []
        id_filter = False
        if 'limit' in load_args.keys():
            load_limit = load_args['limit']
        
        if 'ss_ids' in load_args.keys():
            id_filter = True
            sim_ids = load_args['ss_ids']
        
        path = load_args['load_path']
        files = glob.glob(f'{path}/*')
        # print (files)
        pat = r'.*\_(.*)\..*'    
        processed_snapshots = []
        snapshot_times = {}
        number_files =  0
        for file in files:
            
            np_data, pd_data, c = (None, None, None)
            
            search_result = re.match(pat, file)
            if search_result == None:
                continue
            snapshot_id = search_result.group(1)
            # print (path)
            # print (snapshot_id)
        
            data_filepath = f'{path}/streamedfile_{snapshot_id}.dat'
            # print (data_filepath)
            
            metadata_filepath = f'{path}/metadata_{snapshot_id}.json'
            
            
            
            if snapshot_id not in processed_snapshots:
                if id_filter:
                    if snapshot_id not in sim_ids:
                        continue    
                processed_snapshots.append(snapshot_id)
                try:
                    with open(data_filepath, 'rb') as fr:
                        c = fr.read()
                    np_data = None
                    pd_data = None 
                    dtype = np.dtype("float32")
                    np_data  = np.frombuffer(c, dtype=dtype)
                    pd_data = pd.DataFrame(np_data)
                    fr.close()
                    
                    with open(metadata_filepath, 'rb') as fr:
                        meta_data = json.load(fr)
                    
                    
                    
                    
                    # time considerations
                    start_t_dt = dt.strptime(meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
                    snapshot_times[start_t_dt] = snapshot_id
                    
                    end_t_dt = dt.strptime(meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
                    #print (meta_data['data_frame_end'], end_t_dt)
                   
                
                    
                    if ('marlin_start_time' not in meta_data):
                        meta_data['marlin_start_time'] =  int(start_t_dt.timestamp()) * 1000
                    
                    if ('marlin_end_time' not in meta_data):
                        meta_data['marlin_end_time'] =  int(end_t_dt.timestamp()) * 1000
                    
                    if load_args['snapshot_type'] == "simulation":
                        
                        sig_data = SimulationData(frequency_ts_np = np_data, frequency_ts_pd = pd_data, meta_data = meta_data, start_time=start_t_dt, end_time=end_t_dt)
                        self.simulation_data[snapshot_id] = sig_data
                        # self.simulation_index.append(snapshot_id)
                        
                    else:
                        
                        sig_data = SignatureData(frequency_ts_np = np_data, frequency_ts_pd = pd_data, meta_data = meta_data,  start_time=start_t_dt, end_time=end_t_dt)
                        self.signature_data[snapshot_id] = sig_data
                        # self.signature_index.append(snapshot_id)
            
                except Exception as ex:
                    print(ex)
                    
                load_cnt += 1
                # if load_cnt >= load_limit:
                #     break
            number_files += 1
        # rearrange index vector wrt time
        
        
        # self.simulation_index = []
        # self.signature_index = []
        
        dates_sorted = sorted(snapshot_times.keys())
        # print (f'{number_files} loaded.')
        # print (f'load limit {load_limit}')
        for time_ in dates_sorted[0:load_limit]:
            
            if load_args['snapshot_type'] == "simulation":
                
                snapshot_id = snapshot_times[time_]
                self.simulation_index.append(snapshot_id)
                
                
                
            if load_args['snapshot_type'] == "signature":
                snapshot_id = snapshot_times[time_]
                self.signature_index.append(snapshot_id)
                
        res = {}
        
        
        if load_args['snapshot_type'] == "simulation":
            
            _num = len(self.simulation_index)
            # print (f'{_num} snapshots loaded. Limit : {load_limit}')
            _times = len(snapshot_times.keys())
            _ss = len(self.simulation_data.keys())
            # print (f'{_times} | {_ss}')
            res['number snapshots'] = _ss
            res['number times'] = _times
            res['index size'] = _num
        # for id, time in snapshot_times.items():
        #     print (time)
        
        if load_args['snapshot_type'] == "signature":
            _num = len(self.signature_index)
            # print (f'{_num} snapshots loaded. Limit : {load_limit}')
            _times = len(snapshot_times.keys())
            _ss = len(self.signature_data.keys())
            # print (f'{_times} | {_ss}')
            res['number snapshots'] = _ss
            res['number times'] = _times
            res['index size'] = _num
        
        
        
        return res
    
    def build_game(self):
        """
            Add signature / labelled data to the simulation mix in order to ensure we have labelled data in the simulation.
        """
        # --- add siganture snapshots to simulation game if not already present
        for sig_snap_id in self.signature_index:
            if sig_snap_id  not in self.simulation_index:
                self.simulation_index.append(sig_snap_id)
                self.simulation_data[sig_snap_id] = self.signature_data[sig_snap_id]
        
        # --- re order snapshot ids into chronological order
        snapshot_times = {}
        for snapshot in self.simulation_index:
            # print (self.simulation_data[snapshot])
            start_t_dt = dt.strptime(self.simulation_data[snapshot].meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
            snapshot_times[start_t_dt] = self.simulation_data[snapshot].meta_data['snapshot_id']
        
        
        dates_sorted = sorted(snapshot_times.keys())
        # clear index
        self.simulation_index = []
        # rebuild index
        
        for time_ in dates_sorted:
            snapshot_id = snapshot_times[time_]
            self.simulation_index.append(snapshot_id)
            
        # print (self.simulation_index)
     
    def deserial_data(self, raw_data : {} = None, path : str = "", meta_data : {} = None) -> (np.array, pd.DataFrame):
        """
        Read/stream remote serial data and load into a readable format / data structure.

        Args:
            raw_data from a snapshot data query from Marlin API

        Returns:
            np.array, pd.DataFrame
        """        
        
        np_data, pd_data, c = (None, None, None)
        
        random_tag = meta_data['snapshot_id']
        # pandas_data = None
        # c = None
        if 'raw_data_url' in raw_data:
            
            
            filepath = ""
            if path == "":
                filepath = f'streamedfile_{random_tag}.dat'
                json_filepath = f'metadata_{random_tag}.json'
            else:
                filepath = f'{path}/streamedfile_{random_tag}.dat' 
                json_filepath =  f'{path}/metadata_{random_tag}.json' 

            with open(json_filepath, 'w') as f_:
                json.dump(meta_data, f_)

            serial_domain_data_fn = raw_data['raw_data_url']
            #print (f'grabbing from [{serial_domain_data_fn}]')
            r = requests.get(serial_domain_data_fn, allow_redirects=True, stream=True)
            
            total_length = r.headers.get('content-length')
            
            print (f"[Marlin Data : Fetching binary data : {serial_domain_data_fn}]")
           
            # f = open(f'streamed_file{random_tag}', 'wb')
            f = open(filepath, 'wb')
            dl = 0
            total_length = int(total_length)
            
            for data in r.iter_content(chunk_size=2000):
                dl += len(data)
                f.write(data)
                done = int(50* dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
                sys.stdout.flush()

            sys.stdout.flush()

            
            # with open(f'streamed_file{random_tag}', 'rb') as fr:
            #     c = fr.read()
            with open(filepath, 'rb') as fr:
                c = fr.read()
                
            dt = np.dtype("float32")
            np_data  = np.frombuffer(c, dtype=dt)
            pd_data = pd.DataFrame(np_data)
            fr.close()

            
        return np_data, pd_data
      
    def build_derived_data(self, n_fft : int = 1024):
        self.derived_data = MarlinDerivedData(n_fft=n_fft)

class MarlinDataStreamer(object):
    """
    Class to connect to MarlinData and provide an iterable for data access.

    
    """   
    def __init__(self):
       
        self.data_feed = {}
        self.data_ids = []
        self.feed_index = -1
        self.data_vec_length = 0
    
    def init_data(self, data_feed : {} = {}, data_ids : [] = []) -> None:
        """_summary_

        Args:
            data_feed ({}, optional): Dataclass structure and key. Defaults to {}.
            data_ids ([], optional): keys. Defaults to [].
        """        
        # initiaslise vector of feed epoch ids
        self.data_ids = data_ids
        
        # initialise the feed dataset
        self.data_feed = data_feed
        
        # determine lenght of data feed
        self.data_vec_length = len(self.data_ids)
        
        # start data feed
        self.feed_index = 0
        
    def get_data(self, data_idx : int = 0):
        return self.data_feed[data_idx]
    
    def __iter__(self):
        return self
        
    def __next__(self):
        
        if self.feed_index >= self.data_vec_length:
            
            self.feed_index = 0
            raise StopIteration
        
        feed_value = self.data_feed[self.data_ids[self.feed_index]]
        self.feed_index += 1
        return feed_value


    #---
    # Filters
    #---

    def init_snapshots_time(self, time_of_interest : dt, search_seconds : int):
        """
        Filter data stream by a time of interest.

        Args:
            time_of_interest (dt): time of interest
            search_seconds (int): buffer time for data stream

        Returns:
            int: 1 for success
        """        
        filtered_data = {}
        filtered_index = []
        
        search_seconds_dt = timedelta(seconds = search_seconds)
        
        
        for key_value in self.data_ids:
        
            # for key_value, data_inst in self.data_feed.items():
            
            data_inst = self.data_feed[key_value]
            
            data_time = data_inst.start_time
        
            delta_time = abs(time_of_interest - data_time).total_seconds()
            # print(f'{data_time} | {time_of_interest} | {delta_time}')
            # if delta_time < search_seconds_dt:
            if delta_time<float(search_seconds):
                
                filtered_data[key_value] = data_inst
                filtered_index.append(key_value)
        
        # set feed to filtered data
        self.init_data(filtered_data, filtered_index)
        
        
        return 1

class MarlinDerivedData(object):
    '''
    Define data derived from energy time series
    '''

    def __init__(self, n_fft : int = 2048):
        """
        Initialise Class

        Args:
            n_fft (int, optional): Fourier frame size. Defaults to 1024.
        """
        self.n_fft = n_fft  
        self.energy_frames = []                         # global energy_frames
        self.sample_times = []                          # sample times from fft
        self.model_sample_times = []                    # sample times for model
        self.data_start_time = None                     # time bounds for data
        self.data_end_time = None                       # time bounds for data
        self.number_energy_frames = 0                   # number of energy data frames
       
        self.labelled_data = {}                         # data_structure to xr labelled data with
        
        self.sub_domain_frames = []
        self.power_spectrum = {}
        
        self.fast_index_energy_stats = {}               # frequency bound indexing for optimised energy data
        
        self.spectral_entropy_across_time = {}          # temportal spectral e across all t bins for a f index
        self.spectral_entropy_across_freq = {}          # temportal spectral e across all f bins for a t index
        self.spectral_entropy_f_t = {}
        
        self.fourier = None
        self.fourier_delta_t = 0
        self.fourier_delta_f = 0 
        self.index_delta_t = 0
        self.index_delta_f = 0
        
    def build_derived_data(self, simulation_data : SimulationData = None, f_min : int = 0, f_max : int = 1000):
        """
        

        Args:
            signature_data (SignatureData, optional): _description_. Defaults to None.
        """
        
        '''
        Build derived data from raw energy time series. 
        1. perform fft on dataset -> f and t bins
        '''
        
     
        
        # --- run sft on data --
        raw_data = simulation_data.frequency_ts_np
        # print (raw_data)
        #--- gain ---
        raw_data_ = raw_data * 40 
        # print (raw_data_)
        
        hop_length = self.n_fft // 2
        # logging.critical(f'{raw_data}')
        
        
        
        s = np.abs(librosa.stft(raw_data_, n_fft=self.n_fft, hop_length=hop_length))
        # print (s.shape)
        # print (s[300][2])
        D = s
        
        self.fourier = s
        
        # fft_r = np.abs(librosa.stft(raw_data_, n_fft=self.n_fft, hop_length=hop_length))
        # print (fft_r)
        
        #D = librosa.amplitude_to_db(np.abs(librosa.stft(raw_data_, n_fft=self.n_fft, hop_length=hop_length)), ref=np.max)



        energy = D[300, 2]
        # print (energy)
        
        
        
        # --- get frequemcies and time ranges ---
        
        librosa_time_bins = librosa.frames_to_time(range(0, D.shape[1]), sr=simulation_data.meta_data['sample_rate'], hop_length=(self.n_fft//2), n_fft=self.n_fft)
        print (simulation_data.meta_data['sample_rate'])
        # print (librosa_time_bins)
        print (f'nfft : {self.n_fft}')
        
        librosa_f_bins = librosa.core.fft_frequencies(n_fft=self.n_fft, sr=simulation_data.meta_data['sample_rate'])
        # self.min_f = librosa_f_bins[0]
        # self.max_f = librosa_f_bins[len(librosa_f_bins)-1]
        self.librosa_time_bins=  librosa_time_bins
        # print (self.librosa_time_bins)
      
        self.librosa_f_bins = librosa_f_bins
        df = librosa_f_bins[2]-librosa_f_bins[1]
        dti = librosa_time_bins[2] - librosa_time_bins[1]
        #print (self.min_f, self.max_f)
        
        # print (f'd time : {dti}')
        # print (f'd freq : {df}')
        
        
        self.fourier_delta_t = dti
        self.fourier_delta_f = df
        
        self.dt = dti
        
       
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
       
        # marlin_sample_time_dt = timedelta(seconds = marlin_sample_time)
        
        simulation_data.start_time = signature_frame_start_dt
        simulation_data.end_time = signature_frame_end_dt
        
        
        
        # --- build time reference vector
        librosa_time_bins_dt = list (map(lambda v : signature_frame_start_dt +  timedelta(seconds=v), librosa_time_bins))
        # print (librosa_time_bins)
        # for i in range(1,len(librosa_time_bins)):
        #     print (librosa_time_bins[i]-librosa_time_bins[i-1])
        
        #print (librosa_time_bins_dt)
        
        # librosa_time_bins_dt.sort()
        self.sample_times.extend(librosa_time_bins_dt) 
        self.sample_times.sort()
        self.data_start_time = self.sample_times[0]
        self.data_end_time = self.sample_times[len(self.sample_times)-1]
        # self.build_sample_time_vector(librosa_time_bins)
        # self.sample_times = list(map(lambda i, v : signature_frame_start_dt + timedelta(seconds=((v[i]-v[i-1])/2)),enumerate(librosa_time_bins[1:len(librosa_time_bins)])))
        # self.sample_times = list (map(lambda v : (v[1]-v, enumerate(librosa_time_bins)))
        # # --- build energyframes ---
        
        self.fft_times = []
        
        # iterate over time bins and build energy datastructures
        self.max_freq = 0
        self.min_freq = f_min
        self.max_energy = 0
        self.delta_frequency = 0
        energy_frames = []
        _id = 0
        
        number_fourier_point = 0
        
        tmp_power_vector = []
        for freq_idx in range(1,len(librosa_f_bins)-1):
            # print (librosa_f_bins[len(librosa_f_bins)-1])
            tmp_energy = 0
            tmp_counter = 0
            
            if ((librosa_f_bins[freq_idx]>= f_min) and (librosa_f_bins[freq_idx] <= f_max)):
                self.max_freq = max(self.max_freq, librosa_f_bins[freq_idx] )
                self.min_freq = min(self.min_freq, librosa_f_bins[freq_idx] )
                
                for sample_time_idx in range(0, len(librosa_time_bins)-1):
                    number_fourier_point+=1
                    energy = D[freq_idx, sample_time_idx]
                    
                    #decibal conversion
                    db = 20 * math.log10(abs(energy))
                    
                    tmp_energy+=tmp_energy + energy
                    tmp_counter += 1
                    self.max_energy = max(self.max_energy, energy)
                    
                    sample_time_start = signature_frame_start_dt + timedelta(seconds=librosa_time_bins[sample_time_idx])
                    # sample_time_end = signature_frame_start_dt + timedelta(seconds=librosa_time_bins[sample_time_idx+1])
                    sample_time_end = sample_time_start + timedelta(seconds=self.fourier_delta_t)
                    self.fft_times.append(sample_time_start)
                    # create energy frame
                    delta_f = librosa_f_bins[freq_idx] - librosa_f_bins[freq_idx-1]
                    self.delta_frequency = delta_f
                    ef = EnergyFrame(frequency_bounds=[librosa_f_bins[freq_idx-1], librosa_f_bins[freq_idx]], time_frame=[sample_time_start, sample_time_end], energy_measure=energy, id=_id, delta_frequency = delta_f, db_measure= db)
                    
                    # add energy frame to list of energy frames
                    energy_frames.append(ef)
                    self.energy_frames.append(ef)
                    _id += 1 
                
                avg_energy = tmp_energy/tmp_counter
                tmp_power_vector.append(avg_energy)
        
        
        
        # for ef in self.energy_frames:
        #     print (ef.frequency_bounds[0], ef.time_frame[0])
            
        self.number_energy_frames = len(energy_frames)
        number_freq_frames = len(self.librosa_f_bins)
        number_time_frames = len(self.librosa_time_bins)
       
        
        # print (f'number of fourier points : {number_fourier_point}')
        
        # print (f' Number of energy frames -> {self.number_energy_frames}')
        # print (f' Number of frequency buckets -> {number_freq_frames}') 
        # print (f' Number of time buckets -> {number_time_frames}')  
        
        self.power_spectrum[simulation_data.meta_data['snapshot_id']] = tmp_power_vector
        
        simulation_data.energy_data = energy_frames
        self.number_energy_frames = len(energy_frames)
        
        save_str = {
            'location' :  simulation_data.meta_data['location_name'],
            'snapshot_id' : simulation_data.meta_data['snapshot_id'],
            'meta_data' :  simulation_data.meta_data,
          
            'enegry_vector' : energy_frames,
            'max_f' : f_max,
            'min_f' : f_min
        }
        
        
        return save_str
        
    def build_derived_labelled_data(self, signature_data : SignatureData = None):
        """
        Build structure of signature time frames
        nb. resolution will be an issue here.
        This data structure is used to query validity of decision values in optimisation.
        Args:
            signature_data (SignatureData, optional): _description_. Defaults to None.
        """
        # update time frame of signature
        signature_frame_start_dt = dt.strptime(signature_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(signature_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        signature_data.start_time = signature_frame_start_dt
        signature_data.end_time = signature_frame_end_dt 
        time_bounds = [signature_data.start_time, signature_data.end_time]
        self.labelled_data[str(signature_data.meta_data['snapshot_id'])] = time_bounds
                
    def build_xr_data(self, user_uid = ""):
        
        """
            Here we download all labelled data required and store it in the labelled data structure. Previously, only ss ids where used, but we can now build the label data structure without ss id.
            Labelled data without ss id is scalable and flexible and the preffered methodology. Need to consider how to build game to confirm valid signature / labelled data in simulation
        """
        
        # request the data from DB and build labelled_data stucture
        signature_enpoint = "data/signature"
        api_url = f"{api_server}/rs/api/v{api_version}/{signature_enpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']

        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} | {ex}")

        # print (request_json_data_signature)
        # print (f'user : {user_uid}')
        for data_row in request_json_data_signature:
            
            if user_uid == "":
                
                start_dt =  dt.fromtimestamp(float(data_row['start_time_ms'])/1000)
                # print (start_dt)
                time_bounds = [data_row['start_time_ms'], data_row['end_time_ms']]
                tag = random.random()
                self.labelled_data[tag] = time_bounds
            else:
                if data_row['user_uid'] == user_uid:
                    
                    start_dt =  dt.fromtimestamp(float(data_row['start_time_ms'])/1000)
                    # print (start_dt)
                    time_bounds = [data_row['start_time_ms'], data_row['end_time_ms']]
                    tag = random.random()
                    self.labelled_data[tag] = time_bounds
                        
            
        
        

        logging.info(f"[marlin_data.py]  [1103] XR structure built.")
        
    def build_band_energy_profile(self,sample_delta_t : float = 1000,  simulation_data : SimulationData = None, discrete_size = 200, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        self.delta_t = sample_delta_t
        self.max_energy = 0
        self.min_energy = 1000
        self.max_avg_energy = 0
        
        if sample_delta_t == -1:
            sample_delta_t = self.dt * 3
            print (f'Best temporal resolution mode engaged! {sample_delta_t}')
        
        # print ("Building Energy Profiles")
        
        # iterate over f buckets
        frequency_bound_lower = self.min_freq
        # print (f'min f : {frequency_bound_lower}')
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_sample_time = sample_delta_t  #seconds
        
        # print (self.min_freq,self.max_freq)
        frequency_bound_index = 0
        
        f_hit = False
        t_hit = False
        # print (f'building for : {frequency_bound_lower}, {self.max_freq}')
        
        frequency_bound_index = 0
        
        entropy_time_tracker = {}
        
        
        while frequency_bound_lower < self.max_freq-100:
            
            discrete_bucket_size = min((self.max_freq-frequency_bound_lower ), discrete_size)
            frequency_bound_upper = frequency_bound_lower + discrete_bucket_size
            active_frequency = (frequency_bound_upper + frequency_bound_lower) / 2
            sample_time_start = signature_frame_start_dt
            
            time_bounds_stats = {}
            power_spec_start_idx  = 0
            total_en = 0
            num_t_bins = 0
            time_bound_index = 0
            while sample_time_start < signature_frame_end_dt: 
                
                
                # print (f'{sample_time_start} of {signature_frame_end_dt}')
                
                
                
                
                
                energy_sum = 0
                energy_frames = []
                energy_profile = []
                max_energy = 0
                min_energy = 1000000000
                
                sample_time_end = sample_time_start + timedelta(seconds=sample_delta_t)
                active_sample_time = sample_time_start + timedelta(seconds=(sample_delta_t/2))
                # get raw power spectrum
                s_r = simulation_data.meta_data['sample_rate']
                power_spec_end_idx  = power_spec_start_idx + round(sample_delta_t * s_r)
                snapshot_power_spectrum = simulation_data.frequency_ts_np
                
                
                #e_n = ent.spectral_entropy(simulation_data.frequency_ts_np[power_spec_start_idx:power_spec_end_idx], s_r, method='fft')
                e_n = ent.spectral_entropy(simulation_data.frequency_ts_np[power_spec_start_idx:power_spec_end_idx], s_r, method='fft', normalize=True)
                total_en = total_en + e_n
                #e_n = me.calculate_spectral_entropy(simulation_data.frequency_ts_np[power_spec_start_idx:power_spec_end_idx])
                # print (simulation_data.frequency_ts_np[int(power_spec_start_idx):int(power_spec_end_idx)])
                # print(simulation_data.frequency_ts_np)
                
                power_spec_start_idx = power_spec_end_idx
                number_t_hits = 0
                number_f_hits =0 
                # print (f'{sample_time_start},{sample_time_end}')
                for energy_data in self.energy_frames:
                    # print (energy_data.frequency_bounds)
                    #print (f'searching: {energy_data.time_frame},{energy_data.frequency_bounds}')
                    # print (energy_data.time_frame[0], sample_time_start)
                    # print (energy_data.time_frame[1], sample_time_end)
                    # print ( energy_data.time_frame[0],  energy_data.time_frame[1])
                    # print (sample_time_start, sample_time_end)
                    # exit()
                    avg_frame_f = (energy_data.frequency_bounds[0] + energy_data.frequency_bounds[1]) /2
                    # if energy_data.time_frame[0] >= sample_time_start and energy_data.time_frame[1] <= sample_time_end:
                    if energy_data.time_frame[0] <= active_sample_time and energy_data.time_frame[1] >= active_sample_time:
                        t_hit = True
                        number_t_hits += 1
                        # print (f'active f {active_frequency}')
                       
                        # print (energy_data.frequency_bounds[0])
                        if avg_frame_f >= frequency_bound_lower and avg_frame_f <= frequency_bound_upper: 
                        # if energy_data.frequency_bounds[0] <= active_frequency and energy_data.frequency_bounds[1] >= active_frequency: 
                            f_hit = True
                            number_f_hits += 1
                            energy_frames.append(energy_data)
                           
                    # if energy_data.time_frame[0] >= sample_time_start and energy_data.time_frame[1] <= sample_time_end:
                    #     t_hit = True
                    #     # print (energy_data.frequency_bounds[0])
                    #     if energy_data.frequency_bounds[0] >= frequency_bound_lower and energy_data.frequency_bounds[1] <= frequency_bound_upper: 
                    #         f_hit = True
                    #         energy_frames.append(energy_data)
                            
                            
                number_hits = len(energy_frames)
                # print(f'number hits: {number_hits}')
                # print(f'number t hits: {number_t_hits}')
                # print(f'number f hits: {number_f_hits}')
                
                if number_hits == 0:
                    
                    print ("err")
                    print (sample_time_start)
                    print (frequency_bound_lower)
                    print (f_hit)
                    print (t_hit)
                    print (energy_data)
                    sample_time_start = sample_time_end
                    print (active_frequency)
                    continue
                
                
                
                f_hit = False
                t_hit = False
                energy_sum = 0
                frequency_counter = {}
                for energy_frame in energy_frames:
                    e = abs(energy_frame.energy_measure)
                    max_energy = max(max_energy, e)
                    min_energy = min(min_energy,e)
                    energy_sum += abs(energy_frame.energy_measure)
                    
                    
                    if frequency_bound_index in frequency_counter:
                        frequency_counter[frequency_bound_index].append(e)
                    else:
                        frequency_counter[frequency_bound_index] = []
                        frequency_counter[frequency_bound_index].append(e)
                        
                
                avg_f = math.floor(energy_frame.frequency_bounds[0] + energy_frame.frequency_bounds[1])/2
                # print(f'sum : {energy_sum}')
                
                
                ind_e_profile = []
                
                v = frequency_counter[frequency_bound_index]
                
                # print (v)
                
                avg_energy  = 0
                harmonic    = 0
                median      = 0
                variance    = 0
                kurtosis_value    = 0
                entropy_value = 0
                
                if (len(v) > 2):
                    avg_energy  = statistics.mean(v)
                    harmonic    = statistics.harmonic_mean(v)
                    median      = statistics.median(v)
                    variance    = statistics.variance(v)
                    kurtosis_value    = kurtosis(v)
                    entropy_value = entropy(v)
                    
                
                stdev = 0
                active_f = avg_f
                if len(v) > 2:
                    stdev = statistics.stdev(v)
                
                stats = {
                    'max_energy'    : max_energy,
                    'min_energy'    : min_energy,
                    'mean_energy'   : avg_energy,
                    'stdev'         : stdev,
                    'variance'      : variance,
                    'kurtosis'      : kurtosis_value,
                    'entropy'       : entropy_value,
                    'spectral_entropy' : e_n,
                    'f' : avg_f
                }
                
                # print (stats)
                # update metrics
                self.max_energy = max(self.max_energy, max_energy)
                self.min_energy = min(self.min_energy, min_energy)
                self.max_avg_energy = max(self.max_avg_energy, avg_energy)
                
                # record subdomain frame
                sub_domain_frame= SubDomainFrame([frequency_bound_lower,frequency_bound_upper],[sample_time_start,sample_time_end],stats, v)
                #print(sub_domain_frame.stats)
                self.sub_domain_frames.append(sub_domain_frame)
                time_bounds_stats[sample_time_start] = sub_domain_frame
                
                if time_bound_index in entropy_time_tracker:
                    entropy_time_tracker[time_bound_index] = entropy_time_tracker[time_bound_index] + e_n
                else:
                    entropy_time_tracker[time_bound_index] = e_n
                    
                sample_time_start = sample_time_end
                time_bound_index += 1
                num_t_bins += 1
                
            
            # entropy across all time
            self.spectral_entropy_across_time[frequency_bound_index] = float(total_en/num_t_bins)
            #print (f'spectral e {self.spectral_entropy[frequency_bound_index]}')
            
           
            
            # print (f'time {sample_time_end} complete')
            # print (f'f {frequency_bound_lower} | index: {frequency_bound_index} complete')
            self.fast_index_energy_stats[frequency_bound_index] = time_bounds_stats
            #print (self.fast_index_energy_stats[frequency_bound_index])
            
            #inrement counters
            frequency_bound_index += 1 
            frequency_bound_lower = frequency_bound_upper
        
        # entropy across all f
        
        for e,v in entropy_time_tracker.items():
            self.spectral_entropy_across_freq[e] = float(v/frequency_bound_index)
            #print (self.spectral_entropy_across_freq[e])
        # self.spectral_entropy_across_freq[frequency_bound_index] = float(total_en/num_f_bins)
        # print (f'spectral e {self.spectral_entropy[frequency_bound_index]}')
        # exit()
              
    def ft_build_band_energy_profile(self,sample_delta_t : float = 1000,  simulation_data : SimulationData = None, discrete_size = 200, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        self.number_energy_frames_used = 0
        self.delta_t = sample_delta_t
        self.index_delta_t = sample_delta_t
        self.index_delta_f = discrete_size
        
        query_time_start = t.time()
        
        self.max_energy = 0
        self.min_energy = 1000
        self.max_avg_energy = 0
        
        if sample_delta_t == -1:
            sample_delta_t = self.dt * 3
            print (f'Best temporal resolution mode engaged! {sample_delta_t}')
        
        
        # iterate over f buckets
        frequency_bound_lower = self.min_freq
        # print (f'min f : {frequency_bound_lower}')
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_sample_time = sample_delta_t  #seconds
        
        
        # print (f'sig from {signature_frame_start_dt} -> {signature_frame_end_dt}')
        
        
        # print (self.min_freq,self.max_freq)
        frequency_bound_index = 0
        
        f_hit = False
        t_hit = False
        
        frequency_bound_index = 0
        
        entropy_time_tracker = {}
        self.frequency_index_values = {}
        
        # build indexing
        frequency_bound_lower = self.min_freq
        
        while frequency_bound_lower < self.max_freq:
            # print (f'active f {frequency_bound_lower}')
            sample_time_start = signature_frame_start_dt
            frequency_bound_upper = frequency_bound_lower + discrete_size
            self.fast_index_energy_stats[frequency_bound_index] = {}
            self.frequency_index_values[frequency_bound_index] = []
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_lower)
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_upper)
            time_sub_data = {}
            self.time_index_values = []
            while sample_time_start < signature_frame_end_dt: 
                # (print (f'active f { sample_time_start}'))
                sample_time_end = sample_time_start + timedelta(seconds=sample_delta_t)
                self.time_index_values.append(sample_time_start)
                # build index
                time_sub_data[sample_time_start] = SubDomainFrame([frequency_bound_lower,frequency_bound_upper],[sample_time_start,sample_time_end],{}, [])
                
                sample_time_start = sample_time_end
       
            self.fast_index_energy_stats[frequency_bound_index] = time_sub_data
       
            #inrement counters
            frequency_bound_index += 1 
            frequency_bound_lower = frequency_bound_upper
       
        # print ('f index built')
        idx = 0 
        total_e_frames = len(self.energy_frames) 
        
        
        # fill indexing
        
        for energy_data in self.energy_frames:
            
            status = self.add_to_index(energy_data)
            if (status == 1):
                self.number_energy_frames_used += 1
            # print (f'{idx} of {total_e_frames}')
            idx += 1
        
        

        
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'frames used : {self.number_energy_frames_used} of {self.number_energy_frames}')
        # print (f'adapter build')
        # print (f'index query time {query_time}')


    def accomadate_energy_frames(self,energy_frames=[]):
            # --- fill indexing ---
        query_time_start = t.time()
        total_e_frames = len(energy_frames) 
        idx = 0
        for energy_data in energy_frames:
            # print (energy_data)
            status = self.add_to_index(energy_data)
            if (status == 1):
                self.number_energy_frames_used += 1
            # print (f'{idx} of {total_e_frames}')
            
            idx += 1
        
        

        
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'frames used : {self.number_energy_frames_used} of {self.number_energy_frames}')
        # print (f'adapter build')
        # print (f'index query time {query_time}')


    def ft_mt_build_band_energy_profile(self,sample_delta_t : float = 1000,  simulation_data : SimulationData = None, discrete_size = 200, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        self.number_energy_frames_used = 0
        self.delta_t = sample_delta_t
        self.index_delta_t = sample_delta_t
        self.index_delta_f = discrete_size
        
        query_time_start = t.time()
        
        self.max_energy = 0
        self.min_energy = 1000
        self.max_avg_energy = 0
        
        if sample_delta_t == -1:
            sample_delta_t = self.dt * 3
            print (f'Best temporal resolution mode engaged! {sample_delta_t}')
        
        
        # iterate over f buckets
        frequency_bound_lower = self.min_freq
        # print (f'min f : {frequency_bound_lower}')
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_sample_time = sample_delta_t  #seconds
        
        
        # print (f'sig from {signature_frame_start_dt} -> {signature_frame_end_dt}')
        
        
        # print (self.min_freq,self.max_freq)
        frequency_bound_index = 0
        
        f_hit = False
        t_hit = False
        
        frequency_bound_index = 0
        
        entropy_time_tracker = {}
        self.frequency_index_values = {}
        
        # build indexing
        frequency_bound_lower = self.min_freq
        
        while frequency_bound_lower < self.max_freq:
            # print (f'active f {frequency_bound_lower}')
            sample_time_start = signature_frame_start_dt
            frequency_bound_upper = frequency_bound_lower + discrete_size
            self.fast_index_energy_stats[frequency_bound_index] = {}
            self.frequency_index_values[frequency_bound_index] = []
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_lower)
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_upper)
            time_sub_data = {}
            self.time_index_values = []
            while sample_time_start < signature_frame_end_dt: 
                # (print (f'active f { sample_time_start}'))
                sample_time_end = sample_time_start + timedelta(seconds=sample_delta_t)
                self.time_index_values.append(sample_time_start)
                # build index
                time_sub_data[sample_time_start] = SubDomainFrame([frequency_bound_lower,frequency_bound_upper],[sample_time_start,sample_time_end],{}, [])
                
                sample_time_start = sample_time_end
       
            self.fast_index_energy_stats[frequency_bound_index] = time_sub_data
       
            #inrement counters
            frequency_bound_index += 1 
            frequency_bound_lower = frequency_bound_upper
       
        # print ('f index built')
        idx = 0 
        total_e_frames = len(self.energy_frames) 
        
        
        number_threads = 10
        # print (f'number_index : {total_e_frames}')
        delta_ind = math.floor(total_e_frames/number_threads)
        data_chunks = []
        threads_v = []
        for item in divide_chunks(self.energy_frames,delta_ind):
            data_chunks.append(item)
            l = len(item)
            # print(f'length {l}')
            x = threading.Thread(target=self.accomadate_energy_frames, args=(item,))
            threads_v.append(x)
        
        for thread in threads_v:
            # thread.start()
            # print (thread)
            thread.start()
        
            
        # for i in range(0, number_threads):
            
        #     print (f'thread : {i}')
        #     print (f'start index : {}')
        #     print (f'end index : {}')
        #     x = threading.Thread(target=self.accomadate_energy_frames, args=(0,total_e_frames-1))
        
        
        
        # --- fill indexing ---
        
        # for energy_data in self.energy_frames:
            
        #     status = self.add_to_index(energy_data)
        #     if (status == 1):
        #         self.number_energy_frames_used += 1
        #     print (f'{idx} of {total_e_frames}')
        #     idx += 1
        
        # query_time_end = t.time()
        # query_time = query_time_end - query_time_start
        # print (f'frames used : {self.number_energy_frames_used} of {self.number_energy_frames}')
        # print (f'adapter build')
        # print (f'index query time {query_time}')
        
        # --- fill indexing ---


  
    def add_to_index(self, energy_data):
        
        # print (self.time_index_values[len(self.time_index_values)-1])
        # exit()
        status = 0 # added or not  0: false, 1: true
        
        avg_frame_f = (energy_data.frequency_bounds[0] + energy_data.frequency_bounds[1]) /2
        avg_frame_t = energy_data.time_frame[0] + (((energy_data.time_frame[1])-(energy_data.time_frame[0])) / 2 )
        
        # get f index
        # f_index = min(self.frequency_index_values.keys(), key=lambda x: abs(x[1] -  avg_frame_f))
        # print (f_index)
        
        # get t index
        # t_index = min(self.fast_index_energy_stats[2].keys(), key=lambda x: abs(x -  avg_frame_t))
        #print (t_index)
        f_index = 0
        t_index = 0
        for f, v in self.frequency_index_values.items():
            if avg_frame_f > v[0] and avg_frame_f < v[1]:
                # print (f, v[0], avg_frame_f)
                f_index = f
                break
        msg = ''
        min_delta_t = 1000
        delta_t = abs(avg_frame_t -self.time_index_values[0])
        # for f_index, sub_domain_data in self.fast_index_energy_stats.items():
        for idx in range(0,len(self.time_index_values)-1):
            # delta_t_ = (abs(avg_frame_t -self.time_index_values[idx]))
            # delta_t = min(delta_t, delta_t_)
            # if delta_t == delta_t_:
            #     msg = f'{avg_frame_t} | {self.time_index_values[idx]} : {self.time_index_values[idx+1]} | {idx} | {delta_t} | {self.time_index_values[idx]} -> {self.time_index_values[idx+1]}'
            
            #if avg_frame_t >= (self.time_index_values[idx] - timedelta(milliseconds= 1))  and (avg_frame_t< self.time_index_values[idx+1] + timedelta(milliseconds= 1)):
            if avg_frame_t >= (self.time_index_values[idx])  and (avg_frame_t< self.time_index_values[idx+1] ):
                # print (f'time idx : {idx} value : {self.time_index_values[idx]}')
                t_index = self.time_index_values[idx]
                break
            
        if avg_frame_t >= (self.time_index_values[len(self.time_index_values)-1] ):
        # if avg_frame_t >= (self.time_index_values[len(self.time_index_values)-1] - timedelta(milliseconds= 1)):
            
            # print (f'time idx : {idx} value : {self.time_index_values[idx]}')
            t_index = self.time_index_values[idx+1]
            # break
        
            
        if t_index != 0:
            # print ('idx found')
            subdomain = self.fast_index_energy_stats[f_index][t_index]
            subdomain.energy_profile.append(energy_data.energy_measure)
            # print (f'number in subdomain : {len(subdomain.energy_profile)=}')
            status = 1
            
            avg_energy  = 0
            # harmonic    = 0
            # median      = 0
            # variance    = 0
            # kurtosis_value    = 0
            # entropy_value = 0
            
            v = subdomain.energy_profile
            if (len(subdomain.energy_profile) > 2):
                avg_energy  =   statistics.mean(v)
            #     harmonic    =    statistics.harmonic_mean(v)
            #     median      =   statistics.median(v)
            #     variance    =   statistics.variance(v)
            #     kurtosis_value    = kurtosis(v)
            #     entropy_value = entropy(v)
                
            
            # stdev = 0
            
            # if len(v) > 2:
            #     stdev = statistics.stdev(v)
            
            subdomain.stats = {
                'max_energy'    : max(v),
                'min_energy'    : min(v),
                'mean_energy'   : avg_energy,
            #     'stdev'         : stdev,
            #     'variance'      : variance,
            #     'kurtosis'      : kurtosis_value,
            #     'entropy'       : entropy_value,
            #     'f'             : (energy_data.frequency_bounds[0] + energy_data.frequency_bounds[1])/2
            }
        
           
            
            
        else:
            print (f'no data found for {avg_frame_t} and {avg_frame_f} | f:{f_index} t: {t_index}')
            print (msg)
            # print ("no data")
        
        # if t_index is not 0:
        #     print (self.fast_index_energy_stats[f_index][t_index])
        return status
      
    def query_band_energy_loaded_profile(self, time_start: dt, time_end:dt, frequency_min : float, frequency_max:float):
        
       
        query_time = time_start
        # print (f'frequency max: {frequency_max}')
        # print (f'frequency min: {frequency_min}')
        # print (f'query time  : {query_time}')
        #iterate over frequency bound frames
        query_frames = []
        for domain_frame in self.sub_domain_frames:
            # print (domain_frame.time_frame[0])
            if query_time >= domain_frame.time_frame[0] and query_time <= domain_frame.time_frame[1]:
                
                #print (domain_frame.frequency_bounds[0],domain_frame.frequency_bounds[1] )
                
                #if query_frequency >= domain_frame.frequency_bounds[0] and query_frequency <= domain_frame.frequency_bounds[1]:
                if domain_frame.frequency_bounds[1] >= frequency_min and frequency_min >= domain_frame.frequency_bounds[0] :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                if domain_frame.frequency_bounds[1] >= frequency_max and frequency_max >= domain_frame.frequency_bounds[0] :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                if domain_frame.frequency_bounds[0] >= frequency_min and domain_frame.frequency_bounds[1] <= frequency_max :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                if domain_frame.frequency_bounds[0] >= frequency_min and  domain_frame.frequency_bounds[1] <= frequency_max  :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                    
        data_l = len(query_frames)
        # print (f'found : {data_l}')
        # for f in query_frames:
        #     print (f'{f.frequency_bounds[0]}')
        # print (frequency_min, frequency_max)
        
        return query_frames
    
    def query_energy_frames_at_time(self, _time : dt, data_instance : SimulationData = None):
        """
        
        Query energy frames by frequency bounds. 

        Args:
            time (dt): _description_
            frequency (float): _description_
            data_instance (SimulationData): _description_

        Returns:
              [EnergyFrame]: List of valid energy frames, float : average energy value
        """
        
        energy_frames = []
        if data_instance is not None:
            for energy_data in data_instance.energy_data:
                if _time >= energy_data.time_frame[0] and _time <= energy_data.time_frame[1]:
                    energy_frames.append(energy_data)
        else:
            energy_frames = self.energy_frames
    
        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        
            

        return energy_frames, avg_energy
    
    def query_energy_frames_at_frequency(self, frequency: float, data_instance : SimulationData = None, _time : dt = None):
        """
        
        Query energy frames by frequency bounds and time bounds
    
        Args:
            time (dt): _description_
            frequency (float): _description_
            data_instance (SimulationData): _description_

        Returns:
            [EnergyFrame]: List of valid energy frames, float : average energy value
        """
        
        energy_frames = []
        if _time is not None:
            if data_instance is not None:
                for energy_data in data_instance.energy_data:
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1]  and (energy_data.time_frame[0] <= _time and energy_data.time_frame[1] >= _time):
                        energy_frames.append(energy_data)
            else:
                for energy_data in self.energy_frames:
                    # print (energy_data.frequency_bounds[0],energy_data.frequency_bounds[1] )
                    # print (energy_data.time_frame[0])
                    
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1] and energy_data.time_frame[0] <= _time and energy_data.time_frame[1] >= _time:
                        # print ("here")
                        energy_frames.append(energy_data)
                    
        if _time is None:
            if data_instance is not None:
                for energy_data in data_instance.energy_data:
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1]:
                        energy_frames.append(energy_data)
            
            else:
                for energy_data in self.energy_frames:
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1]:
                        energy_frames.append(energy_data)
    
    
    
        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        return energy_frames, avg_energy
    # def nearest(ts):
    #     # Given a presorted list of timestamps:  s = sorted(index)
    #     i = bisect_left(s, ts)
    #     return min(s[max(0, i-1): i+2], key=lambda t: abs(ts - t))
    def get_max_f_index(self):
        for key, value in self.fast_index_energy_stats.items():
            print (key)
    
    
    def ft_query_energy_frame(self, _time : dt, freq : float):
        # print (self.fft_times[0], self.fft_times[1])
        # print (self.fft_times[len(self.fft_times)-1], self.fft_times[len(self.fft_times)-2])
        # print (self.time_index_values[0], self.time_index_values[len(self.time_index_values)-1])
        # print (self.fast_index_energy_stats[0])
        # exit()
        query_time_start = t.time()

        t_index = min(self.fft_times, key=lambda x: abs(x - _time))
        f_index = min(self.librosa_f_bins, key=lambda x: abs(x -  freq))
        # print (type(self.fft_times), type(self.librosa_f_bins))
        # print (f_index, t_index)
        # print ('---')
       
        f_idx = np.where(self.librosa_f_bins == f_index)[0]
        t_idx = (self.fft_times.index(t_index))
        # # # t_idx = (np.abs(self.fft_times - _time)).argmin()
        # print (f_index, t_index, self.librosa_f_bins[f_idx])
        # print (f_idx, t_idx)
        # print (f_idx, t_idx)
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'index query time {query_time}')
        # print (self.fourier[f_idx, t_idx])
        
        return (self.fourier[f_idx, t_idx], t_index)
        
    def query_stats_freq_index(self, frequency_index : int = 0, _time : dt = None ):
        #v2.0
        query_time_start = t.time()
        if frequency_index in self.fast_index_energy_stats:
            stats_time_vector = self.fast_index_energy_stats[frequency_index]
        else:
            return None
        
        #print (stats_time_vector.keys())
        t_index = min(self.fast_index_energy_stats[frequency_index].keys(), key=lambda x: abs(x - _time))
        # print (_time)
        # print (t_index)
        #print (self.fast_index_energy_stats[frequency_index].keys())
        # print (stats_time_vector[t_index])
        # exit()
        # get time index
        # time_index_list = 
        # print (stats_time_vector[t_index])
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'index query time {query_time}')
        
        return (stats_time_vector[t_index])
    
    def query_stats_vector_freq_index(self, frequency_index : int = 0, _time_start : dt = None, _time_end : dt = None ):
        query_time_start = t.time()
        stats_vector = []
        if frequency_index in self.fast_index_energy_stats:
            stats_time_vector = self.fast_index_energy_stats[frequency_index]
        else:
            return None
        
        
       
        for subdomain, v in stats_time_vector.items():
            
            active_time = (v.time_frame[0]) + ((v.time_frame[1] - v.time_frame[1]) / 2)
            if active_time > _time_start and active_time < _time_end:
                stats_vector.append(v)
            
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'index vector query time {query_time}')
        
        return (stats_vector)
    
    
    
    
    def query_energy_frames_at_frequency_bounds(self, frequency_min: float, frequency_max: float, _time : dt = None):
        """

        Args:
            frequency_min (float): _description_
            frequency_max (float): _description_
            _time (dt, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        query_time_start = t.time()
        energy_frames = []
        if _time is not None:
                # print (f'min_f : {self.min_freq} {self.max_freq}')
                # print (_time)
                t_hit = False
                for energy_data in self.energy_frames:
                    # print (energy_data.time_frame[0], energy_data.time_frame[1])
                    if energy_data.time_frame[0] <= _time and energy_data.time_frame[1] >= _time:
                        t_hit = True
                        if energy_data.frequency_bounds[0] <= frequency_min and energy_data.frequency_bounds[1] >= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                        if  frequency_min >= energy_data.frequency_bounds[0] and energy_data.frequency_bounds[1] >= frequency_min:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        if  frequency_max >= energy_data.frequency_bounds[0] and energy_data.frequency_bounds[1] >= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                        if  frequency_max >= energy_data.frequency_bounds[0] and energy_data.frequency_bounds[1] >= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                        if  energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[1] <= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                       
                        
                        #if domain_frame.frequency_bounds[0] >= frequency_min and domain_frame.frequency_bounds[1] <= frequency_max :
                        #if domain_frame.frequency_bounds[0] >= frequency_min and  domain_frame.frequency_bounds[1] <= frequency_max  :
                        
                    
        if _time is None:
           
                for energy_data in self.energy_frames:
                    if energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[1] <= frequency_max:
                        energy_frames.append(energy_data)
    
    
    
        energy_sum = 0
        db_sum = 0
        data_len = len(energy_frames)
        #print  (f'data length (t): {data_len} fmin : {frequency_min} fmax: {frequency_max} time: {t_hit}')
        for energy_frame in energy_frames:
            # print (energy_frame.energy_measure)
            energy_sum += energy_frame.energy_measure
            db_sum += energy_frame.db_measure
            # print (energy_frame.frequency_bounds[0], energy_frame.frequency_bounds[1])
        
        avg_energy = 0
        avg_energy = energy_sum/max(1,len(energy_frames))
        avg_db = 0
        avg_db = db_sum/max(1,len(energy_frames))
        query_time_end = t.time()
        query_time = query_time_end-query_time_start
        # print (f'time to query data adapter {query_time}')
        
        return energy_frames, avg_energy, avg_db
    
    def query_energy_frames_at_times_bounds(self, time_start: dt, time_end: dt):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_

        Returns:
            _type_: _description_
        """
        
        energy_frames = []
        
           
        for energy_data in self.energy_frames:
            
            
            if energy_data.time_frame[0] >= time_start and energy_data.time_frame[1] <= time_end:
                energy_frames.append(energy_data)


        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        return energy_frames, avg_energy
    
    def query_energy_frequency_time_bounds(self, time_start: dt, time_end: dt, frequency_min: float, frequency_max: float):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        energy_frames = []
        for energy_data in self.energy_frames:
                    
                    if energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[1] <= frequency_max and energy_data.time_frame[0] >= time_start and energy_data.time_frame[1] <= time_end:
                        energy_frames.append(energy_data)
    
        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        return energy_frames, avg_energy
    
    def query_band_energy_profile(self, time_start: dt, time_end:dt, frequency_min : float, frequency_max:float, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        energy_sum = 0
        energy_frames = []
        energy_profile = []
        max_energy = 0
        min_energy = 1000000000
        for energy_data in self.energy_frames:
                    
                    if energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[0] <= frequency_max and energy_data.time_frame[0] >= time_start and energy_data.time_frame[1] <= time_end:
                        
                        energy_frames.append(energy_data)
                        # print (energy_data.time_frame)
    
        energy_sum = 0
        frequency_counter = {}
        for energy_frame in energy_frames:
            e = abs(energy_frame.energy_measure)
            max_energy = max(max_energy, e)
            min_energy = min(min_energy,e)
            energy_sum += abs(energy_frame.energy_measure)
            avg_f = math.floor(energy_frame.frequency_bounds[0] + energy_frame.frequency_bounds[1]/2)
            if avg_f in frequency_counter:
                frequency_counter[avg_f].append(e)
            else:
                frequency_counter[avg_f] = []
                frequency_counter[avg_f].append(e)
            # e_entry = {
            #     'frequency' : energy_frame.frequency_bounds[0],
            #     'energy'    : e
            # }
            # energy_profile.append(e_entry)
        ind_e_profile = []
        
        for f, v in frequency_counter.items():
            
            e_avg = statistics.mean(v)
            harmonic = statistics.harmonic_mean(v)
            median = statistics.median(v)
            stdev = 0
            if len(v) > 2:
                stdev = statistics.stdev(v)
            
            e_entry = {
                'frequency'         : float(f),
                'average_energy'     : float(e_avg),
                'harmonic'          : harmonic,
                'median'            : median,
                'stdev'             : stdev
                
            }
            energy_profile.append(e_entry)
            ind_e_profile.append(e_avg)
            
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        
        if sort:
            energy_profile.sort(key=lambda x: x.frequency, reverse=False)
        
        #f stats
        mode_e_mean     = statistics.mean(ind_e_profile)
        mode_e_stdev    = statistics.stdev(ind_e_profile)
        mode_e_var      = statistics.variance(ind_e_profile)
        
        stats = {
            'max_energy'    : max_energy,
            'min_energy'    : min_energy,
            'avg_energy'    : avg_energy,
            'mean'          : mode_e_mean,
            'stdev'         : mode_e_stdev,
            'variance'      : mode_e_var
        }
        return energy_frames,energy_profile, stats 
    
    def query_label_time(self, time_start: dt, time_end : dt):
        """
        Query for labelled data in a time frame
        Args:
            time_start (dt): _description_
            time_end (_type_): _description_
            dt (_type_): _description_

        Returns:
            _type_: _description_
        """
        xr_data = {"xr":False}
        #math by time rahter than snapshot ids for scalablity / differeing resolutions
        # print(self.labelled_data)
        query_hits = []
        # print (self.labelled_data)
        # exit()
        #print (self.labelled_data)
        for snapshot_id, time_bounds in self.labelled_data.items():
            # print (time_bounds[1])
            # now convert to ms for comparisons
            time_start_ms = dt.timestamp(time_start.replace(tzinfo=timezone.utc)) * 1000
            time_end_ms = dt.timestamp(time_end.replace(tzinfo=timezone.utc)) * 1000
            
            
            # time_start_ms = time_start.timestamp() * 1000
            # time_end_ms = time_end.timestamp() * 1000
            
            
            # print (time_start)
            # print (time_start_ms)
            # print (float(time_bounds[0]))
            # if time_start_ms < float(time_bounds[0]):
            #     print (">")
            # else: 
            #     print ("less")
            # print (dt_stamp * 1000)
            # exit()
            
            if float(time_start_ms) <= float(time_bounds[0]) and float(time_end_ms) >= float(time_bounds[1]):
                
                
                xr_data = {
                    "xr"                : True,
                    "xr_time_start"     : time_start,
                    "xr_time_end"       : time_end,
                    "label_snapshot_id" : snapshot_id
                }
                
                query_hits.append(xr_data)
                return query_hits
                # return (xr_data)
                
            if float(time_start_ms) >= float(time_bounds[0]) and float(time_end_ms) <= float(time_bounds[1]):
                # print (time_start_ms, time_bounds[0], time_end_ms, time_bounds[1])
                
                xr_data = {
                    "xr"                : True,
                    "xr_time_start"     : time_start,
                    "xr_time_end"       : time_end,
                    "label_snapshot_id" : snapshot_id
                }
                query_hits.append(xr_data)
                return query_hits
            
            mid_sig_time = float(time_bounds[0]) + ((float(time_bounds[1])- float(time_bounds[0]))/2)
            mid_iter_time = float(time_start_ms) + ((float(time_end_ms)- float(time_start_ms))/2)
            # print (mid_sig_time, mid_iter_time,abs(mid_sig_time-mid_iter_time) )
            
            if (abs(mid_sig_time-mid_iter_time) < 100):
                xr_data = {
                    "xr"                : True,
                    "xr_time_start"     : time_start,
                    "xr_time_end"       : time_end,
                    "label_snapshot_id" : snapshot_id
                }
                query_hits.append(xr_data)
                return query_hits
    
        # print (time_start,time_end)
        # print (xr_data)        
        
        return query_hits
    
    def query_label_id(self, snapshot_id : str = ""):
        if snapshot_id in self.labelled_data.keys():
            return True
    
    def __str__(self):
        
        return(f'[Max Frequency] : {self.max_freq} [Min Frequency] : {self.min_freq}')
    
    def save(self, args = {}):
        s_id = args['snapshot_id']
        fileName = f'{s_id}.drv'
        saveFile = open(fileName, 'wb')
        pickle.dump(self, saveFile)
        saveFile.close()