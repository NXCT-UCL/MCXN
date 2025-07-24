# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 10:56:35 2025

@author: AXIm Admin
"""

import numpy as np

class BaseDetector():
    
    def acquire_image(self):
        pass

    def initialise(self):
        pass

    def shutdown(self):
        pass

    def set_exposure_time(self, exposure_time_ms):
        pass
  
    def acquire_sequence(self, num_frames):
        
        first_img = self.acquire_image()
        img_shape = first_img.shape
        
        # Choose a wider accumulator type based on input dtype
        if first_img.dtype == np.uint16 or first_img.dtype == np.uint12:
            accumulator = np.zeros(img_shape, dtype=np.uint32)
        elif first_img.dtype == np.uint32:
            accumulator = np.zeros(img_shape, dtype=np.uint64)
        else:
            # Fallback for other types (e.g. float)
            accumulator = np.zeros(img_shape, dtype=np.float64)

        # Add first image
        accumulator += first_img.astype(accumulator.dtype)

        # Loop over remaining frames
        for _ in range(num_frames - 1):
            frame = self.acquire_image()
            accumulator += frame.astype(accumulator.dtype)

        # Average and convert back to original dtype
        avg_image = (accumulator / num_frames).astype(first_img.dtype)

        return avg_image