# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 18:08:55 2024

@author: AXIm Admin
"""

import numpy as np
import os
import time
import ESS_Commands_V5 as ESS
import pressure_sensor as PS
import kinetix_functions as KF
import aerotech_functions as AT
import source_commands as SC

filepath = 'D:/24_06_07/'

num_proj_vec = np.array([8,64,512,4096])

socket=ESS.ESS_Open()
ESS.ESS_Velocity(1268640)
ESS.ESS_Acceleration_Speed(184320)
ESS.ESS_Deceleration_Speed(184320)
ESS.ESS_PGain(2000)
ESS.ESS_VelocityFF(2048)
ESS.ESS_Velocity_PGain(2.5)
ESS.ESS_Close()
AT.AT_connect()

exp = 10
binn = 1
rotation_angle = 360
ESS_start_pos = -8
direction = -1
extra_proj = 1
flat_interval = 50

ii = 5
for num_proj in num_proj_vec:
    Subfolder_name= str(ii) + "_CT_bamboo_recursive_60kv_1p2um/"
    newpath = filepath + Subfolder_name
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        
    print("Exposure time:", exp)
    print("Number of projections per subaquisition:", num_proj)
    print("Pixel bin factor:", binn)
    
    increment = direction*(rotation_angle/num_proj) #rotation increment at each projection
    
    posRot = []
    
    # Newport motors in position, conex focused, ESS Homed
    socket=ESS.ESS_Open()
    press_read = PS.PS_check_pressure()
    if press_read == 0:
        ESS.ESS_Close()
    else:
        ESS.ESS_Absolute_Move(ESS_start_pos) #rotation
    
    for proj_idx in np.arange(0,num_proj):
        
        if proj_idx % flat_interval == 0:
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
            
    #end_flat
    AT.AT_move_axis_linear('X',2)
    time.sleep(2)
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'flat_' + str(exp) + 'sec_' + str(binn) + 'bin_' + 'end' 
    KF.save_image(image, fname)
    AT.AT_move_axis_linear('X',-2)
                        
    ii = ii+1
    
    ESS.ESS_Close()

xcs = SC.XCS("128.40.160.24")
xcs.send('#user')
xcs.send("state=ready")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'ready' state as target"
SC.wait_for_state_transition(xcs)

print('######## FINISHED ########')
