


import sys, requests, re
import numpy as np

import matplotlib
import matplotlib.pyplot as plt

# -- bot id --
decision_id = sys.argv[1]



# -- from --
decisions_path = 'https://marlin-network.hopto.org/mldata/interesting'
decision_data_path = f'{decisions_path}/{decision_id}.dat'

# -- request --
r_ = requests.get(decision_data_path, allow_redirects=True, stream=True) 

total_length = r_.headers.get('content-length')
        
save_filepath = "tmp_dd.dat"

# -- download & write

f = open(save_filepath, 'wb')
dl = 0
total_length = int(total_length)
for data in r_.iter_content(chunk_size=2000):
    dl += len(data)
    f.write(data)
    done = int(50* dl / total_length)
    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
    sys.stdout.flush()

sys.stdout.flush()
    
np_data = None
# -- load  --
with open(save_filepath, 'rb') as fr:
    c = fr.read()
    dt = np.dtype("float32")
    np_data  = np.frombuffer(c, dtype=dt)
    # print (np_data.shape)
    
# -- display
sr = 384000
if np_data is not None:
    
    NFFT = 1024  ## the length of the windowing segments
    Fs = int(1.0 / sr)  ## the sampling frequency

    fig, (ax1, ax2) = plt.subplots(nrows=2)
    ax1.plot(np_data)
    Pxx, freqs, bins, im = ax2.specgram(np_data, NFFT=NFFT, Fs=Fs, noverlap=900)
    
    plt.show()