# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 10:25:34 2024

@author: AXIm Admin
"""
# v3 adds timeout to reading

import serial
import time
import warnings

def PS_check_pressure(PS_Socket, timeout=2):
    start_time = time.time()  # Start timing for the timeout
    
    reading = PS_Reading(PS_Socket)
    
    # Loop until valid reading or timeout is exceeded
    while reading not in ['0', '1']:
        if time.time() - start_time > timeout:
            print("Error: Timeout exceeded while waiting for pressure sensor reading.")
            return None  # Return None if it times out
        
        reading = PS_Reading(PS_Socket)
    
    # Print status based on reading
    if reading == '0':
        warnings.warn('The Pressure is OFF.')
    else:
        print('Pressure Okay')
    
    return int(reading)

def PS_Open():
    PS_Socket = serial.Serial('COM3', baudrate=9600, timeout=2)
    PS_Socket.dtr = False  # Set DTR low
    time.sleep(0.5)        # Wait for the Arduino to reset
    PS_Socket.dtr = True   # Set DTR high again to re-enable communication
    
    print("Pressure Sensor Connected")
    return PS_Socket

def PS_Close(PS_Socket):
    PS_Socket.close()
    print("Pressure Sensor Disconnected")

def PS_Reading(PS_Socket):
    PS_Socket.flushInput()  # Clear the input buffer
    try:
        reading = PS_Socket.readline()
        pressure_binary = reading.decode(errors='ignore').strip()
        return pressure_binary
    except Exception as e:
        print(f"Error reading from sensor: {e}")
        return ''

def PS_Reset(PS_Socket):
    # Reset the Arduino by toggling the DTR (Data Terminal Ready) pin
    PS_Socket.dtr = False  # Reset the Arduino
    time.sleep(0.5)        # Allow some time for the reset to happen
    PS_Socket.dtr = True   # Turn DTR back on
    print("Arduino Reset")
