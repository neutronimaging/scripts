import numpy as np

def golden_sequence(x, arc=[0.0,180.0], golden_inverse=False) :
    x=np.array(x)

    if np.ndim(arc) == 0 :
        arc=[0.0,arc]

    arclen = arc[1]-arc[0]

    if golden_inverse :
        phi = 0.5* (np.sqrt(5)-1) # the only gain is probbly only numerical stability
    else :
        phi = 0.5* (1+np.sqrt(5))

    if arclen % 180 == 0.0 :
        return np.fmod(x*phi*180.0,arclen)+arc[0]
    else : 
        return np.fmod(x*phi*arclen,arclen)+arc[0]