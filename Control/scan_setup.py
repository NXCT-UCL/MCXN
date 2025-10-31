# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 10:52:03 2025

@author: AXIm Admin
"""

from ESS_Commands_V7 import *
from pressure_sensor_v3 import PS_Open, PS_check_pressure


PS_Socket = PS_Open()
PS_check_pressure(PS_Socket)

# %%

socket = ESS_Open()
ESS_Velocity(1268640)
ESS_Acceleration_Speed(184320)
ESS_Deceleration_Speed(184320)
ESS_PGain(2000)
ESS_VelocityFF(2048)
ESS_Velocity_PGain(2.5)
ESS_Prep_Move()

ESS_Position()

# %%

ESS_Relative_Move(-2)
ESS_Relative_Move(2)

# %%

ESS_Home()

#%%

ESS_Absolute_Move(-8)

#%%

from detectors.factory import get_detector

det_name = 'primeBSI'
detector = get_detector(det_name)
detector.initialise()