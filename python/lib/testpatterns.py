def linepattern(segmentlength,f):
	""" Generates a 1D bilevel test pattern with increasing frequency
	
	Arguments:
	segmentlength -- number of pixels for each frequency
	f -- list of periods
	
	"""
    x=np.arange(0.0,segmentlength)
    xx=[]
    for ff in f :
        xx=np.append(xx,np.mod(np.floor(x/ff),2))

    return xx

def linepattern2d(segmentwidth,segmentheight,f) :
	""" Generates a 2D bilevel line pattern with increasing frequency
	
	Arguments:
	segmentwidth -- number of pixels for each frequency
	segmentheight -- number of pixels for each line 
	f -- list of periods
	
	"""
    x=linepattern(segmentwidth,f)
    y=[np.ones(len(x)),x,np.ones(len(x))]
    
    return np.repeat(x,segmentheight)
    
def contraststeps(neutrons=100,scalex=20,scaley=50) :
	""" Generates a constrst step wedge
	  
	"""
    img=np.array([[  1,   1,   1,   1,   1,   1,   1,   1,   1,  1,    1,   1, 1.0],
         [1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 1.0, 1.0],
         [  1,   1,   1,   1,   1,   1,   1,   1,   1,  1,    1,   1, 1.0]])
    
    img=np.repeat(img,scalex,axis=1)
    img=np.repeat(img,scaley,axis=0)
    
    return img