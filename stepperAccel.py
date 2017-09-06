# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 15:15:08 2014

@author: LZM100.00014
"""

from matplotlib.pylab import * 
import time
#MEASURE ACCELERATION PROFILES OF THE STAGE.

from LZM100 import splicer

time.sleep(.5)

vel = .5
vel2 = 1
dist = 4000
splicer.moveZLZR(-dist,vel,-dist,vel)


cp = []
t = []
ts = time.time()
ls = time.time()
notstepped = True
while True:
    
    cp += [splicer.readZLZR()]
    ct = time.time()
    t += [ct]

    if (ct-ls > 0.1) & notstepped:
    #    print 'b'
        #splicer.moveZLZR(-500, vel, -500, vel)
        splicer.updateZLZR(-500,-500)
        splicer.updateVLVR(vel,vel)
        vel+=.01
        ls = time.time()
    
    if time.time()-ts > 5:
        break
    

cpa = array(cp)
x1 = cpa[:,0]
x2 = cpa[:,1]

v1 = diff(x1)/diff(t)
v2 = diff(x2)/diff(t)

print('v1', mean(v1[:-1])/1000)
print('v2', mean(v2[:-1])/1000)

plot(t[:-2],v1[:-1])
plot(t[:-2],v2[:-1])