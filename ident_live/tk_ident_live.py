#!/usr/local/bin/python3

""" 
1.0
Sample script to run a local data file against MARLIN IDent Live features. Documentation for installation
and execution can be found at https://vixen.hopto.org/rs/marlin/docs/ident/site. 

"""


""" 

Import modules. Python modules required for application.

"""
from threading import Thread

# flag for loading multiple models / feature types (env)
multiple_models = True

duration = {}
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

from utils import *

from pathlib import Path

from layer_three import *

# == RT Plots
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

from multiprocessing import Process


# decision tolerance
bm_delta_t = 1



def benchmark(target = "", decisions={},time_seconds = [], start_time_chunk=-1, labels=[]):
    
    benchmark_results = {}
    benchmark_results['correct_times'] = []
    idx=0
    number_correct = 0
    number_incorrect = 0
    number_labels = len(labels)
    for decision in decisions:
        correct = False
        if decision['target'] == target:
            revised_time = float(time_seconds[decision['frame']])
            if start_time_chunk != -1:
                revised_time = float(time_seconds[decision['frame']]) + float(start_time_chunk)
            
            
            for time in labels:
                delta_t = float(revised_time) - float(time)
                if (delta_t) > 0 and (delta_t) < bm_delta_t:
                    benchmark_results['correct_times'].append({'decision_time':revised_time, 'label_time' : time, 'target' : target})
                    # print (f'{revised_time} -> {delta_t}')
                    correct = True
            idx+=1

        if correct:
            number_correct += 1
        else:
            number_incorrect += 1
            
    benchmark_results['number_labels'] = number_labels
    benchmark_results['correct'] = number_correct
    benchmark_results['incorrect'] = number_incorrect
    benchmark_results['number_decision'] = number_correct + number_incorrect
    if float(number_correct + number_incorrect) > 0:
        benchmark_results['winning_pc'] = (float(number_correct) / float(number_correct + number_incorrect)) * 100
    else:
        benchmark_results['winning_pc'] = 0.0
    
    return benchmark_results

run_data = None
xs = []
ys = []
ax1 = None
style.use('fivethirtyeight')
fig = plt.figure()

ax1 = fig.add_subplot(1,1,1)
__plotting__ = True

def animate(i):
    # graph_data = open('example.txt','r').read()
    # lins = graph_data.split('\n')
    # print (i) 
    # x,y = line.split(',')
    # xs.append(float(random.uniform(0,10)))
    # ys.append(float(i))
    # # print (ax1)
    # # global ax1
    global __plotting__
    if __plotting__:
        xs=[]
        ys=[]
        global run_data
        # print ("checking run data")
        
        if run_data is not None:
            for x,y in run_data.active_features_index.items():
                xs.append(float(x))
                ys.append(float(y))
        if ax1 is not None:
            ax1.clear()
        # ax1.plot(xs, ys)
        ax1.bar(xs, ys,1.0)
    
def plotter():
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    # plt.ion()
    plt.show()

    
