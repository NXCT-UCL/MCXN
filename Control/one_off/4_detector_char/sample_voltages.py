# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:31:38 2024

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

filepath = r'D:\24_11_07\Sample_CNR_voltages\\'
folder_name="data\\"

newpath = filepath + folder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exp = 2000 #ms
exp_str=str(int(exp/1000))
sample_out_dx = 5 # change
voltages = [40000, 50000, 60000, 70000, 80000]
numFrames = 1 #Only one frame
numRep = 10
numDarks = 100

# define empty variables
error_flag = c_int(0)
rec_frames = c_int(0)
captured_data = POINTER(DataObj)()
captured_data_mean = POINTER(DataObj)()

# Start Aerotech
AT.AT_connect()

##### Start detecotor
# define pointers
detector_pointer = POINTER(DetObj)()
processor_pointer = Processor_Init()

# initialise detector
print("Initializing the detector...")
result = BrillianSe_Init(byref(detector_pointer))
print("Initialized detector: %s" % BrillianSe_GetErrorMessage(result))

# To start up connection with the source
xcs = SC.XCS("128.40.160.24")
xcs.send('#user')
time.sleep(120)

for vol in voltages:
    
    # Create folder
    vol_str=str(int(vol/1000))
    subvol_name=vol_str+"kVp\\"
    volpath = filepath + folder_name + subvol_name
    if not os.path.exists(volpath):
        os.makedirs(volpath)
    
    # Setting voltage
    print("Changing voltage:")
    xcs.send("nanotube_high_voltage="+str(vol))
    rec = xcs.receive()
    print(rec)
    
    # Reading voltage
    print("Reading voltage:")
    xcs.send("nanotube_high_voltage=?")
    rec = xcs.receive()
    print("voltage (setpoint) = " + rec)
           
    #Every time, it needs refocus
    print("Applying setpoints / fullfocus")
    xcs.send("state=fullfocus")
    rec = xcs.receive()
    print(rec)
    assert rec == "ok\n", "failed to set 'fullfocus' state as target"
    SC.wait_for_state_transition(xcs)
    
    time.sleep(120)
    
    #Set acquisition parameters
    result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
    print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
    
    result = BrillianSe_SetNumFrames(detector_pointer, numFrames)
    print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
    
    #Acquire sample frames
    for n in range(numRep):
        print('Acquiring image')
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fname = f"{volpath}Sample_exp{exp_str}s_rep{n}_{timestamp}.raw"
        WriteToFile(fname, captured_data)
        #Delete data
        Data_Delete(byref(captured_data))
    
    ## Acquire flats
    # Move the sample out
    print('Moving the sample out')
    AT.AT_move_axis_linear('X',sample_out_dx)
    time.sleep(5)
    print('Acquiring flats')
    #Acquire flat frames
    for n in range(numDarks):
        print('Acquiring image')
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fname = f"{volpath}Flat_exp{exp_str}s_rep{n}_{timestamp}.raw"
        WriteToFile(fname, captured_data)
        #Delete data
        Data_Delete(byref(captured_data))

    # Move the sample in
    print('Moving the sample out')
    AT.AT_move_axis_linear('X',-sample_out_dx)
    time.sleep(5)
    
    ## Acquire darks
    #Turn off the source
    print("turning off x-rays")
    xcs.send("state=ready")
    rec = xcs.receive()
    print(rec)
    assert rec == "ok\n", "failed to set 'ready' state as target"
    SC.wait_for_state_transition(xcs)
    
    #time.sleep(120)
    
    print('Acquiring darks')
    #Acquire flat frames
    for n in range(numDarks):
        print('Acquiring image')
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fname = f"{volpath}Dark_exp{exp_str}s_rep{n}_{timestamp}.raw"
        WriteToFile(fname, captured_data)
        #Delete data
        Data_Delete(byref(captured_data))
    

#Delete processor to close connection
Processor_Delete(byref(processor_pointer))

#Close the socket
result=BrillianSe_CloseAllSockets(detector_pointer)
# Alywas remember to shut down the detector (bring down the voltage to zero)
#print("Detector shutdown is in progress...")
#result = BrillianSe_Shutdown(detector_pointer);
#print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')

