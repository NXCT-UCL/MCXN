# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 14:36:59 2024

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

filepath = r'D:\24_11_07\Darks_stabilisation_20h\\'
subfolder_name="data/"

newpath = filepath + subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exp = 2000 #ms
numFrames = 1 #Only one frame
numRep = 14400

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

#time.sleep(300)

# Set times
result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
#####

exp_str = exp/1000
exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')

result = BrillianSe_SetNumFrames(detector_pointer, numFrames)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

for n in range(numRep):
    print('Acquiring image')
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{filepath}{subfolder_name}Dark_exp{exp_str}s_rep{n}_{timestamp}.raw"
    WriteToFile(fname, captured_data)
    #Delete data
    Data_Delete(byref(captured_data))
    
    #Waiting
    print('Waiting')
    time.sleep(3)

#Delete processor to close connection
Processor_Delete(byref(processor_pointer))

#Close the socket
result=BrillianSe_CloseAllSockets(detector_pointer)
# Alywas remember to shut down the detector (bring down the voltage to zero)
print("Detector shutdown is in progress...")
result = BrillianSe_Shutdown(detector_pointer);
print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')

