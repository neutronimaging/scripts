import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def mad(x, th = 1) :
    '''Computes the median absolute deviation
        
        Parameters:
        - x : A 3D data array with N slices arranged as [N,x,y] 
        - th : Regularization parameter to set a lower limit on the weights. Default th=1, to avoid 1/0.
        
        Returns the MAD per voxel
    '''
    
    m=np.median(x,axis=0)
    ma = np.abs(x - m)
    ma[ma<th] = th
    
    return ma

def weighted_avg(x,w) :
    '''Computes a weighted average
        
        Parameters:
        - x : A 3D data array with N slices arranged as [N,x,y] 
        - w : Weight array
        
        Returns the weighted average
    '''
    sw=w.sum(axis=0)
    a = np.sum(x*w,axis=0)/(sw)
    
    return a

def reduce_measurements(x,th=1) :
    '''Reduces repeated measurements by computing a weighted average based on the MAD
        
        Parameters:
        - x : A 3D data array with N slices arranged as [N,x,y] 
        - th : Regularization parameter to set a lower limit on the weights. Default th=1, to avoid 1/0.
        
        Returns the reduced data array
    '''
    
    ma = mad(x,th)
    w = 1/ma
    a = weighted_avg(x,w)
    
    return a

def reduce_repeated_measurements(x, Nrepeats, th=1) :
    '''Reduces repeated measurements by computing a weighted average based on the MAD
        
        Parameters:
        - x : A 3D data array with N slices arranged as [N,x,y] 
        - Nrepeats : Number of repeated measurements per unique measurement
        - th : Regularization parameter to set a lower limit on the weights. Default th=1, to avoid 1/0.
        
        Returns the reduced data array
    '''
    
    Nunique = x.shape[0]//Nrepeats
    x_reduced = np.zeros((Nunique, x.shape[1], x.shape[2]))
    
    for i in range(Nunique) :
        x_subset = x[i*Nrepeats:(i+1)*Nrepeats,:,:]
        x_reduced[i,:,:] = reduce_measurements(x_subset, th)
    
    return x_reduced

def normalize_data(x,ob,dc,dose=None) :
    '''Normalizes the data to have zero mean and unit variance per slice
        
        Parameters:
        - x : A 3D data array with N slices arranged as [N,x,y] 
        
        Returns the normalized data array
    '''
    x = x - dc
    x[x<1] = 1
    ob = ob - dc
    ob[ob<1] = 1

    doses = 1
    if dose is not None :
        if dose.shape[0]==4 :  # Get the dose per projection using ROI 
            x_doses = x[:,dose[0]:dose[2],dose[1]:dose[3]].mean(axis=(1,2))
            ob_doses = ob[:,dose[0]:dose[2],dose[1]:dose[3]].mean(axis=(1,2))

            for i in range(x.shape[0]) :
                x[i,:,:] = x[i,:,:]/x_doses[i]
                ob[i,:,:] = ob[i,:,:]/ob_doses[i]

    x_norm = x/ob
    
    return x_norm
    

import matplotlib.patches as patches

def plot_profiles(x, L, rois, labels = None, figsize = None, vmin=None, vmax=None,cmap='viridis') :
    if figsize is None:
        figsize = [12,5]
        
    fig,ax = plt.subplots(1,2,figsize=figsize)
    
    ax[0].imshow(x.mean(axis=0),vmin=vmin,vmax=vmax)
    
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if type(rois[0]) is list :
        for idx,roi in enumerate(rois) :
            
            R = patches.Rectangle(xy=(roi[0],roi[1]),width=roi[2]-roi[0],height=roi[3]-roi[1],ec=cycle[idx],alpha=0.5)
            ax[0].add_patch(R)
            
            if labels is not None :
                label = labels[idx]
            else :
                label = None
            ax[1].plot(L,x[:,roi[1]:roi[3],roi[0]:roi[2]].mean(axis=(1,2)),label=label,cmap=cmap)
        if labels is not None :
            ax[1].legend()