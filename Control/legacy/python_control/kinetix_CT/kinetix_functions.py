# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 11:38:51 2023

@author: AXIm Admin
"""

from pycromanager import Core
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff

def snap_image():
    #Setup
    # get object representing MMCore
    core = Core()
    
    #### Calling core functions ###
    exposure = core.get_exposure()
    
    #### Setting and getting properties ####
    # Here we set a property of the core itself, but same code works for device properties
    auto_shutter = core.get_property('Core', 'AutoShutter')
    core.set_property('Core', 'AutoShutter', 0)
    
    #### Acquiring images ####
    # The micro-manager core exposes several mechanisms foor acquiring images. In order to
    # not interfere with other pycromanager functionality, this is the one that should be used
    core.snap_image()
    tagged_image = core.get_tagged_image()
    
    # If using micro-manager multi-camera adapter, use core.getTaggedImage(i), where i is
    # the camera index
    
    # pixels by default come out as a 1D array. We can reshape them into an image
    pixels = np.reshape(tagged_image.pix,
                            newshape=[tagged_image.tags['Height'], tagged_image.tags['Width']])
    
    return pixels

def save_image(image, fname):
    
    tiff.imsave(fname, image)
    
