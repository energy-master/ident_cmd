#!/usr/local/bin/python3

""" 
1.0
Sample script to run a local data file against MARLIN IDent Live features. Documentation for installation
and execution can be found at https://vixen.hopto.org/rs/marlin/docs/ident/site. 

"""


""" 

Import modules. Python modules required for application.

"""
import  sys
import  os
import  requests
# --- LOGGER ---
from loguru import logger as logger_
logger_.add('learn.log', format="{level} : {time} : {message}: {process}")
logger_.add(sys.stdout, level="TRACE")  
logger_.add("app.log", level="TRACE") 

logger_.trace("Building application logger.")

# --- LIBROSA ---
import  librosa

# --- FANCY CONSOLE & LOGGING ---
from rich.console import Console
console = Console()

# --- IDent Live Application Game ---
# Import the game and application classes.
from game import IdentGame
from ident_application import *

# --- MARLIN DATA MODULE ---
# Import the marlin_data module. This can be found at pypi.org

from marlin_data.marlin_data import *

# --- CUSTOM DECISION MAKING, BOTS/FEATURES, & EVALUATION CODE ---
# Custom genes, decisions and bots must be present and imported here. The application folder structure
# pulled from github will include the required structures. Contact r.tandon@rsaqua if you wish to build
# custom classes and decision making modules.

from custom_decisions import *
from custom_genes import *
from custom_bots import *

# --- MARLIN brahma ---
# Import MARLIN brahma. MARLIN brahma provides the framework for machine learning(ML) and is required to run
# data against features/bots evolved in brahmas ML framework.
import marlin_brahma.fitness.performance as performance
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.world.population as pop
import marlin_brahma.bots.bot_root as bots

import time

# Import some required pyhton modules.
from    dotenv import load_dotenv, dotenv_values
import  pickle
from    datetime import datetime as dt
from    datetime import datetime, timedelta, timezone
import  json
import  random




# --- MAIN Entry ---

