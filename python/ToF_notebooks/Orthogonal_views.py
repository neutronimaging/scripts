import skimage
import os
import numpy as np
import matplotlib.pyplot as plt

import pylab
import scipy
from skimage import io

from matplotlib.legend_handler import HandlerLine2D
import matplotlib.gridspec as gridspec

def PlotOrtogonalViews(ic,gs,fig, title,vmin, vmax, p_spac):
    
    ax0 = plt.subplot(gs[0])
    ax0.set_title(title, fontsize=14, x=0.8)
    pos = ax0.get_position().get_points().flatten()
    ax0.imshow(ic[:,int(ic.shape[1]/2),:], cmap='gray', vmin=vmin, vmax=vmax)
    x1 = np.arange(0,ic[:,int(ic.shape[1]/2),:].shape[1])
    y1 = np.ones(len(x1))*ic.shape[0]/4
    ax0.plot(x1,y1,'-',color='yellow')
    x2=np.ones(ic[:,int(ic.shape[1]/2),:].shape[0])*(ic[:,int(ic.shape[1]/2),:].shape[1]/2)
    y2=np.arange(0,len(x2))
    ax0.plot(x2,y2,'-',color='yellow')

    ax0.axis('off')
    ax0.set_aspect(1)
    ax0.axis('tight')
    ax0.get_position().get_points().flatten()

    ax1 = plt.subplot(gs[1],sharey=ax0)
    ax1.imshow(ic[:,:,int(ic.shape[2]/2)], cmap='gray', vmin=vmin, vmax=vmax)
#     scalebar = ScaleBar(p_spac,'mm',frameon='false', color='k', location='upper right')
#     ax1.add_artist(scalebar)
    x1 = np.arange(0,ic[:,:,int(ic.shape[2]/2)].shape[1])
    y1 = np.ones(len(x1))*ic.shape[0]/4
    ax1.plot(x1,y1,'-',color='yellow')
    x2=np.ones(ic[:,:,int(ic.shape[2]/2)].shape[0])*(ic[:,:,int(ic.shape[2]/2)].shape[1]/2)
    y2=np.arange(0,len(x2))
    ax1.plot(x2,y2,'-',color='yellow')
#     ax1.set_xlim([0,ic.shape[1]]-1)
#     ax1.set_ylim([0,ic.shape[0]]-1)
    ax1.axis('off')
    ax1.set_aspect(1)
    ax1.axis('tight')
        


    ax2 = plt.subplot(gs[2],sharex=ax0)
    im=ax2.imshow(ic[int(ic.shape[0]/4),:,:], cmap='gray', vmin=vmin, vmax=vmax)
    x1 = np.arange(0,ic[int(ic.shape[0]/2),:,:].shape[1])
    y1 = np.ones(len(x1))*ic.shape[1]/2
    ax2.plot(x1,y1,'-',color='yellow')
    x2=np.ones(ic[int(ic.shape[0]/2),:,:].shape[0])*(ic[int(ic.shape[0]/2),:,:].shape[1]/2)
    y2=np.arange(0,len(x2))
    ax2.plot(x2,y2,'-',color='yellow')
    ax2.axis('off')
#     ax2.set_xlim([0,ic.shape[2]])
#     ax2.set_ylim([0,ic.shape[1]])
    ax2.set_aspect(1)
    ax2.axis('tight')
    
    ax3=plt.subplot(gs[3],sharex=ax1)
    p = ax3.get_position().get_points().flatten()
#     print(p)
    bounds = [vmin,(vmin+(vmax-vmin)/2),vmax]
#     print(bounds)
#     ax_cbar = fig.add_axes([p[0]+0.03, 0.2, p[2]-p[0]-0.03, 0.02])
    ax_cbar = fig.add_axes([p[0]+0.005, 0.2, p[2]-p[0], 0.02])
    cb = plt.colorbar(im,cax=ax_cbar, orientation='horizontal', ticks=bounds)
    # cb.boundaries=bounds
    cb.ax.tick_params(labelsize=12)
    cb.ax.set_xticklabels([str(bounds[0]), str(bounds[1])[1:5], str(bounds[2])])  # horizontal colorbar
    ax3.axis('off')