import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
import skimage.io as io
from skimage.draw import disk
import imageutils as amg
import readers as rd

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
    
    return mask