if __name__ == "__main__":


    # --- APPLICATION CONFIGURATION ---
    # open environment file
    load_dotenv()
    config = dotenv_values("config.env")
    with open(config['CONFIG_FILE_PATH'], 'r') as config_f:
        app_config = json.load(config_f)

    # Add Application and Data paths to system path
    app_path = config['APP_DIR']
    sys.path.insert(0, app_path)

    data_path = config['DATA_DIR']
    working_path = config['WORKING_DIR']
    features_path = config['FEATURE_DIR']
    out_path = config['OUT_DIR']

    # required for librosa
    NUMBA_CACHE_DIR = os.path.join(
        '/', 'home', 'vixen', 'rs', 'dev', 'marlin_hp', 'marlin_hp', 'cache')
    os.environ['NUMBA_CACHE_DIR'] = NUMBA_CACHE_DIR


    # --- INPUT PARAMETERS -------------------------------------------------------
    
    batch_file_names = []
    batch_run_ids = []
    # Input data file (Rules apply : YYYYMMDD_HHMMSS_FFF.wav)
    filename = sys.argv[1]
    
    # Search target (e.g. harbour_porpoise)
    target = sys.argv[2]
    
    # Location
    location = sys.argv[3]
    
    # User UID ( provided by MARLIN )
    user_uid = sys.argv[4]
    
    # Activation level of probability distribution function
    user_activation_level = sys.argv[5]
    
    # Ratio of features/bots above activation energy. Used in softmax.
    user_threshold_above_e = sys.argv[6]
    
    # Number of features (>1000)
    number_features = sys.argv[7]
    
    # Similarity of structure built by features (no longer is use)
    user_similarity_threshold = sys.argv[8]
    
    # Feature versions (2_0_0/3_0_0)
    feature_version = sys.argv[9]
    
    # Feature/bot birth times
    time_version_from = ""
    time_version_to = ""
    update_features = -1
    if len(sys.argv) >= 11:
        time_version_from = f'{sys.argv[10]} {sys.argv[11]}'
    if len(sys.argv) >= 12:
        time_version_to = f'{sys.argv[12]} {sys.argv[13]}'
        update_features = sys.argv[14]

    if int(update_features) == -1:
        update_features = False
    if int(update_features) == 1:
        update_features = True

    print (f'Update feature / bot list: {update_features}.')
    logger_.info("Update feature / bot list: ")
    
    filename_ss_id = ""
    batch_id = ""

    # Batch operations
    if len(sys.argv) >= 16:
        batch_run_number = sys.argv[15]

        for i in range(0, batch_run_number):
            filename_ss_id = f'{sys.argv[15+i]}_{location}'  # obs
            batch_file_names.append(filename_ss_id)
            batch_run_ids.append(sys.argv[15+i])

    else:
        filename_ss_id = f'{filename}_{location}'  # obs
        batch_file_names.append(filename_ss_id)
        batch_run_ids.append(filename)
        

    # ----------------- INPUT PARAMETERS ---------------------------------



    for filename in batch_run_ids:
        
        # --- INITIALISE RUN ---
        
        file_root = filename.split('.')[0]
        # print(f'root : {file_root}')
        filename_ss_id = f'{file_root}{location}'.replace("_", "")
        # print(f'ss_id : {filename_ss_id}')
        
        rnd_run_tag = random.randint(0,99999999)
        filename_ss_id_rnd  = f'{filename_ss_id}{rnd_run_tag}'

        shell_config = {}
        shell_config['filename'] = sys.argv[1]
        shell_config['target'] = sys.argv[2]
        shell_config['location'] = sys.argv[3]
        shell_config['user_uid'] = sys.argv[4]
        shell_config['user_activation_level'] = sys.argv[5]
        shell_config['user_threshold_above_e'] = sys.argv[6]
        shell_config['number_features'] = sys.argv[7]
        shell_config['similarity_threshold'] = sys.argv[8]
        shell_config['feature_version'] = sys.argv[9]
        shell_config['time_version_from'] = time_version_from
        shell_config['time_version_to'] = time_version_to

        # !Run DB updates
        # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))
        # update_run(filename,1.1)

        file_path = f'{data_path}/{filename}'
        sample_rate = librosa.get_samplerate(file_path)
        raw_data, sample_rate = librosa.load(file_path, sr=sample_rate)
        # print(f'sr : {sample_rate}')

        # --- META DATA creation ---
    
        start_time = f'{file_root.split("_")[0]}_{file_root.split("_")[1]}.{file_root.split("_")[2]}'

        # print(f'start time : {start_time}')
        start_t_dt = dt.strptime(start_time, '%Y%m%d_%H%M%S.%f')
        duration_s = len(raw_data)/sample_rate
        start_t_ms = int(start_t_dt.timestamp()) * 1000
        end_t_dt = start_t_dt + timedelta(seconds=duration_s)
        end_t_ms = int(end_t_dt.timestamp()) * 1000
        end_t_f = end_t_dt.strftime('%y%m%d_%H%M%S.%f')

        meta_data = {
            "snapshot_id": filename_ss_id,
            "data_frame_start": start_time,
            "data_frame_end": end_t_f,
            "listener_location": {"latitude": 0, "longitude": 0}, "location_name": location, "frame_delta_t": duration_s, "sample_rate": sample_rate, "marlin_start_time": start_t_ms,
            "marlin_end_time": end_t_ms
        }

        # --- INITIALISE RUN END ---

        # --- NO EDIT START ---

        # --- DATA ADAPTER / DERIVED DATA CREATION ---
        # Now we have the raw data, we need to build the derived data object using marlin_data. The script checks if the derived data object has
        # already been written and if so, loads that instead. DO NOT change parameters here.

        # write the file to the tmp folder

        tmp_stream = f'streamedfile_{filename_ss_id}.dat'
        tmp_meta = f'metadata_{filename_ss_id}.json'

        raw_data.tofile(f'{working_path}/{tmp_stream}')
        with open(f'{working_path}/{tmp_meta}', 'w') as f:
            json.dump(meta_data, f)

        # Split file into x second intervals
        wav_data_idx_start = 0
        wav_data_idx_end = 0

        src_data_id = filename_ss_id
        cnt = 0
       
        delta_f_idx = (sample_rate * app_config['streaming_delta_t'])
        
        f_start_time = start_time
        f_start_time_dt = start_t_dt
        sim_ids = []

        #! Update DB
        # update_run(filename,1.2)

        while wav_data_idx_end < len(raw_data):

            f_end_time_dt = f_start_time_dt + \
                timedelta(seconds=app_config['streaming_delta_t'])
            f_end_time = f_end_time_dt.strftime('%y%m%d_%H%M%S.%f')
            f_start_time = f_start_time_dt.strftime('%y%m%d_%H%M%S.%f')

            wav_data_idx_end = wav_data_idx_start + \
                (sample_rate * app_config['streaming_delta_t'])
            tmp_stream = f'streamedfile_{src_data_id}{cnt}.dat'
            tmp_meta = f'metadata_{filename_ss_id}{cnt}.json'

            meta_data = {
                "snapshot_id": f'{src_data_id}{cnt}',
                "data_frame_start": f_start_time,
                "data_frame_end": f_end_time,
                "listener_location": {"latitude": 0, "longitude": 0}, "location_name": "67149847", "frame_delta_t": app_config['streaming_delta_t'], "sample_rate": sample_rate, "marlin_start_time":  int((f_start_time_dt.timestamp()) * 1000),
                "marlin_end_time": int((f_end_time_dt.timestamp()) * 1000)
            }
            
            raw_data[wav_data_idx_start: wav_data_idx_end].tofile(
                f'{working_path}/{tmp_stream}')
            with open(f'{working_path}/{tmp_meta}', 'w') as f:
                json.dump(meta_data, f)

            wav_data_idx_start = wav_data_idx_end
            f_start_time_dt = f_end_time_dt
            sim_ids.append(f'{src_data_id}{cnt}')

            cnt += 1

        # Create the data adapter
        limit = 200
        simulation_data_path = f'{working_path}'
        data_adapter = MarlinData(load_args={'limit': limit})

        # Build marlin data adapter
        r = data_adapter.load_from_path(load_args={
                                        'load_path': simulation_data_path, "snapshot_type": "simulation", "limit": limit, "ss_ids": sim_ids})

        data_feed = MarlinDataStreamer()
        data_feed.init_data(data_adapter.simulation_data,
                            data_adapter.simulation_index)

        data_avail = False
        derived_data_use = None

        #! update
        # update_run(filename,1.3)

        # if not os.path.isfile(f'{working_path}/{src_data_id}0.da'):

        for snapshot in data_feed:
            snapshot_derived_data = None
            
            s_id = snapshot.meta_data['snapshot_id']
            # print (f'Searching for derived data : {s_id} ...')
            logger_.info(f'Searching for derived data : {s_id}.')
            if not os.path.isfile(f'{working_path}/{s_id}.da'):
                #! update
                # update_run(filename,1)

                # print (f'...not found so building for {s_id}.')
                logger_.info(f'...not found so building for {s_id}.')
                data_adapter.derived_data = None
                data_adapter.build_derived_data(n_fft=8192)
                snapshot_derived_data = data_adapter.derived_data.build_derived_data(
                    simulation_data=snapshot,  f_min=100000, f_max=140000)
                
                data_adapter.derived_data.ft_build_band_energy_profile(
                    sample_delta_t=0.01, simulation_data=snapshot, discrete_size=500)
                
                data_adapter.multiple_derived_data[s_id] = data_adapter.derived_data
                if derived_data_use == None:
                    derived_data_use = data_adapter.derived_data
                
                with open(f'{working_path}/{s_id}.da', 'wb') as f:  # open a text file
                    # serialize the list
                    pickle.dump(data_adapter.derived_data, f)
                
                # print (f'{s_id} derived data structure built.')
                logger_.info(f'{s_id} derived data structure built.')
            else:
                # !update
                # update_run(filename,2)
                data_avail = True
                # print (f'...{s_id} found.')
                logger_.info(f'...{s_id} found.')
               
        # Load saved derived data objects

        max_frequency_index = 0
        tmp_derived_data = None


        if not os.path.isfile(f'{working_path}/{filename}_all.da'):
            
            if data_avail:
                number_dd_loaded = 0
                number_to_load = len(sim_ids)
                for active_ssid in sim_ids:
                    # print (f'Loading MARLIN data {active_ssid} [{number_dd_loaded} of {number_to_load}]')
                    logger_.info(f'Loading MARLIN data {active_ssid} [{number_dd_loaded} of {number_to_load}]')
                    with open(f'{working_path}/{active_ssid}.da', 'rb') as f:  # open a text file
                        load_start = time.time()
                        data_adapter.derived_data = None
                        tmp_derived_data = pickle.load(f)
                        
                        data_adapter.derived_data = tmp_derived_data
                        

                        max_frequency_index = 0
                        # for f_index, value in tmp_derived_data.fast_index_energy_stats.items():
                        #     max_frequency_index = max(f_index, max_frequency_index)
                        
                        
                        data_adapter.multiple_derived_data[active_ssid] = tmp_derived_data

                        if derived_data_use == None:
                            derived_data_use = tmp_derived_data

                        number_dd_loaded+=1
                        dur = time.time()-load_start
                        # print(f'Time to load MARLIN data [active_ssid] -> {dur}')
                        logger_.info(f'Time to load MARLIN data [active_ssid] -> {dur}')
                with open(f'{working_path}/{filename}_all.da', 'wb') as f: 
                    # serialize the list
                    pickle.dump(data_adapter.multiple_derived_data, f)
                    
                with open(f'{working_path}/{filename}_all_dd.da', 'wb') as f: 
                    # serialize the list
                    pickle.dump(data_adapter.derived_data, f)
                    

        else:
            # print (f'{filename} has a single project MARLIN data structure available.')
            logger_.info(f'{filename} has a single project MARLIN data structure available.')
            with open(f'{working_path}/{filename}_all.da', 'rb') as f:  # open a text file
                multiple_dd = pickle.load(f)
                data_adapter.multiple_derived_data = multiple_dd

            with open(f'{working_path}/{filename}_all_dd.da', 'rb') as f:  # open a text file
                dd = pickle.load(f)
                data_adapter.derived_data = dd



        algo_setup = AlgorithmSetup(config_file_path=f'{app_path}/config.json')

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
        #! update
        # update_run(filename,4.5)
        # print(f'Loading features / bots. {update_features}')
        logger_.info(f'Loading features / bots. {update_features}')
        shell_config['number_working_features'] = application.load_bots(
            target, version=feature_version, version_time_from=time_version_from,  version_time_to=time_version_to, bot_dir=features_path, number_features=number_features, update=update_features, direct=True)
        num_loaded = shell_config['number_working_features']
        
        # print (f'Number loaded : {num_loaded}')
        logger_.info(f'Number loaded : {num_loaded}')
        

        application.mode = 1
        application.multiple_data = 1
        # create new run in db
        # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))

        # ------------------------------------------------------------------
        #
        # World and Data Initialised. Let's play the game.
        #
        # ------------------------------------------------------------------

        marlin_game = IdentGame(
            application, None, activation_level=user_activation_level)
        marlin_game.game_id = filename_ss_id_rnd

        from layer_three import *
        from utils import *

        if application.mode == 1:

            feature_f = {}

           
            # Initial conditions
            frequency_activity = []
            for feature in list(application.loaded_bots.values()):
                # print (feature.dNA[0].genome)
                for k, v in feature.dNA.items():
                    for kg, vg in v.genome.items():
                        for kgg, vgg in vg.genome.items():
                            # if 'frequency_index' in vgg:
                            # idx = vgg.frequency_index
                            # f = application.derived_data.min_freq + \
                            #     (idx * (application.derived_data.index_delta_f))
                            f = vgg.frequency
                            feature_f[feature.name] = f
                            frequency_activity.append(f)

            distributed_list = shape_input(feature_f,500)
            
            # Build initial feature frequency distribution plot
            plot_hist(frequency_activity,
                      f'{out_path}/f_d_{marlin_game.game_id}_init_all.png')

            
            # Update the loaded bots
            marlin_game.game.update_bots(
                bot_dir=features_path, feature_list=distributed_list)

            frequency_activity = []
            for feature in list(application.loaded_bots.values()):
                
                for k, v in feature.dNA.items():
                    for kg, vg in v.genome.items():
                        for kgg, vgg in vg.genome.items():
                            # if 'frequency_index' in vgg:
                            # idx = vgg.frequency_index
                            # f = application.derived_data.min_freq + \
                            #     (idx * (application.derived_data.index_delta_f))
                            # feature_f[feature.name] = f
                            f = vgg.frequency
                            feature_f[feature.name] = f
                            frequency_activity.append(f)

            # Plot prescribed f distribution
            plot_hist(frequency_activity,
                      f'{out_path}/f_d_{marlin_game.game_id}_reshaped_all.png')

            # Determine total time
            s_interval = duration_s
            number_runs = math.floor(duration_s / s_interval)
            delta_idx = s_interval * sample_rate

            # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))
            end_idx = 0

            all_decisions = {}

            combined_bulk_energies = {}
            combined_bulk_times = {}
            combined_active_features = {}

           
            bot_run_time_start = t.time()

            for run_i in range(0, number_runs):

                if run_i == number_runs:
                    break

                sub_filename = f'{marlin_game.game_id}_{run_i}'
                # send_new_run(sub_filename, target, user_uid, location, json.dumps(shell_config))

                start_idx = end_idx
                end_idx = start_idx+delta_idx

                marlin_game.active_features = {}

                marlin_game.run_bots(sub_filename=sub_filename, start_idx=start_idx, end_idx=end_idx,
                                     filename=filename_ss_id, out_path=out_path)

                bot_run_time_end = t.time()

                bots_run_time = bot_run_time_end - bot_run_time_start

              
                # ------- Softmax API ------------
                softmax_data = {
                    
                    "target" : target,
                    "activation_threshold" : user_activation_level,
                    "threshold_above_activation": user_threshold_above_e,
                    "energies": marlin_game.bulk_energies,
                    "times": marlin_game.bulk_times,
                    "similarity_factor": user_similarity_threshold
                }
                
                # print("Sending to Softmax API")
                logger_.info("Sending to Softmax API")
                softmax_key = "key1"
                headers = {}
                softmax_url = 'https://vixen.hopto.org/rs/api/v1/data/softmax'
                headers = {'Authorization': softmax_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
                r = requests.post(softmax_url, data=json.dumps(softmax_data), headers=headers)
                
                softmax_results = r.json()
                
                # ------- Softmax API ------------

                hits = []
               
           
            softmax_return_data = json.loads(softmax_results['result'][0])
            decisions = softmax_return_data['decisions']
            ratio_active = softmax_return_data['r_active']
            avg_energies = softmax_return_data['avg_energies']
            pc_above_tracker = softmax_return_data['pc_above_tracker']
            # max_energy_tracker = softmax_return_data['max_energies']
            number_decisions = len(decisions)
            # print (f'{number_decisions} made.')
            logger_.info(f'{number_decisions} made.')

            #! update
            # update_run(filename,12)
            # update_run(filename,12.1)


            #! update
            # update_run(filename,12.2)
          
            if len(marlin_game.bulk_times) > 2:
                # print('build spec')
                build_spec_upload(sample_rate, marlin_game.game_id, hits=hits, decisions=decisions, peak=ratio_active,
                                  avg=avg_energies, times=marlin_game.bulk_times, pc_above_e=pc_above_tracker, f=[], full_raw_data=raw_data, save_path=out_path)

            #! update
            # update_run(filename,12.4)
            with open(f'{out_path}/decisions_{marlin_game.game_id}.json', 'w') as fp:
                json.dump(decisions, fp)

            #! update
            # update_run(filename,13)
           
            # --- NO EDIT END ---

        break
