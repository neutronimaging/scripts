import numpy as np
import astropy.io.fits as fits
from amglib.imageutils import *
import tifffile as tiff
from tqdm.notebook import tqdm

def readImage(fname) :
    ext = fname.split('.')[-1]

    img = []
    
    if ext == 'tif' :
        img = tiff.imread(fname).astype('float32')
    
    if ext == 'fits' :
        img = fits.getdata(fname,ext=0).astype('float32')
        
    return img
        
def readImages(fname,first,last, average = 'none', averageStack=False, stride=1, count=1, size = 5) :
    tmp = readImage(fname.format(first))
    img = np.zeros([(last-first+1) // stride,tmp.shape[0],tmp.shape[1]],dtype='float32')
    img[0]=tmp.astype('float32')
    if 1<count :
        for idx in tqdm(np.arange(first,last,step=stride)) : 
            img[(idx-first) // stride] =  readImages(fname,
                                                     idx,
                                                     idx+count-1,
                                                     stride=1,
                                                     count=1,
                                                     size=size, 
                                                     average=average,
                                                     averageStack=True)
    else :
        for idx in tqdm(np.arange(first,last,step=stride)) : 
            img[(idx-first) // stride] = readImage(fname.format(idx))

    
    if averageStack == True :
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


def saveTIFF(fname, img, startIndex=0) :
    if len(img.shape)<3 :
        tiff.imsave(fname,np.squeeze(img), {'photometric': 'minisblack'})
    else :
        for idx in tqdm(range(img.shape[0])) :
            tiff.imsave(fname.format(idx+startIndex),np.squeeze(img[idx]), {'photometric': 'minisblack'})
