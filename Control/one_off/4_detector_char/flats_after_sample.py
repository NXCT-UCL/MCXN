# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 13:39:22 2025

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

filepath = r'D:\24_11_07\Flats_after_sample_in\\'
folder_name="data\\"

newpath = filepath + folder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exp = 4000 #ms
numFrames = 1 #Only one frame
numRep_sample = 10
numRep_flat = 75
numRep_darks = 75

sample_out_dx=3
# To start up connection with the source
xcs = SC.XCS("128.40.160.24")
xcs.send('#user')

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
#Set acquisition parameters
result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))

result = BrillianSe_SetNumFrames(detector_pointer, numFrames)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

# Start Aerotech
AT.AT_connect()

#Bring sample inside
AT.AT_move_axis_linear('X',sample_out_dx)

exp_str = exp/1000
exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')

#Acquire frames
for n in range(numRep_sample):
    print('Acquiring image')
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{filepath}{folder_name}Sample_exp{exp_str}s_rep{n}_{timestamp}.raw"
    WriteToFile(fname, captured_data)
    #Delete data
    Data_Delete(byref(captured_data))

#Bring sample out
AT.AT_move_axis_linear('X',-sample_out_dx)

#Acquire flats
for n in range(numRep_flat):
    print('Acquiring image')
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{filepath}{folder_name}Flat_exp{exp_str}s_rep{n}_{timestamp}.raw"
    WriteToFile(fname, captured_data)
    #Delete data
    Data_Delete(byref(captured_data))
    
#Turn off the source
print("turning off x-rays")
xcs.send("state=ready")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'ready' state as target"
SC.wait_for_state_transition(xcs)

#Acquire darks
for n in range(numRep_darks):
    print('Acquiring image')
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{filepath}{folder_name}Darks_exp{exp_str}s_rep{n}_{timestamp}.raw"
    WriteToFile(fname, captured_data)
    #Delete data
    Data_Delete(byref(captured_data))

#Delete processor to close connection
Processor_Delete(byref(processor_pointer))

#Close the socket
result=BrillianSe_CloseAllSockets(detector_pointer)

print('######## FINISHED ########')
