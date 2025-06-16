"""
A set of fucntions to make the focusing of lens-coupled scintillator detectors a lot easier.
In principle, a scan of the scintillator to lens distance should be performed,
which is then analysed to provide an estimate of the best focus position and adjustments
required to complete the pitch and yaw alignment of the scintillator.
"""

#%%

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from PIL import Image
import cv2
import os
from natsort import natsorted
from scipy.optimize import curve_fit
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

def loadIms(fileLoc):
    """ 
    A function to load images from a folder into a stack.

    # fileLoc is the location of the folder containing the images
    # returns a stack of images as a numpy array
    """

    # load ans sort file names
    files = natsorted(os.listdir(fileLoc))

    for i in range(len(files)):
        im = Image.open(fileLoc + '\\' + files[i])

        if i == 0:
            ims = np.zeros((len(files),im.size[1],im.size[0]))
        ims[i,:,:] = np.array(im)

    return ims

def select_roi(img):
    """
    A function allowing the interactive selection of a roi in the image to
    use for analysing focus.

    img is an input image as a 2d numpy array
    """
    cv2.namedWindow("ROI selector", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ROI selector", 500, 500)
    roi = cv2.selectROI("ROI selector", img/np.max(img), fromCenter=False)
    cv2.destroyAllWindows()

    return roi


def remove_outliers(im, threshold=50, radius=3):
    """
    A function to remove outliers (e.g. due to direct hits) from an image. 
    Based approximately on ImageJ's outlier removal filter.

    im is the image as a 2d numpy array
    threshold is the threshold for the outlier removal, values more than
    this distance from the region median are replaced
    radius is the radius of the median filter
    """

    # apply median filter
    im_filt = ndimage.median_filter(im, radius)

    # find outliers
    outliers = ((im > im_filt + threshold) | (im < im_filt - threshold))

    # replace outliers with median filtered value
    im[outliers] = im_filt[outliers]

    return im

def get_grid_points(roi, grid_spacing):
    """
    A function to return a set of evenly spaced grid points to evaluate
    focus at. Note it is likely that actual roi will be changed to accomodate
    the requested grid spacing.

    roi is the region of interest as a tuple (x,y,w,h)
    grid_spacing is the spacing of the grid as a tuple (x,y)
    """

    roi = np.array(roi)

    # if roi is not compatible with grid_space, adjust roi
    if roi[2]%grid_spacing[0] != 0:
        roi[2] = roi[2] - roi[2]%grid_spacing[0]
    if roi[3]%grid_spacing[1] != 0:
        roi[3] = roi[3] - roi[3]%grid_spacing[1]
    

    # output grid is a numpy array of shape (n,2)
    # where n is the number of grid points
    # and the columns are the x and y coordinates of the grid points
    grid = np.mgrid[roi[1]:roi[1]+roi[3]:grid_spacing[1],roi[0]:roi[0]+roi[2]:grid_spacing[0]]
    grid = grid.reshape(2,-1).T

    return grid, roi

def contrast_measure(im):
    """ 
    For each pixel, calculate the absolute difference between it and its nearest
    neighbours along the x and y axes, to give G(x,y).
    Then take the sum of the square of these differences, normalized to the number of pixels used

    Based on: 'The autofocusing system of the IMAT neutron camera'. V. Finocchiaro et al
    

    im is the image as a 2d numpy array
    """

    # empty array to store G(x,y)
    G = np.zeros(im.shape)

    # pad im by reflecting the edges
    im = np.pad(im, 1, mode='reflect')

    # calculate G(x,y)
    for i in range(1,im.shape[0]-1):
        for j in range(1,im.shape[1]-1):
            G[i-1,j-1] = abs(im[i,j]-im[i-1,j]) + abs(im[i,j]-im[i+1,j]) + abs(im[i,j]-im[i,j-1]) + abs(im[i,j]-im[i,j+1])

    # calculate contrast measure
    contrast = np.sum(G**2)/im.size

    return contrast

def get_vis_oneCoor_contrast(ims, positions, coor, window_size=(100,100)):
    """
    Uses contrast measure to calculate visibility across a stack of images.
    Interrogates a region surrounding the specified coordinate defined by window_size.
    Fits gaussian to visibility values to estimate where peak visibility occurs.

    ims is a stack of images as a numpy array
    coor is the coordinate to extract the visibility values from (centre)
    window_size is the size of the window as a tuple (x,y)
    """
    
    print(coor)

    # extract visibility values
    vis = np.zeros((ims.shape[0]))
    for i in range(ims.shape[0]):
        vis[i] = contrast_measure(ims[i,int(coor[1]-window_size[1]/2):int(coor[1]+window_size[1]/2),int(coor[0]-window_size[0]/2):int(coor[0]+window_size[0]/2)])

    # fit gaussian to visibility values
    # define gaussian function
    def gauss(x, a, x0, sigma, b):
        return a*np.exp(-(x-x0)**2/(2*sigma**2)) + b
    
    # fit gaussian
    try:
        popt, pcov = curve_fit(gauss, positions, vis, p0=[1,np.mean(positions),1,0])
    except:
        popt = [np.nan,np.nan,np.nan,np.nan]
        print('Fit failed on coordinate ' + str(coor))

    # find best focus
    x0 = popt[1]

    # plot visibility
    plt.plot(positions,vis/np.max(vis))
    x = np.linspace(np.min(positions),np.max(positions),10000)
    fitt = gauss(x, *popt)
    plt.plot(x,fitt/np.max(fitt))
    plt.xlabel('Stage Position [mm]')
    plt.ylabel('Visibility')

    # show images
    #for i in range(ims.shape[0]):
    #    plt.figure()
    #    plt.imshow(ims[i,int(coor[1]-window_size[1]/2):int(coor[1]+window_size[1]/2),int(coor[0]-window_size[0]/2):int(coor[0]+window_size[0]/2)])

    return vis, x0

def getFocus_stack(ims, positions, coors, px_size, window_size=(100,100)):
    """
    A function to extract best focus from a stack of images at a set of stated coordinates
    with a given window size. Uses the contrast measure and gaussian fitting to estimate best focus.
    
    ims is a stack of images as a numpy array
    coors is a 2d array of coordinates of form [[x1,y1],[x2,y2],...]
    pixel size is the pixel size in um
    window_size is the size of the window as a tuple (x,y)
    """

    # create array to store best focus position for each coordinate
    best_focus = np.zeros((coors.shape[0],1))

    # loop through coordinates
    for i in range(coors.shape[0]):
        _,best_focus[i] = get_vis_oneCoor_contrast(ims, positions, coors[i,:], window_size)
    
    # convert to a set of 3d coordinates in a 2d array
    coors = np.hstack((coors,best_focus))

    # remove any rows with nan values
    coors = coors[~np.isnan(coors).any(axis=1)]

    # convert pixel coordinates to mm (focus should already be in mm)
    coors[:,0] = coors[:,0]*px_size/1000
    coors[:,1] = coors[:,1]*px_size/1000

    return coors

def fit_plane(coors):
    """
    A function to fit a plane to a set of 3d coordinates and return the fit.
    Will also make an estimate of the number of rotations required to align the plane
    based on the Thorlabs KM200PM/M kinematic mount. Tests for outliers based on residuals
    and removes them.

    coors is a 2d array of coordinates of form [[x1,y1,z1],[x2,y2,z2],...],
    where x and y are coordinates on the detector plane in mm, and z is the focus position in mm.
    """

    # fit a plane to the points
    tmp_A = []
    tmp_b = []

    for i in range(len(coors)):
        tmp_A.append([coors[i,0], coors[i,1], 1])
        tmp_b.append(coors[i,2])

    b = np.matrix(tmp_b).T
    A = np.matrix(tmp_A)

    fit = (A.T * A).I * A.T * b

    # identify outliers
    fit = np.array(fit).reshape(-1)
    residuals = np.abs(np.dot(A,fit) - b)
    outliers = residuals > np.std(residuals)*4

    # warn if outliers are present
    if np.sum(outliers) > 0:
        print("Warning: outliers present in data and were removed")
        print("Number of outliers: %i" % np.sum(outliers))

    # remove outliers and repeat fit
    b = np.delete(b, np.where(outliers), axis=0)
    A = np.delete(A, np.where(outliers), axis=0)

    fit = (A.T * A).I * A.T * b

    # print solution
    print("solution:")
    print("%f x + %f y + %f = z" % (fit[0], fit[1], fit[2]))

    # convert to angles along x and y axes
    x_angle = np.arctan(fit[0])
    y_angle = np.arctan(fit[1])
    # in degrees
    print("x angle: %f deg, y angle: %f deg" % (x_angle*180/np.pi, y_angle*180/np.pi))

    # each rotation of Thorlabs KM200PM/M kinematic mount is 5 mrad
    # use clockwise as positive
    # convert to number of rotations
    rot = 0.005
    x_rot = x_angle/rot
    y_rot = y_angle/rot

    print("x rotations: %f, y rotations: %f" % (x_rot, y_rot))

    return fit

def plot_plane_plotly(fit,coors):
    """
    A function to plot a plane fit to a set of 3d coordinates using plotly. As 
    default, this will be plotted in a browser window (adjust during imports).

    fit is the plane fit as a 1d numpy array of form [a,b,c] where a,b,c are the
    coefficients of the plane equation ax + by + c = z
    coors is a 2d array of coordinates of form [[x1,y1,z1],[x2,y2,z2],...]
    """
    
    fit = np.array(fit).reshape(-1)

    # plot the points
    fig = go.Figure(data=[go.Scatter3d(
        x=coors[:,0],
        y=coors[:,1],
        z=coors[:,2],
        mode='markers',
        marker=dict(
            size=5,
            color='red',
            opacity=0.8
        )
    )])
    
    # plot plane
    x = np.linspace(np.min(coors[:,0]),np.max(coors[:,0]),100)
    y = np.linspace(np.min(coors[:,1]),np.max(coors[:,1]),100)
    X, Y = np.meshgrid(x, y)
    Z = fit[0]*X + fit[1]*Y + fit[2]

    fig.add_trace(go.Surface(x=X, y=Y, z=Z, opacity=0.5))

    fig.update_layout(scene=dict(
        xaxis_title='Bottom [mm]',
        yaxis_title='Side [mm]',
        zaxis_title='Z [mm]'
    ))
    
    return fig

#%% Initialising everything 

fileLoc = r'D:\23_12_05_harry\folder\focusTest'

ims = loadIms(fileLoc)

# remove all outliers (outliers due to e.g. direct hits vastly
# affect the contrast-based 'focus quality' metric and so should be removed)
# this may not always be required
#for i in range(ims.shape[0]):
#    ims[i,:,:] = remove_outliers(ims[i,:,:], threshold=50, radius=9)

#%%
# choose roi
roi = select_roi(ims[0,:,:])

plt.imshow(ims[0,roi[1]:roi[1]+roi[3],roi[0]:roi[0]+roi[2]])


# camera positions in units mm
#positions = np.linspace(2,6,ims.shape[0])

grid, roi = get_grid_points(roi, (100,100))

#%% Finding plane of scintillator and estimating corrections

# for current setup (thorlabs mvl lens with 5mm spacer), px_size = 15.1 um
px_size = 15.1
focus_coors = getFocus_stack(ims, positions, grid, px_size, window_size=(100,100))
fit = fit_plane(focus_coors)
plot_plane_plotly(fit,focus_coors)
#print(np.median(focus_coors[:,2]))
