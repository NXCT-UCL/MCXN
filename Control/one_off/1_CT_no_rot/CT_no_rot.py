# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 12:04:35 2024

@author: AXIm Admin

run CT without rotation

"""

import numpy as np
import os
import time
import kinetix_functions as KF
import aerotech_functions as AT

filepath = 'D:/24_03_25/'
Subfolder_name="4_CT_noMov_50kv_1p2um/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 10
binn = 1
num_proj = 60

print("Exposure time:", exp)
print("Pixel bin factor:", binn)

for proj_idx in np.arange(0,num_proj):
    
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'Im_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'proj' + str(proj_idx) 
    KF.save_image(image, fname)
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    time.sleep(50)

print('######## FINISHED ########')

###################

Subfolder_name="5_CT_noRot_50kv_1p2um/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

AT.AT_connect()

for proj_idx in np.arange(0,num_proj):
    
    AT.AT_move_axis_linear('X',2)
    time.sleep(2) 
    AT.AT_move_axis_linear('X',-2)
    
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'Im_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'proj' + str(proj_idx) 
    KF.save_image(image, fname)
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    time.sleep(50)

print('######## FINISHED ########')