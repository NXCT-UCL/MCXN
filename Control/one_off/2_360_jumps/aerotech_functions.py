# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:47:36 2024

@author: AXIm Admin
"""

import automation1 as a1
controller: a1.Controller = None

def AT_start_up():
    
    AT_connect()
    AT_start_controller()
    AT_enable_all()
    
def AT_turn_off():
    
    AT_disable_all()
    AT_stop_controller()
    AT_disconnect()

def AT_connect():
	'''
	Connects to the Automation1 controller.
	'''
	global controller
	if controller:
		print('Already connected')
		return

	controller = a1.Controller.connect_usb()
	print('Connected to Automation1 controller')
    
def AT_disconnect():
	'''
	Disconnects from the Automation1 controller.
	'''
	global controller
	if not controller:
		print('Already disconnected')
		return
	
	controller.disconnect()
	controller = None
	print('Disconnected from Automation1 controller')
    
def AT_start_controller():
	'''
	Starts the Automation1 controller.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before you can start it')
		return

	controller.start()
	print('Controller started')
    
def AT_stop_controller():
	'''
	Stops the Automation1 controller.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before you can stop it')
		return

	controller.stop()
	print('Controller stopped')
    
def AT_enable_axis(axis):
	'''
	Enables an axis.

	Args:
		axis: The name of the axis to enable.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before enabling an axis')
		return

	controller.runtime.commands.motion.enable(axis)
	print(f'Axis {axis} enabled')
    
def AT_enable_all():
    AT_enable_axis("X")
    AT_enable_axis("Y")
    AT_enable_axis("Z")
    
def AT_disable_axis(axis):
	'''
	Disables an axis.

	Args:
		axis: The name of the axis to disable.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before disabling an axis')
		return

	controller.runtime.commands.motion.disable(axis)
	print(f'Axis {axis} disabled')
    
def AT_disable_all():
    AT_disable_axis("X")
    AT_disable_axis("Y")
    AT_disable_axis("Z")
    
def AT_home_axis(axis):
	'''
	Homes an axis.

	Args:
		axis: The name of the axis to home.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before homing an axis')
		return

	# We can home an axis using the home() method in the MotionCommands API.
	# The Commands API provides access to many of the AeroScript commands that are used to perform actions
	# on the controller.
	# 
	# Similar commands are grouped together under the top-level Commands property. For example,
	# Commands.motion provides access to the motion commands, Commands.io provides access to commands
	# for I/O operations, etc.
	#
	# If an error occurs while executing a command, like if the controller is not started or an axis fault
	# has occurred, the command will throw a ControllerException that provides information on the error.
	# See the try/except in main() for more information about handling ControllerException.
	controller.runtime.commands.motion.home(axis)
	print(f'Axis {axis} homed')
    
def AT_home_all():
    AT_home_axis("X")
    AT_home_axis("Y")
    AT_home_axis("Z")
    
def AT_abort_axis(axis):
	'''
	Aborts motion on an axis.

	Args:
		axis: The name of the axis to abort.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before aborting')
		return

	# We can abort motion on an axis using the abort() method in the MotionCommands API.
	# The Commands API provides access to many of the AeroScript commands that are used to perform actions
	# on the controller.
	# 
	# Similar commands are grouped together under the top-level Commands property. For example,
	# Commands.motion provides access to the motion commands, Commands.io provides access to commands
	# for I/O operations, etc.
	#
	# If an error occurs while executing a command, like if the controller is not started or an axis fault
	# has occurred, the command will throw a ControllerException that provides information on the error.
	# See the try/except in main() for more information about handling ControllerException.
	controller.runtime.commands.motion.abort(axis)
	print(f'Motion aborted on axis {axis}')

def AT_show_axis_status(axis):
	'''
	Gets common and important information about an axis.

	Args:
		axis: The name of the axis to get information on.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before getting an axis\'s status')
		return

	# We can get information about the current state of the controller, tasks, and axes via status items. To do so, we must first
	# specify the items we want to query by creating a StatusItemConfiguration object. We then add each status item to the axis category
	# using the axis.add() method. To actually get the values of these items, we call get_status_items(status_item_configuration), which 
	# returns a StatusItemResults object.
	status_item_configuration = a1.StatusItemConfiguration()
	# Status items are defined in enums in the Python API. ProgramPosition is the position specified in program-space, before being
	# transformed and sent to the drive. See the Controller Motion Signals help file topic for more details.
	status_item_configuration.axis.add(a1.AxisStatusItem.ProgramPosition, axis)
	# DriveStatus is a series of bits that can be masked. We will use it to get the axis enabled bit.
	status_item_configuration.axis.add(a1.AxisStatusItem.DriveStatus, axis)
	# AxisStatus is another series of bits that can be masked. We will use it to get the axis homed bit, calibration enabled 1D bit,
	# and calibration enabled 2D bit. In this case, homed indicates whether or not the axis in question has been homed since the last
	# controller reset. The calibration bits indicate if the axis is currently calibrated.
	status_item_configuration.axis.add(a1.AxisStatusItem.AxisStatus, axis)
	result = controller.runtime.status.get_status_items(status_item_configuration)

	print(f'Axis {axis} Status')
	print('------------')

	# ProgramPosition is acquired directly as a float, which is what we need.
	program_position = result.axis.get(a1.AxisStatusItem.ProgramPosition, axis).value
	print(f'Position: {program_position}')

	# DriveStatus is a series of status bits that can be masked to get various information about the state of the drive.
	# It is acquired as a float, but we need to interpret it as a series of maskable bits. To do so, we construct an int
	# from the float value. We next apply the "Enabled" mask from the enum and check if the result equals the mask to determine
	# if the drive axis is enabled.
	drive_status = int(result.axis.get(a1.AxisStatusItem.DriveStatus, axis).value)
	is_enabled = (drive_status & a1.DriveStatus.Enabled) == a1.DriveStatus.Enabled
	print(f'Enabled: {is_enabled}')

	# AxisStatus is similar to DriveStatus in that it can be masked to get information about the state of the axis.
	# It is also acquired as a float, so we again need to interpret it as a series of maskable bits. To do so, we repeat
	# the process outlined for DriveStatus with AxisStatus.
	axis_status = int(result.axis.get(a1.AxisStatusItem.AxisStatus, axis).value)
	is_homed = (axis_status & a1.AxisStatus.Homed) == a1.AxisStatus.Homed
	print(f'Homed: {is_homed}')

	# AxisStatus also contains status bits relating to the calibration state of the axis.  To get these, we simply need to 
	# apply different masks and "or" the results.
	calibration_enabled_1D = (axis_status & a1.AxisStatus.CalibrationEnabled1D) == a1.AxisStatus.CalibrationEnabled1D
	calibration_enabled_2D = (axis_status & a1.AxisStatus.CalibrationEnabled2D) == a1.AxisStatus.CalibrationEnabled2D
	print(f'Calibration State: {calibration_enabled_1D or calibration_enabled_2D}') 

def AT_move_axis_linear(axis, distance, speed=5):
	'''
	Executes a linear move on an axis.

	Args:
		axis: The name of the axis to move.
		distance: The distance to move the axis.
		speed: The speed at which to move the axis.
	'''
	# Make sure we are connected before trying to do anything.
	if not controller:
		print('You must connect to the controller before moving an axis')
		return

	# The movelinear() method will not return until the move is complete.
	# We can keep this application responsive during the move if we do the move on a background thread.
	# If we change movelinear(axisName, [distance], speed) to Thread(target=movelinear, args=(axis, [distance], speed)).start(),
	# then the method will run on its own thread and we can continue doing things while the axis is moving. This requires
	# importing the "Thread" class from the "threading" module. You should be familiar with multi-threaded programming before 
	# doing this.
	print(f'Moving axis {axis}')
	controller.runtime.commands.motion.movelinear(axis, [distance], speed)
	print('Move complete')

def AT_get_pos(axis):
    
    if not controller:
    		print('You must connect to the controller before moving an axis')
    		return
    
    status_item_configuration = a1.StatusItemConfiguration()
    status_item_configuration.axis.add(a1.AxisStatusItem.ProgramPosition, axis)
    results = controller.runtime.status.get_status_items(status_item_configuration)
     
    program_position = results.axis.get(a1.AxisStatusItem.ProgramPosition, axis).value
    print(program_position)
