# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 10:52:29 2024

@author: AXIm Admin
"""

import numpy as np
import os
import time
import ESS_Commands_V4 as ESS
import pressure_sensor as PS
import kinetix_functions as KF
import aerotech_functions as AT
import numpy as np

filepath = 'D:/24_03_25/'
Subfolder_name="3_movement_rotations_50kv_1p2um/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 10
binn = 1
num_proj = 20
ESS_start_pos = -8
direction = -1

angles = np.linspace(ESS_start_pos,num_proj*direction*360+ESS_start_pos,num_proj+1)

print("Exposure time:", exp)
print("Number of projections per subaquisition:", num_proj)
print("Pixel bin factor:", binn)

socket=ESS.ESS_Open()
ESS.ESS_Velocity(1268640)
ESS.ESS_Acceleration_Speed(184320)
ESS.ESS_Deceleration_Speed(184320)
ESS.ESS_PGain(2000)
ESS.ESS_VelocityFF(2048)
ESS.ESS_Velocity_PGain(2.5)
ESS.ESS_Close()

AT.AT_connect()

posRot = []

# Newport motors in position, conex focused, ESS Homed
socket=ESS.ESS_Open()
press_read = PS.PS_check_pressure()
if press_read == 0:
    ESS.ESS_Close()
else:
    ESS.ESS_Absolute_Move(ESS_start_pos) #rotation


for proj_idx in np.arange(0,num_proj+1):
    
    if proj_idx == 0:
        AT.AT_move_axis_linear('X',2)
        time.sleep(2)
        
        image = KF.snap_image()
        fname = filepath + Subfolder_name + 'flat_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'proj' + str(proj_idx) 
        KF.save_image(image, fname)
        
        AT.AT_move_axis_linear('X',-2)
    
    press_read = PS.PS_check_pressure()
    if press_read == 0:
        ESS.ESS_Close()
        break
    
    posRot=np.append(posRot,ESS.ESS_Position())
    
    Step_position = angles[proj_idx]
    ESS.ESS_Absolute_Move(Step_position) #rotation
    
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'Im_forwards_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'ang' + str(Step_position) 
    KF.save_image(image, fname)
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    np.savetxt(filepath+Subfolder_name+'/RotatorPositionLog.txt',posRot)

for proj_idx in np.arange(0,num_proj+1):
    
    press_read = PS.PS_check_pressure()
    if press_read == 0:
        ESS.ESS_Close()
        break
    
    posRot=np.append(posRot,ESS.ESS_Position())
    
    Step_position = angles[num_proj-proj_idx]
    ESS.ESS_Absolute_Move(Step_position) #rotation
    
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'Im_backwards_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'ang' + str(Step_position) 
    KF.save_image(image, fname)
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    np.savetxt(filepath+Subfolder_name+'/RotatorPositionLog.txt',posRot)
    
ESS.ESS_Close()
print('######## FINISHED ########')