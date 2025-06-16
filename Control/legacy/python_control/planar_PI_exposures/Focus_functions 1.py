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
from scipy.stats import entropy
from scipy.optimize import minimize


#%%

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

    plt.imshow(img[roi[1]:roi[1]+roi[3],roi[0]:roi[0]+roi[2]])

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

def contrast_measure_absDiff(im):
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


def contrast_measure_deriv(im):
    """ 
    For each pixel, calculate the absolute difference between it and its nearest
    neighbours along the x and y axes, to give G(x,y).
    Then take the sum of the square of these differences, normalized to the number of pixels used

    Based on: 'The autofocusing system of the IMAT neutron camera'. V. Finocchiaro et al
    

    im is the image as a 2d numpy array
    """

    # x partial derivative
    dx = np.diff(im, axis=1)

    # y partial derivative
    dy = np.diff(im, axis=0)

    # calculate contrast measure
    contrast = 0.5*(np.sqrt(np.mean(dx**2)) + np.sqrt(np.mean(dy**2)))
    
    return contrast

def contrast_measure_derivsq(im):
    """ 
    Total variation contrast measure based on the sum of the square of the first derivative
    """

    # x partial derivative
    dx = np.diff(im, axis=1)

    # y partial derivative
    dy = np.diff(im, axis=0)

    # calculate contrast measure
    contrast = 0.5*(np.sqrt(np.mean(dx**2)) + np.sqrt(np.mean(dy**2)))
    
    return contrast

def contrast_measure_TV(im):

    dx = np.diff(im, axis=1)
    dy = np.diff(im, axis=0)

    contrast = np.sum(np.sqrt(dx**2)) + np.sum(np.sqrt(dy**2))

def contrast_measure_entropy(im):
    """ 
    For each pixel, calculate the absolute difference between it and its nearest
    neighbours along the x and y axes, to give G(x,y).
    Then take the sum of the square of these differences, normalized to the number of pixels used

    Based on: 'The autofocusing system of the IMAT neutron camera'. V. Finocchiaro et al
    

    im is the image as a 2d numpy array
    """

    im = im - np.min(im)
    im = im/np.max(im)
    im = np.round(im*255).astype(int)

    hist = np.histogram(im, bins=256, range=(0,255))[0]
    hist = hist/np.sum(hist)

    # calculate contrast measure
    contrast = entropy(hist, base=2)
   

    return contrast


def contrast_measure_squaredLaplacian(im):
    """ 
    For each pixel, calculate the absolute difference between it and its nearest
    neighbours along the x and y axes, to give G(x,y).
    Then take the sum of the square of these differences, normalized to the number of pixels used

    Based on: 'The autofocusing system of the IMAT neutron camera'. V. Finocchiaro et al
    

    im is the image as a 2d numpy array
    """

    # kernel for laplacian
    kernel = np.array([[0,-1,0],[-1,4,-1],[0,-1,0]])

    # apply laplacian
    im = cv2.filter2D(im, -1, kernel, borderType=cv2.BORDER_REFLECT)

    # calculate contrast measure as normalised sum of squared laplacian
    contrast = np.sum(im**2)/im.size
   

    return contrast

def contrast_measure_variance(im):

    contrast = np.var(im)/np.mean(im)
    

    return contrast


