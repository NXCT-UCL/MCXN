# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 11:39:54 2023

@author: AXIm Admin
"""

import numpy as np
import os
import time
import ESS_Commands_V4 as ESS
import pressure_sensor as PS
import kinetix_functions as KF

filepath = 'D:/23_09_19/'
Subfolder_name="First_CT_test_V2/"
newpath = filepath + Subfolder_name
if not os.path.exists(newpath):
    os.makedirs(newpath)

exp = 3
binn = 2
num_proj = 360
rotation_angle = 360

print("Exposure time:", exp)
print("Number of projections per subaquisition:", num_proj)
print("Pixel bin factor:", binn)

increment = (rotation_angle/num_proj) #rotation increment at each projection

socket=ESS.ESS_Open()
ESS.ESS_Velocity(36864000)
ESS.ESS_Acceleration_Speed(184320)
ESS.ESS_Deceleration_Speed(184320)
ESS.ESS_PGain(2000)
ESS.ESS_VelocityFF(2048)
ESS.ESS_Velocity_PGain(2.5)
ESS.ESS_Close()

posRot=[]
Step_position = 0

socket=ESS.ESS_Open()
press_read = PS.PS_check_pressure()
if press_read == 0:
    ESS.ESS_Close()
else:
    ESS.ESS_Home# put sample at 0 plus a potential offset
print('######## Waiting ########')
time.sleep(30)

for proj_idx in np.arange(0,num_proj):
    
    press_read = PS.PS_check_pressure()
    if press_read == 0:
        ESS.ESS_Close()
        break
    
    ESS.ESS_Absolute_Move(Step_position) #rotation
    
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'Im_' + str(exp) + 'sec_' + str(binn) + 'binning_' + str(proj_idx) 
    KF.save_image(image, fname)
    
    Step_position = Step_position+increment
    posRot=np.append(posRot,ESS.ESS_Position())
    
    print('######### Projection '+str(proj_idx) + ' ##########')
    np.savetxt(filepath+Subfolder_name+'/RotatorPositionLog.txt',posRot)
    
ESS.ESS_Close()
print('######## FINISHED ########')