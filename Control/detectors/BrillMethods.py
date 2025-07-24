from BrillStructs import *
import numpy as np
import os

lib_path = os.path.join(os.getcwd(), "BrillianSe.dll")
lib1 = CDLL(lib_path)

### BUILT-IN METHODS ###
libc = windll.msvcrt
fopen = libc.fopen
fopen.argtypes = c_char_p, c_char_p,
fopen.restype = c_void_p

fwrite = libc.fwrite
fwrite.argtypes = c_void_p, c_size_t, c_size_t, c_void_p
fwrite.restype = c_size_t

fclose = libc.fclose
fclose.argtypes = c_void_p,
fclose.restype = c_int


### BRILLIANSE METHODS ###
BrillianSe_GetVersion = lib1.BrillianSe_GetVersion
BrillianSe_GetVersion.argtypes = [c_char_p]
BrillianSe_GetVersion.restype = None

BrillianSe_Init = lib1.BrillianSe_Init
BrillianSe_Init.argtypes = [POINTER(POINTER(DetObj))]
BrillianSe_Init.restype = c_int

BrillianSe_ObserverConnect = lib1.BrillianSe_ObserverConnect
BrillianSe_ObserverConnect.argtypes = [POINTER(POINTER(DetObj))]
BrillianSe_ObserverConnect.restype = c_int

BrillianSe_New = lib1.BrillianSe_New
BrillianSe_New.argtypes = [c_int, c_int]
BrillianSe_New.restype = POINTER(DetObj)

BrillianSe_ObserverConnect_WithIP = lib1.BrillianSe_ObserverConnect_WithIP
BrillianSe_ObserverConnect_WithIP.argtypes = [POINTER(DetObj), c_char_p, c_int]
BrillianSe_ObserverConnect_WithIP.restype = c_int

BrillianSe_Connect = lib1.BrillianSe_Connect
BrillianSe_Connect.argtypes = [POINTER(DetObj), c_char_p, c_int]
BrillianSe_Connect.restype = c_int

BrillianSe_Disconnect = lib1.BrillianSe_Disconnect
BrillianSe_Disconnect.argtypes = [POINTER(DetObj)]
BrillianSe_Disconnect.restype = c_int

BrillianSe_Delete = lib1.BrillianSe_Delete
BrillianSe_Delete.argtypes = [POINTER(POINTER(DetObj))]
BrillianSe_Delete.restype = c_int

BrillianSe_SetVoltage = lib1.BrillianSe_SetVoltage
BrillianSe_SetVoltage.argtypes = [POINTER(DetObj), c_int, c_int, c_int]
BrillianSe_SetVoltage.restype = c_int

BrillianSe_GetVoltage = lib1.BrillianSe_GetVoltage
BrillianSe_GetVoltage.argtypes = [POINTER(DetObj), POINTER(c_int)]
BrillianSe_GetVoltage.restype = c_int

BrillianSe_SetDetectorMode = lib1.BrillianSe_SetDetectorMode
BrillianSe_SetDetectorMode.argtypes = [POINTER(DetObj), c_int]
BrillianSe_SetDetectorMode.restype = c_int

BrillianSe_GetDetectorMode = lib1.BrillianSe_GetDetectorMode
BrillianSe_GetDetectorMode.argtypes = [POINTER(DetObj), POINTER(c_int)]
BrillianSe_GetDetectorMode.restype = c_int

BrillianSe_SetCDSConfig = lib1.BrillianSe_SetCDSConfig
BrillianSe_SetCDSConfig.argtypes = [POINTER(DetObj), c_bool, c_int]
BrillianSe_SetCDSConfig.restype = c_int

BrillianSe_SetNonoverlapReset = lib1.BrillianSe_SetNonoverlapReset
BrillianSe_SetNonoverlapReset.argtypes = [POINTER(DetObj), c_bool]
BrillianSe_SetNonoverlapReset.restype = c_int

BrillianSe_SetAveFrames = lib1.BrillianSe_SetAveFrames
BrillianSe_SetAveFrames.argtypes = [POINTER(DetObj), c_int]
BrillianSe_SetAveFrames.restype = c_int

