# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 14:00:25 2023

@author: xpci3540
"""
import serial
import time

def PS_check_pressure():
    
    PS_Socket = PS_Open()
    
    reading = PS_Reading
    while reading not in ['0','1']:
        reading = PS_Reading()
        
    if reading == '0':
        print("Warning: Pressure Off")
    else:
        print('Pressure Okay')
        
    PS_Close()
    
    return int(reading)

def PS_Open(): 

    global PS_Socket 

    # The drive is connected to COM port 14 (but this is set-up dependant) 
    PS_Socket = serial.Serial('COM8', baudrate=9600, timeout=2) 

    # Inform user that the drive has been connected  
    print("Pressure Sensor Connected") 

    return PS_Socket 
 
# Close the socket for the ESS drive  

def PS_Close(): 

    PS_Socket.close() 

    # Tell the user that the socket has been closed  
    print("Pressure Sensor Disconnected") 
    
def PS_Reading(): 
    
    reading = PS_Socket.readline()    
    pressure_binary = reading.decode(errors='ignore').strip()
    
    return pressure_binary