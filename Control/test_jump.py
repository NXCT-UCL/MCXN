## Assume we start with source warmed up and detector warmed up
## All motors in position

import time
import os
from BrillMethods import *
import source_commands as SC
import aerotech_functions as AT
import pressure_sensor_v3 as PS
import ESS_Commands_V7 as ESS
import shutil
import numpy as np

filepath = 'D:/25_02_25/2_test_jump/'
Subfolder_name="data/"

newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

# Parameters for reference scan
pre_scan = 1
pre_scan_step = 9 #degrees, must be multiple of increment
pre_scan_folder = 'pre_scan/'
newpath = filepath + pre_scan_folder
if pre_scan:
    if not os.path.exists(newpath):
        os.makedirs(newpath)


exp = 5000 #ms
sample_out_dx = 5 # relative move of sample out, sample_out = AT_x + dx
num_proj = 2 # num projections
rotation_angle = 360 # angular range
ESS_start_pos = -8 # rotator pos at proj 0
start_proj = 0 # can start at projection number start_proj
direction = -1 # rotation direction
extra_proj = 1 # bolean, extra projection at ESS_start_pos at end of scan
flat_interval = 1000 # how many proj to take flats 
numDarkFr = 1 # number of darks, taken 10mins after scan
numFlatFr = 5 # number of flat frames averaged 
numSampleFr = 1 # number of sample frames averaged
increment = direction*(rotation_angle/num_proj) #rotation increment at each projection

print("Exposure time:", exp*numSampleFr)
print("Number of projections:", num_proj)
print("Total exposure time (mins):", num_proj*exp*numSampleFr/60/1000)

# Start Aerotech
AT.AT_connect()
AT_x = np.round(AT.AT_get_pos('X'),3)
AT_y = np.round(AT.AT_get_pos('Y'),3)
AT_z = np.round(AT.AT_get_pos('Z'),3)

socket=ESS.ESS_Open()
ESS.ESS_Velocity(1268640)
ESS.ESS_Acceleration_Speed(184320)
ESS.ESS_Deceleration_Speed(184320)
ESS.ESS_PGain(2000)
ESS.ESS_VelocityFF(2048)
ESS.ESS_Velocity_PGain(2.5)
ESS.ESS_Prep_Move()

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
    file.write(f"rotation_angle = {rotation_angle}\n")
    file.write(f"ESS_start_pos = {ESS_start_pos}\n")
    file.write(f"start_proj = {start_proj}\n")
    file.write(f"direction = {direction}\n")
    file.write(f"extra_proj = {extra_proj}\n")
    file.write(f"flat_interval = {flat_interval}\n")
    file.write(f"numDarkFr = {numDarkFr}\n")
    file.write(f"numFlatFr = {numFlatFr}\n")
    file.write(f"numSampleFr = {numSampleFr}\n")
    file.write(f"Sample X = {AT_x}\n")
    file.write(f"Sample Y = {AT_y}\n")
    file.write(f"Sample Z = {AT_z}\n")

# 
PS_socket = PS.PS_Open()
press_read = PS.PS_check_pressure(PS_socket)
if press_read == 0:
    ESS.ESS_Close()
else:
    ESS.ESS_Absolute_Move(ESS_start_pos) #rotation

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
posRot = []

if pre_scan:
    
    if PS.PS_check_pressure(PS_socket):
        ESS.ESS_Absolute_Move(ESS_start_pos) #rotation
    
    for angle in np.arange(0,rotation_angle,pre_scan_step):
               
        press_read = PS.PS_check_pressure(PS_socket)
        if press_read == 0:
            ESS.ESS_Close()
            break
        
        ESS.ESS_Absolute_Move(ESS_start_pos+direction*angle) #rotation
        posRot=np.append(posRot,ESS.ESS_Position())
        
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        
        fname = filepath + pre_scan_folder + 'Im_' + str(angle) + '.raw'
        WriteToFile(fname, captured_data)
        Data_Delete(byref(captured_data))

        print('######### Pre Scan Angle: '+str(angle) + ' ##########')
        
result = BrillianSe_SetNumFrames(detector_pointer, 1)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

AT.AT_move_axis_linear('X',sample_out_dx)
time.sleep(60)
AT.AT_move_axis_linear('X',-sample_out_dx)
    
#################################################
for proj_idx in np.arange(start_proj,num_proj):
    
    if proj_idx % flat_interval == 0:
        AT.AT_move_axis_linear('X',sample_out_dx)
        time.sleep(5)
        
        if proj_idx > 0:
            time.sleep(60)
        
        result = BrillianSe_SetNumFrames(detector_pointer, numFlatFr)
        print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
        
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
        
        fname = filepath + Subfolder_name + 'flat_' + exp_str + 'sec_' + str(numFlatFr) + 'proj' + str(proj_idx) + '.raw'
        WriteToFile(fname, captured_data_mean)
        Data_Delete(byref(captured_data))
        Data_Delete(byref(captured_data_mean))
        
        AT.AT_move_axis_linear('X',-sample_out_dx)
        
        result = BrillianSe_SetNumFrames(detector_pointer, numSampleFr)
        print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
    
    press_read = PS.PS_check_pressure(PS_socket)
    if press_read == 0:
        ESS.ESS_Close()
        break
    
    Step_position = ESS_start_pos+proj_idx*increment
    ESS.ESS_Absolute_Move(Step_position) #rotation
    posRot=np.append(posRot,ESS.ESS_Position())

    captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
    captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
    fname = filepath + Subfolder_name + 'Im_' + exp_str + 'sec_' + 'proj' + str(proj_idx) + '.raw'
    WriteToFile(fname, captured_data_mean)
    Data_Delete(byref(captured_data))
    Data_Delete(byref(captured_data_mean))
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    np.savetxt(filepath+Subfolder_name+'/RotatorPositionLog.txt',posRot)
    

if extra_proj:
    
    Step_position = ESS_start_pos

    if PS.PS_check_pressure(PS_socket):
        ESS.ESS_Absolute_Move(Step_position) #rotation
        posRot=np.append(posRot,ESS.ESS_Position())
        captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
        captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
        fname = filepath + Subfolder_name + 'Im_' + exp_str + 'sec_' + 'proj_end.raw'
        WriteToFile(fname, captured_data_mean)
        Data_Delete(byref(captured_data))
        Data_Delete(byref(captured_data_mean))

##### End flat
AT.AT_move_axis_linear('X',sample_out_dx)
time.sleep(5)
result = BrillianSe_SetNumFrames(detector_pointer, numFlatFr)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))
captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
fname = filepath + Subfolder_name + 'flat_' + exp_str + 'sec_' + str(numFlatFr) + 'Fr_proj_end.raw'
WriteToFile(fname, captured_data_mean)
Data_Delete(byref(captured_data))
Data_Delete(byref(captured_data_mean))
AT.AT_move_axis_linear('X',-sample_out_dx)
time.sleep(5)
#####

Processor_Delete(byref(processor_pointer))

print('######## FINISHED ########')
