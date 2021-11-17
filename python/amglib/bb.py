import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
import skimage.io as io
from skimage.draw import disk
import amglib.imageutils as amg

def get_black_bodies(img, greythres,areas = [2000,4000],R=2) :
    bb=img<greythres
    lbb=label(bb)

    mask = np.zeros(lbb.shape)
    regions=[]
    
    for region in regionprops(lbb):
        if (region.area<areas[0]) or (areas[1]<region.area) :
            lbb[lbb==region.label]=0
        else:
            regions.append(region)
            x,y = region.centroid
            rr, cc = disk((x,y), R)
            mask[rr, cc] = 255  

    mask=mask.astype('uint8')
    r,c = np.where(0<mask)
    
    return mask,r,c

def compute_scatter_image(img,r,c) :
    y = img[r,c]

    H=np.transpose([r,c,r**2,c**2,r*c])
    H=np.concatenate((np.ones([H.shape[0],1]),H),axis=1)

    q=np.linalg.lstsq(H, y, rcond=None)

    res=polynomial_image(img.shape,q[0])
    return res

def polynomial_image(size,q) :
    c,r = np.meshgrid(np.arange(size[1]),np.arange(size[0]))

    img = np.ones(size)*q[0]
    img = img + r*q[1]
    img = img + c*q[2]
    img = img + r**2*q[3]
    img = img + c**2*q[4]
    img = img + r*c*q[5]

    return img
