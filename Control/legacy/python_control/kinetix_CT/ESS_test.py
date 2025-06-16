# -*- coding: utf-8 -*-
"""
Created on Thu May  5 11:48:46 2022

@author: xpci
"""
# Includes pressure check

import numpy as np
import math
import matplotlib.pyplot as plt
import csv
import os
import time
import shutil
import ESS_Commands_V4 as ESS
import pressure_sensor as PS

#Specify the path for the save folder
path="C:/Users/xpci3540/Documents/Python Scripts/ESS/Nanofocus_testing/"
Subfolder_name="test_230914"

#Reading the control parameters
with open(r'C:\Users\xpci3540\Documents\Python Scripts\ESS\Nanofocus_testing\CT input data.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    ControlMatrix = []
    for row in readCSV:
        Parameter = float(row[1])
        ControlMatrix.append(Parameter)
#print(ControlMatrix)
Number_of_Subaquisitions=int(ControlMatrix[0])
Number_of_Projections=int(ControlMatrix[1])
nFrames=int(ControlMatrix[2])
Number_of_darks=int(ControlMatrix[3])
Exposure_time=(ControlMatrix[4])
Exposure_number=ControlMatrix[5]
Sample_outX=ControlMatrix[6]
Sample_outY=ControlMatrix[7]
Sample_outZ=ControlMatrix[8]
Sample_inX=ControlMatrix[9]
Sample_inY=ControlMatrix[10]
Sample_inZ=ControlMatrix[11]
Offset=(ControlMatrix[12])
print("Number of subaquisitions:", Number_of_Subaquisitions)
print("Number of projections per subaquisition:", Number_of_Projections)
print("Number of flats per subaquisition:", nFrames)
print("Number of darks per subaquisition:", Number_of_darks)
print("Exposure time:", Exposure_time)
print("Number of exposures:", Exposure_number)
print("Sample out of beam position X:", Sample_outX)
print("Sample out of beam position Y:", Sample_outY)
print("Sample out of beam position Z:", Sample_outZ)
print("Sample in beam position X:", Sample_inX)
print("Sample in beam position Y:", Sample_inY)
print("Sample in beam position Z:", Sample_inZ)
print("Initial offset:", Offset)
#print("Total exposure time", Number_of_Subaquisitions*Number_of_Projections*Exposure_time)
print("Number of images", Number_of_Subaquisitions*Number_of_Projections)
print("Total flats", Number_of_Subaquisitions*nFrames)
print("Total darks", Number_of_Subaquisitions*Number_of_darks)
arcDeg=360/Number_of_Subaquisitions
increment = (arcDeg/Number_of_Projections) #rotation increment at each projection
S=0.5

socket=ESS.ESS_Open()
#ESS.ESS_Velocity(36864000)
ESS.ESS_Velocity(36000)
ESS.ESS_Acceleration_Speed(184320)
ESS.ESS_Deceleration_Speed(184320)
ESS.ESS_PGain(2000)
ESS.ESS_VelocityFF(2048)
ESS.ESS_Velocity_PGain(2.5)
ESS.ESS_Close()
posRot=[]
for subacq in np.arange(0,Number_of_Subaquisitions):
   Temp_offset=Offset+(subacq)*arcDeg 
   socket=ESS.ESS_Open()
   #time.sleep(S)
   press_read = PS.PS_check_pressure()
   if press_read == 0:
       ESS.ESS_Close()
       break
   ESS.ESS_Absolute_Move(Temp_offset)# put sample at 0 plus a potential offset
   #time.sleep(S)
   ESS.ESS_Close()
   print('######## Waiting ########')
   time.sleep(30)

   Step_position=Temp_offset
   for proj in np.arange(0,Number_of_Projections):
            socket=ESS.ESS_Open()
           #time.sleep(S)
            press_read = PS.PS_check_pressure()
            if press_read == 0:
                ESS.ESS_Close()
                break
            ESS.ESS_Absolute_Move(Step_position) #rotation
            #time.sleep(S)
            Step_position=Step_position+increment
            posRot=np.append(posRot,ESS.ESS_Position())
            ESS.ESS_Close()
            time.sleep(Exposure_time)
            print('######### Subaquisition '+str(subacq+1)+ ' Projection '+str(proj) + ' ##########')
            np.savetxt(path+Subfolder_name+'/RotatorPositionLog.txt',posRot)
socket=ESS.ESS_Open()
press_read = PS.PS_check_pressure()
if press_read == 1:
    ESS.ESS_Home()
ESS.ESS_Close()
print('######## FINISHED ########')
    
