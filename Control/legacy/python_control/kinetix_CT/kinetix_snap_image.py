# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 14:41:42 2023

@author: AXIm Admin
"""
import kinetix_functions as KF

filepath = 'D:/23_09_19/'
Subfolder_name="First_CT_test/"

exp = 3
binn = 2

for idx in range(20):
    image = KF.snap_image()
    fname = filepath + Subfolder_name + 'test_expsoure_' + str(exp) + 'sec_' + str(binn) + 'binning_' + str(idx) 
    KF.save_image(image, fname)