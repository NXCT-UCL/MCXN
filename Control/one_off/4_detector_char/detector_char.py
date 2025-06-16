# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 15:52:59 2024

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

filepath = 'D:\24_11_07\Darks_stabilisation/'
Subfolder_name="data/"

newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exp_vec = [500,1000,2000,4000,8000] #ms
rep_vec = [1,2,4,8,16]

sample_out_dx = 5 # change

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

time.sleep(300)
# Start Aerotech
#AT.AT_connect()

for exp in exp_vec:
    
    # Set times
    result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
    print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
    #####
    
    exp_str = exp/1000
    exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
    
    for numRep in rep_vec:
        
        result = BrillianSe_SetNumFrames(detector_pointer, numRep)
        print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
        
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
        
        fname = filepath + Subfolder_name + 'Dark_exp' + exp_str + '_rep' + str(numRep)
        WriteToFile(fname, captured_data_mean)
        Data_Delete(byref(captured_data))
        Data_Delete(byref(captured_data_mean))

########################################################################

xcs = SC.XCS("128.40.160.24")
xcs.send('#user')
xcs.send("state=fullfocus")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'fullfocus' state as target"
SC.wait_for_state_transition(xcs)

time.sleep(600)

for exp in exp_vec:
    
    # Set times
    result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
    print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
    #####
    
    exp_str = exp/1000
    exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
    
    for numRep in rep_vec:
        
        result = BrillianSe_SetNumFrames(detector_pointer, numRep)
        print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
        
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
        
        fname = filepath + Subfolder_name + 'Flat_exp' + exp_str + '_rep' + str(numRep)
        WriteToFile(fname, captured_data_mean)
        Data_Delete(byref(captured_data))
        Data_Delete(byref(captured_data_mean))

AT.AT_connect()
AT.AT_move_axis_linear('X',sample_out_dx)
time.sleep(5)

for exp in exp_vec:
    
    # Set times
    result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
    print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
    #####
    
    exp_str = exp/1000
    exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
    
    for numRep in rep_vec:
        
        result = BrillianSe_SetNumFrames(detector_pointer, numRep)
        print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
        
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
        
        fname = filepath + Subfolder_name + 'Sample_exp' + exp_str + '_rep' + str(numRep)
        WriteToFile(fname, captured_data_mean)
        Data_Delete(byref(captured_data))
        Data_Delete(byref(captured_data_mean))


xcs = SC.XCS("128.40.160.24")
xcs.send('#user')
xcs.send("state=ready")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'ready' state as target"
SC.wait_for_state_transition(xcs)


# Capture many darks
idx = 0
time_limit = 10 * 60  # 10 minutes in seconds
start_time = time.time()
# Set times
exp = 1000 
result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
exp_str = exp/1000
exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
numRep = 1 
result = BrillianSe_SetNumFrames(detector_pointer, numRep)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
while time.time() - start_time < time_limit: 
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
    fname = filepath + Subfolder_name + 'Dark_end_exp' + exp_str + '_rep' + str(numRep) + '_idx' + str(idx)
    WriteToFile(fname, captured_data_mean)
    Data_Delete(byref(captured_data))
    Data_Delete(byref(captured_data_mean))
    idx += 1


Processor_Delete(byref(processor_pointer))
print("Detector shutdown is in progress...")
result = BrillianSe_Shutdown(byref(detector_pointer))
print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')
