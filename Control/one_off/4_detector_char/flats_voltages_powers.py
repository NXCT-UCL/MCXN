# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:50:26 2024

@author: AXIm Admin
"""
import time
import os
from BrillMethods import *
import source_commands as SC
import aerotech_functions as AT
import shutil
import source_commands as SC

voltages=[40000, 50000, 60000, 70000, 80000]
power_factors=[0.2, 0.4, 0.6, 0.8, 1.0]
exposures = [500, 1000, 2000, 4000, 8000] #ms

numFrames=1
numDarks=10

filepath =  r'D:\24_11_07\Voltages_powers\\'
folder_name="data\\"

newpath = filepath + folder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

# To start up connection with the source
xcs = SC.XCS("128.40.160.24")
xcs.send('#user')

# define empty variables for the detector
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

for vol in voltages:
    # Create folder
    vol_str=str(vol/1000)
    subvol_name=vol_str+"kVp\\"
    volpath = filepath + folder_name + subvol_name
    if not os.path.exists(volpath):
        os.makedirs(volpath)
        
    for power in power_factors:
        # Create folder
        pow_str = str(int(power)) if power.is_integer() else str(power).replace('.', 'p')
        
        subpow_name=pow_str+"_pow_factor\\"
        powpath = volpath + subpow_name
        if not os.path.exists(powpath):
            os.makedirs(powpath)
            
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
        
        #Change power factor
        print("Changing power factor:")
        xcs.send("nanotube_power_factor="+str(power))
        rec = xcs.receive()
        
        # Reading power factor
        print("Reading power factor:")
        xcs.send("nanotube_power_factor=?")
        rec = xcs.receive()
        print("power factor (setpoint) = " + rec)
               
        #Every time, it needs refocus
        print("Applying setpoints / fullfocus")
        xcs.send("state=fullfocus")
        rec = xcs.receive()
        print(rec)
        assert rec == "ok\n", "failed to set 'fullfocus' state as target"
        SC.wait_for_state_transition(xcs)
    
        for exp in exposures:
            exp_str = exp/1000
            exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
            
            print("turning on x-rays")
            xcs.send("state=on")
            rec = xcs.receive()
            print(rec)
            assert rec == "ok\n", "failed to set 'on' state as target"
            SC.wait_for_state_transition(xcs)
            
            #Set acquisition parameters
            result = BrillianSe_SetFrameTime(detector_pointer, exp+5, exp)
            print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))
            
            result = BrillianSe_SetNumFrames(detector_pointer, numFrames)
            print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
            
            #Acquire image
            print('Acquiring image')
            captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            fname = f"{powpath}Flat_exp{exp_str}s_rep{numFrames}_{timestamp}.raw"
            WriteToFile(fname, captured_data)
            #Delete data
            Data_Delete(byref(captured_data))
        
            print("turning off x-rays")
            xcs.send("state=ready")
            rec = xcs.receive()
            print(rec)
            assert rec == "ok\n", "failed to set 'ready' state as target"
            SC.wait_for_state_transition(xcs)
            
            #Acquire darks
            result = BrillianSe_SetNumFrames(detector_pointer, numDarks)
            print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
            
            print('Acquiring darks')
            captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
            captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            fname = f"{powpath}Dark_exp{exp_str}s_rep{numDarks}_{timestamp}.raw"
            WriteToFile(fname, captured_data_mean)
            #Delete data
            Data_Delete(byref(captured_data))
            Data_Delete(byref(captured_data_mean))

#Delete processor to close connection
Processor_Delete(byref(processor_pointer))

#Close the socket
result=BrillianSe_CloseAllSockets(detector_pointer)
# Alywas remember to shut down the detector (bring down the voltage to zero)
print("Detector shutdown is in progress...")
result = BrillianSe_Shutdown(detector_pointer);
print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')




