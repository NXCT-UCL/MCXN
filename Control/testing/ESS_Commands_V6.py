# Program: ESS_Commands_V3.0  
# The following script has basic command to use the ESS stage   
# Version log  
# V1.0 had all the basic commands for ESS stage implemented    
# V2.0 uses the global variable function to call the ESS socket removing some redundant code
# V3.0 adds commands for regulating the acceleraion/deceleration of the turntable and accessing fault registry  
# V5 takes out sleep on absolute move
# V6 tests operating mode
# Author: Christopher Thornton  
# Date: 7-Jun-2022 
#!/usr/bin/python 
# use Python Version 3.8 (or higher as the ASCII convention changed after V3.0)  

# Import standard libraries  

# socket = ESS_Open()

import serial # Serial library  
import re # Used to split up a function  
import time

# Global variables  

# -----------------  Variables of the stage -----------------------------------  
  
Steps_per_full_revolution = int(3686400) # For a full 360 deg for the ESS stage purchased in 2021 is 3686400 steps      
    
# ------------------ Program functions ---------------------------------------- 

# Implements if stage position is checked when rotating (ON=1, OFF=0) 

Postion_check_flag = 1 

# Silent mode/debug mode, this turns off the messages given for ASCII respond and send (ON=1, OFF=0) 

Silent_mode = 0  

# -------------------------- OPEN/CLOSE the socket ------------------------------------- 

# Open the socket for the ESS drive  

def ESS_Open(): 

    global ESS_Socket 

    # The drive is connected to COM port 14 (but this is set-up dependant) 
    ESS_Socket = serial.Serial('COM5', baudrate=9600, timeout=0.5) 

    # Inform user that the drive has been connected  
    print("Drive Connected") 

    return ESS_Socket 
 
# Close the socket for the ESS drive  

def ESS_Close(): 

    ESS_Socket.close() 

    # Tell the user that the socket has been closed  
    print("Drive Closed") 

     
# ----------------------- Set the parameters of ESS drive  ---------------------------------------------- 

# Set the velocity of the stage where the speed variable is 0.1 count per second (Standard 36864000 the max is 368640000) 
def ESS_Velocity (speed):     

    SendAsciiCmd(ESS_Socket, 's r0xcb ' + str(speed) ) 

# Set the turntable's acceleration magnitude. The unit of 'acceleration' variable is 10 counts per second^2 
    
def ESS_Acceleration_Speed(acceleration):
    
    SendAsciiCmd(ESS_Socket,'s r0xcc ' + str(acceleration) )
      
# Set the turntable's deceleration magnitude. The unit of 'deceleration' variable is 10 counts per second^2 
    
def ESS_Deceleration_Speed(deceleration):     

    SendAsciiCmd(ESS_Socket,'s r0xcd ' + str(deceleration) )

# Set the controller proportional gain

def ESS_PGain(gain):
    
    SendAsciiCmd(ESS_Socket,'s r0x30 ' + str(gain) )
    
# Set the velocity feed forward

def ESS_VelocityFF(VFF):
    
    SendAsciiCmd(ESS_Socket,'s r0x33 ' + str(VFF) )
    
def ESS_Velocity_PGain(VPG):
    
    SendAsciiCmd(ESS_Socket,'s r0x27 ' + str(VPG))

# ----------------------- Set the position of ESS drive  ---------------------------------------------- 

# Tell the user the position  

def ESS_Position(): 

# Send the ASCII command to find the stage position, get the answer back as a string  
    Current_position = SendAsciiCmd(ESS_Socket,'g r0x32') 
    #print(Current_position)
# Break the string up so that it can be used else where      
    result = re.split(' ', Current_position ) 


        
    #print(result) #Testing command  

# Convert the steps into an angle   
    Degs = ((int(result[1]))/Steps_per_full_revolution)*360
    Deg_position = round(Degs, 4) 

    print(Deg_position) 

# Return the angle position   
    return Deg_position 

def ESS_Prep_Move():
    
    SendAsciiCmd(ESS_Socket, 's r0x24 21')


# Move to an absolute position      

