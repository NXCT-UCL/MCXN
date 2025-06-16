# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:40:16 2024

@author: AXIm Admin
"""

import ESS_Commands_V7 as ESS
import time

def Measure_Position_For_One_Second():
    start_time = time.time()  # Record the start time
    positions = []  # To store all measured positions
    
    while (time.time() - start_time) < 2:  # Run for approximately 1 second
        current_position = ESS.ESS_Position()  # Call the function to get the current position
        positions.append(current_position)  # Store the position
        
        # Print the position (optional, or save them to a file)
        print(f"Measured Position: {current_position}")
        
        # Wait for a small interval to avoid excessive polling (e.g., 0.1s)
        time.sleep(0.02)
    
    # After the loop, you can return or save the positions
    return positions

socket=ESS.ESS_Open()
ESS.ESS_Velocity(1268640)
ESS.ESS_Acceleration_Speed(184320)
ESS.ESS_Deceleration_Speed(184320)
ESS.ESS_PGain(2000)
ESS.ESS_VelocityFF(2048)
ESS.ESS_Velocity_PGain(2.5)
ESS.ESS_Prep_Move()

ESS.ESS_Absolute_Move(-8)

time.sleep(4)

# ESS.ESS_Absolute_Move(-8)
# pos_0 = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-8)
# pos_0b = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-9)
# pos_1 = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-10)
# pos_1b = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-20)
# pos_10 = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-30)
# pos_10b = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-130)
# pos_100 = Measure_Position_For_One_Second()

# ESS.ESS_Absolute_Move(-230)
# pos_100b = Measure_Position_For_One_Second()

pos = -8
ESS.ESS_Absolute_Move(pos)
pos_a = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_b = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_c = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_d = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_e = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_f = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_g = Measure_Position_For_One_Second()

pos = pos-0.15
ESS.ESS_Absolute_Move(pos)
pos_h = Measure_Position_For_One_Second()

ESS.ESS_Close()