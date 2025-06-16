import os

from BrillMethods import *

Exp = 2000
FR = Exp+5

# define pointers
detector_pointer = POINTER(DetObj)()
processor_pointer = Processor_Init()

# initialise detector
print("Initializing the detector...")
result = BrillianSe_Init(byref(detector_pointer))
print("Initialized detector: %s" % BrillianSe_GetErrorMessage(result))

# Set exposure time
result = BrillianSe_SetNumFrames(detector_pointer, 1)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

# Set times
result = BrillianSe_SetFrameTime(detector_pointer, FR, Exp)
print("Exposure time set: %s" % BrillianSe_GetErrorMessage(result))

# Capture image
error_flag = c_int(0)
rec_frames = c_int(0)
captured_data = POINTER(DataObj)()
captured_data = BrillianSe_Capture(detector_pointer, 0, byref(error_flag), byref(rec_frames))
print("Projection capture %s" % BrillianSe_GetErrorMessage(error_flag.value))
print("Number of received frames %d" % rec_frames.value)
WriteToFile("Projection.raw", captured_data)

Data_Delete(byref(captured_data))
Processor_Delete(byref(processor_pointer))

print("Detector shutdown is in progress...")
result = BrillianSe_Shutdown(byref(detector_pointer))
print("Shutdown %s" % BrillianSe_GetErrorMessage(result))