def ESS_Absolute_Move (deg): 

    # Convert from angle to steps  
    deg_to_step = int(((deg/360)*Steps_per_full_revolution))  

    # Send the new position   
    SendAsciiCmd(ESS_Socket,'s r0xca ' + str(deg_to_step) ) 
    # Move the stage  
    SendAsciiCmd(ESS_Socket,'t 1') 
    # Monitor the move  
    if Postion_check_flag == 1: 
       done = 0   # local flag  

       while done == 0: 
           # Command to check position  
           check_message = re.split('(\d+)',(SendAsciiCmd(ESS_Socket,'g r0xa0'))) [1] 
   #        print(check_message)     # debug tool  
           
   # how to break the while loop  
           if int(check_message) == 0 : 
              done = 1    

# Move relative to your current position  

def ESS_Relative_Move (deg): 

    # Calculate the position to move knowing the current position  
    current_position_deg = ESS_Position() # Will print the current position can be confusing on the output  

    deg_to_step = int(((deg+current_position_deg)/360)*Steps_per_full_revolution)   

    #Specify the acceleration/deceleration profile: 0 for trapezoid, 1 for sinusoid
    SendAsciiCmd(ESS_Socket,'s r0xc8 1')
    time.sleep(0.5)
    # Send the new position  
    SendAsciiCmd(ESS_Socket,'s r0xca ' + str(deg_to_step) ) 

    # Move the stage  
    SendAsciiCmd(ESS_Socket,'t 1') 

    # Monitor the move  
    if Postion_check_flag == 1: 
       done = 0   # local flag  

       while done == 0: 
            # Command to check position  
           check_message = re.split('(\d+)',(SendAsciiCmd(ESS_Socket,'g r0xa0'))) [1] 
   #        print(check_message)     # debug tool  

   # How to break the while loop  
           if int(check_message) == 0 : 
              done = 1       

# Home the drive, completes the last 360 deg and set the new position to zero  

def ESS_Home ():     
    
    SendAsciiCmd(ESS_Socket,'s r0xc2 544')
    SendAsciiCmd(ESS_Socket,'t 2')
    

    
def ESS_Read(): 

    Read = SendAsciiCmd(ESS_Socket,'g r0xa4')  
    value = re.split(' ', Read )
    print(value)
    
def ESS_Reset(): 

    Reset = SendAsciiCmd(ESS_Socket,'r')  

def ESS_Read_Parameters():
    
    ESS_Read_PGain=SendAsciiCmd(ESS_Socket,'g r0x30 ')
    ESS_Read_VFeedForward=SendAsciiCmd(ESS_Socket,'g r0x33 ')
    ESS_Read_AFeedForward=SendAsciiCmd(ESS_Socket,'g r0x34 ')
    ESS_Acceleration=SendAsciiCmd(ESS_Socket,'g r0xcc ')
    ESS_Deceleration=SendAsciiCmd(ESS_Socket,'g r0xcc ')
    ESS_Read_Velocity_PGain=SendAsciiCmd(ESS_Socket, 'g r0x27 ')
    ESS_Read_Velocity_IGain=SendAsciiCmd(ESS_Socket, 'g r0x28 ')
    print("Proportional gain: ", ESS_Read_PGain)
    print("Velocity feed forward: ", ESS_Read_VFeedForward)
    print("Acceleration feed forward: ", ESS_Read_AFeedForward)
    print("Acceleration: ", ESS_Acceleration)
    print("Deceleration: ", ESS_Deceleration)
    print("Velocity loop proportional gain: ", ESS_Read_Velocity_PGain)
    print("Velocity loop integral gain: ", ESS_Read_Velocity_IGain)
 
# ---------------------   ASCII command handling commands for Copley ------------------------     

  

# Send an ASCII command and return the drive's response 

def SendAsciiCmd(ser,cmd): 

    cmd = cmd + '\r' 

    ser.write(cmd.encode()) 

    if Silent_mode == 0: 

        print("ASCII Cmd Sent: " + cmd) 

    return SerReadASCIIResponse(ser) 

  

# Collects all ASCII responses from drive 

def SerReadASCIIResponse(ser): 

    ret = '' 

    while (True): 

        ch = ser.read(1) 

        if (len(ch) < 1 or ch == '\r'): 

            if Silent_mode == 0: 

                print("ASCII Response: " + ret) 

            return ret 

        ret += str(ch, 'utf-8') 

         

  

# Collects all serial binary response data (NOT USED) 

def SerReadSerialBinaryResponse(ser): 

    ret = [] 

    while (True): 

        ch = ser.read(1) 

        if (len(ch) < 1 or ch == '\r'): 

            print("Serial Binary Response: " + (" ".join(ret))) 

            return(ret) 

        ch = ch.hex() 

        ret.append(ch) 

  