BrillianSe_SendCommand = lib1.BrillianSe_SendCommand
BrillianSe_SendCommand.argtypes = [POINTER(DetObj), c_char_p]
BrillianSe_SendCommand.restype = c_int

BrillianSe_GetFrameSize = lib1.BrillianSe_GetFrameSize
BrillianSe_GetFrameSize.argtypes = [POINTER(DetObj), POINTER(c_int)]
BrillianSe_GetFrameSize.restype = c_int

BrillianSe_SetFrameTime = lib1.BrillianSe_SetFrameTime
BrillianSe_SetFrameTime.argtypes = [POINTER(DetObj), c_double, c_double]
BrillianSe_SetFrameTime.restype = c_int

BrillianSe_SetFrameTime_Intl = lib1.BrillianSe_SetFrameTime_Intl
BrillianSe_SetFrameTime_Intl.argtypes = [POINTER(DetObj), c_double, c_double]
BrillianSe_SetFrameTime_Intl.restype = c_int

BrillianSe_SetPixelTime = lib1.BrillianSe_SetPixelTime
BrillianSe_SetPixelTime.argtypes = [POINTER(DetObj), c_int, c_int, c_int]
BrillianSe_SetPixelTime.restype = c_int

BrillianSe_SetNumFrames = lib1.BrillianSe_SetNumFrames
BrillianSe_SetNumFrames.argtypes = [POINTER(DetObj), c_int]
BrillianSe_SetNumFrames.restype = c_int

BrillianSe_SetRows = lib1.BrillianSe_SetRows
BrillianSe_SetRows.argtypes = [POINTER(DetObj), c_int]
BrillianSe_SetRows.restype = c_int

BrillianSe_SetColumns = lib1.BrillianSe_SetColumns
BrillianSe_SetColumns.argtypes = [POINTER(DetObj), c_int]
BrillianSe_SetColumns.restype = c_int

BrillianSe_LoadImage = lib1.BrillianSe_LoadImage
BrillianSe_LoadImage.argtypes = [POINTER(DetObj), c_int]
BrillianSe_LoadImage.restype = c_int

BrillianSe_Capture = lib1.BrillianSe_Capture
BrillianSe_Capture.argtypes = [POINTER(DetObj), c_int, POINTER(c_int), POINTER(c_int)]
BrillianSe_Capture.restype = POINTER(DataObj)

BrillianSe_StopCapture = lib1.BrillianSe_StopCapture
BrillianSe_StopCapture.argtypes = [POINTER(DetObj), c_bool]
BrillianSe_StopCapture.restype = c_int

BrillianSe_GetHardwareVersion = lib1.BrillianSe_GetHardwareVersion
BrillianSe_GetHardwareVersion.argtypes = [POINTER(DetObj), c_char_p, c_char_p]
BrillianSe_GetHardwareVersion.restype = c_int

BrillianSe_GetStatus = lib1.BrillianSe_GetStatus
BrillianSe_GetStatus.argtypes = [POINTER(DetObj), POINTER(DetStat)]
BrillianSe_GetStatus.restype = c_int

BrillianSe_GetStatus_Intl = lib1.BrillianSe_GetStatus_Intl
BrillianSe_GetStatus_Intl.argtypes = [POINTER(DetObj), POINTER(DetStatIntl)]
BrillianSe_GetStatus_Intl.restype = c_int

BrillianSe_StatusReport = lib1.BrillianSe_StatusReport
BrillianSe_StatusReport.argtypes = [POINTER(DetObj), c_char_p]
BrillianSe_StatusReport.restype = c_int

BrillianSe_SoftwareMode = lib1.BrillianSe_SoftwareMode
BrillianSe_SoftwareMode.argtypes = [POINTER(DetObj)]
BrillianSe_SoftwareMode.restype = c_int

BrillianSe_HardwareMode = lib1.BrillianSe_HardwareMode
BrillianSe_HardwareMode.argtypes = [POINTER(DetObj)]
BrillianSe_HardwareMode.restype = c_int

