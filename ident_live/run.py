#!/usr/local/bin/python3
import sys, os
import librosa
from dotenv import load_dotenv, dotenv_values
import math
# python3 ident_live.py 
# .wav sonar_1 new_dir 0001vixen 0.80 0.05 20 0.5 1_0_0/2_0_0/3_0_0/noise/1_0_1 2025-02-01 10:15:00 2025-11-22 10:17:0001 -1 1 0 120

batch_data = {
    "filename" : "20250101_000000_000.wav",
    "target" : "general_search",
    "time_increment" : 1200,
    "start_t_s" : 3600,
    "run_name" : "general_run",
    "user_id" : "001vixen",
    "activation_threshold" : 0.80,
    "ratio_threshold" : 0.05,
    "number_bots" : 20,
    "similarity_threshold" : 0.5,
    "versions" : "1_0_0/2_0_0/3_0_0/noise/1_0_1",
    "from_time" : "10:15:00 2025-11-22",
    "to_time" : "10:17:00",
    "flag_1" : -1,
    "flag_2" : 1
}


# get increments required
load_dotenv()
config = dotenv_values("config.env")


data_dir = config['DATA_DIR']
filename = batch_data['filename']
input_filepath = f'{data_dir}/{filename}'
sample_rate = librosa.get_samplerate(input_filepath)
data, sr = librosa.load(input_filepath, sr=sample_rate)

print (f'File has a sample rate : {sr}')
file_duration = float(math.floor(len(data)/sr))
print (f'File duration : {file_duration} s')

number_increment_runs = int(math.floor(file_duration/float(batch_data['time_increment'])))
print (f'Number of incremental runs required : {number_increment_runs}')


start_t_s = int(batch_data['start_t_s'])
start_times = [i for i in range(start_t_s,int(file_duration),batch_data['time_increment'])]
# print (start_times)
number_starts = len(start_times)

MAX_RUNS = 5

for start_time in start_times[:MAX_RUNS]:

    filename = batch_data['filename']
    target = batch_data['target']
    run_name = batch_data['run_name']
    user_id = batch_data['user_id']
    activation_threshold = batch_data['activation_threshold']
    ratio_threshold = batch_data['ratio_threshold']
    number_bots = batch_data['number_bots']
    start_s = int (start_time)
    end_s = int (start_time + int(batch_data['time_increment']))
    print ("Running cmd")
    cmd = f'nohup python3 ident_live.py {filename} {target} {run_name}_{start_time}_ {user_id} {activation_threshold} {ratio_threshold} {number_bots} 0.5 1_0_0/2_0_0/3_0_0/noise/1_0_1 2025-02-01 10:15:00 2025-11-22 10:17:0001 -1 1 {start_s} {end_s} &'
    
    os.system(cmd)
    
