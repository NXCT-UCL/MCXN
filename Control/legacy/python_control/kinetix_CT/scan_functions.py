# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 14:09:52 2022

@author: AAstolfo
"""

# Functions to import including the pre made modules 
import os
import numpy as np
import random
import datetime
import time
from tifffile import imread,imwrite
import subprocess
#import smaract_functions as SM
#import newport_functions as NP

def journal(filedirectory, message):
    # this is to have a sort of journal file with the scan information
    
    # checking if the file exists already
    if os.path.isfile(filedirectory + '/journal.txt'):
        journal_file = open(filedirectory + '/journal.txt','a')
    else:
        journal_file = open(filedirectory + '/journal.txt','w')
    
    journal_file.write( message + '\n')
    
    journal_file.close()

#def save_motors_positions(filedirectory):
#    # this is to save all the motors positons in the journal file
#    
#    # start with Newport controller
#    NP.init()
#    
#    for i in range(1,8):
#        # since I don't know how many axis we have active
#        try:
#            pos = NP.get_position(i)
#            if pos != 'Error':
#                print('Newport axis ' + str(i) + ' position is: ' + str(pos))
#                journal(filedirectory, 'Newport axis ' + str(i) + ' position is: ' + str(pos))
#        except:
#            pass
#    NP.close()
 #   
#    SM.init(1)
#    
#    for i in range(0,5):
#        try:
#            pos = SM.get_position(1,i)
#            print('Smaract axis ' + str(i) + ' position is: ' + str(pos))
#            journal(filedirectory, 'Smaract axis ' + str(i) + ' position is: ' + str(pos))
#        except:
#            pass
#    
#    SM.close()
    
    
def write_scan_parameters(parameters_path,parameters):
    
    # checking if the folder exists
    try:
        os.makedirs(parameters_path)
    except FileExistsError:
        pass
    
    # check for the next scan_parameters filename available
    
    name_suffix = ''
    count = 0
    # check if the file exist
    while os.path.isfile(parameters_path + '/scan_parameters' + name_suffix + '.txt'):
        count = count + 1
        name_suffix = '_'+ str(count)

    print('scan_parameters' + name_suffix + '.txt')
        
    
    
    txt_file = open(parameters_path + '/scan_parameters' + name_suffix + '.txt','w')
    txt_file.write("# Parameters of the CT SCAN" + '\n')
    txt_file.write("Saving_path = " + parameters.saving_path + '\n')
 
    txt_file.write("sample_IN_X_position = " + parameters.sample_IN_X_position + '\n')
    txt_file.write("sample_IN_Y_position = " + parameters.sample_IN_Y_position + '\n')
    txt_file.write("sample_OUT_position = " + parameters.sample_OUT_position + '\n')
    txt_file.write("No_projections = " + parameters.No_projections + '\n')
    txt_file.write("angular_range = " + parameters.angular_range + '\n')
    txt_file.write("start_from_angle = " + parameters.start_from_angle + '\n')
    txt_file.write("how_many_images_per_projection = " + parameters.how_many_images_per_projection + '\n')
    txt_file.write("how_many_flat_images = " + parameters.how_many_flat_images + '\n')
    txt_file.write("how_many_dark_images = " + parameters.how_many_dark_images + '\n')
    txt_file.write("jitter_flag = " + parameters.jitter_flag + '\n')
    txt_file.write("pixel_size = " + parameters.pixel_size + '\n')
    txt_file.write("Subfolder_names = " + parameters.Subfolder_names + '\n')



def read_scan_parameters(parameters_path):
    
    # default values
    saving_path = ''
    sample_IN_X_position = "-6.0"
    sample_IN_Y_position = "-6.0"
    sample_OUT_position = "0.0"
    
    No_projections =  "2500"
    angular_range = "180"
    start_from_angle = "0.0"
    
    how_many_images_per_projection = "1"
    how_many_flat_images = "5"
    how_many_dark_images = "5"
    
    jitter_flag = "1"
    pixel_size = "1.1"
    Subfolder_names = "SCAN1"
    
    with open(parameters_path) as txt_file:
        for line in txt_file:
            print(line)
            tmp = line.split('=')
            if str.strip(tmp[0]) == 'saving_path':
                saving_path = str.strip(tmp[1])

            if str.strip(tmp[0]) == 'sample_IN_X_position':
                sample_IN_X_position = str.strip(tmp[1])
            if str.strip(tmp[0]) == 'sample_IN_Y_position':
                sample_IN_Y_position = str.strip(tmp[1])                   
            if str.strip(tmp[0]) == 'sample_OUT_position':
                sample_OUT_position = str.strip(tmp[1])

            if str.strip(tmp[0]) == 'No_projections':
                No_projections = str.strip(tmp[1])               
            if str.strip(tmp[0]) == 'angular_range':
                angular_range = str.strip(tmp[1])
            if str.strip(tmp[0]) == 'start_from_angle':
                start_from_angle = str.strip(tmp[1])
                            
            if str.strip(tmp[0]) == 'how_many_images_per_projection':
                how_many_images_per_projection = str.strip(tmp[1])
            if str.strip(tmp[0]) == 'how_many_flat_images':
                how_many_flat_images = str.strip(tmp[1])
            if str.strip(tmp[0]) == 'how_many_dark_images':
                how_many_dark_images = str.strip(tmp[1])
                
            if str.strip(tmp[0]) == 'jitter_flag':
                jitter_flag = str.strip(tmp[1])                
            if str.strip(tmp[0]) == 'pixel_size':
                pixel_size = str.strip(tmp[1])
            if str.strip(tmp[0]) == 'Subfolder_names':
                Subfolder_names = str.strip(tmp[1])  
                
    
    scan_parameters = scan_param( saving_path, sample_IN_X_position, sample_IN_Y_position, sample_OUT_position, No_projections,
                                  angular_range, start_from_angle, how_many_images_per_projection, how_many_flat_images,
                                  how_many_dark_images, jitter_flag, pixel_size, Subfolder_names)
    
    return scan_parameters

class scan_param:

    def __init__(self,saving_path, sample_IN_X_position, sample_IN_Y_position, sample_OUT_position,
                 No_projections, angular_range, start_from_angle,
                 how_many_images_per_projection, how_many_flat_images, how_many_dark_images,
                 jitter_flag, pixel_size, Subfolder_names):
        self.saving_path = str(saving_path)
        
        self.sample_IN_X_position = str(sample_IN_X_position)
        self.sample_IN_Y_position = str(sample_IN_Y_position)
        self.sample_OUT_position = str(sample_OUT_position)
        
        self.No_projections =  str(No_projections)
        self.angular_range = str(angular_range)
        self.start_from_angle = str(start_from_angle)
        
        self.how_many_images_per_projection = str(how_many_images_per_projection)
        self.how_many_flat_images = str(how_many_flat_images)
        self.how_many_dark_images = str(how_many_dark_images)
        
        self.jitter_flag = str(jitter_flag)
        self.pixel_size = str(pixel_size)
        self.Subfolder_names = str(Subfolder_names)

def acquire_dark(saving_path, No_frames):
    
    #acquire_dark('D:/22_10_07/Alberto/test2',10)
    
    # Checking the entry:   
    No_frames = int(No_frames)
    
    print('path = ', saving_path)
    print('nFrames = ', No_frames)
    print('===================================')

    journal(saving_path,'path = ' + saving_path)
    journal(saving_path,'nFrames = ' + str(No_frames))
    journal(saving_path,'===================================')

    
    
    #acquire_sequence_wrapper('D:/22_10_07/Alberto/test2', 1, 'test', 1, -6.2, -6.18, 0,10,5,0,0,0)
    
    
    cmd = "python acquire_dark.py " + saving_path + " " + str(No_frames)
    print('Command sent:')
    print(cmd)

    journal(saving_path,'Command sent:')
    journal(saving_path, cmd)

    
    os.system(cmd)
    
def acquire_flat(saving_path, No_frames, SampleOUT_Pos_x):
    
    #acquire_flat('D:/22_10_07/Alberto/test2',10,0)
    
    # Checking the entry:   
    No_frames = int(No_frames)
    
    print('path = ', saving_path)
    print('nFrames = ', No_frames)
    print('SampleOUT_Pos_x = ', SampleOUT_Pos_x)
    print('===================================')

    journal(saving_path,'path = ' + saving_path)
    journal(saving_path,'nFrames = ' + str(No_frames))
    journal(saving_path,'SampleOUT_Pos_x = ' + str(SampleOUT_Pos_x))
    journal(saving_path,'===================================')

    
    
    #acquire_sequence_wrapper('D:/22_10_07/Alberto/test2', 1, 'test', 1, -6.2, -6.18, 0,10,5,0,0,0)
    
    
    cmd = "python acquire_flat.py " + saving_path + " " + str(No_frames) + " " + str(SampleOUT_Pos_x) 
    print('Command sent:')
    print(cmd)

    journal(saving_path, 'Command sent:')
    journal(saving_path, cmd)

    
    os.system(cmd)    

def acquire_alignment_images(saving_path, angle1, angle2, angle3, angle4, acquisition_type):
    
    #acquire_alignment_images('D:/22_10_07/Alberto/test2',0,180,-90,90,1)
    
    # Checking the entry:   
    
    print('path = ', saving_path)
    print('angle1 = ', angle1)
    print('angle2 = ', angle2)
    print('angle3 = ', angle3)
    print('angle4 = ', angle4)
    print('acquisition_type = ', acquisition_type)
    print('===================================')

    journal(saving_path,'path = ' + saving_path)
    journal(saving_path,'angle1 = ' + str(angle1))
    journal(saving_path,'angle2 = ' + str(angle2))
    journal(saving_path,'angle3 = ' + str(angle3))
    journal(saving_path,'angle4 = ' + str(angle4))
    journal(saving_path,'acquisition_type = ' + str(acquisition_type))
    journal(saving_path,'===================================')
    
    #acquire_sequence_wrapper('D:/22_10_07/Alberto/test2', 1, 'test', 1, -6.2, -6.18, 0,10,5,0,0,0)
    
    
    cmd = "python acquire_alignment_images.py " + saving_path + " " + str(angle1) + " " + str(angle2) + " " + str(angle3) + " " + str(angle4) + " " + str(acquisition_type)
    print('Command sent:')
    print(cmd)

    journal(saving_path, 'Command sent:')
    journal(saving_path, cmd)

    
    os.system(cmd)      
    
    

def acquire_CT(saving_path, samplePos_x, samplePos_y, arcDeg, nProj, nFrames_perProj, offset, jitt_flag, pixel_size):
    
    #acquire_flat('D:/22_10_07/Alberto/test2',10,0)
    #acquire_CT('D:/22_10_07/Alberto',-6,-6,30,5,2,0,0,1.1)
    
    
    # Checking the entry:   
    nFrames_perProj = int(nFrames_perProj)
    nProj = int(nProj)
    
    print('path = ', saving_path)
    print('samplePos_x = ', samplePos_x)
    print('samplePos_y = ', samplePos_y)
    print('arcDeg = ', arcDeg)
    print('nProj = ', nProj)
    print('nFrames_perProj = ', nFrames_perProj)
    print('offset = ', offset)
    print('jitt_flag = ', jitt_flag)
    print('pixel_size = ', pixel_size)
    print('===================================')

    journal(saving_path,'path = ' + saving_path)
    journal(saving_path,'samplePos_x = ' + str(samplePos_x))
    journal(saving_path,'samplePos_y = ' + str(samplePos_y))
    journal(saving_path,'arcDeg = ' + str(arcDeg))
    journal(saving_path,'nProj = ' + str(nProj))
    journal(saving_path,'nFrames_perProj = ' + str(nFrames_perProj))
    journal(saving_path,'offset = ' + str(offset))
    journal(saving_path,'jitt_flag = ' + str(jitt_flag))
    journal(saving_path,'pixel_size = ' + str(pixel_size))
    journal(saving_path,'===================================')

    
    
    cmd = "python acquire_CT.py " + saving_path + " " + str(samplePos_x) + " " + str(samplePos_y) + " " + str(arcDeg) + " " + str(nProj) + " " + str(nFrames_perProj) + " " + str(offset) + " " + str(jitt_flag) + " " + str(pixel_size)
    print('Command sent:')
    print(cmd)

    journal(saving_path,'Command sent:')
    journal(saving_path, cmd)

    
    os.system(cmd) 

def scan_3D(saving_path, sample_IN_X_position, sample_IN_Y_position, sample_OUT_position,
           No_projections, angular_range, start_from_angle,
           how_many_images_per_projection, how_many_flat_images, how_many_dark_images,
           jitter_flag, pixel_size):

    #scan_3D(r'D:\22_10_07', -6., -5, 0, 10, 10, 0, 1, 5, 5, 0, 1.1)

    
    # this is to wrap up all the actions required for a CT scan sent via the START_GUI
    
    # to fix the issue with one IC point or more
    # try:
    #     Y_no = len(sample_IN_Y_position)
    # except:
    #     sample_IN_Y_position = np.array([sample_IN_Y_position])
    #     Y_no = 1
    
    # print("Y_no = ", Y_no)
    
    # print('sample_IN_Y_position = ',sample_IN_Y_position)
    
    # print('Add the extra CT folder')
    
    try:
        os.makedirs(saving_path)
    except FileExistsError:
        pass
    
    
    # acquiring darks...
    acquire_dark(saving_path, how_many_dark_images)
    
    # acquiring flats...
    acquire_flat(saving_path, how_many_flat_images, sample_OUT_position)
    #print('scan start')
    #for i in range(0,Y_no):
    acquire_CT(saving_path, sample_IN_X_position, sample_IN_Y_position, angular_range, No_projections, how_many_images_per_projection, start_from_angle, jitter_flag, pixel_size)
    #print('scan done')
    

# def CTstep_acquire(saving_path, name, IC_centre, IC_positions, Exposure_time, Motor_No_Sample_Mask, No_repeated_images,
#                    sample_IN_position = 0, IC_positions_sample = 0, Motor_No_Sample_X = 0, jitter_flag = 0, dither_flag = 0):
  
#     # this works for both the flats (calling without sample_IN_position and following)
#     # and the normal scan step (calling with all the entries)
    
#     # this is for saving in .tif
#     image_format = 0
    
#     # checking if the folder exists
#     try:
#         os.makedirs(saving_path)
#     except FileExistsError:
#         pass
    
#     # used later to check if it is a multi IC request of a single one
#     IC_No_points = len(IC_positions)
    
    
#     if Motor_No_Sample_X == 0: # this is the case fo a flat sequence, the sample is not moved
        
#         # I move the mask only if the positions on IC are non-zero (otherwise the mask is already in position and no need of backlash compensation)
#         #if IC_No_points != 1: 
#             # move the mask stage at the backlash position
#             #NP.NP_ma(Motor_No_Sample_Mask,IC_centre + IC_positions[0]-0.1,1)
        
        
#         for i in range(IC_No_points):
#             # I move the mask only if the positions on IC are non-zero
#             if IC_No_points != 1: 
#                 NP.NP_ma(Motor_No_Sample_Mask, IC_centre + IC_positions[i],1)
            
#             # here I finally take the images and save
#             for rep in range(No_repeated_images):
#                 image_name = saving_path + '/' + name + '_IC_' + str(i).zfill(len(str(IC_No_points))) + '_rep_' + str(rep).zfill(len(str(No_repeated_images)))
#                 HM.HM_AcquireWaitSave(image_name,image_format)
#                 print('Acquired image ', image_name)
    
#     else: # this is the case of normal scan step
    
#         # I move the mask only if the positions on IC are non-zero (otherwise the mask is already in position and no need of backlash compensation)
#         #if IC_No_points != 1: 
#             # move the mask stage at the backlash position
#             #NP.NP_ma(Motor_No_Sample_Mask, IC_centre + IC_positions[0]-0.1, 1)    
        
#         # I move the sample only if I have jitter or dithering
#         #if jitter_flag == 1 or dither_flag == 1:
#             # move the sample stage at the backlash position
#             #NP.NP_ma(Motor_No_Sample_X, sample_IN_position + IC_positions_sample[0]-0.1, 1)
                
#         for i in range(IC_No_points):
#             if IC_No_points != 1: 
#                 # move the mask stage at the backlash position
#                 NP.NP_ma(Motor_No_Sample_Mask, IC_centre + IC_positions[i],1)             
#             # I move the sample only if I have jitter or dithering
#             if jitter_flag == 1 or dither_flag == 1:       
#                 NP.NP_ma(Motor_No_Sample_X, sample_IN_position + IC_positions_sample[i], 1)
            
#             for rep in range(No_repeated_images):
#                 image_name = saving_path + '/' + name + '_IC_' + str(i).zfill(len(str(IC_No_points))) + '_rep_' + str(rep).zfill(len(str(No_repeated_images)))
#                 HM.HM_AcquireWaitSave(image_name,image_format)
#                 print('Acquired image ', image_name)     


# def Acquire_single_image(saving_path, IC_centre, IC_span, IC_No_points, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask, G,
#             No_dithering, sample_IN_position, sample_OUT_position, Motor_No_Sample_X,
#             how_many_images_per_flat_step, how_many_images_per_scan_step):

#     # start a journal file and save some information
#     journal(saving_path,'SCAN File of : '                       + str(datetime.datetime.now()))
#     journal(saving_path,'INPUT PART: '                          )
#     journal(saving_path,'IC_centre = '                          + str(IC_centre))
#     journal(saving_path,'IC_span = '                            + str(IC_span))
#     journal(saving_path,'IC_No_points = '                       + str(IC_No_points))
#     journal(saving_path,'Exposure_time = '                      + str(Exposure_time))
#     journal(saving_path,'Motor_No_Sample_Mask = '               + str(Motor_No_Sample_Mask))
#     journal(saving_path,'G = '                                  + str(G))
#     journal(saving_path,'No_dithering = '                       + str(No_dithering))
#     journal(saving_path,'IC_positions_scan = '                  + str(IC_positions_scan))
#     journal(saving_path,'sample_IN_position = '                 + str(sample_IN_position))
#     journal(saving_path,'sample_OUT_position = '                + str(sample_OUT_position))
#     journal(saving_path,'Motor_No_Sample_X = '                  + str(Motor_No_Sample_X))
#     journal(saving_path,'--------------------------------------')
    
    
 
#     # to fix the issue with one IC point or more
#     try:
#         len(IC_positions_scan)
#     except:
#         IC_positions_scan = np.array([IC_positions_scan])
    

#     try:
#         os.makedirs(saving_path)
#     except FileExistsError:
#         pass


#     # NB: SAMPLE AND SAMPLE MASK STAGES HAVE FLIPPED X-AXES 
#     #IC_positions_sample = - IC_positions_scan * G 
    
#     # NB: SAMPLE AND SAMPLE MASK STAGES ARE NOT FLIPPED ANYMORE 
#     IC_positions_sample = IC_positions_scan * G     
    
    
#     dither_step = (IC_span / No_dithering) * G

#     # initialize Newport controller
#     NP.NP_init()
    
#     # initialize Hamamatsu detector
#     HM.HM_init()
    
#     # stop detector if live
#     HM.HM_StopLive()
    
#     HM.HM_setExposureTime(Exposure_time)
    
#     sample_translation_scanning_speed = 4
#     sample_translation_scanning_acceleration = 20
    
#     sample_translation_default_speed = 20
#     sample_translation_default_acceleration = 20    
    
 
#     #set default speed for sample X (only if 6)
#     if Motor_No_Sample_X == 6:
#         NP.NP_sv(Motor_No_Sample_X,sample_translation_default_speed,sample_translation_default_acceleration)
    
#     # move sample out with wait
#     NP.NP_ma(Motor_No_Sample_X, sample_OUT_position,1)
    
#     # it all start with an IC acquisition to define a new IC centre 
    
#     IC_folder_name = IC_acq.IC_acquire(saving_path,IC_centre,IC_span,IC_No_points,Exposure_time,Motor_No_Sample_Mask,0)
    
#     time.sleep(1)
    
#     IC_position_mean = IC_ana.IC_analysis_alignment(saving_path + '/' + IC_folder_name)
    
#     print("IC_positions_scan = ", IC_positions_scan + IC_position_mean)
#     journal(saving_path,'IC_positions_scan =  = '                  + str(IC_positions_scan + IC_position_mean))
    
    
#     # test as the source is off
#     #IC_position_mean = IC_centre
    
#     journal(saving_path,'Open the shutter')
#     print("Open the shutter")
#     RG.Open_Shutter()
    
#     # if only one position for the mask is set, I move the mask there
#     if len([IC_positions_scan]) == 1:
#         # move the mask stage at the backlash position
#         NP.NP_ma(Motor_No_Sample_Mask,IC_position_mean + IC_positions_scan[0]-0.1,1)
#         NP.NP_ma(Motor_No_Sample_Mask,IC_position_mean + IC_positions_scan[0],1)
    
   
#     flat_name = 'flat'
    
#     CTstep_acquire(saving_path + '/1PROJ', flat_name, IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask,how_many_images_per_flat_step)

#     # move sample in with wait
#     NP.NP_ma(Motor_No_Sample_X, sample_IN_position,1)
   
#     #set scanning speed for sample (only if 6)
#     if Motor_No_Sample_X == 6:
#         NP.NP_sv(Motor_No_Sample_X,sample_translation_scanning_speed,sample_translation_scanning_acceleration)
    

#     projection_name = 'proj'
    
#     if No_dithering == 1:
#         CTstep_acquire(saving_path + '/1PROJ', projection_name, IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask,how_many_images_per_scan_step)
#     else:
#         for dither in range(0,No_dithering):
#             sample_IN_position_now =  sample_IN_position + dither * dither_step
#             projection_name_with_dither = projection_name + '_dither_' + str(dither).zfill(len(str(No_dithering)))
#             CTstep_acquire(saving_path + '/1PROJ', projection_name_with_dither , IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask, how_many_images_per_scan_step, sample_IN_position_now, IC_positions_sample, Motor_No_Sample_X, 0, No_dithering > 1)
    
#     journal(saving_path,'Close the shutter')
#     print("Close the shutter")
#     RG.Close_Shutter()
    
#     HM.HM_AcquireWaitSave(saving_path + '/1PROJ/dark_end')
    
#     HM.HM_close()
#     NP.NP_close()        

def normalise_merge_single_projection(saving_path, IC_positions_scan, No_dithering,how_many_images_per_flat_step, how_many_images_per_scan_step):
    
      
    # search for an image to get dimension
    all_names = [f for f in os.listdir(saving_path + '\\1PROJ') if f.endswith('.tif')]
    
    flat_names = [f for f in all_names if 'flat' in f]
    proj_names = [f for f in all_names if 'proj' in f]
    
    # NB: x is the second dimension with the apertures vertical
    tmp = imread(saving_path + '\\1PROJ\\' + all_names[0])
    nx = len(tmp[0,:])
    ny = len(tmp[:,0])
    
    
    # find a dark image on a illumination curve path
    try:
        dark = imread(saving_path + '\\illumination_curve\\dark.tif')
    except:
        print('Cannot find a dark image define as zeros')
        dark = np.zeros(shape=(nx,ny))
    
    # getting no of IC points
    # try:
    #     IC_no = len(IC_positions_scan.split(','))
    # except:
    #     IC_no = 1  

    # to fix the issue with one IC point or more
    try:
        IC_no = len(IC_positions_scan)
    except:
        IC_positions_scan = np.array([IC_positions_scan])
        IC_no = 1
                  
    
    No_dithering = int(No_dithering)
    
    flats =  np.zeros(shape=(ny,nx,IC_no))      
    
    flats_rep = int(how_many_images_per_flat_step)
    
    
    for i in flat_names:    
        IC_entry = int(i.split('IC_')[1][0])
        #rep_entry = int(i.split('rep_')[1][0])
        flats[:,:,IC_entry] = flats[:,:,IC_entry] + imread(saving_path + '\\1PROJ\\' + i) / flats_rep
    
    images = np.zeros(shape=(ny, nx, No_dithering, IC_no))    
    
    images_rep = int(how_many_images_per_scan_step)
    
    for i in proj_names:
        if IC_no < 10:
            IC_entry = int(i.split('IC_')[1][0])
        else:
            IC_entry = int(i.split('IC_')[1][0:2])
        try:
            if No_dithering < 10:
                dither_entry = int(i.split('dither_')[1][0])
            else:
                dither_entry = int(i.split('dither_')[1][0:2])
        except:
            # to accound of case when there is no dithers
            dither_entry = 0
    
        images[:,:,dither_entry,IC_entry] = images[:,:,dither_entry,IC_entry] + imread(saving_path + '\\1PROJ\\' + i) / images_rep
    
    # normalize images and merge ditherings
    images_merged = np.zeros(shape=(ny, int(nx * No_dithering/2), IC_no))
    
    # images for moment analysis
    M_images_merged = np.zeros(shape=(ny, int(nx * No_dithering/2), IC_no))
    flats_merged = np.zeros(shape=(ny, int(nx * No_dithering/2), IC_no))
    M_merged = np.zeros(shape=(ny, int(nx * No_dithering/2), 3))
    M_flats = np.zeros(shape=(ny, int(nx * No_dithering/2), 3))
    
    # images with IC position
    IC_position_images = np.zeros(shape=(ny, int(nx * No_dithering/2), IC_no))
    for i in range(0,IC_no):
        IC_position_images[:,:,i] = IC_position_images[:,:,i] + IC_positions_scan[i]

    
    # here I pick the good columns for the skipped mask case
    if np.average(flats[:,1::2,:]) > np.average(flats[:,0::2,:]):
        bright_column = 1
    else:
        bright_column = 0
    
    for i in range(0,IC_no):
        for j in range(0,No_dithering):
            
            with np.errstate(divide='ignore',invalid='ignore'):
                tmp = (images[:,:,j,i] - dark ) / (flats[:,:,i] - dark) * ( np.average( flats[:,bright_column::2,i]) - np.average(dark[:,bright_column::2]) )
            
            images_merged[:,j::No_dithering,i] = tmp[:,bright_column::2]
    
            # I do not want the normalization for Moment analysis
            tmp = images[:,:,j,i] - dark
            M_images_merged[:,j::No_dithering,i] = tmp[:,bright_column::2]
            flats_merged[:,j::No_dithering,i] = flats[:,bright_column::2,i] - dark[:,bright_column::2]

    # creating an output folder if not already there
    try:
        os.makedirs(saving_path + '\\OUTPUT')
    except FileExistsError:
        pass


    
    # perform the moment analysis only if I have enough IC points
    if IC_no > 3:
    
    
        # moments calculation as in: Appl. Phys. Lett. 82, 3421 (2003); https://doi.org/10.1063/1.1575508
        for i in range(0,3):
            print(i)
            for j in range(0,IC_no):
                M_merged[:,:,i] = M_merged[:,:,i] + np.power(IC_position_images[:,:,j],i) * M_images_merged[:,:,j]
                M_flats[:,:,i] = M_flats[:,:,i] + np.power(IC_position_images[:,:,j],i) * flats_merged[:,:,j]
    
        M_results = np.zeros(shape=(ny, int(nx * No_dithering/2), 3))
    
        with np.errstate(divide='ignore',invalid='ignore'):
            M_results[:,:,0] = M_merged[:,:,0] / M_flats[:,:,0]
            M_results[:,:,1] =  (M_merged[:,:,1] / M_merged[:,:,0] - M_flats[:,:,1] / M_flats[:,:,0]) * 1000
            M_results[:,:,2] = (M_merged[:,:,2] / M_merged[:,:,0] - np.power(M_merged[:,:,1] / M_merged[:,:,0],2)) - (M_flats[:,:,2] / M_flats[:,:,0] - np.power(M_flats[:,:,1] / M_flats[:,:,0],2))

        imwrite(saving_path + '\\OUTPUT\\att.tif',data = M_results[:,:,0])    
        imwrite(saving_path + '\\OUTPUT\\ref.tif',data = M_results[:,:,1]) 
        imwrite(saving_path + '\\OUTPUT\\sca.tif',data = M_results[:,:,2])
    
    
    images_merged = np.ushort(images_merged)
    

    
    for i in range(0,IC_no):
        imwrite(saving_path + '\\OUTPUT\\proj_'+ 'IC_' + str(i)+'.tif',data = images_merged[:,:,i])
  


    # if we want ImageJ opening the image when done
    #ImageJ_path = r'C:\Users\rmapaas\Documents\Fiji.app' 
    #current_dir = os.getcwd()  
    #os.chdir(ImageJ_path)
    # run ImageJ with the image open
    #subprocess.run(["ImageJ-win64.exe",scan_path + '\\OUTPUT\\proj_'+ 'IC_0.tif'],shell=True,capture_output=True)
    #os.chdir(current_dir)
    
    
    
# def scan_3D(saving_path, IC_centre, IC_span, IC_No_points, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask, G,
#             No_dithering, sample_IN_position, sample_OUT_position, Motor_No_Sample_X, Motor_No_Sample_ROTY, No_projections,
#             angular_range, how_many_projection_before_flat, how_many_images_per_flat_step, how_many_images_per_scan_step,
#             start_from_projection, sub_acquisition_start, jitter_flag, extra_projection_flag):


# # 3D scan procedure 

# # Example:
# # =============================================================================
# # 
# # # Location to save the data (files need to be pre created)
# # saving_path = 'C:/Data/21_10_10/Carlo'
# # 
# # #++++++++++++++++++++++++++++++  Illumination curve ++++++++++++++++++++++++++
# # # Illumination curve center 
# # IC_centre = -50.84536877085035
# # 
# # # Illimination curve span, full range from first to last step. Represents the pitch of the mask.
# # IC_span = 0.079
# # 
# # # Number of points to be taken on the illumination curve 
# # IC_No_points = 50
# # 
# #  # NOT IMPLIMENTED YET
# # check_illumination_curve_flat = 1
# # 
# # # Defined positions to be taken on the illumination curve in mm. 
# # 
# # IC_positions_scan = [-0.025,-0.0128,0,0.0128,0.025]#[-0.0128]  
# # #++++++++++++++++++++++++++++ Camera Parameters ++++++++++++++++++++++++++++++
# # # Exposure time of the camera in seconds 
# # Exposure_time = 1.2
# # 
# # # Number of the Newport XPS group, for the sample masks 
# # Motor_No_Sample_Mask = 1
# # 
# # # Magnification between the pre-sample mask and the sample. Overall system magnification is 1.25(?), of sample on the detector. 
# # G = 1.0528
# # 
# # # Number of dithering steps to increase resolution (recomended range = 1 - 8)
# # No_dithering = 8
# # 
# # #++++++++++++++++++++++++++ Sample Parameters ++++++++++++++++++++++++++++++++
# # #Position when sample is in the scanning postion in mm  
# # sample_IN_position = -30.5
# # 
# # # Position when sample is out of the beam in mm 
# # sample_OUT_position = 20
# # 
# # # Define the motor numbers that are used by Newport to move the sample 
# # Motor_No_Sample_X = 6
# # 
# # Motor_No_Sample_ROTY = 7
# # 
# # #+++++++++++++++++++++++++++ Parameters of the scan ++++++++++++++++++++++++++
# # #Number of projections to be collected 
# # No_projections = 2000
# # 
# # # What angular range to collect the projections over 
# # angular_range = 360
# # 
# # 
# # # Number of projections taken before additional flat taken 
# # how_many_projection_before_flat = 200
# # 
# # # Number of images taken per flat position
# # how_many_images_per_flat_step = 5
# # 
# # # Number of images taken per projection
# # how_many_images_per_scan_step = 1
# # 
# # start_from_projection = 0
# #
# # # re-start position in the event of a scan being stopped mid-way. Normally set to 0 at the start of a scan. 
# # sub_acquisition_start = 7
# # 
# # # Moves the sample left and right to improve the ring artifact. flag: on = 1 off = 0
# # jitter_flag = 1
# # =============================================================================
    
#     # to fix the issue with one IC point or more
#     try:
#         len(IC_positions_scan)
#     except:
#         IC_positions_scan = np.array([IC_positions_scan])
    

#     try:
#         os.makedirs(saving_path)
#     except FileExistsError:
#         pass



#     # start a journal file and save some information
#     journal(saving_path,'SCAN File of : '                       + str(datetime.datetime.now()))
#     journal(saving_path,'INPUT PART: '                          )
#     journal(saving_path,'IC_centre = '                          + str(IC_centre))
#     journal(saving_path,'IC_span = '                            + str(IC_span))
#     journal(saving_path,'IC_No_points = '                       + str(IC_No_points))
#     journal(saving_path,'Exposure_time = '                      + str(Exposure_time))
#     journal(saving_path,'Motor_No_Sample_Mask = '               + str(Motor_No_Sample_Mask))
#     journal(saving_path,'G = '                                  + str(G))
#     journal(saving_path,'No_dithering = '                       + str(No_dithering))
#     journal(saving_path,'IC_positions_scan = '                  + str(IC_positions_scan))
#     journal(saving_path,'sample_IN_position = '                 + str(sample_IN_position))
#     journal(saving_path,'sample_OUT_position = '                + str(sample_OUT_position))
#     journal(saving_path,'Motor_No_Sample_X = '                  + str(Motor_No_Sample_X))
#     journal(saving_path,'Motor_No_Sample_ROTY = '               + str(Motor_No_Sample_ROTY))
#     journal(saving_path,'No_projections = '                     + str(No_projections))
#     journal(saving_path,'angular_range = '                      + str(angular_range))
#     journal(saving_path,'start_from_projection = '              + str(start_from_projection))
#     journal(saving_path,'how_many_projection_before_flat = '    + str(how_many_projection_before_flat))
#     journal(saving_path,'jitter_flag = '                        + str(jitter_flag))
#     journal(saving_path,'--------------------------------------')

#     # NB: SAMPLE AND SAMPLE MASK STAGES HAVE FLIPPED X-AXES 
#     #IC_positions_sample = - IC_positions_scan * G 
    
#     # NB: SAMPLE AND SAMPLE MASK STAGES NOW HAVE SAME X-AXES DIRECTION
#     IC_positions_sample = IC_positions_scan * G     
    
    
#     dither_step = (IC_span / No_dithering) * G

#     # here I add an extra projection to complete the 360
#     if extra_projection_flag == 1:
#         No_real_projections = No_projections + 1
#     else:
#         No_real_projections = No_projections
    
#     #initialize jitter sequence
#     jitter_sequence = np.zeros(No_real_projections)

#     # create the jitter pixels sequence and save a file with it
#     if jitter_flag:
#         # check if the file exists already (from a previous broken CT for example)
#         if os.path.isfile(saving_path + '/jitter.txt'):
#             # read it            
#             jitter_file = open(saving_path + '/jitter.txt')
#             read_jitter = jitter_file.readlines()
#             lines = len(read_jitter)
#             jitter_file.close()
#             # if the number of projections don't match I create a new one (and overwrite it)                
#             if lines != No_real_projections:
#                 jitter_sequence = [random.randrange(-4,5,1) for i in range(No_real_projections)]
#                 jitter_file = open(saving_path + '/jitter.txt','w')
#                 for j in jitter_sequence:
#                     jitter_file.write( str(j) + '\n')
#                 jitter_file.close()
#             # otherwise I use the one existing
#             else:
#                 jitter_sequence = np.array(read_jitter).astype(int)
#         else:
#             jitter_sequence = [random.randrange(-4,5,1) for i in range(No_real_projections)]
#             jitter_file = open(saving_path + '/jitter.txt','w')
#             for j in jitter_sequence:
#                 jitter_file.write( str(j) + '\n')
#             jitter_file.close()
    
#     jitter_shift = IC_span * G * np.array(jitter_sequence)
    
    
#     # I divide the scans in sub-acquisitions each with new flats and IC at the beginning
    
#     No_sub_acquisitions = int(np.ceil(No_real_projections / how_many_projection_before_flat))
    
#     # this to have the sub_acquisition_scan rules by the start_acquisition in case
#     if start_from_projection > how_many_projection_before_flat:
#         sub_acquisition_start = int(np.floor(start_from_projection / how_many_projection_before_flat))
    
#     angles = np.arange(0,No_real_projections,1) / (No_projections) * angular_range
    
#     Sub_acquisition_No = np.arange(0,No_real_projections) // how_many_projection_before_flat
    
#     #IC_folder_name = IC_acq.IC_acquire(saving_path,IC_centre,IC_span,IC_No_points,Exposure_time,Motor_No_Sample_Mask)
    
#     #IC_position_mean = IC_ana.IC_analysis(saving_path + '/' + IC_folder_name)
    
#     # initialize Newport controller
#     NP.NP_init()
    
#     # initialize Hamamatsu detector
#     HM.HM_init()
    
#     # stop detector if live
#     HM.HM_StopLive()
    
#     HM.HM_setExposureTime(Exposure_time)
    
#     rotation_scanning_speed = 4
#     rotation_scanning_acceleration = 4
    
#     sample_translation_scanning_speed = 4
#     sample_translation_scanning_acceleration = 20
    
#     sample_translation_default_speed = 20
#     sample_translation_default_acceleration = 20    
    
#     #set default speed for sample rotation (it is always at max)
#     NP.NP_sv(Motor_No_Sample_ROTY,rotation_scanning_speed,rotation_scanning_acceleration)
    
  
#     # this to get the angle of the first projection to be done
#     if sub_acquisition_start * how_many_projection_before_flat < start_from_projection:
#         start_from = start_from_projection - sub_acquisition_start * how_many_projection_before_flat
#     else:
#         start_from = 0
    
#     print('Moving the sample rotation now.')
    
#     # move the sample rotation 1 degree back (for the backlash)
#     NP.NP_ma(Motor_No_Sample_ROTY, angles[start_from]-1,1)  
#     NP.NP_ma(Motor_No_Sample_ROTY, angles[start_from],1) 
    
#     print('Sample at Starting position.')
    
    
#     journal(saving_path,'CALCULATED PART: '                          )
#     journal(saving_path,'IC_positions_sample = '                          + str(IC_positions_sample))
#     journal(saving_path,'dither_step = '                            + str(dither_step))
#     journal(saving_path,'No_sub_acquisitions = '                            + str(No_sub_acquisitions))
    
#     # writing newport positions
#     All_positions = NP.NP_gp_all()
#     for motors in range(0,len(All_positions)):
#         journal(saving_path,'Motor #' + str(motors+1) + ' = ' + str(All_positions[motors]))
        
    
    
#     for sub_acquisition in range(sub_acquisition_start,No_sub_acquisitions):
        
#         print('Sub-acquisition ', sub_acquisition)
        
#         journal(saving_path,'Sub-acquisition ' + str(sub_acquisition))
        
#         #set default speed for sample X (only if 6)
#         if Motor_No_Sample_X == 6:
#             NP.NP_sv(Motor_No_Sample_X,sample_translation_default_speed,sample_translation_default_acceleration)
        
#         print('Moving the sample OUT.')
#         # move sample out with wait
#         NP.NP_ma(Motor_No_Sample_X, sample_OUT_position,1)
#         journal(saving_path,'Moved sample out')
#         print('Moved sample out')
        
#         # it all start with an IC acquisition to define a new IC centre 
        
#         print('Acquiring an IC')
#         journal(saving_path,'Acquiring an IC')
#         IC_folder_name = IC_acq.IC_acquire(saving_path,IC_centre,IC_span,IC_No_points,Exposure_time,Motor_No_Sample_Mask,0)
        
#         time.sleep(1)
        
#         IC_position_mean = IC_ana.IC_analysis_alignment(saving_path + '/' + IC_folder_name)
        
#         # test as the source is off
#         #IC_position_mean = IC_centre
        
#         journal(saving_path,'IC_position_mean is: ' + str(IC_position_mean))
        
#         journal(saving_path,'Open the shutter')
#         RG.Open_Shutter()
        
#         # if only one position for the mask is set, I move the mask there
#         if len([IC_positions_scan]) == 1:
#             # move the mask stage at the backlash position
#             #NP.NP_ma(Motor_No_Sample_Mask,IC_position_mean + IC_positions_scan[0]-0.1,1)
#             NP.NP_ma(Motor_No_Sample_Mask,IC_position_mean + IC_positions_scan[0],1)
        
#         journal(saving_path,'Acquire the flat')
#         print('Acquire the flat')

        
#         flat_name = 'SUBSCAN_' + str(sub_acquisition).zfill(len(str(No_sub_acquisitions))) + '_flat'
        
#         # here I need to check it flats exists already and eventually add a different name
#         check_flat_exists = 0         
#         count_name = 1
#         while os.path.exists(saving_path + '/SCAN/' + flat_name + '_IC_0_rep_0.tif'):
#             flat_name = 'SUBSCAN_' + str(sub_acquisition).zfill(len(str(No_sub_acquisitions))) + '_flat' + str(count_name)
#             count_name = count_name + 1

        
#         CTstep_acquire(saving_path + '/SCAN', flat_name, IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask,how_many_images_per_flat_step)
        
#         No_projections_in_sub_acquisition = sum( map(lambda x: x == sub_acquisition,Sub_acquisition_No))
        
#         # move sample in with wait
#         NP.NP_ma(Motor_No_Sample_X, sample_IN_position,1)
#         journal(saving_path,'Moved sample in')
#         print('Moved sample in')
        
#         #set scanning speed for sample (only if 6)
#         if Motor_No_Sample_X == 6:
#             NP.NP_sv(Motor_No_Sample_X,sample_translation_scanning_speed,sample_translation_scanning_acceleration)
        
        
#         # this to start on an user-input projection
#         if sub_acquisition * how_many_projection_before_flat < start_from_projection:
#             start_from = start_from_projection - sub_acquisition * how_many_projection_before_flat
#         else:
#             start_from = 0
        
        
#         for i in range(start_from,No_projections_in_sub_acquisition):
#             scan_angle = angles[sub_acquisition * how_many_projection_before_flat + i]
#             journal(saving_path,'Acquiring angle: ' + str(scan_angle))
#             print(scan_angle)
#             # move the stage at the angle position
#             NP.NP_ma(Motor_No_Sample_ROTY, scan_angle,1)
#             projection_name = 'SUBSCAN_' + str(sub_acquisition).zfill(len(str(No_sub_acquisitions))) + '_proj_' + str(sub_acquisition * how_many_projection_before_flat + i).zfill(len(str(No_real_projections))) 
            
#             if No_dithering == 1:
#                 if jitter_flag == 0:
#                     CTstep_acquire(saving_path + '/SCAN', projection_name, IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask,how_many_images_per_scan_step)
#                 else:
#                     sample_IN_position_now =  sample_IN_position + jitter_shift[sub_acquisition * how_many_projection_before_flat + i]
#                     CTstep_acquire(saving_path + '/SCAN', projection_name , IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask, how_many_images_per_scan_step, sample_IN_position_now, IC_positions_sample, Motor_No_Sample_X, jitter_flag, No_dithering > 1)
    
#             else:
#                 for dither in range(0,No_dithering):
#                     sample_IN_position_now =  sample_IN_position + dither * dither_step + jitter_shift[sub_acquisition * how_many_projection_before_flat + i]
#                     projection_name_with_dither = projection_name + '_dither_' + str(dither).zfill(len(str(No_dithering)))
#                     CTstep_acquire(saving_path + '/SCAN', projection_name_with_dither , IC_position_mean, IC_positions_scan, Exposure_time, Motor_No_Sample_Mask, how_many_images_per_scan_step, sample_IN_position_now, IC_positions_sample, Motor_No_Sample_X, jitter_flag, No_dithering > 1)
    
#     journal(saving_path,'Close the shutter')
#     RG.Close_Shutter()
    
#     HM.HM_AcquireWaitSave(saving_path + '/SCAN/dark_end')
    
#     # writing newport positions
#     All_positions = NP.NP_gp_all()
#     for motors in range(0,len(All_positions)):
#         journal(saving_path,'Motor #' + str(motors+1) + ' = ' + str(All_positions[motors]))
    
    
#     HM.HM_close()
#     NP.NP_close()    