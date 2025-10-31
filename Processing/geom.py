# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:38:57 2024

@author: ReconMCXN
"""
from cil.processors import Slicer


slice_idx = 920/2
dslice = 200
#slice_idx2 = 0

roi = {'vertical':(slice_idx-dslice,slice_idx+dslice,1)}
processor = Slicer(roi)
processor.set_input(Acq_data)
Acq_data2 = processor.get_output()

#%%

outFolder = os.path.join(checkFolder, 'geom' + str(len(next(os.walk(checkFolder))[1])+1))
os.makedirs(outFolder, exist_ok=True)

angles=np.linspace(0, angular_range, num_proj+1)[0:-1]

#np.round(np.linspace(0.0,0.03,31),5)

rot_theta_vec = [0] #np.round(np.linspace(-0.09,-0.05,17),5)
rot_phi_vec = [0] #np.round(np.linspace(-0.015,-0.025,11),5)
cor_vec = np.round(np.linspace(-0.1,0.1,5),4)
Z_pos_vec = np.round([Z_so],3)
x_pos_vec = [0]
Z2_vec = np.round([Z_sd-Z_so],3)
rot_dir_vec = [1]

ii = 0

for Z2_pos in Z2_vec:
    for Z_pos in Z_pos_vec:
        for rot_theta in rot_theta_vec:
            for rot_phi in rot_phi_vec:
                for CoR in cor_vec:
                    for rot_dir in rot_dir_vec:
                        #Z_pos = np.round((Z2_pos+Z_pos)/(24/11.9),3)
                        # M = (Z2_pos+Z_pos)/Z_pos
                        # CoR = np.round(cor_vec[0]*60/6/M,5) #if changing z pos, adjust CoR from known at known Z
                        
                        Acq_data2.geometry.config.system.rotation_axis.position[0] = CoR
                        Acq_data2.geometry.config.system.rotation_axis.direction[1] = rot_theta
                        Acq_data2.geometry.config.system.rotation_axis.direction[0] = rot_phi
                        Acq_data2.geometry.config.system.detector.position[1] = Z2_pos
                        Acq_data2.geometry.config.system.source.position[1] = -Z_pos
                        Acq_data2.geometry.set_angles(angles = rot_dir*angles)
                        
                        ig = Acq_data2.geometry.get_ImageGeometry()
        
                        ig.voxel_num_x = lx
                        ig.voxel_num_y = lx
                        ig.voxel_num_z = 1
                            
                        #ig.center_z = (-ly/2+slice_idx)*ig.voxel_size_z
                        #ig.center_z = (-slice_idx2)*ig.voxel_size_z
                        
                        show_geometry(Acq_data2.geometry)
                        
                        print('Recon...')
                        fdk =  FDK(Acq_data2, ig)
                        recon = fdk.run(verbose=0)
                        
                        ##
                        cent_slice = Image.fromarray(recon.as_array())
                        cent_slice.save(os.path.join(outFolder, f'{ii}_CoR_{CoR}_theta_{rot_theta}_phi_{rot_phi}_Z_{Z_pos}_Z2_{Z2_pos}_dir_{rot_dir}.tif'), format="TIFF", tile=True)
                        
                        ii = ii+1
    

