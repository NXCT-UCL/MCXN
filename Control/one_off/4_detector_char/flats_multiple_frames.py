# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:31:38 2024

@author: AXIm Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 11:15:32 2024

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

filepath = r'D:\24_11_07\Flats_multiple_frames\\'
folder_name="data\\"

newpath = filepath + folder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exposures = [8000] #ms
numFrames = 1 #Only one frame
numRep = 256
numDarks=10

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
time.sleep(120)

for exp in exposures:
    exp_str = exp/1000
    exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
    # Create folder
    subfolder_name=folder_name+exp_str+"s\\"
    newpath = filepath + subfolder_name
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    #Turn the source on
    print("turning on x-rays")
    xcs.send("state=on")
    rec = xcs.receive()
    print(rec)
    assert rec == "ok\n", "failed to set 'on' state as target"
    SC.wait_for_state_transition(xcs)
    
    time.sleep(120)
    
    #Set acquisition parameters
    result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
    print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
    
    result = BrillianSe_SetNumFrames(detector_pointer, numFrames)
    print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
    
    #Acquire frames
    for n in range(numRep):
        print('Acquiring image')
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fname = f"{filepath}{subfolder_name}Flat_exp{exp_str}s_rep{n}_{timestamp}.raw"
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
    
    
    time.sleep(120)
    
    #Acquire darks
    result = BrillianSe_SetNumFrames(detector_pointer, numDarks)
    print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{filepath}{subfolder_name}Dark_exp{exp_str}s_rep{numDarks}_{timestamp}.raw"
    WriteToFile(fname, captured_data_mean)
    #Delete data
    Data_Delete(byref(captured_data))
    Data_Delete(byref(captured_data_mean))
    

#Delete processor to close connection
Processor_Delete(byref(processor_pointer))

#Close the socket
result=BrillianSe_CloseAllSockets(detector_pointer)
# Alywas remember to shut down the detector (bring down the voltage to zero)
#print("Detector shutdown is in progress...")
#result = BrillianSe_Shutdown(detector_pointer);
#print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')

