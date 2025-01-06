#!/usr/local/bin/python3

from rich.console import Console
console = Console()


# from ident_softmax.ident_softmax.harbour_porpoise import *
from game import IdentGame
from ident_application import *
from marlin_data.marlin_data import *
from custom_decisions import *
from custom_genes import *
from custom_bots import *
import marlin_brahma.fitness.performance as performance
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.world.population as pop
import marlin_brahma.bots.bot_root as bots
from dotenv import load_dotenv, dotenv_values
import pickle
from datetime import datetime as dt
from datetime import datetime, timedelta, timezone
import json
import random
import librosa
import sys
import os
import requests

SOFTMAX_FOLDER_USR = os.path.join(
    '/', 'Users', 'vixen', 'rs', 'dev', 'ident_softmax')
os.environ['SOFTMAX_FOLDER_USR'] = SOFTMAX_FOLDER_USR


# Import Brahma


# Import custom / gene libraries

# Import marlin_data

import operator
# input feature distribution
def shape_input(features, f_bucket_size):
    """shape_input Generate a seleceted distribution of features/bots for a simulation run.

    :param features: list of features/bots
    :type features: List[bot]
    """
    
    f_buckets = {}
    f_buckets_names = {}
    f_name_list = []
    
    for feature, f in features.items():
        if f not in list(f_buckets.keys()):
            f_buckets[f] = 0
            f_buckets_names[f] = []
            
    t_ = 0
    for feature,f in features.items():
        # print (f'{feature}, {f}')
        

        for fr,v in f_buckets.items():
            if abs(f-fr)<f_bucket_size:
                if fr in list(f_buckets.keys()):
                    f_buckets[fr]+=1
                    f_buckets_names[f].append(feature)
                    f_name_list.append(feature)
                    t_+=1
                else:
                    f_buckets[fr] = 1
                    f_buckets_names[f].append(feature)
                    f_name_list.append(feature)
                    t_ += 1
   
                    
    # build distribution
    f_buckets_s = dict(sorted(f_buckets.items(), key=operator.itemgetter(0)))
        
    min_count = 9999
    min_f = 0
    for fr, v in f_buckets.items():
        if v > 2:
            min_count = min(min_count,v)
    
    # print(f'min count : {min_count}')
    
    distributed_name_list = []
    for fr, v in f_buckets.items():
        if len(f_buckets_names[fr]) >= min_count:
            distributed_name_list.extend(
                random.sample(f_buckets_names[fr], min_count))


    # print (f'Number of features : {len(features)}.')
    # # print (f_buckets_s)
    # print (f'Number counted : {t_}')
    
    dist_data = {}
    dist_data['ids'] = distributed_name_list
    
    with open('feature_names.json','w+') as f:
        json.dump(dist_data, f)
    
    # print (distributed_name_list)
    return distributed_name_list

