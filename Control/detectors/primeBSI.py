# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 10:57:22 2025

@author: AXIm Admin
"""

from .base import BaseDetector
from pycromanager import Core
import numpy as np

class PrimeBSI(BaseDetector):
    
    def __init__(self):
        pass
    
    def initialise(self):
        
        self.core = Core()
        self.core.set_roi('Camera-1',356,382,1314,1314)
    
    def acquire_image(self):

        #### Calling core functions ###
        exposure = self.core.get_exposure()
        
        #### Setting and getting properties ####
        # Here we set a property of the core itself, but same code works for device properties
        auto_shutter = self.core.get_property('Core', 'AutoShutter')
        self.core.set_property('Core', 'AutoShutter', 0)
        
        #### Acquiring images ####
        # The micro-manager core exposes several mechanisms foor acquiring images. In order to
        # not interfere with other pycromanager functionality, this is the one that should be used
        self.core.snap_image()
        tagged_image = self.core.get_tagged_image()
        
        # If using micro-manager multi-camera adapter, use core.getTaggedImage(i), where i is
        # the camera index
        
        # pixels by default come out as a 1D array. We can reshape them into an image
        pixels = np.reshape(tagged_image.pix,
                                newshape=[tagged_image.tags['Height'], tagged_image.tags['Width']])
        
        return pixels
    
    def set_exposure_time(self, exp):
        
        self.core.set_exposure(exp)