import numpy as np
from scipy.ndimage.morphology import distance_transform_edt as edt
from scipy.ndimage import sobel
import skimage.filters as flt

def misclasification_distance(gt,pr,decimals=0) :
    '''
    Counts the number of false positves and false negatives as function of distance from the edge of the ground truth.

            Parameters:
                    gt (np array) : The ground truth image
                    pr (np array) : The prediction image

            Returns:
                    binary_sum (str): Binary string of the sum of a and b
    '''
    
    dpos = np.around(edt(gt != 0),decimals=decimals)
    dneg = np.around(edt(gt == 0),decimals=decimals)
    
    m=4*gt*pr+ 2*gt*(1-pr) + 3*(1-gt)*pr + (1-gt)*(1-pr)
    
    dneg=dneg*(m==3)
    
    duneg = np.unique(dneg)
    fpcnt = []
    
    for d in duneg :
        fpcnt.append((dneg==d).sum())

    dpos=dpos*(m==2)
    
    dupos = np.unique(dpos)
    fncnt = []
    
    for d in dupos :
        fncnt.append((dpos==d).sum())
       
    res = {'fp_dist':duneg,'fp_count':fpcnt,'fn_dist':dupos,'fn_count':fncnt,'confusion_map':m}

    return res


def gmsd(ref, img, c=1e-6):
    '''
    Computes the Gradient Magnitude Similarity Deviation (gmsd) between two images.
    
    Parameters:
    ref : the reference image
    img : the processed image
    c   : bais value to protect against div by zero
    
    Returns :
    The computed gmsd value
    '''
    
    gx_r = sobel(ref, axis=0)
    gy_r = sobel(ref, axis=1)
    gx_p = sobel(img, axis=0)
    gy_p = sobel(img, axis=1)

    G_r = np.hypot(gx_r, gy_r)
    G_p = np.hypot(gx_p, gy_p)

    gms = (2*G_r*G_p + c) / (G_r**2 + G_p**2 + c)
    return np.std(gms)

def edge_masked_gmsd(ref, img, sigma=0.8, k=3, eps=1e-6):
    '''
    Computes the Edge Masked Gradient Magnitude Similarity Deviation (gmsd) between two images.
    
    Parameters:
    ref   : the reference image
    img   : the processed image
    sigma : width of the smoothing Gaussian filter
    k     : edge magnitude threshold
    eps   : bais value to protect against div by zero
    
    Returns :
    The computed gmsd value
    '''
        
    ref_s = gaussian_filter(ref, sigma)
    img_s = gaussian_filter(img, sigma)

    gx_r = sobel(ref_s, axis=0)
    gy_r = sobel(ref_s, axis=1)
    gx_p = sobel(img_s, axis=0)
    gy_p = sobel(img_s, axis=1)

    Gr = np.hypot(gx_r, gy_r) / np.sqrt(ref_s + eps)
    Gp = np.hypot(gx_p, gy_p) / np.sqrt(ref_s + eps)

    mask = Gr > k * np.median(Gr)

    c = 1e-6
    gms = (2*Gr*Gp + c) / (Gr**2 + Gp**2 + c)

    return np.std(gms[mask])
    
def outlier_counter(x,k=3) :
    x = np.asarray(x)
    med = np.median(x)
    mad = np.median(np.abs(x - med))

    z = 0.6745 * (x - med) / mad
    f_out = np.mean(np.abs(z) > k)

    return f_out

import numpy as np

def mad_outlier_fraction(
    img,
    k=3.0,
    mask=None,
    ignore_nan=True,
    return_z=False,
    eps=1e-12
):
    """
    Compute outlier fraction using MAD-based robust z-score.

    Parameters
    ----------
    img : ndarray
        Input image (2D or 3D).
    k : float
        Threshold for outlier detection (typically 2.5–3.5).
    mask : ndarray (bool), optional
        Boolean mask of valid pixels (True = include).
    ignore_nan : bool
        If True, ignore NaN values.
    return_z : bool
        If True, also return z-score image.
    eps : float
        Small constant to avoid division by zero.

    Returns
    -------
    f_out : float
        Fraction of outliers.
    z : ndarray, optional
        Robust z-score image (if return_z=True).
    """

    x = np.asarray(img)

    # Build valid mask
    valid = np.ones_like(x, dtype=bool)
    if mask is not None:
        valid &= mask
    if ignore_nan:
        valid &= np.isfinite(x)

    x_valid = x[valid]

    if x_valid.size == 0:
        return (np.nan, None) if return_z else np.nan

    med = np.median(x_valid)
    mad = np.median(np.abs(x_valid - med))

    # Avoid division by zero (flat image case)
    mad = max(mad, eps)

    z = np.zeros_like(x, dtype=float)
    z[valid] = 0.6745 * (x[valid] - med) / mad

    outliers = np.abs(z[valid]) > k
    f_out = np.mean(outliers)

    if return_z:
        return f_out, z
    else:
        return f_out
    
def local_mad_outlier_fraction(
    img,
    k=3.0,
    footprint=7,
    eps=1e-12,
    return_z=False
):
    """
    Compute outlier fraction using MAD-based robust z-score.

    Parameters
    ----------
    img : ndarray
        Input image (2D or 3D).
    k : float
        Threshold for outlier detection (typically 2.5–3.5).
    footprint : int
        Size of the local neighborhood (must be odd).
    eps : float
        Small constant to avoid division by zero.
    return_z : bool
        If True, also return z-score image.

    Returns
    -------
    f_out : float
        Fraction of outliers.
    z : ndarray, optional
        Robust z-score image (if return_z=True).
    """

    x = np.asarray(img)
    med = flt.median(x, footprint=footprint)
    mad = np.median(np.abs(x - med))

    # Avoid division by zero (flat image case)
    mad = max(mad, eps)

  
    z = 0.6745 * (x - med) / mad

    outliers = np.abs(z) > k
    f_out = np.mean(outliers)

    if return_z:
        return f_out, z
    else:
        return f_out