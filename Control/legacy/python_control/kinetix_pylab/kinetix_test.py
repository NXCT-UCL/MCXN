# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 12:06:25 2023

@author: AXIm Admin
"""

from pylablib.devices import Photometrics


cam = Photometrics.PvcamCamera()
cam.open()

cam.get_all_attributes()
cam.get_all_attribute_values()

cam.set_exposure(100)

cam.setup_acquisition(mode='snap',nframes=5)
cam.start_acquisition()
cam.read_multiple_images()

cam.close()
