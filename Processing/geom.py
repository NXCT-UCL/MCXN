# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:38:57 2024

@author: ReconMCXN
"""
from cil.processors import Slicer


slice_idx = 200
dslice = 200

roi = {'vertical':(slice_idx-dslice,slice_idx+dslice,1)}
processor = Slicer(roi)
processor.set_input(Acq_data)
Acq_data2 = processor.get_output()

outFolder = os.path.join(checkFolder, 'geom')
os.makedirs(outFolder, exist_ok=True)

angles=np.linspace(0, angular_range, num_proj+1)[0:-1]

#np.round(np.linspace(0.0,0.03,31),5)

rot_theta_vec = np.round(np.linspace(-0.01,0.01,11),5)
rot_phi_vec = [-0.003]
cor_vec = [-0.05183317]
Z_pos_vec =[4.0769]
x_pos_vec = [0]
Z2_vec = [64.5785-4.0769]

ii = 0

for Z2_pos in Z2_vec:
    for x_pos in x_pos_vec:
        for Z_pos in Z_pos_vec:
            for rot_theta in rot_theta_vec:
                for rot_phi in rot_phi_vec:
                    for CoR in cor_vec:
                    
                        M = (Z2_pos+Z_pos)/Z_pos
                        #CoR = np.round(0.019*57.5/3/M,5) #if changing z pos, adjust CoR from known at known Z
                        
                        Acq_data2.geometry.config.system.rotation_axis.position[0] = CoR
                        Acq_data2.geometry.config.system.rotation_axis.direction[1] = rot_theta
                        Acq_data2.geometry.config.system.rotation_axis.direction[0] = rot_phi
                        Acq_data2.geometry.config.system.detector.position[1] = Z2_pos
                        Acq_data2.geometry.config.system.source.position[1] = -Z_pos
                        Acq_data2.geometry.config.system.detector.position[0] = x_pos
                        
                        ig = Acq_data2.geometry.get_ImageGeometry()
        
                        ig.voxel_num_x = 3000
                        ig.voxel_num_y = 3000
                        ig.voxel_num_z = 1
                            
                        ig.center_z = (-ly/2+slice_idx)*ig.voxel_size_z
                        
                        #show_geometry(Acq_data2.geometry)
                        
                        print('Recon...')
                        fdk =  FDK(Acq_data2, ig)
                        recon = fdk.run(verbose=0)
                        
                        ##
                        cent_slice = Image.fromarray(recon.as_array())
                        cent_slice.save(os.path.join(outFolder, f'{ii}_CoR_{CoR}_theta_{rot_theta}_phi_{rot_phi}_Z_{Z_pos}_Z2_{Z2_pos}_X_{x_pos}.tif'), format="TIFF", tile=True)
                        
                        ii = ii+1
    