def main_run():
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



    # get feature ids from folder to load or use features.json
    direct = int(sys.argv[15])
    if direct == 1:
        direct = True
    if direct == 0:
        direct = False


    # time range
    start_time_chunk = -1
    end_time_chunk = -1
    if len(sys.argv) > 16:
        start_time_chunk = int (sys.argv[16])
        end_time_chunk = int (sys.argv[17])

    # print (start_time_chunk,end_time_chunk)
    
    bench_mark = False
    if sys.argv[18] == "bm":
        bench_mark = True

    


    # print (f'Direct load of features from folder : {direct}')

    print (f'Update feature / bot list: {update_features}.')
    logger_.info("Update feature / bot list: ")

    filename_ss_id = ""
    batch_id = ""

    # Batch operations
    # if len(sys.argv) >= 16:
    #     batch_run_number = sys.argv[15]

    #     for i in range(0, batch_run_number):
    #         filename_ss_id = f'{sys.argv[15+i]}_{location}'  # obs
    #         batch_file_names.append(filename_ss_id)
    #         batch_run_ids.append(sys.argv[15+i])

    # else:
    #     filename_ss_id = f'{filename}_{location}'  # obs
    #     batch_file_names.append(filename_ss_id)
    #     batch_run_ids.append(filename)
        

    # ----------------- INPUT PARAMETERS ---------------------------------

    # batch operations turned off. Execute in script to achieve batch operations
    batch_run_ids.append(filename)
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
        
        shell_config['time_chunk_from'] = start_time_chunk
        shell_config['time_chunk_to'] = end_time_chunk
        

        # !Run DB updates
        # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))
        # update_run(filename,1.1)

        file_path = f'{data_path}/{filename}'
        sample_rate = librosa.get_samplerate(file_path)
        raw_data, sample_rate = librosa.load(file_path, sr=sample_rate)
        print (f'Sample rate of input data : {sample_rate}')
       
        
        
        # data chunk considerations
        if start_time_chunk != -1:
           
            start_time_idx = int(sample_rate * int(start_time_chunk))
            
            end_time_idx = int(sample_rate * int(end_time_chunk))
            
            raw_data = raw_data[start_time_idx:end_time_idx]

        
        # --- META DATA creation ---

        # get start time string from filename
        start_time = f'{file_root.split("_")[0]}_{file_root.split("_")[1]}.{file_root.split("_")[2]}'

        # data chunk considerations
        
        
        # print(f'start time : {start_time}')
        start_t_dt = dt.strptime(start_time, '%Y%m%d_%H%M%S.%f')
        if start_time_chunk != -1:
            start_t_dt = start_t_dt + timedelta(seconds=int(start_time_chunk))
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

        app_config['streaming_delta_t'] = min(duration_s,app_config['streaming_delta_t'])

        
        
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
        
        f_start_time = start_t_dt.strftime("%y%m%d_%H%M%S.%f")
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
                (sample_rate * int(app_config['streaming_delta_t']))
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
        limit = 2000
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
                
                data_adapter.build_derived_data(n_fft=app_config['n_fft'])
                
                startt(name="build_derived_data")
                snapshot_derived_data = data_adapter.derived_data.build_derived_data(
                    simulation_data=snapshot,  f_min=app_config['adapter_f_min'], f_max=app_config['adapter_f_max'])
                stopt(desc="build_derived_data")
                startt(name="build index")
                # data_adapter.derived_data.ft_build_band_energy_profile(
                #     sample_delta_t=0.001, simulation_data=snapshot, discrete_size=1000)
                stopt(desc="build index")
                data_adapter.multiple_derived_data[s_id] = data_adapter.derived_data
                if derived_data_use == None:
                    derived_data_use = data_adapter.derived_data
                
                # with open(f'{working_path}/{s_id}.da', 'wb') as f:  # open a text file
                #     # serialize the list
                #     pickle.dump(data_adapter.derived_data, f)
                
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
                        startt(name="loading_da")
                        tmp_derived_data = pickle.load(f)
                        stopt(desc="loading_da")
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
                # with open(f'{working_path}/{filename}_all.da', 'wb') as f: 
                #     # serialize the list
                #     pickle.dump(data_adapter.multiple_derived_data, f)
                    
                # with open(f'{working_path}/{filename}_all_dd.da', 'wb') as f: 
                #     # serialize the list
                #     pickle.dump(data_adapter.derived_data, f)
                    
        
        
        else:
            # print (f'{filename} has a single project MARLIN data structure available.')
            logger_.info(f'{filename} has a single project MARLIN data structure available.')
            with open(f'{working_path}/{filename}_all.da', 'rb') as f:  # open a text file
                multiple_dd = pickle.load(f)
                data_adapter.multiple_derived_data = multiple_dd

            with open(f'{working_path}/{filename}_all_dd.da', 'rb') as f:  # open a text file
                dd = pickle.load(f)
                data_adapter.derived_data = dd

        # ---MARLIN DATA BUILT ---
        
        # print (data_adapter.derived_data.discretised_psd[0][1])
        #plot_rain_psd(data_adapter.derived_data.discretised_psd,time_vector= data_adapter.derived_data.discretised_time_index)

        
        algo_setup = AlgorithmSetup(config_file_path=f'{app_path}/config.json')

        application = SpeciesIdent(algo_setup)
        application.ss_ids = sim_ids
        # for env_pressure in marlin_game.game.data_feed:
        application.derived_data = data_adapter.derived_data

        application.data_feed = data_feed
        application.multiple_derived_data = data_adapter.multiple_derived_data

        # debug - post snapshot build
        # exit()

        # ------------------------------------------------------------------
        #
        #   Bot(s) download for forward testing
        #
        # ------------------------------------------------------------------
        #! update
        # update_run(filename,4.5)
        # print(f'Loading features / bots. {update_features}')
        logger_.info(f'Loading features / bots. {update_features}')
        
        features_paths = []
        if multiple_models == True:
            #get all paths in define feature path and add to features_paths
            # f_directories = os.walk)
            # print ("features_path")
            features_paths  = [ f.path for f in os.scandir(features_path) if f.is_dir() ]
            # print (config)
            # print (features_paths)
            
            selected_models = config['SELECT_MODEL_DIR']
            # print (selected_models)
            if selected_models != "*":
                edited_feature_paths = []
                for model in features_paths:
                    model_name = model.split('/')[-1]
                    if model_name in selected_models:
                        edited_feature_paths.append(model)
                    # print (model_name)
                    
                features_paths = edited_feature_paths
                    
                
            
            
            
        else:
            features_paths.append(features_path)
        
        
        num_loaded = 0
        print (features_paths)
        
        for f_path in features_paths:
            
            shell_config['number_working_features'] = application.load_bots(
                target, version=feature_version, version_time_from=time_version_from,  version_time_to=time_version_to, bot_dir=f_path, number_features=number_features, update=update_features, direct=True)
            num_loaded += shell_config['number_working_features']
            # print (f'Number loaded live: {num_loaded}')
        
        
        application.loaded_bots = application.selected_loaded_bots
        
        num_live_bots = len(application.loaded_bots.keys())
        print (f'Number of live bots : {num_live_bots}')
        print (f'Signatures : {application.loaded_targets}')
        
        
        logger_.info(f'Number loaded : {num_loaded}')
        
        # exit()
        application.mode = 1
        application.multiple_data = 1
        # create new run in db
        # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))


        # ==== LABELS
        my_labels = [] 
        import csv
        if bench_mark:
            f_marker = filename.split('.')[0]
            with open(f'{data_path}/{f_marker}_labels.csv', newline='') as csvfile:
                label_data = list(csv.reader(csvfile))
                
            my_labels = [] 
            # print (data)
            for label in label_data:
                v = label[0].split('\t')
                # print (v)
                my_labels.append(v[0])

            my_labels.pop(0)
        #  LABELS ===
        
        
        

        # ------------------------------------------------------------------
        #
        # World and Data Initialised. Let's play the game.
        #
        # ------------------------------------------------------------------

        marlin_game = IdentGame(
            application, None, activation_level=user_activation_level)
        marlin_game.game_id = filename_ss_id_rnd

        Path(f'{out_path}/{marlin_game.game_id}').mkdir(parents=True, exist_ok=True)
        Path(f'{out_path}/{marlin_game.game_id}/layers').mkdir(parents=True, exist_ok=True)
        out_path = f'{out_path}/{marlin_game.game_id}'
        
        

        if application.mode == 1:

            feature_f = {}

            
            # Initial conditions
            # frequency_activity = []
            # for feature in list(application.loaded_bots.values()):
            #     # print (feature.dNA[0].genome)
            #     for k, v in feature.dNA.items():
            #         for kg, vg in v.genome.items():
            #             for kgg, vgg in vg.genome.items():
            #                 # if 'frequency_index' in vgg:
            #                 # idx = vgg.frequency_index
            #                 # f = application.derived_data.min_freq + \
            #                 #     (idx * (application.derived_data.index_delta_f))
            #                 f = vgg.frequency
            #                 feature_f[feature.name] = f
            #                 frequency_activity.append(f)

            # distributed_list = shape_input(feature_f,500)
            
            # # print(feature_f)
            # # Build initial feature frequency distribution plot
            # plot_hist(frequency_activity,
            #           f'{out_path}/f_d_{marlin_game.game_id}_init_all.png')

            
            # # exit()
            # # Update the loaded bots
            # # marlin_game.game.update_bots(
            # #     bot_dir=features_path, feature_list=distributed_list)

            
            # frequency_activity = []
            # for feature in list(application.loaded_bots.values()):
                
            #     for k, v in feature.dNA.items():
            #         for kg, vg in v.genome.items():
            #             for kgg, vgg in vg.genome.items():
            #                 # if 'frequency_index' in vgg:
            #                 # idx = vgg.frequency_index
            #                 # f = application.derived_data.min_freq + \
            #                 #     (idx * (application.derived_data.index_delta_f))
            #                 # feature_f[feature.name] = f
            #                 f = vgg.frequency
            #                 feature_f[feature.name] = f
            #                 frequency_activity.append(f)

            # # Plot prescribed f distribution
            # plot_hist(frequency_activity,
            #           f'{out_path}/f_d_{marlin_game.game_id}_reshaped_all.png')

            # Determine total time
            s_interval = duration_s
            # s_interval = 20
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
                
                # Real time data
                global run_data
                run_data = RT_Data()
                run_data.set_data(marlin_game.bulk_energies, marlin_game.active_features, application.loaded_targets, application.loaded_bots)
                run_data.stream()
                
                # Real time plotting (poc)
                

                # style.use('fivethirtyeight')
                # fig = plt.figure()
                
                # ax1 = fig.add_subplot(1,1,1)
                # print (fig)
                # print (ax1)
                
                # ani = animation.FuncAnimation(fig, animate, interval=1000)
                # # plt.ion()
                # plt.show()
                # plt.pause(0.1)
                
                # Run game
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
                    "similarity_factor": user_similarity_threshold,
                    "bot_targets" : marlin_game.game.feature_targets
                    
                }
                
                print("Sending to IDent Softmax API")
                logger_.info("Sending to Softmax API")
                softmax_key = "key1"
                headers = {}
                softmax_url = 'https://vixen.hopto.org/rs/api/v1/data/softmax'
                headers = {'Authorization': softmax_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
                r = requests.post(softmax_url, data=json.dumps(softmax_data), headers=headers)
                
                softmax_results = r.json()
                
                # ------- Softmax API ------------

                hits = []
                

            # get softmax reply
            softmax_return_data = json.loads(softmax_results['result'][0])
            
            decisions = softmax_return_data['decisions']
            decisions_csv = softmax_return_data['decisions_csv']
            ratio_active = softmax_return_data['r_active']
            avg_energies = softmax_return_data['avg_energies']
            pc_above_tracker = softmax_return_data['pc_above_tracker']
            max_energy = softmax_return_data['max_energies']
            active_features = softmax_return_data['active_features']
            soft_max_targets = softmax_return_data['targets']
            interesting = softmax_return_data['interesting']
            interesting_csv = softmax_return_data['interesting_csv']
            number_decisions = len(decisions)
            
            
            logger_.info(f'{number_decisions} made.')
            # print (soft_max_targets)
            #! update
            # update_run(filename,12)
            # update_run(filename,12.1)

            #! update
            # update_run(filename,12.2)

            
            


            if len(marlin_game.bulk_times) > 2:
                # build spec with overlaying decisions & energy plots
                time_seconds = build_spec_upload(sample_rate, marlin_game.game_id, hits=hits, decisions=decisions, peak=ratio_active,
                                    avg=avg_energies, times=marlin_game.bulk_times, bulk_energies = marlin_game.bulk_energies,pc_above_e=ratio_active, f=[], full_raw_data=raw_data, save_path=out_path, max_energies = max_energy, targets=soft_max_targets, interesting=interesting, training_labels = my_labels, memory = marlin_game.memory_tracker)


            #! update
            # update_run(filename,12.4)
            with open(f'{out_path}/decisions_{marlin_game.game_id}.json', 'w') as fp:
                json.dump(decisions, fp)
            
            with open(f'{out_path}/interesting_{marlin_game.game_id}.json', 'w') as fp:
                json.dump(interesting, fp)

            with open(f'{out_path}/decisions_{marlin_game.game_id}.csv', 'w') as fp:
                for d in decisions_csv:
                    fp.write(f'{d} \n')
                    
            with open(f'{out_path}/interesting_{marlin_game.game_id}.csv', 'w') as fp:
                for d in interesting_csv:
                    fp.write(f'{d} \n')

            
            #! update
            # update_run(filename,13)
            
            # --- NO EDIT END ---
            
            
            for target in soft_max_targets:
            
                with open(f'{out_path}/layers/ratio_active_{target}_{marlin_game.game_id}_{sample_rate}.txt', 'w') as f:
                    idx = 0
                    for line in ratio_active[target]:
                        revised_time = time_seconds[idx]
                        if start_time_chunk != -1:
                            revised_time = float(time_seconds[idx]) + float(start_time_chunk)
                        f.write(f"{revised_time},{line}, {target}\n")
                        idx += 1
                        
                with open(f'{out_path}/layers/time_s.txt', 'w') as f:
                    for line in time_seconds:
                        # revised_time = int(time_seconds[idx] + start_time_chunk)
                        f.write(f"{line}\n")
                        
                with open(f'{out_path}/layers/avg_e_{target}_{marlin_game.game_id}_{sample_rate}.txt', 'w') as f:
                    idx = 0
                    for line in avg_energies[target]:
                        revised_time = time_seconds[idx]
                        if start_time_chunk != -1:
                            revised_time = float(time_seconds[idx]) + float(start_time_chunk)
                        f.write(f"{revised_time},{line}, {target}\n")
                        idx+=1 
                        
                with open(f'{out_path}/layers/decisions_{target}.txt', 'w') as f:
                    idx = 0
                    
                    
                    
                    for decision in decisions:
                        
                        if decision['target'] == target:
                            revised_time = float(time_seconds[decision['frame']])
                            if start_time_chunk != -1:
                                revised_time = float(time_seconds[decision['frame']]) + float(start_time_chunk)
                            f.write(f"{revised_time},1, {target}\n")
                            idx+=1
                    
                        
                        
                            
                with open(f'{out_path}/layers/activity_{target}.txt', 'w') as f:
                    idx = 0
                    for activity in interesting:
                        
                        if activity['target'] == target:
                            revised_time = float(time_seconds[activity['frame']])
                            if start_time_chunk != -1:
                                revised_time = float(time_seconds[activity['frame']]) + float(start_time_chunk)
                            f.write(f"{revised_time},1, {target}\n")
                            idx+=1

                

            with open(f'{out_path}/active_features_{marlin_game.game_id}.json', 'w') as fp:
                json.dump(active_features, fp)
                
            with open(f'{out_path}/avg_energies_{marlin_game.game_id}.json', 'w') as fp:
                json.dump(avg_energies, fp)
            
            
            if bench_mark:
                for target in soft_max_targets:
                    bm_results = benchmark(target,decisions,time_seconds, start_time_chunk, my_labels)
                    print (bm_results)


        # quit real time data stream  
        global __plotting__
        __plotting__ = False          
        run_data.quit_stream()
        # plt.show()
        break





# --- GUI ---
# import customtkinter
from ident_gui import *
# app = customtkinter.CTk()


# build_main_app(app)


# run_app(app)
# p = Process(target=plotter)
# p.start()\
# thread = Thread(target=main_run, daemon=False)
# thread.start()
# MainProgram()
main_run()
# p.join()
# plotter()