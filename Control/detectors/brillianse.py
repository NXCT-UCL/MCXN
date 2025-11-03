# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 11:07:30 2025

@author: AXIm Admin
"""

from .base import BaseDetector
from BrillMethods import *

class Brillianse(BaseDetector):
    
    def __init__(self, detector_pointer = None, image_shape=(4096,4096)):
        super().__init__()
        self.detector_pointer = POINTER(DetObj)()
        self.image_shape = image_shape
        self.z_axis_channel = 2
        self.z_offset_mm = 0.0
        self.z_direction = 1

    def initialise(self):
        print("Initialising BrillianSe detector...")
        result = BrillianSe_Init(byref(self.detector_pointer))
        print("Initialized detector: %s" % BrillianSe_GetErrorMessage(result))
        result = BrillianSe_SetNumFrames(self.detector_pointer, 1)
        print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

    def shutdown(self):
        print("Detector shutdown is in progress...")
        result = BrillianSe_Shutdown(byref(self.detector_pointer))
        print("Shutdown %s" % BrillianSe_GetErrorMessage(result))

    def acquire_image(self):
        error_flag = c_int(0)
        rec_frames = c_int(0)
        captured_data = POINTER(DataObj)()

        # Acquire data
        captured_data = BrillianSe_Capture(
            self.detector_pointer, 0,
            byref(error_flag), byref(rec_frames)
        )

        # Get buffer and size
        buffer_ptr = Data_GetBuffer(captured_data)
        frame_size = c_int(0)
        Data_GetFrameSize(captured_data, byref(frame_size))

        num_pixels = frame_size.value // 2  # assuming uint16 = 2 bytes

        # Convert to NumPy
        array_type = c_ushort * num_pixels
        raw_array = cast(buffer_ptr, POINTER(array_type)).contents
        np_array = np.ctypeslib.as_array(raw_array)

        # Reshape
        shape = self.image_shape
        np_array = np_array.reshape(shape)

        # Free C memory
        Data_Delete(byref(captured_data))

        return np_array

    def set_exposure_time(self, exp=1000):
        result = BrillianSe_SetFrameTime(self.detector_pointer, exp+5, exp)
        print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))