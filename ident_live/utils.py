import operator
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import random
import numpy as np
from scipy.interpolate import make_interp_spline

from scipy import signal
from scipy.fft import fftshift
from datetime import datetime
import json
import matplotlib
import matplotlib.patches as mpatches
from matplotlib import colormaps
import seaborn as sns

cmap = matplotlib.cm.get_cmap('Spectral')

"""
    Game level utils library.
"""


def get_bin_f(librosa_f_bins, freq_lower, freq_end):
    cnt = 0
    start_diff = 100000
    end_diff = 10000
    for value in librosa_f_bins:

        # print (f'{value}')
        if (abs(value-freq_lower) < start_diff):
            print(abs(value-freq_lower))
            start_diff = abs(value-freq_lower)
            index_start = cnt
            print(f'{index_start}')
        if (abs(value-freq_end) < end_diff):
            index_end = cnt
            end_diff = abs(value-freq_end)
            print(abs(value-freq_lower))
            print(f'{index_end}')
        cnt += 1

    print(
        f'{index_start} | {librosa_f_bins[index_start]} => {index_end} | {librosa_f_bins[index_end]}')
    return index_start, index_end





def plot_rain_psd(data = None,time_vector = [], min_f = 100000, max_f = 140000, f_interval = 100, t_interval = 1, min_t = 0, max_t = 500, filepath = ""):
    
    
    #build 2 Data Array
    
    
    filepath = "psd_.png"
    
    time_cnt = 0
    energy_data = [] # f domain
    time_data = [] # t domain
    full_energy_data = []
    discretised_time_cnt = 0
    t_ref = -1
    
    for t_int in data:
        
        if t_ref == -1:
            t_ref = time_vector[time_cnt]
            
        
        f_int = 0
        energy_data.append([])
        energy_val = 0
        f_ref = -1
        delta_f = 0
        energy_v = []
        
        for f_data in t_int[1]:
            
            if t_int[0][f_int]<min_f:
                f_int +=1 
                continue
            
            if t_int[0][f_int]>max_f:
                f_int +=1 
                continue
            
            if f_ref == -1:
                f_ref = t_int[0][f_int]
            
            energy_v.append(f_data)
          
            
            if float(t_int[0][f_int] - f_ref) > float(f_interval):
                
                energy_data[time_cnt].append(max(energy_v))
                f_ref = -1
                energy_v = []
            
            f_int +=1 
        
        
        time_data.append(energy_data[time_cnt])
        
        if (float(time_vector[time_cnt]) - t_ref) > t_interval:
            print (float(time_vector[time_cnt]) - t_ref)
            
            t_ref = -1
            full_energy_data.append([])
            f_data_idx = 0
            
            
            while f_data_idx < len(time_data[0]):
                e_vals = []
                for t_data in time_data:
            
                    e_vals.append(t_data[f_data_idx])
                
                full_energy_data[discretised_time_cnt].append(float(sum(e_vals))/len(e_vals))
                  
                f_data_idx += 1

            time_data = []
            discretised_time_cnt +=1
            
        
        
        
        
        time_cnt +=1 
        if time_cnt > max_t:
            break
    print (full_energy_data)
    ax = sns.heatmap(full_energy_data)
    plt.savefig(filepath)
    return full_energy_data
   


def build_psd(data = None, time_vector = [], min_f = 100000, max_f = 140000, f_interval = 100, t_interval = 1, min_t = 0, max_t = 500, filepath = ""):
    
    
    #build 2 Data Array
    
    
    filepath = "psd_.png"
    
    time_cnt = 0
    energy_data = [] # f domain
    time_data = [] # t domain
    full_energy_data = []
    discretised_time_cnt = 0
    t_ref = -1
    
    for t_int in data:
        
        if t_ref == -1:
            t_ref = time_vector[time_cnt]
            
        
        f_int = 0
        energy_data.append([])
        energy_val = 0
        f_ref = -1
        delta_f = 0
        energy_v = []
        
        for f_data in t_int[1]:
            
            if t_int[0][f_int]<min_f:
                f_int +=1 
                continue
            
            if t_int[0][f_int]>max_f:
                f_int +=1 
                continue
            
            if f_ref == -1:
                f_ref = t_int[0][f_int]
            
            energy_v.append(f_data)
          
            
            if float(t_int[0][f_int] - f_ref) > float(f_interval):
                
                energy_data[time_cnt].append(max(energy_v))
                f_ref = -1
                energy_v = []
            
            f_int +=1 
        
        
        time_data.append(energy_data[time_cnt])
        
        if (float(time_vector[time_cnt]) - t_ref) > t_interval:
            print (float(time_vector[time_cnt]) - t_ref)
            
            t_ref = -1
            full_energy_data.append([])
            f_data_idx = 0
            
            
            while f_data_idx < len(time_data[0]):
                e_vals = []
                for t_data in time_data:
            
                    e_vals.append(t_data[f_data_idx])
                
                full_energy_data[discretised_time_cnt].append(float(sum(e_vals))/len(e_vals))
                  
                f_data_idx += 1

            time_data = []
            discretised_time_cnt +=1
            
        
        
        
        
        time_cnt +=1 
        if time_cnt > max_t:
            break
    print (full_energy_data)
    ax = sns.heatmap(full_energy_data)
    plt.savefig(filepath)
    return full_energy_data
    

