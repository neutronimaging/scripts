import numpy as np
import scipy.ndimage.filters as flt2
from scipy import ndimage
import matplotlib.pyplot as plt

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

def linepattern(segmentlength,f):
    """ Generates a 1D bilevel test pattern with increasing frequency
    
    Arguments:
    segmentlength -- number of pixels for each frequency
    f -- list of periods
    
    """
    
    x=np.arange(0.0,segmentlength)
    xx=np.ones(int(np.floor(segmentlength/3)))
    for ff in f :
        xx=np.append(xx,np.mod(np.floor(x/ff),2))
    
    return xx

def linepattern2d(segmentwidth,segmentheight,f,margin=False) :
    """ Generates a 2D bilevel line pattern with increasing frequency
    
    Arguments:
    segmentwidth -- number of pixels for each frequency
    segmentheight -- number of pixels for each line 
    f -- list of periods
    
    """
    
    
    x=linepattern(segmentwidth,f)
    
    if (margin==True) :
        y=np.stack([np.ones(len(x)),x,np.ones(len(x))])
    else :
        y=[x,x]
    
    return np.repeat(y,segmentheight,axis=0)
    
def contraststeps(neutrons=100,scalex=20,scaley=50) :
    """ Generates a constrst step wedge
      
    """
    img=np.array([[  1,   1,   1,   1,   1,   1,   1,   1,   1,  1,    1,   1, 1.0],
         [1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 1.0, 1.0],
         [  1,   1,   1,   1,   1,   1,   1,   1,   1,  1,    1,   1, 1.0]])
    
    img=np.repeat(img,scalex,axis=1)
    img=np.repeat(img,scaley,axis=0)
    
    return img

def neutronimage(img,sigma,photons,photonstrength):
    nimg=np.random.poisson(img)
    nimg=nimg-img
    
    nimg=img+ndimage.gaussian_filter(nimg,sigma)
    if (0.0<photons) :
        nimg=np.random.poisson(nimg*photons)/photons*photonstrength
    
    return nimg
    
def generatespots(size, fraction, width, amplitude,bias) :
    if (len(size)==1) :
        img=(np.random.uniform(0.0,1.0,(size,size))<fraction)*1.0
    else :
        img=(np.random.uniform(0.0,1.0,size)<fraction)*1.0
    img=ndimage.filters.gaussian_filter(img,sigma=width)
    img=(img/img.max())*amplitude+bias
    
    return img
    
def buildimagestack(size,nimg,ncount) :
    imgs=np.ones(shape=[size,size,nimg])*ncount
    for i in np.arange(nimg) :
        imgs[:,:,i] = neutronimage(imgs[:,:,i],1.0,2.0,1.0)
    
    return imgs
    
def singleimage(size,ncount) :
    img=np.ones(shape=[size,size])*ncount
    img = neutronimage(img,1.0,2.0,1.0)
    
    return img
    
def averageimage(imgs, axis=0) :
    img=imgs.mean(axis=axis)
    
    return img
    
def medianimage(imgs,axis=0) :
    img=np.median(imgs,axis=axis)
    
    return img
    
def weightedaverageimage(imgs,size) :
    dims=imgs.shape
    w=np.zeros(imgs.shape)
    M=size**2
    print('M=',M)
    fig,ax = plt.subplots(dims[0],4,figsize=(12,30))
    ax = ax.ravel()
    for i in np.arange(dims[0]) :
        print('i=',i)
        f=ndimage.filters.uniform_filter(imgs[i], size=size)*M
        f2=ndimage.filters.uniform_filter(imgs[i]**2, size=size)*M
        
        sigma=(1/(M-1)*(f2-(f**2)/M))**2
        w[i]=1.0/sigma
        ax[i*4].imshow(f)
        ax[i*4+1].imshow(f2)
        ax[i*4+2].imshow(sigma)
        ax[i*4+3].imshow(w[i])

    wsum=w.sum(axis=0)
    for i in np.arange(dims[0]) :
        w[i]=w[i]/wsum

    imgs=w*imgs
    img=imgs.sum(axis=0)
    
    return img
    
def sigmaclipaverageimage(imgs,fact=2) :
    dims=imgs.shape
    img = np.zeros(dims[0:2])
    for y in np.arange(dims[1]) :
        for x in np.arange(dims[0]) :
            c,upp,low=stats.sigmaclip(imgs[x,y,:],fact,fact)
            if (c.size!=0) :
                img[x,y]=c.mean()
            else :
                img[x,y]=img[x-1,y]
            
    return img
    
def periodicSpotPattern(dims, width, distance, amplitude) :
    x,y = np.meshgrid(range(0,dims[1]),range(0,dims[0]))
    dots=amplitude*(np.mod(x,distance)==0)*(np.mod(y,distance)==0)
    fdots=ndimage.filters.gaussian_filter(dots,width)
    m=np.max(fdots);
    fdots=amplitude/m*fdots
    
    return fdots    
    
def SNR(data,reference) :
    MSE = np.mean((data-reference)**2)
    s=np.sqrt(MSE)
    m=np.mean(reference)
    
    return s

def normalizeImage(img, ob, dc, neglog = True, doseROI = []) :
    
    normed = img.copy() - dc
    normed[normed<1]=1
    
    ob = ob - dc
    ob[ob<1] = 1
    
    if len(doseROI) == 4 :
        D0 = ob[doseROI[0]:doseROI[2],doseROI[1]:doseROI[3]].mean()
    else :
        D0 = 1
    
    if len(normed) == 2 :
        if len(doseROI) == 4 :
            D = normed[doseROI[0]:doseROI[2],doseROI[1]:doseROI[3]].mean()
        else :
            D = 1

        if neglog :
            normed = -np.log((D0/D)*normed/ob)
        else :
            normed = (D0/D)*normed/ob
    
    else :
        for idx in range(norm.shape[0]) :
            if len(doseROI) == 4 :
                D = normed[idx,doseROI[0]:doseROI[2],doseROI[1]:doseROI[3]].mean()
            else :
                D = 1

            if neglog :
                normed[idx] = -np.log(D0/D*normed[idx]/ob)
            else :
                normed[idx] = D0/D*normed[idx]/ob
        
    return normed