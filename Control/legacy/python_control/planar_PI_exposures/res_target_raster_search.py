# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:21:07 2023
Remember to set exposure time and bin factor in micromanager
@author: AXIm Admin
"""

import numpy as np
import os
import time
import kinetix_functions as KF
import pipython 

filepath = 'D:/23_10_13/raster_search_target/'
Subfolder_name="run_1/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 5
binn = 2
d_step = 0.1
x_pos_vec = np.arange(-6.6,-6.2+d_step,d_step)
y_pos_vec = np.arange(-4.5,-4.1+d_step,d_step)

#x_pos_vec = np.arange(-2,0+d_step,d_step)
#y_pos_vec = np.arange(4.5,6.5+d_step,d_step)

print("Exposure time:", exp)
print("Pixel bin factor:", binn)

PI_COM = 3
PI_BR = 9600
PI_Z = 1
PI_X = 2
PI_Y = 3

# Create a connection to the PI controller
pidevice = pipython.GCSDevice() 
# Open the connection
pidevice.ConnectRS232(PI_COM, PI_BR)

idx = 0

for x_pos in x_pos_vec:
    for y_pos in y_pos_vec:
        
        x_pos = np.round(x_pos,3)
        y_pos = np.round(y_pos,3)
        
        print('Moving Motors')
        pidevice.MOV(PI_X, x_pos)
        pidevice.MOV(PI_Y, y_pos)
        time.sleep(2)
        
        print('Acquring Image x:', x_pos, 'y:', y_pos)
        image = KF.snap_image()
        fname = filepath+Subfolder_name + 'Im_' + str(idx) + '_' + str(exp) + 'sec_' + str(binn) + 'binning_' + 'x' + str(x_pos) + 'y' + str(y_pos)
        KF.save_image(image, fname)
        idx = idx+1
        
pidevice.CloseConnection()