BrillianSe_CapturePatternMode = lib1.BrillianSe_CapturePatternMode
BrillianSe_CapturePatternMode.argtypes = [POINTER(DetObj), c_int]
BrillianSe_CapturePatternMode.restype = c_int

BrillianSe_GetParamsRange = lib1.BrillianSe_GetParamsRange
BrillianSe_GetParamsRange.argtypes = [POINTER(DetObj), POINTER(ValdnInfo)]
BrillianSe_GetParamsRange.restype = c_int

BrillianSe_GetParamsRange_Intl = lib1.BrillianSe_GetParamsRange_Intl
BrillianSe_GetParamsRange_Intl.argtypes = [POINTER(DetObj), POINTER(ValdnInfoIntl)]
BrillianSe_GetParamsRange_Intl.restype = c_int

BrillianSe_GetParams = lib1.BrillianSe_GetParams
BrillianSe_GetParams.argtypes = [POINTER(DetObj), POINTER(ParamsInfo)]
BrillianSe_GetParams.restype = c_int

BrillianSe_GetParams_Intl = lib1.BrillianSe_GetParams_Intl
BrillianSe_GetParams_Intl.argtypes = [POINTER(DetObj), POINTER(ParamsInfoIntl)]
BrillianSe_GetParams_Intl.restype = c_int

BrillianSe_GetHVTimeRemained = lib1.BrillianSe_GetHVTimeRemained
BrillianSe_GetHVTimeRemained.argtypes = [POINTER(DetObj), POINTER(c_int)]
BrillianSe_GetHVTimeRemained.restype = c_int

BrillianSe_StopHV = lib1.BrillianSe_StopHV
BrillianSe_StopHV.argtypes = [POINTER(DetObj)]
BrillianSe_StopHV.restype = c_int

BrillianSe_MiniFrame = lib1.BrillianSe_MiniFrame
BrillianSe_MiniFrame.argtypes = [POINTER(DetObj), c_bool]
BrillianSe_MiniFrame.restype = c_int

BrillianSe_MiniTiming = lib1.BrillianSe_MiniTiming
BrillianSe_MiniTiming.argtypes = [POINTER(DetObj), c_bool]
BrillianSe_MiniTiming.restype = c_int

BrillianSe_DefectMode = lib1.BrillianSe_DefectMode
BrillianSe_DefectMode.argtypes = [POINTER(DetObj), c_int]
BrillianSe_DefectMode.restype = c_int

BrillianSe_SetUnixTime = lib1.BrillianSe_SetUnixTime
BrillianSe_SetUnixTime.argtypes = [POINTER(DetObj), c_long]
BrillianSe_SetUnixTime.restype = c_int

BrillianSe_TriggerChbox = lib1.BrillianSe_TriggerChbox
BrillianSe_TriggerChbox.argtypes = [POINTER(DetObj), POINTER(c_int), c_int]
BrillianSe_TriggerChbox.restype = c_int

BrillianSe_TriggerIndicators = lib1.BrillianSe_TriggerIndicators
BrillianSe_TriggerIndicators.argtypes = [POINTER(DetObj), POINTER(c_int), POINTER(POINTER(c_int))]
BrillianSe_TriggerIndicators.restype = c_int

BrillianSe_TriggerStateChange = lib1.BrillianSe_TriggerStateChange
BrillianSe_TriggerStateChange.argtypes = [POINTER(DetObj), c_int, c_int, c_double]
BrillianSe_TriggerStateChange.restype = c_int

BrillianSe_TriggerReadStates = lib1.BrillianSe_TriggerReadStates
BrillianSe_TriggerReadStates.argtypes = [POINTER(DetObj), POINTER(c_int), POINTER(POINTER(c_int))]
BrillianSe_TriggerReadStates.restype = c_int

BrillianSe_TriggerConfig = lib1.BrillianSe_TriggerConfig
BrillianSe_TriggerConfig.argtypes = [POINTER(DetObj), POINTER(c_int), c_int]
BrillianSe_TriggerConfig.restype = c_int

