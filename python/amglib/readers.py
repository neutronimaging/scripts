import numpy as np
import astropy.io.fits as fits
from imageutils import *

def readImages(fname,first,last, average = 'none', size = 5) :
    tmp = fits.getdata(fname.format(first),ext=0)
    img = np.zeros([last-first+1,tmp.shape[0],tmp.shape[1]])
    img[0]=tmp.astype(float)
    
    for idx in np.arange(first+1,last) :
        img[idx-first]=fits.getdata(fname.format(idx+1),ext=0).astype(float)

    if average == 'mean' :
        img = averageimage(img)
    if average == 'weighted' :
        img = weightedaverageimage(img,size=size)
    if average == 'median' :
        img = medianimage(img)
        
        
    return img

def getSinograms(fmask,ob,dc,N,lines,stride=1, counts=1) :
    img = fits.getdata(fmask.format(1),ext=0)
    sino = np.zeros([len(lines),N,img.shape[1]])
    
    angles   = goldenSequence(N)
    angleIdx = np.argsort(angles)
    ob = ob-dc
    ob[ob<1]=1
    D0 = ob[100:200,100:200].mean()
    
    for idx in range(len(angleIdx)) :
        for count in range(counts) :
            fileIdx = 1 + angleIdx[idx]*stride + count
            img = fits.getdata(fmask.format(fileIdx),ext=0).astype(float)-dc
            img[img<1]=1
            D = img[100:200,100:200].mean()
            # Normalize (img-dc)/(ob-dc)*(D0/D)
            img = -np.log((D0/D)*(img)/(ob))
            for lineIdx,line in enumerate(lines) :
                sino[lineIdx,idx] = sino[lineIdx,idx] + img[line]
                
    sino = sino / counts
    
    angles = angles[angleIdx]
    
    return sino,angles
