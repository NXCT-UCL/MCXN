# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:47:36 2024

@author: AXIm Admin
"""

import automation1 as a1

def AT_Connect():
    
    global controller
    
    controller = a1.Controller.connect_usb()
    controller.start()
    
    return controller

def AT_Home():
    
    return 0
    
def AT_Disconnect():
    
    controller.disconnect()
    
def AT_enable_axis(axis):
    controller.runtime.commands.motion.enable("X")
    
def AT_enable_axes():
    AT_enable_axis("X")
    AT_enable_axis("Y")
    AT_enable_axis("Z")
    
def AT_rel_move(axis,distance):
    controller.runtime.commands.motion.movelinear(axis, 5)
    