BrillianSe_TriggerWireRole = lib1.BrillianSe_TriggerWireRole
BrillianSe_TriggerWireRole.argtypes = [POINTER(DetObj), c_int, c_int]
BrillianSe_TriggerWireRole.restype = c_int

BrillianSe_TriggerStateInvert = lib1.BrillianSe_TriggerStateInvert
BrillianSe_TriggerStateInvert.argtypes = [POINTER(DetObj), POINTER(c_int), c_int]
BrillianSe_TriggerStateInvert.restype = c_int

BrillianSe_SetGUIState = lib1.BrillianSe_SetGUIState
BrillianSe_SetGUIState.argtypes = [POINTER(DetObj), c_int, c_int]
BrillianSe_SetGUIState.restype = c_int

BrillianSe_SetTriggerMode = lib1.BrillianSe_SetTriggerMode
BrillianSe_SetTriggerMode.argtypes = [POINTER(DetObj), c_int]
BrillianSe_SetTriggerMode.restype = c_int

BrillianSe_GetTriggerMode = lib1.BrillianSe_GetTriggerMode
BrillianSe_GetTriggerMode.argtypes = [POINTER(DetObj), POINTER(c_int)]
BrillianSe_GetTriggerMode.restype = c_int

BrillianSe_SetTriggerWire = lib1.BrillianSe_SetTriggerWire
BrillianSe_SetTriggerWire.argtypes = [POINTER(DetObj), c_bool]
BrillianSe_SetTriggerWire.restype = c_int

BrillianSe_HVRampUp = lib1.BrillianSe_HVRampUp
BrillianSe_HVRampUp.argtypes = [POINTER(DetObj)]
BrillianSe_HVRampUp.restype = c_int

BrillianSe_HVRampDown = lib1.BrillianSe_HVRampDown
BrillianSe_HVRampDown.argtypes = [POINTER(DetObj)]
BrillianSe_HVRampDown.restype = c_int

BrillianSe_ObserverDisconnect = lib1.BrillianSe_ObserverDisconnect
BrillianSe_ObserverDisconnect.argtypes = [POINTER(POINTER(DetObj))]
BrillianSe_ObserverDisconnect.restype = c_int

BrillianSe_Shutdown = lib1.BrillianSe_Shutdown
BrillianSe_Shutdown.argtypes = [POINTER(POINTER(DetObj))]
BrillianSe_Shutdown.restype = c_int

Data_New = lib1.Data_New
Data_New.argtypes = [POINTER(c_ushort), c_int, c_int, c_int]
Data_New.restype = POINTER(DataObj)

Data_Delete = lib1.Data_Delete
Data_Delete.argtypes = [POINTER(POINTER(DataObj))]
Data_Delete.restype = c_int

Data_GetBuffer = lib1.Data_GetBuffer
Data_GetBuffer.argtypes = [POINTER(DataObj)]
Data_GetBuffer.restype = POINTER(c_ushort)

Data_GetFrameSize = lib1.Data_GetFrameSize
Data_GetFrameSize.argtypes = [POINTER(DataObj), POINTER(c_int)]
Data_GetFrameSize.restype = c_int

Data_GetNumFrames = lib1.Data_GetNumFrames
Data_GetNumFrames.argtypes = [POINTER(DataObj), POINTER(c_int)]
Data_GetNumFrames.restype = c_int

Data_GetBufferSize = lib1.Data_GetBufferSize
Data_GetBufferSize.argtypes = [POINTER(DataObj), POINTER(c_longlong)]
Data_GetBufferSize.restype = c_int

Processor_Init = lib1.Processor_Init
Processor_Init.argtypes = None
Processor_Init.restype = POINTER(ProcObj)

Processor_New = lib1.Processor_New
Processor_New.argtypes = [c_int, c_int]
Processor_New.restype = POINTER(ProcObj)