if __name__ == "__main__":

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

    NUMBA_CACHE_DIR = os.path.join(
        '/', 'home', 'vixen', 'rs', 'dev', 'marlin_hp', 'marlin_hp', 'cache')
    os.environ['NUMBA_CACHE_DIR'] = NUMBA_CACHE_DIR

    # Read command line arguments
    batch_file_names = []
    batch_run_ids = []
    filename = sys.argv[1]
    target = sys.argv[2]
    location = sys.argv[3]
    user_uid = sys.argv[4]
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

    # Batch operations
    if len(sys.argv) >= 15:
        batch_run_number = sys.argv[14]

        for i in range(0, batch_run_number):
            filename_ss_id = f'{sys.argv[14+i]}_{location}'  # obs
            batch_file_names.append(filename_ss_id)
            batch_run_ids.append(sys.argv[14+i])

    else:
        filename_ss_id = f'{filename}_{location}'  # obs
        batch_file_names.append(filename_ss_id)
        batch_run_ids.append(filename)
        

    for filename in batch_run_ids:
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

        # -- META DATA
        # get sample end time
        # start_time = "140822_155229.000000"
        start_time = f'{file_root.split("_")[0]}_{file_root.split("_")[1]}.{file_root.split("_")[2]}'

        # print(f'start time : {start_time}')
        start_t_dt = dt.strptime(start_time, '%Y%m%d_%H%M%S.%f')
        duration_s = len(raw_data)/sample_rate
        start_t_ms = int(start_t_dt.timestamp()) * 1000
        end_t_dt = start_t_dt + timedelta(seconds=duration_s)
        end_t_ms = int(end_t_dt.timestamp()) * 1000
        end_t_f = end_t_dt.strftime('%y%m%d_%H%M%S.%f')

        # print(f'Sample Rate : {sample_rate}')
        # print(f'Number of seconds : {duration_s}')
        # print(start_t_dt, end_t_dt)
        # print(start_t_ms, end_t_ms)
        # print(end_t_f)

        meta_data = {
            "snapshot_id": filename_ss_id,
            "data_frame_start": start_time,
            "data_frame_end": end_t_f,
            "listener_location": {"latitude": 0, "longitude": 0}, "location_name": location, "frame_delta_t": duration_s, "sample_rate": sample_rate, "marlin_start_time": start_t_ms,
            "marlin_end_time": end_t_ms
        }

        # --- now we have the raw data, we need to build the derived data object using marlin_data

        # write the file to the tmp folder

        tmp_stream = f'streamedfile_{filename_ss_id}.dat'
        tmp_meta = f'metadata_{filename_ss_id}.json'

        raw_data.tofile(f'{working_path}/{tmp_stream}')
        with open(f'{working_path}/{tmp_meta}', 'w') as f:
            json.dump(meta_data, f)

        # print(meta_data)

        # split file into x second intervals
        wav_data_idx_start = 0
        wav_data_idx_end = 0

        # print(f'sr : {sample_rate}')
        # print(f'{filename}')

        src_data_id = filename_ss_id
        cnt = 0
        # print(f'{len(raw_data)}')
        delta_f_idx = (sample_rate * app_config['streaming_delta_t'])
        # print(delta_f_idx)
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

            # print(f' {wav_data_idx_start} -> {wav_data_idx_end}')
            # print(f'{f_start_time} -> {f_end_time}')

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

        # create the data adapter
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
            # print (snapshot.meta_data)
            s_id = snapshot.meta_data['snapshot_id']
            # print (f'{snapshot.meta_data}')
            if not os.path.isfile(f'{working_path}/{s_id}.da'):
                #! update
                # update_run(filename,1)

                # print(f'Building derived data feed structure {s_id}')
                data_adapter.derived_data = None
                data_adapter.build_derived_data(n_fft=8192)
                snapshot_derived_data = data_adapter.derived_data.build_derived_data(
                    simulation_data=snapshot,  f_min=115000, f_max=145000)
                # add to existing derived data

                data_adapter.derived_data.ft_build_band_energy_profile(
                    sample_delta_t=0.01, simulation_data=snapshot, discrete_size=500)
                # add to multiple derived data holder, too
                data_adapter.multiple_derived_data[s_id] = data_adapter.derived_data
                if derived_data_use == None:
                    derived_data_use = data_adapter.derived_data
                # print(f'saving...{working_path}/{s_id}.da')
                with open(f'{working_path}/{s_id}.da', 'wb') as f:  # open a text file
                    # serialize the list
                    pickle.dump(data_adapter.derived_data, f)

            else:
                # !update
                # update_run(filename,2)
                data_avail = True
                # print(f'Derived data for {s_id} already available.')
            # # with open(f'{s_id}_.der', 'wb') as f:  # open a text file
            # #     pickle.dump(snapshot_derived_data, f) # serialize the list

            # if not data_avail:
            #     update_run(filename,3)
            #     print ('saving')
            #     with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{src_data_id}.da', 'wb') as f:  # open a text file
            #         pickle.dump(data_adapter.derived_data, f) # serialize the list

        # Load saved derived data objects

        max_frequency_index = 0
        tmp_derived_data = None

        if data_avail:
            # print('loading saved data')
            for active_ssid in sim_ids:

                with open(f'{working_path}/{active_ssid}.da', 'rb') as f:  # open a text file
                    # print(f'Building derived data : {active_ssid}')
                    data_adapter.derived_data = None
                    tmp_derived_data = pickle.load(f)
                    # tmp_derived_data.get_max_f_index()
                    data_adapter.derived_data = tmp_derived_data
                    # print(tmp_derived_data.fast_index_energy_stats)

                    max_frequency_index = 0
                    for f_index, value in tmp_derived_data.fast_index_energy_stats.items():
                        max_frequency_index = max(f_index, max_frequency_index)
                    data_adapter.multiple_derived_data[active_ssid] = tmp_derived_data

                    if derived_data_use == None:
                        derived_data_use = tmp_derived_data

                    # print(f'max frequency index : {max_frequency_index}')
                    # print(f'{data_adapter.derived_data.fourier_delta_t}')
                    # if max_frequency_index != 59:
                    #     print (f'{active_ssid} has incorrect number of frequency indices')
                    #     exit()

        # debug
        for feed in data_feed:
            # print (feed.start_time)
            # print (feed.end_time)
            # env_pressure_length = feed.frequency_ts_np.shape[0]
            # print (f'l : {env_pressure_length}')
            pass

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
        # print('Loading features / bots.')
        shell_config['number_working_features'] = application.load_bots(
            target, version=feature_version, version_time_from=time_version_from,  version_time_to=time_version_to, bot_dir=features_path, number_features=number_features, update=False)
        num_loaded = shell_config['number_working_features']

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

            # update_run(filename,5)
            # print("*** STARTING GAME ***")

            # show init f dist
            frequency_activity = []
            for feature in list(application.loaded_bots.values()):
                # print (feature.dNA[0].genome)
                for k, v in feature.dNA.items():
                    for kg, vg in v.genome.items():
                        for kgg, vgg in vg.genome.items():
                            # if 'frequency_index' in vgg:
                            idx = vgg.frequency_index
                            f = application.derived_data.min_freq + \
                                (idx * (application.derived_data.index_delta_f))
                            feature_f[feature.name] = f
                            frequency_activity.append(f)

            distributed_list = shape_input(feature_f,500)
            
            # build initial feature frequency distribution plot
            plot_hist(frequency_activity,
                      f'{out_path}/f_d_{marlin_game.game_id}_init_all.png')

            
            
            marlin_game.game.update_bots(
                bot_dir=features_path, feature_list=distributed_list)

            frequency_activity = []
            for feature in list(application.loaded_bots.values()):
                # print (feature.dNA[0].genome)
                for k, v in feature.dNA.items():
                    for kg, vg in v.genome.items():
                        for kgg, vgg in vg.genome.items():
                            # if 'frequency_index' in vgg:
                            idx = vgg.frequency_index
                            f = application.derived_data.min_freq + \
                                (idx * (application.derived_data.index_delta_f))
                            feature_f[feature.name] = f
                            frequency_activity.append(f)

           
            plot_hist(frequency_activity,
                      f'{out_path}/f_d_{marlin_game.game_id}_reshaped_all.png')

            # get total time:
            s_interval = duration_s
            number_runs = math.floor(duration_s / s_interval)
            delta_idx = s_interval * sample_rate

            # send_new_run(filename, target, user_uid, location, json.dumps(shell_config))
            end_idx = 0

            all_decisions = {}

            combined_bulk_energies = {}
            combined_bulk_times = {}
            combined_active_features = {}

            # print(f'number_runs {number_runs}')
            # number_runs = 1
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

                # print (marlin_game.bulk_energies)
                # print (len(marlin_game.bulk_times))
                # print (marlin_game.number_run_idx)
                bots_run_time = bot_run_time_end - bot_run_time_start

                # ---MP---
                # for k, v in marlin_game.bulk_energies.items():
                #     energies_d = v
                #     for ke, ve in v.items():
                #         if k not in combined_bulk_energies:
                #             combined_bulk_energies[k] = {}

                #         combined_bulk_energies[k][ke +
                #                                   (run_i*(marlin_game.number_run_idx+1))] = ve

                # for k, v in marlin_game.bulk_times.items():
                #     combined_bulk_times[k +
                #                         (run_i*(marlin_game.number_run_idx+1))] = v

                # for k, v in marlin_game.active_features.items():
                #     combined_active_features[k +
                #                              (run_i*(marlin_game.number_run_idx+1))] = v

                # # print (marlin_game.bulk_times)
                # for k, v in combined_bulk_energies.items():
                #     # print (f'le : {len(v)}')
                #     break

                # for k, v in marlin_game.bulk_energies.items():
                #     # print (f'mge : {len(v)}')
                #     break

                # --MP---

                # marlin_game.run_bot()

                # save game
                # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{sub_filename}.game', 'wb') as f:
                #     pickle.dump(marlin_game, f)

                # write all decisions to json
                #! update
                # update_run(sub_filename,11)
                # print (marlin_game.active_features)
                # print (marlin_game.bulk_times)
                # layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)


                # ------- Softmax API ------------
                # softmax_data = {
                    
                #     "target" : target,
                #     "activation_threshold" : user_activation_level,
                #     "threshold_above_activation": user_threshold_above_e,
                #     "energies": marlin_game.bulk_energies,
                #     "times": marlin_game.bulk_times
                    
                # }
                
                
                
                # softmax_key = "key1"
                # headers = {}
                # softmax_url = 'https://vixen.hopto.org/rs/api/v1/data/softmax'
                # headers = {'Authorization': softmax_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
                # r = requests.post(softmax_url, data=json.dumps(softmax_data), headers=headers)
                
               
                # ------- Softmax API ------------




                # ------- Layer 3 Local -------

                layer_3 = Layer_Three(activation_level=user_activation_level, threshold_above_activation=user_threshold_above_e,
                                      derived_data=application.derived_data, similarity_threshold=user_similarity_threshold, run_id=filename, target=target, out_path=out_path)

                freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times,
                                         active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()))

                # ------------------------
                
                

                hits = []
                decisions = layer_3.decisions
                a_ratio = layer_3.ratio_active
                # print(f't: {len(marlin_game.bulk_times)}')
                # print(f'd: {len(layer_3.ratio_active)}')
                # print(f'c_t :{len(combined_bulk_times)}')
                # print(f'avg: {len(layer_3.avg_energies)}')

                # update_run(sub_filename,13)

            # print("*** ENDING & PROCESSING GAME RESULTS***")

            #! update
            # update_run(filename,12)
            # update_run(filename,12.1)

            # print (combined_bulk_energies)

            for k, v in combined_bulk_energies.items():
                # print(len(v))
                break

            # marlin_game.bulk_times = combined_bulk_times
            # marlin_game.bulk_energies = combined_bulk_energies
            # marlin_game.active_features = combined_active_features
            # print (marlin_game.active_features)

            # ---
            # layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
            # freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times, active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()) )

            # -----
            # print (len(layer_3.ratio_active))
            # save game

            #! update
            # update_run(filename,12.2)
            # with open(f'{out_path}/game_{marlin_game.game_id}.game', 'wb') as f:
            #     pickle.dump(marlin_game, f)

            # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{filename}.json', 'w') as fp:
            #         json.dump(layer_3.decisions, fp)

            # for env_pressure in marlin_game.game.data_feed:
            #! update
            # update_run(filename,12.3)

            # print(f'len of t = {len(marlin_game.bulk_times)}')
            # print(f'len of e = {len(marlin_game.bulk_energies)}')
            if len(marlin_game.bulk_times) > 2:
                # print('build spec')
                build_spec_upload(sample_rate, marlin_game.game_id, hits=hits, decisions=layer_3.decisions, peak=layer_3.ratio_active,
                                  avg=layer_3.avg_energies, times=marlin_game.bulk_times, pc_above_e=layer_3.pc_above_tracker, f=freq, full_raw_data=raw_data, save_path=out_path)

            #! update
            # update_run(filename,12.4)
            with open(f'{out_path}/decisions_{marlin_game.game_id}.json', 'w') as fp:
                json.dump(layer_3.decisions, fp)

            #! update
            # update_run(filename,13)
            # print(f'time to run : {bots_run_time}')

        break
