# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 11:08:46 2025

@author: AXIm Admin
"""

from .brillianse import Brillianse
from .primeBSI import PrimeBSI
from .moment import Moment

def get_detector(name, **kwargs):
    detectors = {
        "brillianse": Brillianse,
        "kinetix": PrimeBSI,
        "moment": Moment,
    }
    try:
        return detectors[name.lower()](**kwargs)
    except KeyError:
        raise ValueError(f"Unknown detector name: {name}")