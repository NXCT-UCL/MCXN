# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 10:24:00 2023

10 x 10 dithering steps, moving object (5um period accounted for mag)
1 min exposure per step (6x10sec)
then take flat field
Repeat this 30 times

Resolution target
40kVp, 1.2um spot size, 4cm Z_sd, 2cm Z_sm, 2x2 binning

@author: AXIm Admin
"""

import numpy as np
import os
import time
import kinetix_functions as KF
import pipython 

filepath = 'D:/23_10_13/BT_scan/'
Subfolder_name="attempt_4/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 1
binn = 2
num_samp = 6
num_flat = 6
num_subscans = 30

sample_out = 11 

sample_mag = 1.075 
start_x = -6.45
start_y = -4.25
d_step = 0.0005*sample_mag
period = 0.005*sample_mag
x_pos_vec = np.arange(start_x,start_x+period,d_step)
y_pos_vec = np.arange(start_y,start_y+period,d_step)

print("Exposure time:", exp)
print("Pixel bin factor:", binn)
print("Number of sample images:", num_samp)
print("Number of flat images:", num_flat)

PI_COM = 3
PI_BR = 9600
PI_Z = 1
PI_X = 2
PI_Y = 3

# Create a connection to the PI controller
pidevice = pipython.GCSDevice() 
# Open the connection
pidevice.ConnectRS232(PI_COM, PI_BR)

for idx_subscan in range(0,num_subscans):
    
    print('Subscan', idx_subscan+1 , '/', num_subscans)
    
    print('Moving Motors to start')
    pidevice.MOV(PI_X, start_x)
    pidevice.MOV(PI_Y, start_y)
    time.sleep(5)
    
    idx_x = 0
    for x_pos in x_pos_vec:
        
        idx_y = 0
        for y_pos in y_pos_vec:
            
            x_pos = np.round(x_pos,6)
            y_pos = np.round(y_pos,6)
            
            pidevice.MOV(PI_X, x_pos)
            pidevice.MOV(PI_Y, y_pos)
            time.sleep(2)
            
            print('Sample at x:', x_pos, 'y:', y_pos)
            
            for idx_rep in range(0,num_flat):
                print("Acquiring sample image ", idx_rep+1, '/', num_flat)
                image = KF.snap_image()
                fname = filepath+Subfolder_name + 'Im_subscan_' + str(idx_subscan) + '_x' + str(idx_x) + '_y' + str(idx_y) + '_rep_' + str(idx_rep)
                KF.save_image(image, fname)
                
            idx_y = idx_y+1
        idx_x = idx_x+1
            
    ##flat field
    print("Moving sample out")
    pidevice.MOV(PI_X, sample_out)
    time.sleep(5)
    
    for idx_rep in range(0,num_flat):
        print("Acquiring flat image ", idx_rep+1, '/', num_flat)
        image = KF.snap_image()
        fname = filepath+Subfolder_name + 'flat_subscan_' + str(idx_subscan) + '_rep_' + str(idx_rep) 
        KF.save_image(image, fname)
        
pidevice.CloseConnection()
   