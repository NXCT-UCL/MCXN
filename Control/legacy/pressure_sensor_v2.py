import serial
import time

def PS_check_pressure(PS_Socket):
    # Get the reading
    reading = PS_Reading(PS_Socket)
    
    # Ensure reading is valid (either '0' or '1')
    while reading not in ['0', '1']:
        reading = PS_Reading(PS_Socket)
    
    # Print status based on reading
    if reading == '0':
        print("Warning: Pressure Off")
    else:
        print('Pressure Okay')
    
    return int(reading)

def PS_Open():
    # Open a serial connection (adjust COM port as necessary)
    PS_Socket = serial.Serial('COM6', baudrate=9600, timeout=2)
    
    # Inform the user
    print("Pressure Sensor Connected")
    
    return PS_Socket

def PS_Close(PS_Socket):
    # Close the serial connection
    PS_Socket.close()
    
    # Inform the user
    print("Pressure Sensor Disconnected")

def PS_Reading(PS_Socket):
    # Flush input to clear any buffered data
    PS_Socket.flushInput()  # Clear the input buffer
    
    # Read the pressure sensor data from the serial port
    reading = PS_Socket.readline()
    
    # Decode the reading, removing any errors or whitespace
    pressure_binary = reading.decode(errors='ignore').strip()
    
    return pressure_binary
