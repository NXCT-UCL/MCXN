import os

from BrillianSe_py.Methods import *

print(os.getcwd())
roi = ROI()
roi.x = c_ushort(0)
roi.y = c_ushort(0)
roi.width = c_ushort(4096)
roi.height = c_ushort(4096)
# The ROI applied to the gain map and bad pixel map affects their values, but they are still full-size images. Therefore, the resulting FFC/BPC corrected projections are also full-size images, but only the ROI is corrected in these images. 
# If you want to only save the corrected area, you can crop the image using arrays to match the ROI dimensions, but you must keep track of the height and width of the crop so that you can correctly load the image in the future.
# cropped_arr = arr[y:y+hight, x:x+width]

processor_pointer = Processor_Init()

version = create_string_buffer(20)
BrillianSe_GetVersion(version)
print("The SDK version is %s" % version.value)


use_all_frames = False   
# True means that you have already saved all frames in a numpyArray, which could be in the form of either a 3D array or a flattened array with all frames arranged in order
#False means that you have saved the maps and the mean of projection frames and now you want to load them. In this case, you have two options:
#either you previously saved the single frame (offset/gain maps or projection_mean_frame) in a file and you can load it from there, or you have stored them in a numpy array and can load them directly from the array without using a file.



#These numpy arrays are used solely for testing the functionality of the code.
multi_frame= np.zeros((2, 4096, 4096), dtype=np.uint16)
# first frame
multi_frame[0, :, :] = 8000
# second frame
multi_frame[1, :, :] = 9000

single_frame = np.zeros((4096,4096), dtype=np.uint16)
single_frame.fill(10000)



offset_calibration_data = POINTER(DataObj)()
offset_map = POINTER(DataObj)()
if use_all_frames:
    raw_offset_frames = single_frame
    offset_calibration_data = npArryToDataObj(raw_offset_frames)
    result = Processor_OffsetCalibration(processor_pointer, offset_calibration_data)
    print("Offset calibration: %s" % BrillianSe_GetErrorMessage(result))
    offset_map = Processor_GetOffsetMap(processor_pointer)
    WriteToFile("OffsetMap.raw", offset_map)
else:
    offset_map = LoadFileToDataObj("E:\\OffsetMap.raw",4096,4096)
    result = Processor_LoadOffsetMap(processor_pointer, offset_map)
    print("Loading OffsetMap: %s" % BrillianSe_GetErrorMessage(result))
    #uncomment if you want to double check that the map is loaded into SDK properly
    #Data_Delete(byref(offset_map))
    #offset_map = Processor_GetOffsetMap(processor_pointer)
    #WriteToFile("OffsetMap.raw", )

gain_calibration_data = POINTER(DataObj)()
gain_map = POINTER(DataObj)()
bad_pixel_map = POINTER(DataObj)()
if use_all_frames:
    raw_gain_frames = single_frame - 1000
    gain_calibration_data  = npArryToDataObj(raw_gain_frames)
    result = Processor_GainCalibration(processor_pointer, gain_calibration_data, byref(roi))
    print("Gain calibration %s" % BrillianSe_GetErrorMessage(result))
    gain_map = Processor_GetGainMap(processor_pointer)
    WriteToFile("GainMap.raw", gain_map)
    bad_pixel_map = Processor_GetBadPixelMap(processor_pointer)
    WriteToFile("BadPixelMap.raw", bad_pixel_map)
else:
    gain_map = LoadFileToDataObj("E:\\GainMap.raw",4096,4096) 
    result = Processor_LoadGainMap(processor_pointer, gain_map, byref(roi))
    print("Loading GainMap: %s" % BrillianSe_GetErrorMessage(result))
    #uncomment if you want to double check that the map is loaded into SDK properly
    #Data_Delete(byref(gain_map))
    #gain_map = Processor_GetGainMap(processor_pointer)
    #WriteToFile("GainMap.raw", gain_map)
    result = Processor_BadPixelMap(processor_pointer, gain_map, byref(roi))  #A BadPixel Map should be generated if you are directly loading the gain map.
    print("Generating BadPixel Map %s" % BrillianSe_GetErrorMessage(result))
    bad_pixel_map = Processor_GetBadPixelMap(processor_pointer)
    WriteToFile("BadPixelMap.raw", bad_pixel_map)

projection_raw_data = POINTER(DataObj)()
projection_data_mean = POINTER(DataObj)()
if use_all_frames:
    raw_projection_Frames = multi_frame
    projection_raw_data  = npArryToDataObj(raw_projection_Frames)
    projection_data_mean = Processor_MeanFrame(processor_pointer, projection_raw_data)
    WriteToFile("Projection.raw", projection_data_mean)
else:
    projection_data_mean = LoadFileToDataObj("E:\\Projection.raw",4096,4096)

result = Processor_FFC(processor_pointer, projection_data_mean)
print("FFC %s" % BrillianSe_GetErrorMessage(result))
WriteToFile("FFC.raw", projection_data_mean)

result = Processor_BPC(processor_pointer, projection_data_mean)
print("BPC %s" % BrillianSe_GetErrorMessage(result))
WriteToFile("BPC.raw", projection_data_mean)

Data_Delete(byref(projection_raw_data))
Data_Delete(byref(projection_data_mean))
Data_Delete(byref(gain_calibration_data))
Data_Delete(byref(offset_calibration_data))
Data_Delete(byref(offset_map))
Data_Delete(byref(gain_map))
Data_Delete(byref(bad_pixel_map))
Processor_Delete(byref(processor_pointer))