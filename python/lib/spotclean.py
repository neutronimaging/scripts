import numpy as np
import scipy.ndimage.filters as flt2

def spotclean(img,size=5,threshold=0.95):
    fimg=flt2.median_filter(img,size)
    dimg=np.abs(img-fimg)
    
    nbins=256
    h,dx=np.histogram(dimg, bins=nbins, density=True)
    ch=np.cumsum(h)
    ch=ch/np.max(ch)
    th=np.min(dx[np.where(ch>threshold)])
    mask=dimg<th
    
    cimg=mask*img+(1-mask)*fimg
    
    return cimg