def get_vis_oneCoor_contrast(ims, positions, coor, method, window_size=(100,100)):
    """
    Uses contrast measure to calculate visibility across a stack of images.
    Interrogates a region surrounding the specified coordinate defined by window_size.
    Fits gaussian to visibility values to estimate where peak visibility occurs.

    ims is a stack of images as a numpy array
    coor is the coordinate to extract the visibility values from (centre)
    window_size is the size of the window as a tuple (x,y)
    """

    # extract visibility values
    vis = np.zeros((ims.shape[0]))
    for i in range(ims.shape[0]):
        im = ims[i,int(coor[1]-window_size[1]/2):int(coor[1]+window_size[1]/2),int(coor[0]-window_size[0]/2):int(coor[0]+window_size[0]/2)]
        
        if method == 'deriv':
            vis[i] = contrast_measure_deriv(im)
        elif method == 'entropy':
            vis[i] = contrast_measure_entropy(im)
        elif method == 'absDiff':
            vis[i] = contrast_measure_absDiff(im)
        elif method == 'laplacian':
            vis[i] = contrast_measure_squaredLaplacian(im)
        elif method == 'derivsq':
            vis[i] = contrast_measure_derivsq(im)
        elif method == 'variance':
            vis[i] = contrast_measure_variance(im)
        elif method == 'TV':
            vis[i] = contrast_measure_TV(im)
        else:
            print('Invalid method')
            return

    # fit gaussian to visibility values
    # define gaussian function
    def gauss(x, a, x0, sigma, b):
        return a*np.exp(-(x-x0)**2/(2*sigma**2)) + b
    
    bounds = ([-np.inf,np.min(positions),0,-np.inf],[np.inf,np.max(positions),np.inf,np.inf])

    vis = vis - np.min(vis)
    vis = vis/np.max(vis)

    # fit gaussian
    try:
        popt, pcov = curve_fit(gauss, positions, vis, p0=[1,np.mean(positions),1,0], bounds=bounds,loss='soft_l1')
    except:
        popt = [np.nan,np.nan,np.nan,np.nan]
        print('Fit failed on coordinate ' + str(coor))

    # r-squared value for gaussian fit
    residuals = vis - gauss(positions, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((vis-np.mean(vis))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # find best focus
    x0 = popt[1]

    if r_squared > 0.95:
        # plot visibility
        plt.plot(positions,vis,'x')
        x = np.linspace(np.min(positions),np.max(positions),10000)
        fitt = gauss(x, *popt)
        plt.plot(x,fitt)
        plt.xlabel('Stage Position [mm]')
        plt.ylabel('Visibility')

    # show images
    #for i in range(ims.shape[0]):
    #    plt.figure()
    #    plt.imshow(ims[i,int(coor[1]-window_size[1]/2):int(coor[1]+window_size[1]/2),int(coor[0]-window_size[0]/2):int(coor[0]+window_size[0]/2)])

    return vis, x0, r_squared

def getFocus_stack(ims, positions, coors, px_size, method, window_size=(100,100)):
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

    # r-squared values for gaussian fit
    r2 = np.zeros((coors.shape[0],1))

    # loop through coordinates
    for i in range(coors.shape[0]):

        # if i is multiple of 50, print progress
        if i%50 == 0:
            print('Processing coordinate ' + str(i) + ' of ' + str(coors.shape[0]))

        _,x0, r = get_vis_oneCoor_contrast(ims, positions, coors[i,:], method, window_size)
        if r > 0.98:
            best_focus[i] = x0
            r2[i] = r
        else:
            best_focus[i] = np.nan
            r2[i] = np.nan


    # convert to a set of 3d coordinates in a 2d array
    coors = np.hstack((coors,best_focus))

    # remove any rows with nan values 
    coors = coors[~np.isnan(coors).any(axis=1)]
    r2 = r2[~np.isnan(r2)]

    # convert pixel coordinates to mm (focus should already be in mm)
    coors[:,0] = coors[:,0]*px_size/1000
    coors[:,1] = coors[:,1]*px_size/1000

    return coors, r2


def fit_plane(coors):
    """
    A function to fit a plane to a set of 3d coordinates and return the fit.
    Will also make an estimate of the number of rotations required to align the plane
    based on the Thorlabs KM200PM/M kinematic mount. Tests for outliers based on residuals
    and removes them.

    coors is a 2d array of coordinates of form [[x1,y1,z1],[x2,y2,z2],...],
    where x and y are coordinates on the detector plane in mm, and z is the focus position in mm.
    """

    # function for plane fit
    def plane(xy, a, b, c):
        x, y = xy
        return a*x + b*y + c

    # fit a plane to the points
    popt, pcov = curve_fit(plane, (coors[:,0], coors[:,1]), coors[:,2], method='trf', loss='soft_l1')

    # print solution
    print("solution:")
    print("%f x + %f y + %f = z" % (popt[0], popt[1], popt[2]))

    # get r^2 value
    residuals = coors[:,2] - plane((coors[:,0], coors[:,1]), *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((coors[:,2]-np.mean(coors[:,2]))**2)
    r_squared = 1 - (ss_res / ss_tot)
    print("fit r^2 value: %f" % r_squared)

    # convert to angles along x and y axes
    x_angle = np.arctan(popt[0])
    y_angle = np.arctan(popt[1])
    # in degrees
    print("x angle: %f deg, y angle: %f deg" % (x_angle*180/np.pi, y_angle*180/np.pi))

    # each rotation of Thorlabs KM200PM/M kinematic mount is 5 mrad
    # use clockwise as positive
    # convert to number of rotations
    rot = 0.005
    x_rot = x_angle/rot*16667
    y_rot = y_angle/rot*16667

    if x_rot > 0:
        x_direction = 'anticlockwise'
    else:
        x_direction = 'clockwise'

    if y_rot > 0:
        y_direction = 'anticlockwise'
    else:
        y_direction = 'clockwise'

    print("Rotate top thumbscrew %s: %f \nRotate bottom thumbscrew %s: %f" % (x_direction, np.abs(x_rot), y_direction, np.abs(y_rot)))

    # average focus position
    print("Average focus position: %f" % np.median(coors[:,2]))

    return popt 

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

fileLoc = r'D:\23_12_13\3_tilt_correction_40kv_1p2um\attempt_13_27000_m57000'

ims = loadIms(fileLoc)

# remove all outliers (outliers due to e.g. direct hits vastly
# affect the contrast-based 'focus quality' metric and so should be removed)
# this may not always be required
#for i in range(ims.shape[0]):
#    ims[i,:,:] = remove_outliers(ims[i,:,:], threshold=50, radius=9)

#%%
# choose roi
roi = select_roi(ims[0,:,:])

#plt.imshow(ims[0,roi[1]:roi[1]+roi[3],roi[0]:roi[0]+roi[2]])


# camera positions in units mm
positions = np.linspace(40.358,40.374,ims.shape[0])

grid, roi = get_grid_points(roi, (50,50))

#%% Finding plane of scintillator and estimating corrections

# method options are 'contrast', 'deriv', 'derivsq', 'entropy', 'laplacian'

# for current setup (thorlabs mvl lens with 5mm spacer), px_size = 15.1 um
focus_coors, r2 = getFocus_stack(ims, positions, grid, 0.65, 'derivsq', window_size=(200,200))

#%
fit = fit_plane(focus_coors)
plot_plane_plotly(fit,focus_coors)
#print(np.median(focus_coors[:,2]))

#%% Once pitch and yaw are optimised, can run indiviudal point scan
# to find position of best z-focus

#vis, x0, r_sq = get_vis_oneCoor_contrast(ims, positions, np.array((int(np.shape(ims)[0]/2),int(np.shape(ims)[1]/2))), 'deriv', window_size=(100,100))