Processor_Delete = lib1.Processor_Delete
Processor_Delete.argtypes = [POINTER(POINTER(ProcObj))]
Processor_Delete.restype = c_int

Processor_SumFrame = lib1.Processor_SumFrame
Processor_SumFrame.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_SumFrame.restype = POINTER(DataObj)

Processor_MeanFrame = lib1.Processor_MeanFrame
Processor_MeanFrame.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_MeanFrame.restype = POINTER(DataObj)

Processor_OffsetCalibration = lib1.Processor_OffsetCalibration
Processor_OffsetCalibration.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_OffsetCalibration.restype = c_int

Processor_CT_OffsetCalibration = lib1.Processor_CT_OffsetCalibration
Processor_CT_OffsetCalibration.argtypes = [POINTER(ProcObj), POINTER(DataObj), POINTER(ROI)]
Processor_CT_OffsetCalibration.restype = c_int

Processor_GainCalibration = lib1.Processor_GainCalibration
Processor_GainCalibration.argtypes = [POINTER(ProcObj), POINTER(DataObj), POINTER(ROI)]
Processor_GainCalibration.restype = c_int

Processor_GainCalibration_Intl = lib1.Processor_GainCalibration_Intl
Processor_GainCalibration_Intl.argtypes = [POINTER(ProcObj), POINTER(DataObj), c_int, POINTER(ROI)]
Processor_GainCalibration_Intl.restype = c_int

Processor_BadPixelMap = lib1.Processor_BadPixelMap
Processor_BadPixelMap.argtypes = [POINTER(ProcObj), POINTER(DataObj), POINTER(ROI)]
Processor_BadPixelMap.restype = c_int

Processor_RTNMap = lib1.Processor_RTNMap
Processor_RTNMap.argtypes = [POINTER(ProcObj), POINTER(DataObj), POINTER(ROI), c_int, c_int]
Processor_RTNMap.restype = c_int

Processor_AddBPMap = lib1.Processor_AddBPMap
Processor_AddBPMap.argtypes = [POINTER(ProcObj), POINTER(DetObj), c_char_p]
Processor_AddBPMap.restype = c_int

Processor_LoadOffsetMap = lib1.Processor_LoadOffsetMap
Processor_LoadOffsetMap.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_LoadOffsetMap.restype = c_int

Processor_LoadGainMap = lib1.Processor_LoadGainMap
Processor_LoadGainMap.argtypes = [POINTER(ProcObj), POINTER(DataObj),POINTER(ROI)]
Processor_LoadGainMap.restype = c_int

Processor_GetOffsetMap = lib1.Processor_GetOffsetMap
Processor_GetOffsetMap.argtypes = [POINTER(ProcObj)]
Processor_GetOffsetMap.restype = POINTER(DataObj)

Processor_GetGainMap = lib1.Processor_GetGainMap
Processor_GetGainMap.argtypes = [POINTER(ProcObj)]
Processor_GetGainMap.restype = POINTER(DataObj)

Processor_GetBadPixelMap = lib1.Processor_GetBadPixelMap
Processor_GetBadPixelMap.argtypes = [POINTER(ProcObj)]
Processor_GetBadPixelMap.restype = POINTER(DataObj)

Processor_GetOffsetRTNMap = lib1.Processor_GetOffsetRTNMap
Processor_GetOffsetRTNMap.argtypes = [POINTER(ProcObj)]
Processor_GetOffsetRTNMap.restype = POINTER(DataObj)

Processor_GetGainRTNMap = lib1.Processor_GetGainRTNMap
Processor_GetGainRTNMap.argtypes = [POINTER(ProcObj)]
Processor_GetGainRTNMap.restype = POINTER(DataObj)

Processor_OffsetCorrection = lib1.Processor_OffsetCorrection
Processor_OffsetCorrection.argtypes = [POINTER(ProcObj), POINTER(DataObj), c_int, c_int, POINTER(c_int)]
Processor_OffsetCorrection.restype = POINTER(DataObj)

Processor_FFC = lib1.Processor_FFC
Processor_FFC.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_FFC.restype = c_int

