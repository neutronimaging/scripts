import numpy as np
from golden_sequence import golden_sequence
    
Nproj    = 4000
Nrepeat = 1

x = np.repeat(range(Nproj),Nrepeat)

angles = golden_sequence(x)

scan(sp2_ry,angles.tolist())