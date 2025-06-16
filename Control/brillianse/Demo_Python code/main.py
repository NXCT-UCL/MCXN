import os

from BrillianSe_py.Methods import *

print(os.getcwd())
roi = ROI()
roi.x = c_ushort(0)
roi.y = c_ushort(0)
roi.width = c_ushort(4096)
roi.height = c_ushort(4096)

detector_pointer = POINTER(DetObj)()
processor_pointer = Processor_Init()

version = create_string_buffer(20)
BrillianSe_GetVersion(version)
print("The SDK version is %s" % version.value)

print("Initializing the detector...")
result = BrillianSe_Init(byref(detector_pointer))
print("Initialized detector: %s" % BrillianSe_GetErrorMessage(result))

result = BrillianSe_SetDetectorMode(detector_pointer, 0)
print("Set detector mode: %s" % BrillianSe_GetErrorMessage(result))

result = BrillianSe_SetTriggerMode(detector_pointer, 0)
print("Set trigger mode: %s" % BrillianSe_GetErrorMessage(result))

result = BrillianSe_SetNumFrames(detector_pointer, 1)
print("Set num frames: %s" % BrillianSe_GetErrorMessage(result))

mode = c_int(0)
error_flag = c_int(0)
rec_frames = c_int(0)

# If you are using the simulator, please uncomment this section.
#result = BrillianSe_LoadImage(detector_pointer, 0)
#print("loading offset image %s" % BrillianSe_GetErrorMessage(result))

Offset_Calibration_data = POINTER(DataObj)()
print("Offset capture is in progress...")
Offset_Calibration_data = BrillianSe_Capture(detector_pointer, mode, byref(error_flag), byref(rec_frames))
print("Offset capture %s" % BrillianSe_GetErrorMessage(error_flag.value))
print("Number of received frames %d" % rec_frames.value)

result = Processor_OffsetCalibration(processor_pointer, Offset_Calibration_data)
print("Offset calibration: %s" % BrillianSe_GetErrorMessage(result))

offset_map = POINTER(DataObj)()
offset_map = Processor_GetOffsetMap(processor_pointer)
WriteToFile("OffsetMap.raw", offset_map)

# If you are using the simulator, please uncomment this section.
#result = BrillianSe_LoadImage(detector_pointer, 1)
#print("loading gain image %s" % BrillianSe_GetErrorMessage(result))

Gain_Calibration_data = POINTER(DataObj)()
print("Gain capture is in progress...")
Gain_Calibration_data = BrillianSe_Capture(detector_pointer, mode, byref(error_flag), byref(rec_frames))
print("Gain capture %s" % BrillianSe_GetErrorMessage(error_flag.value))
print("Number of received frames %d" % rec_frames.value)

result = Processor_GainCalibration(processor_pointer, Gain_Calibration_data, byref(roi))
print("Gain calibration %s" % BrillianSe_GetErrorMessage(result))

gain_map = POINTER(DataObj)()
gain_map = Processor_GetGainMap(processor_pointer)
WriteToFile("GainMap.raw", gain_map)

bad_pixel_map = POINTER(DataObj)()
bad_pixel_map = Processor_GetBadPixelMap(processor_pointer)
WriteToFile("BadPixelMap.raw", bad_pixel_map)

trigger_mode = c_int(0)
result = BrillianSe_SetTriggerMode(detector_pointer, trigger_mode)
print("Set trigger mode %s" % BrillianSe_GetErrorMessage(result))

# If you are using the simulator, please uncomment this section.
#result = BrillianSe_LoadImage(detector_pointer, 2)
#print("loading projection image %s" % BrillianSe_GetErrorMessage(result))

captured_data = POINTER(DataObj)()
print("Projection capture is in progress...")
captured_data = BrillianSe_Capture(detector_pointer, mode, byref(error_flag), byref(rec_frames))
print("Projection capture %s" % BrillianSe_GetErrorMessage(error_flag.value))
print("Number of received frames %d" % rec_frames.value)

captured_data_mean = POINTER(DataObj)()
captured_data_mean = Processor_MeanFrame(processor_pointer, captured_data)
WriteToFile("Projection.raw", captured_data_mean)

result = Processor_FFC(processor_pointer, captured_data_mean)
print("FFC %s" % BrillianSe_GetErrorMessage(result))
WriteToFile("FFC.raw", captured_data_mean)

result = Processor_BPC(processor_pointer, captured_data_mean)
print("BPC %s" % BrillianSe_GetErrorMessage(result))
WriteToFile("BPC.raw", captured_data_mean)

Data_Delete(byref(captured_data))
Data_Delete(byref(captured_data_mean))
Data_Delete(byref(Gain_Calibration_data))
Data_Delete(byref(Offset_Calibration_data))
Data_Delete(byref(offset_map))
Data_Delete(byref(gain_map))
Data_Delete(byref(bad_pixel_map))
Processor_Delete(byref(processor_pointer))
print("Detector shutdown is in progress...")
result = BrillianSe_Shutdown(byref(detector_pointer))
print("Shutdown %s" % BrillianSe_GetErrorMessage(result))