def plot_hist(frequency_activity, filename):

    plt.hist(frequency_activity, range=(0, 200000), bins=10)
    plt.savefig(filename)
    plt.clf()


def build_spec_upload(sample_rate, game_id,  hits, decisions, peak, avg, times, bulk_energies = None, pc_above_e=[], f=[], full_raw_data=[], save_path="", max_energies = [], targets=[], interesting=[], training_labels = [], memory = {}, activation_level = 0.8):

    start_time_dt = datetime.strptime(times[0], "%Y-%m-%dT%H:%M:%S.%fZ")
    delta_t_dt = datetime.strptime(
        times[1], "%Y-%m-%dT%H:%M:%S.%fZ") - start_time_dt
    

    t_len = len(times)
    

    # if peak != []:
    #     peak.append(0.0)
    #     avg.append(0.0)
    #     pc_above_e.append(0.0)

    # sample_rate = data.meta_data['sample_rate']





    # decisions
    n_fft = 8192
    y = None
    # if len(full_raw_data) == 0:
    #     y = data.frequency_ts_np * 40
    # else:
    y = full_raw_data

    fig, ax1 = plt.subplots(figsize=(8, 8))
    plt.specgram(y, NFFT=n_fft, Fs=sample_rate, scale="dB",
                 mode="magnitude", cmap="ocean")

    r_flag = random.randint(0,99999)

    filepath = f'{save_path}/{game_id}{r_flag}_decisions.png'
    plot_time = []


    # training data plot
    for label_time in training_labels:
        training_y = 40000
        training_x = float(label_time)
        rgba = cmap(0.999)
        plt.plot(training_x, training_y, 'go', color=rgba)
        
   
    
        
    
    for idx in decisions:

        _t = datetime.strptime(idx['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        _s = _t.strftime('%-S.%f')
        # print (_s)
        _d_t = _t - start_time_dt
        # print (idx)
        search_v = float(int(targets.index(idx['target']))/len(targets))
        
        rgba = cmap(search_v)
        y_val = (int(targets.index(idx['target'])) * 2000) + 1000
        plt.plot(float(_d_t.total_seconds()), y_val, 'go', color=rgba)


    for time in times:
        _t = datetime.strptime(times[time], "%Y-%m-%dT%H:%M:%S.%fZ")
        _d_t = _t - start_time_dt
        plot_time.append(float(_d_t.total_seconds()))

    

    labels = []
    lcnt = 0
    
    for target in targets:
        search_v = float(int(targets.index(target))/len(targets))
        lclr = cmap(search_v)
        # print (search_v, lclr)
        labels.append(mpatches.Patch(color=lclr, label=target))
        lcnt = lcnt + 1
    
    
  

    # for i, val in enumerate(peak):
    #     if val<0.7:
    #         peak[i] = 0

    # avg_plot_50 = [((0.5 * 50000) + 200000) for i in avg]
    # pc_above_e_plot_50 = [(((50/100) * 50000) + 250000) for i in pc_above_e]
    # energy_50_plot = [(((50/100) * 20000)) for i in pc_above_e]

    # peak_plot = [i * 20000 for i in peak]
    # avg_plot = [((i * 50000) + 200000) for i in avg]
    # pc_above_e_plot = [(((i/100) * 50000) + 250000) for i in pc_above_e]

    # color = (0.2,  # redness
    #          0.4,  # greenness
    #          0.2,  # blueness
    #          1.0  # transparency
    #          )
    # pk_color = (1.0,  # redness
    #             0.2,  # greenness
    #             0.4,  # blueness
    #             1.0  # transparency
    #             )
    # print (avg)
    # print (avg_plot)
    # print (len(plot_time), len(avg_plot))
    # plt.plot(plot_time, avg_plot[0:t_len], color=pk_color)
    # # print (len(plot_time), len(peak_plot))
    # plt.plot(plot_time, peak_plot[0:t_len], color=pk_color)
    # plt.plot(plot_time, pc_above_e_plot[0:t_len], color=pk_color)
    # plt.plot(plot_time, avg_plot_50[0:t_len], color='w')
    # plt.plot(plot_time, pc_above_e_plot_50[0:t_len], color='w')
    # plt.plot(plot_time, energy_50_plot[0:t_len], color='w')

    plt.colorbar()
    plt.legend(handles=labels)

    # plt.legend(loc="upper left")
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.savefig(filepath)
    plt.clf()
    
    
    # interesting
    n_fft = 8192
    y = None
    # if len(full_raw_data) == 0:
    #     y = data.frequency_ts_np * 40
    # else:
    y = full_raw_data

    fig, ax1 = plt.subplots(figsize=(8, 8))
    plt.specgram(y, NFFT=n_fft, Fs=sample_rate, scale="dB",
                 mode="magnitude", cmap="ocean")

    r_flag = random.randint(0,99999)

    filepath = f'{save_path}/{game_id}{r_flag}_activity.png'
    plot_time = []





    for idx in interesting:

        _t = datetime.strptime(idx['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        _s = _t.strftime('%-S.%f')
        # print (_s)
        _d_t = _t - start_time_dt
        # print (idx)
        search_v = float(int(targets.index(idx['target']))/len(targets))
        
        rgba = cmap(search_v)
        y_val = (int(targets.index(idx['target'])) * 2000) + 1000
        plt.plot(float(_d_t.total_seconds()), y_val, 'go', color=rgba)


    for time in times:
        _t = datetime.strptime(times[time], "%Y-%m-%dT%H:%M:%S.%fZ")
        _d_t = _t - start_time_dt
        plot_time.append(float(_d_t.total_seconds()))


    labels = []
    lcnt = 0
    
    for target in targets:
        search_v = float(int(targets.index(target))/len(targets))
        lclr = cmap(search_v)
        # print (search_v, lclr)
        labels.append(mpatches.Patch(color=lclr, label=target))
        lcnt = lcnt + 1
    
  
    plt.colorbar()
    plt.legend(handles=labels)

    # plt.legend(loc="upper left")
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.savefig(filepath)
    plt.clf()
    
   
        
   
    
    # plot individual bot energy profiles for debugging and interest
    for bot_id, energy_profile in bulk_energies.items():
        t_vals = [] 
        e_vals = []
        active_segments_x = []
        active_segments_y = []
        
        for iter_number, energy_pt in energy_profile.items():
            t_vals.append(float(plot_time[iter_number]))
            e_vals.append(float(energy_pt))
            if energy_pt > activation_level:
                active_segments_y.append(0.5)
                active_segments_y.append(0.5)
                history_time = max(0,(float(plot_time[iter_number]) - float((memory[bot_id] / 1000))))
                print (float((memory[bot_id] / 1000)))
                active_segments_x.append(history_time)
                active_segments_x.append(float(plot_time[iter_number]))
                plt.plot((active_segments_x),(active_segments_y), color = 'red')
                active_segments_x = []
                active_segments_y = []
                
        plt.plot((t_vals),(e_vals))
        
        # training data plot
        for label_time in training_labels:
            training_y = 0.5
            training_x = float(label_time)
            rgba = cmap(0.999)
            plt.plot(training_x, training_y, 'go', color=rgba)
        plt.ylabel('Energy')
        plt.xlabel('Time (s)')
        filepath = f'{save_path}/{bot_id}_activity.png'
        plt.savefig(filepath)
        plt.clf()
            
    
    
    
    for target in targets:
        
        search_v = 0.2
        rgba = cmap(search_v)
        plt.plot(plot_time[0:t_len-2], avg[target][0:t_len-2], color=rgba)
        plt.ylabel('<E>')
        plt.xlabel('Time (s)')
        filepath = f'{save_path}/{game_id}{r_flag}_avg_e_{target}.png'
        plt.ylim(0,1)
        plt.savefig(filepath)
        plt.clf()
        
    for target in targets:
        
        search_v = 0.2
        rgba = cmap(search_v)
        plt.plot(plot_time[0:t_len-2], pc_above_e[target][0:t_len-2], color=rgba)
        plt.ylabel('R [A/Sum]')
        plt.xlabel('Time (s)')
        plt.ylim(0,1)
        filepath = f'{save_path}/{game_id}{r_flag}_ratio_active_{target}.png'
        plt.savefig(filepath)
        plt.clf()
        
    for target in targets:
        
        search_v = 0.2
        rgba = cmap(search_v)
        plt.plot(plot_time[0:t_len-2], max_energies[target][0:t_len-2], color=rgba)
        plt.ylabel('R [A/Sum]')
        plt.xlabel('Time (s)')
        plt.ylim(0,1)
        filepath = f'{save_path}/{game_id}{r_flag}_max_{target}.png'
        plt.savefig(filepath)
        plt.clf()
    
    
        
        
        
        
        
    # plt.plot(plot_time[0:t_len-2], max_energies[0:t_len-2], color=pk_color)
    # plt.ylabel('Max(E)')
    # plt.xlabel('Time (s)')
    # filepath = f'{save_path}/{game_id}{r_flag}_max_e.png'
    # plt.savefig(filepath)
    # plt.clf()
    
    # plt.plot(plot_time[0:t_len-2], peak[0:t_len-2], color=pk_color)
    # plt.ylabel('Active/All')
    # plt.xlabel('Time (s)')
    # filepath = f'{save_path}/{game_id}{r_flag}_ratio_e.png'
    # plt.savefig(filepath)
    # plt.clf()
    
    
    
    
    
    #return time in delta t from start to file
    return plot_time

def build_spec(data,  id, bot_id, n_fft=None, f_min=0, f_max=0, custom=0, sr=96000, identifier=0, times=[], energies=[], hits=[], activation_level=0.2):
    print("building spec")

    if custom == 0:

        e_profile = np.array(energies)
        t_profile = np.array(times)

        y = data.frequency_ts_np * 40
        if n_fft == None:
            n_fft = 8192
        else:
            n_fft = int(n_fft)

        sample_rate = data.meta_data['sample_rate']
        print(activation_level)
        print("build")
        plt.specgram(y, NFFT=n_fft, Fs=sample_rate, scale="dB",
                     mode="magnitude", cmap="ocean")

        # X_Y_Spline = make_interp_spline(f_profile, e_profile)
        # # Returns evenly spaced numbers
        # # over a specified interval.
        # X_ = np.linspace(f_profile.min(), f_profile.max(), 500)
        # Y_ = X_Y_Spline(X_)

        # plt.plot( t_profile,e_profile , '-')
        # plt.plot( X_,Y_ , '-',color='green' )

        for idx, e in enumerate(energies):
            if e > float(activation_level):

                plt.plot(times[idx], 100000, 'go')

        for idx, e in enumerate(hits):
            if e == 1:
                plt.plot(times[idx], 150000, 'bv')

        plt.colorbar()
        print("done")

        plt.ylabel('Frequency (H)')
        plt.xlabel('Time (s)')

        if f_max != 0:
            plt.ylim([int(f_min), int(f_max)])

        if bot_id != "debug":
            snapshot_id = data.meta_data['snapshot_id']
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_spec.png'

        else:
            snapshot_id = data.meta_data['snapshot_id']
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{id}.png'

        plt.savefig(filepath)

    if custom == 1:

        y = data * 40
        if n_fft == None:
            n_fft = 8192
        else:
            n_fft = int(n_fft)

        sample_rate = sr
        print("build")
        plt.specgram(y, NFFT=n_fft, Fs=sample_rate, scale="dB",
                     mode="magnitude", cmap="ocean")
        plt.colorbar()
        print("done")

        plt.ylabel('Frequency (H)')
        plt.xlabel('Time (s)')

        if f_max != 0:
            plt.ylim([int(f_min), int(f_max)])

        if bot_id != "debug":
            snapshot_id = data.meta_data['snapshot_id']
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_spec.png'

        else:

            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{identifier}.png'

        plt.savefig(filepath)


def build_waveform(data, id, bot_id):
    v = data.frequency_ts_np
    snapshot_id = data.meta_data['snapshot_id']
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_waveform.png'
    sampling_rate = data.meta_data['sample_rate']

    fig, ax = plt.subplots(figsize=(10, 5))
    img = librosa.display.waveshow(v, sr=sampling_rate)
    # plt.colorbar()
    fig.savefig(f'{filepath}')
    plt.close(fig)


def build_f_profile(data, id, bot_id):
    v = data.frequency_ts_np
    print('data')
    print(v)
    snapshot_id = data.meta_data['snapshot_id']

    sampling_rate = data.meta_data['sample_rate']
    n_fft = 16384
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile1.png'
    ft = np.abs(librosa.stft(data.frequency_ts_np[:n_fft], hop_length=n_fft+1))
    librosa_f_bins = librosa.core.fft_frequencies(
        n_fft=n_fft, sr=sampling_rate)

    # index_start  = min(range(len(librosa_f_bins)), key=lambda i: abs(librosa_f_bins[i]-freq_lower))
    # index_end  = min(range(len(librosa_f_bins)), key=lambda i: abs(librosa_f_bins[i]-freq_end))

    # --- plt 1

    index_start = 0
    index_end = 0
    freq_lower = 30
    freq_end = 1000
    index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)

    freqs = []
    ft_p = []
    # ft = ft[index_start:index_end]
    for i in range(index_start, index_end):
        freqs.append(librosa_f_bins[i])
        ft_p.append(ft[i])

    plt.plot(freqs, ft_p)

    plt.title(f'Power Spectrum {freq_lower}:{freq_end}')
    # plt.xlim(20,1000)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (db)')
    plt.savefig(filepath)
    plt.clf()

    # --- plt 2

    index_start = 0
    index_end = 0
    freq_lower = 0
    freq_end = 2000
    index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)
    ft_p = []
    freqs = []
    # ft = ft[index_start:index_end]
    for i in range(index_start, index_end):
        freqs.append(librosa_f_bins[i])
        ft_p.append(ft[i])

    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile2.png'
    print('data length')
    print(len(ft))
    print('f length')
    print(len(freqs))
    print(f'{index_start} => {index_end}')

    plt.plot(freqs, ft_p)
    plt.title(f'Power Spectrum {freq_lower}:{freq_end}')
    plt.xlabel('Frequency Bin')
    plt.ylabel('Amplitude')
    plt.savefig(filepath)
    plt.clf()

    # --- plt 3

    index_start = 0
    index_end = 0
    freq_lower = 0
    freq_end = 400
    index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)

    freqs = []
    # ft = ft[index_start:index_end]

    ft_p = []
    for i in range(index_start, index_end):
        freqs.append(librosa_f_bins[i])
        ft_p.append(ft[i])

    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile3.png'
    print(len(ft))
    plt.plot(freqs, ft_p)
    plt.title(f'Power Spectrum {freq_lower}:{freq_end}')
    plt.xlabel('Frequency Bin (Hz)')
    plt.ylabel('Amplitude (db)')
    plt.savefig(filepath)
    plt.clf()

    # --- plt 4

    # index_start = 0
    # index_end = 0
    # freq_lower = 0
    # freq_end = librosa_f_bins[len(librosa_f_bins)-3]
    # freq_end = 20000
    # index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)

    # ft_p = []
    # freqs = []

    # for i in range(index_start,index_end):
    #     freqs.append(librosa_f_bins[i])
    #     ft_p.append(ft[i])
    # filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile3.png'
    # print (len(ft))
    # plt.bar(freqs, ft_p);
    # plt.title(f'Power Spectrum {freq_lower}:{freq_end}');
    # plt.xlabel('Frequency Bin (Hz)');
    # plt.ylabel('Amplitude (db)');
    # plt.savefig(filepath)
    # plt.clf()


# --- input feature distribution ---
import operator
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
    for feature, f in features.items():
        # print (f'{feature}, {f}')

        for fr, v in f_buckets.items():
            if abs(f-fr) < f_bucket_size:
                if fr in list(f_buckets.keys()):
                    f_buckets[fr] += 1
                    f_buckets_names[f].append(feature)
                    f_name_list.append(feature)
                    t_ += 1
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
            min_count = min(min_count, v)

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

    with open('feature_names.json', 'w+') as f:
        json.dump(dist_data, f)

    # print (distributed_name_list)
    return distributed_name_list
