# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 16:34:10 2024

@author: ReconMCXN
"""

import os
import re
from PIL import Image
import numpy as np
from multiprocessing import Pool, cpu_count
import matplotlib.pyplot as plt
from cil.framework import AcquisitionGeometry, AcquisitionData, DataContainer
from cil.utilities.display import show_geometry, show2D
from cil.recon import FDK
from cil.io import TIFFStackReader, TIFFWriter
from cil.processors import CentreOfRotationCorrector, Slicer, RingRemover, PaganinProcessor, Padder
import time
from scipy.ndimage import affine_transform
from multiprocessing import Pool

# Setup folder paths and constants
sampleFolder = r'D:\25_04_07\8_MuscleGFPD9_40kv_1p2um'
inFolder = os.path.join(sampleFolder, 'phase')
outFolder = os.path.join(sampleFolder, 'recon')
checkFolder = os.path.join(outFolder, 'checkpoints')
os.makedirs(outFolder, exist_ok=True)
os.makedirs(checkFolder, exist_ok=True)

# Constants for the reconstruction
Z_so = 4.0769
Z_sd = 64.5785
lx = 4000
ly = 4000
angular_range = 360
num_proj = 4000
px = 8e-3
rot_dir = -1 # moment -1, bsi +1

# Get the list of TIFF files
file_list = [f for f in os.listdir(inFolder) if f.endswith('.tif')]

# Extract numbers from filenames and sort numerically
def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

sorted_files = sorted(file_list, key=extract_number)

# Function to load a single image (used by multiprocessing)
def load_image(file_name):
    file_path = os.path.join(inFolder, file_name)
    image = Image.open(file_path)
    return np.array(image)

# Apply RingRemover to each chunk
def apply_ring_remover(sino):
    ag_mini = AcquisitionGeometry.create_Cone2D(source_position = [0,0], detector_position = [0,0])
    ag_mini.set_angles(np.linspace(0,360,num_proj))
    ag_mini.set_panel(num_pixels=lx, pixel_size=px)
    Acq_data_mini = AcquisitionData(sino, geometry=ag_mini, deep_copy=False)
    processor = RingRemover(decNum=5, wname='db5', sigma=5, info=True)
    processor.set_input(Acq_data_mini)
    return processor.get_output().as_array()

# Use multiprocessing to load images
if __name__ == '__main__':
    # Limit the number of processes to avoid memory overload
    num_workers = min(cpu_count(), len(sorted_files))

    with Pool(processes=num_workers) as pool:
        data = pool.map(load_image, sorted_files)

    # Convert the list of images to a 3D NumPy array
    data = np.stack(data, axis=0)
    data = data[0:num_proj, :, :]
    print(f"Loaded {len(data)} images into the stack.")
    
    # Process data further as needed
    data = np.flip(data, 0)
    
    # data = data.transpose(1, 0, 2)
    # # Apply RingRemover in parallel
    # print('Removing Rings...')
    # num_workers = min(cpu_count(), data.shape[0])  # Limit to available CPUs or rows
    # with Pool(processes=num_workers) as pool:
    #     data = pool.map(apply_ring_remover, data)
    
    # # Convert processed sinograms back to a NumPy array
    # data = np.array(data).transpose(1, 0, 2)  # Back to original shape
    
    ag = AcquisitionGeometry.create_Cone3D(source_position=[0, -Z_so, 0],
                                            detector_position=[0, Z_sd - Z_so, 0],
                                            units='mm').set_panel(num_pixels=[lx, ly], pixel_size=px)\
        .set_angles(angles=rot_dir*np.linspace(0,angular_range,num_proj+1)[0:-1])
    Acq_data = AcquisitionData(data, geometry=ag, deep_copy=True)
    del data

    print('Padding...')
    roi = {'horizontal':(40,-40)}
    processor = Slicer(roi)
    processor.set_input(Acq_data)
    Acq_data = processor.get_output()
    processor = Padder.edge(pad_width={'horizontal':(440,440)})
    processor.set_input(Acq_data)
    Acq_data = processor.get_output()
    
    print('Finding CoR...')
    # Acq_data = CentreOfRotationCorrector.image_sharpness()(Acq_data)
    # rot_theta = 0.009
    # Acq_data.geometry.config.system.rotation_axis.direction[1] = rot_theta
    # rot_phi = -0.003
    # Acq_data.geometry.config.system.rotation_axis.direction[0] = rot_phi
    CoR = -0.05183317
    Acq_data.geometry.config.system.rotation_axis.position[0] = CoR
    print(f'COR = {Acq_data.geometry.config.system.rotation_axis.position[0]}')

    ig = Acq_data.geometry.get_ImageGeometry()
    
    ig.voxel_num_x = lx
    ig.voxel_num_y = lx
    ig.voxel_num_z = ly
    
    print('Recon...')
    fdk =  FDK(Acq_data, ig)
    recon = fdk.run()
    
    ##
    TIFFWriter(data=recon, file_name=os.path.join(outFolder, "slice"), compression='uint16').write()
    
    




