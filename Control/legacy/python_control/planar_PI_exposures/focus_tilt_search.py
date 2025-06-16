# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 16:39:49 2023

@author: AXIm Admin
"""

import numpy as np
import os
import time
import kinetix_functions as KF
import serial

filepath = 'D:/23_12_18/12_focusing_60kv_0p3um/'
Subfolder_name="attempt_1/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 10
binn = 2

start_pos = 40.360
step_size = 0.001
end_pos = 40.370
num_pos = round(((end_pos-start_pos)/step_size)+1)
pos_vec = np.arange(start_pos,end_pos+step_size,step_size)
pos_vec = [round(num, 3) for num in pos_vec]

print("Exposure time:", exp)
print("Pixel bin factor:", binn)
print("Number focus positions:", num_pos)

conex_com = 3
conex_BR = 9600

ser = serial.Serial('COM3', baudrate=115200, timeout=1,bytesize=8,parity='N',stopbits=1,xonxoff=True)

for idx in pos_vec:
    
    str_com = '1PA'+str(idx) + '\r\n'
    ser.write(str_com.encode('ascii'))
    time.sleep(1)
    
    pos_name = str(idx).replace('.','p')

    image = KF.snap_image()
    fname = filepath+Subfolder_name + 'Im_' + str(exp) + 'sec_' +'bin_' + str(binn) + '_z_' + pos_name + '.tiff'
    KF.save_image(image, fname)

ser.close()
   