Processor_FFC_Intl = lib1.Processor_FFC_Intl
Processor_FFC_Intl.argtypes = [POINTER(ProcObj), POINTER(DataObj), c_int, c_int, c_int]
Processor_FFC_Intl.restype = c_int

Processor_BPC = lib1.Processor_BPC
Processor_BPC.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_BPC.restype = c_int

Processor_SetRows = lib1.Processor_SetRows
Processor_SetRows.argtypes = [POINTER(ProcObj), c_int]
Processor_SetRows.restype = c_int

Processor_SetColumns = lib1.Processor_SetColumns
Processor_SetColumns.argtypes = [POINTER(ProcObj), c_int]
Processor_SetColumns.restype = c_int

Processor_CorrectionReady = lib1.Processor_CorrectionReady
Processor_CorrectionReady.argtypes = [POINTER(ProcObj)]
Processor_CorrectionReady.restype = c_int

Processor_DecimateData = lib1.Processor_DecimateData
Processor_DecimateData.argtypes = [POINTER(ProcObj), POINTER(DataObj)]
Processor_DecimateData.restype = POINTER(DataObj)

BrillianSe_GetErrorMessage = lib1.BrillianSe_GetErrorMessage
BrillianSe_GetErrorMessage.argtypes = [c_int]
BrillianSe_GetErrorMessage.restype = c_char_p

BrillianSe_SetVerbosityLevel = lib1.BrillianSe_SetVerbosityLevel
BrillianSe_SetVerbosityLevel.argtypes = [c_int]
BrillianSe_SetVerbosityLevel.restype = c_int

BrillianSe_CloseAllSockets = lib1.BrillianSe_CloseAllSockets
BrillianSe_CloseAllSockets.argtypes = [POINTER(DetObj)]
BrillianSe_CloseAllSockets.restype = c_int

### UTILS ###

def WriteToFile(file_path,data): #this should be used to save a single frame otherwise it only saves the first frame
    frame_size = c_int(0)
    data_buffer = Data_GetBuffer(data)
    Data_GetFrameSize(data, byref(frame_size))
    file_path_bytes = bytes(file_path, 'utf-8')
    fp = c_void_p(fopen(file_path_bytes, b"wb"))
    result = c_size_t(fwrite(data_buffer, c_size_t(1), c_size_t(frame_size.value), fp)) 
    print(f"{result.value} bytes written to {file_path}")
    result = fclose(fp)
    print(f"closing file: {result}")


def LoadFileToDataObj(file_path, rows, cols):

    try:
        with open(file_path, 'rb') as infile:
            data = np.fromfile(infile, dtype=np.uint16)
    except Exception as e:
        print('Error reading file:', e)
        data = None
        return None
    data_object = POINTER(DataObj)()
    data_object = Data_New(data.ctypes.data_as(POINTER(c_ushort)), rows, cols, 1)
    print(data.ctypes.data_as(POINTER(c_ushort)))
    print(f"{len(data)*2} bytes was loaded from {file_path}")
    return data_object

def npArryToDataObj(np_array):
    if np_array.ndim == 3:
        num_images, rows, cols = np_array.shape
    elif np_array.ndim == 2:
        num_images = 1
        rows, cols = np_array.shape
    else:
        return None
    # Create 1D array to store flattened images
    flattened_data = np.empty(num_images * rows * cols, dtype=np.uint16)

   # Loop through each image and flatten
    if num_images == 1:
        flattened_data = np_array.flatten()
    else:
        for i in range(num_images):
    	    # Get the 2D numpy array for this image
            image = np_array[i,:,:]     
    	    # Flatten the 2D array and store in flattened_data
            start_idx = i *  rows * cols
            end_idx = start_idx +  rows * cols
            flattened_data[start_idx:end_idx] = image.flatten()

    print('Flattened data shape:', flattened_data.shape)
    
    data_object = POINTER(DataObj)()
    data_object = Data_New(flattened_data.ctypes.data_as(POINTER(c_ushort)), rows, cols, num_images)
    return data_object
