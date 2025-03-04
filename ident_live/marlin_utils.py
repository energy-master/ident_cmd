#/usr/bin/python3

import numpy as np
import os
from scipy.io import wavfile
import time as t
# ================================== timers ==================

duration = {}
def startt(name=""):
    duration[name] = t.time()
    
def stopt(desc = "", name="", out=0):
    # print (desc)
   
    if name == "":
        name = desc
    
    d_ = t.time() - duration[name]
    if out == 1:
        print (f'{desc} => {d_} (s)')
    duration[name] = d_


# ================================== band pass ==================