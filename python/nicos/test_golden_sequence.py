# Call: pytest test_goldenScan.py
import pytest
import numpy as np
import matplotlib.pyplot as plt

from golden_sequence import golden_sequence

def plotAngles2(angles,ax, label = None) :

    for idx,angle in enumerate(angles) :
        ax.plot([-np.cos(angle/180*np.pi),np.cos(angle/180*np.pi)],[-np.sin(angle/180*np.pi),np.sin(angle/180*np.pi)])
        ax.text(np.cos(angle/180*np.pi),np.sin(angle/180*np.pi),"{0}".format(idx))
    
    if (label != None) :
        ax.text(0.5, -0.1, label, transform=ax.transAxes, fontsize=14, ha='center',va='center')    
    ax.axis('square')

def test_golden_sequence() :
    x = [0,1,2,5,10,20,50,100]

    arc = 180.0

    res180 = np.array([ 0.,           111.24611797,
                        42.49223595,  16.23058987,
                        32.46117975,  64.9223595,
                        162.30589875, 144.6117975])

    assert np.sum(golden_sequence(x,arc) - res180) < 1e-6

    arc=[0.0,180.0]
    assert np.sum(golden_sequence(x,arc) - res180) < 1e-6

    arc=[-90.0,90.0]
    assert np.sum(golden_sequence(x,arc) - (res180-90)) < 1e-6

    arc = 360.0

    res360 = np.array([ 0.,             291.24611797, 
                        222.49223595,   16.23058987,
                        32.46117975,    64.9223595,
                        162.30589875,   324.6117975 ])

    assert np.sum(golden_sequence(x,arc) - res360) < 1e-6

    arc=[0.0,360.0]
    assert np.sum(golden_sequence(x,arc) - res360) < 1e-6

    arc=[-180.0,180.0]
    assert np.sum(golden_sequence(x,arc) - (res360-180)) < 1e-6

    arc = 80.0
    res80 = np.array([ 0.,          49.4427191, 
                      18.8854382,   7.2135955, 
                      14.427191 ,   28.854382, 
                      72.135955 ,   64.27191])

    assert np.sum(golden_sequence(x,arc) - res80) < 1e-6

    arc=[0.0,80.0]
    assert np.sum(golden_sequence(x,arc) - res80) < 1e-6

    arc=[-40.0,40.0]
    assert np.sum(golden_sequence(x,arc) - (res80-40)) < 1e-6

    y = np.arange(0,11)
    fig,ax =plt.subplots(1,3,figsize=(15,5))
    plotAngles2(golden_sequence(y,arc=180),ax[0], label = "180")
    plotAngles2(golden_sequence(y,arc=360),ax[1], label = "360")
    plotAngles2(golden_sequence(y,arc=[-40,40]),ax[2], label = "80")

    fig.savefig("golden_sequence.png")

def test_generate_golden() :
    startpoint = 0
    nangles = 10
    angles0 = np.array([golden_sequence(i) for i in range(startpoint, nangles)])

    startpoint = 5
    nangles = 10
    angles1 = np.array([golden_sequence(i) for i in range(startpoint, nangles)])

    assert angles0[5] == angles1[0]
    assert np.sum(angles0[:-5] - angles1[:5]) < 1e-6
