## Assume we start with source warmed up and detector warmed up
## All motors in position


import os
from BrillMethods import *
import source_commands as SC
import aerotech_functions as AT
import time

filepath = 'D:/24_09_20/'
Subfolder_name="1_test_brillianse/"

newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
exp = 2000 #ms
sample_out_dx = 5 # change

print("Exposure time:", exp)

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

# Start Aerotech
AT.AT_connect()

# define empty variables
error_flag = c_int(0)
rec_frames = c_int(0)
captured_data = POINTER(DataObj)()

# Take flat field
#####
AT.AT_move_axis_linear('X',sample_out_dx)
time.sleep(5)
captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
fname = filepath + Subfolder_name + 'flat.raw'
WriteToFile(fname, captured_data)
AT.AT_move_axis_linear('X',-sample_out_dx)
time.sleep(5)
#####

# Take sample
captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
fname = filepath + Subfolder_name + 'Sample.raw'
WriteToFile(fname, captured_data)

xcs = SC.XCS("128.40.160.24")
xcs.send('#user')
xcs.send("state=ready")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'ready' state as target"
SC.wait_for_state_transition(xcs)

# capture dark
captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
fname = filepath + Subfolder_name + 'dark.raw'
WriteToFile(fname, captured_data)

Data_Delete(byref(captured_data))
Processor_Delete(byref(processor_pointer))

print("Detector shutdown is in progress...")
result = BrillianSe_Shutdown(byref(detector_pointer))
print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

print('######## FINISHED ########')
