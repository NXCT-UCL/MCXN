# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 10:19:13 2025

@author: AXIm Admin

for finding geometry
start with x-rays on and sample marker in center of FoV
"""

import os
from detectors.factory import get_detector
import aerotech_functions as AT
import numpy as np
import source_commands as SC
import shutil
import time
import tifffile as tiff

filepath = 'D:/25_08_11/2_geom/'

if not os.path.exists(filepath):
    os.makedirs(filepath)
    
# save the current file
script_name = os.path.basename(__file__)
destination = os.path.join(filepath, script_name)
shutil.copy(__file__, destination)

exp = 1000 #ms
sample_dx = 1.0 #mm
sample_dz = 1.0 #mm
numSampleFr = 1
det_name = 'primeBSI'

print("Exposure time:", exp*numSampleFr)
print("Number of Frames:", numSampleFr)
print("Movement X (mm):", sample_dx)
print("Movement Z (mm):", sample_dz)

# Start Aerotech
AT.AT_connect()
AT_x = np.round(AT.AT_get_pos('X'),3)
AT_y = np.round(AT.AT_get_pos('Y'),3)
AT_z = np.round(AT.AT_get_pos('Z'),3)

# convert exposure time to string for saving
exp_str = exp/1000
exp_str = str(int(exp_str)) if exp_str.is_integer() else str(exp_str).replace('.', 'p')
dx_str = str(int(sample_dx)) if sample_dx.is_integer() else str(sample_dx).replace('.', 'p')
dz_str = str(int(sample_dz)) if sample_dz.is_integer() else str(sample_dz).replace('.', 'p')

# Open a file in write mode to save parameters
param_file = os.path.join(filepath, 'scan_parameters.txt')
with open(param_file, 'w') as file:
    # Write each variable to the file
    file.write(f"exp = {exp/1000} #sec\n")
    file.write(f"numSampleFr = {numSampleFr}\n")
    file.write(f"Sample X = {AT_x}\n")
    file.write(f"Sample Y = {AT_y}\n")
    file.write(f"Sample Z = {AT_z}\n")

detector = get_detector(det_name)
detector.initialise()
detector.set_exposure_time(exp)

im = detector.acquire_image()
fname = filepath + 'Im_Pos_x0_z0.tiff'
tiff.imsave(fname, im)
print('######### Pos x0 z0 ##########')

AT.AT_move_axis_linear('X',sample_dx)
time.sleep(2)

im = detector.acquire_image()
fname = filepath + 'Im_Pos_x' + dx_str + '_z0.tiff'
tiff.imsave(fname, im)
print('######### Pos x1 z0 ##########')

AT.AT_move_axis_linear('Y',sample_dz)
time.sleep(2)

im = detector.acquire_image()
fname = filepath + 'Im_Pos_x' + dx_str + '_z' + dz_str + '.tiff'
tiff.imsave(fname, im)
print('######### Pos x1 z1 ##########')

AT.AT_move_axis_linear('X',-sample_dx)
time.sleep(2)

im = detector.acquire_image()
fname = filepath + 'Im_Pos_x0_z' + dz_str + '.tiff'
tiff.imsave(fname, im)
print('######### Pos x0 z1 ##########')

AT.AT_move_axis_linear('Y',-sample_dz)
time.sleep(2)

AT.AT_disconnect()

# xcs = SC.XCS("128.40.160.24")
# xcs.send('#user')
# xcs.send("state=ready")
# rec = xcs.receive()
# print(rec)
# assert rec == "ok\n", "failed to set 'ready' state as target"
# SC.wait_for_state_transition(xcs)

detector.shutdown()

print('######## FINISHED ########')
