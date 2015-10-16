__author__ = 'ayanmukhopadhyay'

import numpy as np
result = np.empty((10,961))
for counter in range(10):
    tempArray = np.load("patrolByTimeStep"+str(counter)+".npy")
    result[counter] = tempArray
np.savetxt("patrolData",result,fmt='%.8f',delimiter=',',newline='\n')
