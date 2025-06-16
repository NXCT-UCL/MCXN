# -*- coding: utf-8 -*-
"""
Created on 16 July 2020
Adapted 18 Sept 2023

@author: Michela Esposito
adapted: Adam Doherty for Kinetix detector

"""
#from pycromanager import Bridge, Acquisition
import pycromanager as pycro
import numpy as np
import argparse
import scan_functions as SF

#import tools as tools

#parsing of command line options
parser = argparse.ArgumentParser(description = 'Grabs N flat frames and saves them in a TIFF stacks.')
parser.add_argument('path', help='Absolute path where TIFF stack will be saved in a folder name /path/Flat_M/. No quotes!')
parser.add_argument('nFrames', type=int, help='Number of frames to be acquired.')
args = parser.parse_args()

path = args.path
nFrames = args.nFrames

#################################################
##################set up#########################
#################################################

#establish communication with micro-manager
core = pycro.Core()
#################################################

exposure = core.get_exposure() #ms
fname ='Im_'+str(exposure)+'ms'

#tools.shutter('open')
#time.sleep(2)#second


def hook_fn(event, bridge, event_queue):
	#tools.put_theta_increment(increment)
	print('post_hardware_hook')
	return event

if __name__ == '__main__':

    print('Saving '+str(nFrames)+' frames with '+str(exposure)+' ms exposure in ' +path+'\n')
    SF.journal(path,'Saving '+str(nFrames)+' frames with '+str(exposure)+' ms exposure in ' +path+'\n')

    with pycro.Acquisition(path, fname) as acq:
	#create one event for the image at each z-slic
        events = []
        for index, proj in enumerate(np.arange(start=0, stop=nFrames, step=1)):
            evt = {
				#'axes' is required. It is used by the image viewer and data storage to
				#identify the acquired image
				'axes': {'theta': index},

				#the 'z' field provides the z position in µm
				'theta': proj}
			#events.append(evt)

            acq.acquire(evt)


#tools.shutter('close')



