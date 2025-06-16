from ctypes import *


class DetObj(Structure):
    pass

DetObj._fields_ = []


class DataObj(Structure):
    pass

DataObj._fileds_ = []


class ProcObj(Structure):
    pass

ProcObj._fields_ = []


class DetStatIntl(Structure):
    pass

DetStatIntl._fields_ = []


class ValdnInfoIntl(Structure):
    pass

ValdnInfoIntl._fields_ = []


class ParamsInfoIntl(Structure):
    pass

ParamsInfoIntl._fields_ = []


class DetStat(Structure):
    pass

DetStat._fields_ = [
    ('capture_progress', c_bool),
    ('main_connection_exist', c_bool),
    ('num_connections', c_int),
    ('temp', c_double),
    ('humidity', c_double)
]


class ValdnInfo(Structure):
    pass

ValdnInfo._fields_ = [
    ('num_frames_max', c_int),
    ('num_frames_min', c_int),
    ('frame_period_min', c_double),
    ('frame_period_max', c_double),
    ('integ_time_min', c_double),
    ('integ_time_max', c_double)
]


class ParamsInfo(Structure):
    pass

ParamsInfo._fields_ = [
    ('integration_time', c_double),
    ('frame_period', c_double),
    ('cds_offset', c_int),
    ('cds_raw', c_bool),
    ('mini_frame_mode', c_bool),
    ('mini_timing_mode', c_bool)
]


class ROI(Structure):
    pass

ROI._fields_ = [
    ('x', c_ushort),
    ('y', c_ushort),
    ('width', c_ushort),
    ('height', c_ushort)
    ]

