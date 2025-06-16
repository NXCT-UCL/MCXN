# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 10:24:00 2023

For moving PI sample in and out, taking sample and flat field images
Remember to set exposure time and bin factor in micromanager
@author: AXIm Admin
"""

import numpy as np
import os
import time
import kinetix_functions as KF
import pipython 

filepath = 'D:/23_09_27/'
Subfolder_name="testing_PI_movement/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 10
binn = 1
num_flat = 10
num_samp = 10
sample_in_y = -7.8
sample_out_y = 3.8

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

# get flat image
print("Moving sample out")
pidevice.MOV(PI_Y, sample_out_y)
time.sleep(5)

for idx_rep in range(0,num_flat):
    print("Acquiring flat image ", idx_rep+1, '/', num_flat)
    image = KF.snap_image()
    fname = filepath+Subfolder_name + 'flat_' + str(exp) + 'sec_' + str(binn) + 'binning_' + str(idx_rep) 
    KF.save_image(image, fname)
    
# get sample image
print("Moving sample in")
pidevice.MOV(PI_Y, sample_in_y)
time.sleep(5)
for idx_rep in range(0,num_flat):
    print("Acquiring sample image ", idx_rep+1, '/', num_flat)
    image = KF.snap_image()
    fname = filepath+Subfolder_name + 'Im_' + str(exp) + 'sec_' + str(binn) + 'binning_' + str(idx_rep) 
    KF.save_image(image, fname)

pidevice.CloseConnection()
