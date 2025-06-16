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

filepath = 'D:/24_03_27/'
Subfolder_name="5_CT_stem_40kv_1p2um/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 5
binn = 1
num_proj = 1440
rotation_angle = 360
ESS_start_pos = -8
direction = -1
extra_proj = 1

print("Exposure time:", exp)
print("Number of projections per subaquisition:", num_proj)
print("Pixel bin factor:", binn)

increment = direction*(rotation_angle/num_proj) #rotation increment at each projection

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

#socket=ESS.ESS_Open()
#press_read = PS.PS_check_pressure()
#if press_read == 0:
#    ESS.ESS_Close()
#else:
#    ESS.ESS_Home# put sample at 0 plus a potential offset
#print('######## Waiting ########')
#time.sleep(30)

# Newport motors in position, conex focused, ESS Homed
socket=ESS.ESS_Open()
press_read = PS.PS_check_pressure()
if press_read == 0:
    ESS.ESS_Close()
else:
    ESS.ESS_Absolute_Move(ESS_start_pos) #rotation


for proj_idx in np.arange(0,num_proj):
    
    if proj_idx % 120 == 0:
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
    
    Step_position = ESS_start_pos+proj_idx*increment
    posRot=np.append(posRot,ESS.ESS_Position())
    
    ESS.ESS_Absolute_Move(Step_position) #rotation
    
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'Im_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'proj' + str(proj_idx) 
    KF.save_image(image, fname)
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    np.savetxt(filepath+Subfolder_name+'/RotatorPositionLog.txt',posRot)
    
if extra_proj:
    
    Step_position = ESS_start_pos+proj_idx*increment+increment
    posRot=np.append(posRot,ESS.ESS_Position())

    if PS.PS_check_pressure():
        ESS.ESS_Absolute_Move(Step_position) #rotation
        image = KF.snap_image()
        fname = filepath + Subfolder_name + 'Im_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'proj_end'
        KF.save_image(image, fname)
    
ESS.ESS_Close()
print('######## FINISHED ########')