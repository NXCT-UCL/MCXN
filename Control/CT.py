# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 15:48:27 2025

@author: AXIm Admin
"""

## Assume we start with source warmed up and detector warmed up
## All motors in position

import time
import os
import source_commands as SC
import aerotech_functions as AT
import pressure_sensor_v3 as PS
import ESS_Commands_V7 as ESS
import shutil
import numpy as np
import newport_functions as NP
import random
from detectors.factory import get_detector
import tifffile as tiff
import paramiko
import pandas as pd
from datetime import datetime

filepath = 'D:/25_10_31/test_crash/'
Subfolder_name="data/"

newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)
FLAG_FILE = os.path.join(filepath,"source_failure_log.txt")

    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

# Parameters for reference scan
pre_scan = 0
pre_scan_step = 30 #degrees, must be multiple of increment
pre_scan_folder = 'pre_scan/'
newpath = filepath + pre_scan_folder
if pre_scan:
    if not os.path.exists(newpath):
        os.makedirs(newpath)


exp = 2000 #ms
sample_out_dx = 2 # relative move of sample out, sample_out = AT_x + dx
num_proj = 2400 # num projections
rotation_angle = 360 # angular range
ESS_start_pos = -8 # rotator pos at proj 0
start_proj = 0 # can start at projection number start_proj
direction = -1 # rotation direction
extra_proj = 1 # bolean, extra projection at ESS_start_pos at end of scan
flat_interval = 200 # how many proj to take flats 
numDarkFr = 1 # number of darks, taken 10mins after scan
numFlatFr = 1 # number of flat frames averaged 
numSampleFr = 1 # number of sample frames averaged
increment = direction*(rotation_angle/num_proj) #rotation increment at each projection
det_name = 'moment'


# Jitter
jitter_flag = 1
px = 4.5e-3
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
            jitter_sequence[np.arange(0,num_proj,flat_interval)] = 0
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
        jitter_sequence[np.arange(0,num_proj,flat_interval)] = 0
        jitter_file = open(filepath + '/jitter.txt','w')
        for j in jitter_sequence:
            jitter_file.write( str(j) + '\n')
            jitter_file.close()

est_time = num_proj*exp*numSampleFr/60/1000
print("Exposure time:", exp*numSampleFr)
print("Number of projections:", num_proj)
print("Total exposure time (mins):", est_time)

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

# Newport
NP_xaxis = 1
NP_zaxis = 3
NP.NP_init()
NP_x = NP.NP_gp(NP_xaxis)
NP_z = NP.NP_gp(NP_zaxis)

# Source
xcs = SC.XCS("128.40.160.24")
xcs.send("nanotube_spotsize=?")
NT_ss = float(xcs.receive().strip())
xcs.send("nanotube_high_voltage=?")
NT_kvp = float(xcs.receive().strip())
xcs.send("nanotube_workpoint=?")
NT_wp = float(xcs.receive().strip())

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
    file.write(f"pre_scan_step = {pre_scan_step}\n")
    file.write(f"Sample X = {AT_x}\n")
    file.write(f"Sample Y = {AT_y}\n")
    file.write(f"Sample Z = {AT_z}\n")
    file.write(f"Detector X = {NP_x}\n")
    file.write(f"Detector Z = {NP_z}\n")
    file.write(f"Source Voltage = {NT_kvp:,} kVp\n")
    file.write(f"Source Size = {NT_ss}\n")
    file.write(f"Source workpoint = {NT_wp}\n")

# 
PS_socket = PS.PS_Open()
press_read = PS.PS_check_pressure(PS_socket)
if press_read == 0:
    ESS.ESS_Close()
else:
    ESS.ESS_Absolute_Move(ESS_start_pos) #rotation
    
detector = get_detector(det_name)
detector.initialise()
detector.set_exposure_time(exp)

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
        
        im = detector.acquire_image()
        
        fname = filepath + pre_scan_folder + 'Im_' + str(angle) + '.tiff'
        tiff.imsave(fname, im)

        print('######### Pre Scan Angle: '+str(angle) + ' ##########')

# AT.AT_move_axis_linear('X',sample_out_dx)
# time.sleep(10)
# AT.AT_move_axis_linear('X',-sample_out_dx)
    
#################################################
for proj_idx in np.arange(start_proj,num_proj):
    
    if proj_idx % flat_interval == 0:
        AT.AT_move_axis_linear('X',sample_out_dx)
        time.sleep(5)
        
        if jitter_flag:
            NP.NP_ma(NP_xaxis, NP_x)
        
        if proj_idx > 0:
            time.sleep(10)
            
        for idx_fr in range(numFlatFr):
            im = detector.acquire_image()
            fname = filepath + Subfolder_name + 'Flat_proj' + str(proj_idx) + '_fr' + str(idx_fr) + '.tiff'
            tiff.imsave(fname, im)
                
        AT.AT_move_axis_linear('X',-sample_out_dx)
    
    press_read = PS.PS_check_pressure(PS_socket)
    if press_read == 0:
        ESS.ESS_Close()
        break
    
    if jitter_flag:
        NP.NP_ma(NP_xaxis, NP_x+jitter_sequence[proj_idx])
    
    Step_position = ESS_start_pos+proj_idx*increment
    ESS.ESS_Absolute_Move(Step_position) #rotation
    posRot=np.append(posRot,ESS.ESS_Position())
    
    # for idx_fr in range(numSampleFr):
    #     im = detector.acquire_image()
    #     fname = filepath + Subfolder_name + 'Im_proj' + str(proj_idx) + '_fr' + str(idx_fr) + '.tiff'
    #     tiff.imsave(fname, im)
        
    im = detector.acquire_sequence(numSampleFr)

    fname = filepath + Subfolder_name + 'Im_proj' + str(proj_idx) + '.tiff'
    tiff.imsave(fname, im)
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    np.savetxt(filepath+Subfolder_name+'/RotatorPositionLog.txt',posRot)
    
    # If source has turned off, turn it back on again    
    xcs.send("state=?")
    rec = xcs.receive()
    if rec == "'ready'\n":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FLAG_FILE, "a") as f:
            f.write(f"{timestamp}\tProjection {proj_idx}\n")
        print(f"Source failure detected and logged at projection {proj_idx}")
        time.sleep(60) # pause for 60 seconds
        xcs = SC.XCS("128.40.160.24")
        xcs.send('#user')
        xcs.send("state=on")
        rec = xcs.receive()
        print(rec)
        assert rec == "ok\n", "failed to set 'fullfocus' state as target"
        SC.wait_for_state_transition(xcs)
    

if extra_proj:
    
    Step_position = ESS_start_pos
    
    if jitter_flag:
        NP.NP_ma(NP_xaxis, NP_x)

    if PS.PS_check_pressure(PS_socket):
        ESS.ESS_Absolute_Move(Step_position) #rotation
        posRot=np.append(posRot,ESS.ESS_Position())
        im = detector.acquire_sequence(numSampleFr)
        fname = filepath + Subfolder_name + 'Im_proj_end.tiff'
        tiff.imsave(fname, im)

##### End flat
AT.AT_move_axis_linear('X',sample_out_dx)
time.sleep(5)
for idx_fr in range(numFlatFr):
    im = detector.acquire_image()
    fname = filepath + Subfolder_name + 'Flat_proj_end_fr' + str(idx_fr) + '.tiff'
    tiff.imsave(fname, im)
AT.AT_move_axis_linear('X',-sample_out_dx)
time.sleep(5)
#####

ESS.ESS_Reset()
ESS.ESS_Close()
PS.PS_Close(PS_socket)
########################################################################

xcs = SC.XCS("128.40.160.24")
xcs.send('#user')
xcs.send("state=ready")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'ready' state as target"
SC.wait_for_state_transition(xcs)

time.sleep(300)
# capture dark
for idx in range(numDarkFr):                            
    im = detector.acquire_image()
    fname = filepath + Subfolder_name + 'Dark_end_idx' + str(idx) +'.tiff'
    tiff.imsave(fname, im)

detector.shutdown()

#Get Temp
# connection details
hostname = "128.40.160.22"   # or use the IP address
username = "mcxntv"
remote_file = "/home/mcxntv/temp_probe/temperature_log.csv"
local_file = "D:/temperature_log.csv"
last_n = 2*int(np.round(est_time))
output_file = os.path.join(filepath,"temp.csv")
# connect to Raspberry Pi
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username)  # no password needed now with SSH keys
# copy the full CSV to local machine
sftp = ssh.open_sftp()
sftp.get(remote_file, local_file)
sftp.close()
ssh.close()
# read only last N rows
df = pd.read_csv(local_file)
last_rows = df.tail(last_n)
# save to new local CSV
last_rows.to_csv(output_file, index=False, header=False)
print(f"Saved the last {last_n} mins to {output_file}")

print('######## FINISHED ########')
