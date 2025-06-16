# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 11:46:01 2025

@author: AXIm Admin
"""

## Assume we start with source warmed up and detector warmed up
## All motors in position

import time
import os
from BrillMethods import *
import source_commands as SC
import aerotech_functions as AT
import shutil
import numpy as np
import newport_functions as NP
import random

filepath = 'D:/25_04_07/3_MuscleGFPD9_vibr_test/'
Subfolder_name="data/"

newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exp = 3000 #ms
sample_out_dx = 10 # relative move of sample out, sample_out = AT_x + dx
num_proj = 20 # num projections
numDarkFr = 1 # number of darks, taken 10mins after scan
numFlatFr = 1 # number of flat frames averaged 
numSampleFr = 1 # number of sample frames averaged

# Jitter
jitter_flag = 0
px = 8e-3
jitter_range_px = 20 # number of pixels in max jitter (twice this number)
if jitter_flag:
    # check if the file exists already (from a previous broken CT for example)
    if os.path.isfile(filepath + '/jitter.txt'):
        # read it            
        jitter_file = open(filepath + '/jitter.txt')
        read_jitter = jitter_file.readlines()
        lines = len(read_jitter)
        jitter_file.close()
        # if the number of projections don't match I create a new one (and overwrite it)                
        if lines != num_proj:
            jitter_sequence = [random.randrange(-jitter_range_px,jitter_range_px,1) for i in range(num_proj)]
            jitter_sequence = np.array(jitter_sequence)*px 
            jitter_sequence[0] = 0
            jitter_file = open(filepath + '/jitter.txt','w')
            for j in jitter_sequence:
                jitter_file.write( str(j) + '\n')
            jitter_file.close()
        # otherwise I use the one existing
        else:
            jitter_sequence = np.array(read_jitter).astype(float)
    else:
        jitter_sequence = [random.randrange(-jitter_range_px,jitter_range_px,1) for i in range(num_proj)]
        jitter_sequence = np.array(jitter_sequence)*px
        jitter_sequence[0] = 0
        jitter_file = open(filepath + '/jitter.txt','w')
        for j in jitter_sequence:
            jitter_file.write( str(j) + '\n')
            jitter_file.close()

print("Exposure time:", exp*numSampleFr)
print("Number of projections:", num_proj)
print("Total exposure time (mins):", num_proj*exp*numSampleFr/60/1000)

# Start Aerotech
AT.AT_connect()
AT_x = np.round(AT.AT_get_pos('X'),3)
AT_y = np.round(AT.AT_get_pos('Y'),3)
AT_z = np.round(AT.AT_get_pos('Z'),3)

# Newport
NP_xaxis = 1
NP_zaxis = 2
NP.NP_init()
NP_x = NP.NP_gp(NP_xaxis)
NP_z = NP.NP_gp(NP_zaxis)

# convert exposure time to string for saving
exp_str = exp/1000
exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')

# Open a file in write mode to save parameters
param_file = os.path.join(filepath, 'scan_parameters.txt')
with open(param_file, 'w') as file:
    # Write each variable to the file
    file.write(f"exp = {exp/1000} #sec\n")
    file.write(f"sample_out_dx = {sample_out_dx}\n")
    file.write(f"num_proj = {num_proj}\n")
    file.write(f"numDarkFr = {numDarkFr}\n")
    file.write(f"numFlatFr = {numFlatFr}\n")
    file.write(f"numSampleFr = {numSampleFr}\n")
    file.write(f"Sample X = {AT_x}\n")
    file.write(f"Sample Y = {AT_y}\n")
    file.write(f"Sample Z = {AT_z}\n")
    file.write(f"Detector X = {NP_x}\n")
    file.write(f"Detector Z = {NP_z}\n")

# define empty variables
error_flag = c_int(0)
rec_frames = c_int(0)
captured_data = POINTER(DataObj)()
captured_data_mean = POINTER(DataObj)()

##### Start detecotor
# define pointers
detector_pointer = POINTER(DetObj)()
processor_pointer = Processor_Init()
# initialise detector
print("Initializing the detector...")
result = BrillianSe_Init(byref(detector_pointer))
print("Initialized detector: %s" % BrillianSe_GetErrorMessage(result))
result = BrillianSe_SetNumFrames(detector_pointer, 1)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
# Set times
result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
#####

result = BrillianSe_SetNumFrames(detector_pointer, 1)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

# flats
AT.AT_move_axis_linear('X',sample_out_dx)
time.sleep(30)
result = BrillianSe_SetNumFrames(detector_pointer, numFlatFr)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
fname = filepath + Subfolder_name + 'flat_' + exp_str + 'sec_' + str(numFlatFr) + '.raw'
WriteToFile(fname, captured_data_mean)
Data_Delete(byref(captured_data))
Data_Delete(byref(captured_data_mean))
AT.AT_move_axis_linear('X',-sample_out_dx)
result = BrillianSe_SetNumFrames(detector_pointer, numSampleFr)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
    
#################################################
for proj_idx in np.arange(num_proj):
        
    if jitter_flag:
        NP.NP_ma(NP_xaxis, NP_x+jitter_sequence[proj_idx])
    
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
    fname = filepath + Subfolder_name + 'Im_' + exp_str + 'sec_' + 'proj' + str(proj_idx) + '.raw'
    WriteToFile(fname, captured_data_mean)
    Data_Delete(byref(captured_data))
    Data_Delete(byref(captured_data_mean))
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    
if jitter_flag:
    NP.NP_ma(NP_xaxis, NP_x)
    
# xcs = SC.XCS("128.40.160.24")
# xcs.send('#user')
# xcs.send("state=ready")
# rec = xcs.receive()
# print(rec)
# assert rec == "ok\n", "failed to set 'ready' state as target"
# SC.wait_for_state_transition(xcs)

Processor_Delete(byref(processor_pointer))

#print("Detector shutdown is in progress...")
#result = BrillianSe_Shutdown(byref(detector_pointer))
#print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')
