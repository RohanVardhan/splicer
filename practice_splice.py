# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 12:34:07 2014

@author: LZM100.00014
"""

from  LZM100 import splicer

#splicer.zoomin() #ZoomOut
#0/0
splicer.stopSplicerWithoutStageReset() #Stop the splicer
splicer.zoomout() #ZoomOut

def moveZLZR(dL,sL,dR,sR):
    result = splicer.cmd('&MTRARC|ZL,%0.1f,%0.3f|ZR,%0.1f,%0.3f' % (dL,sL,dR,sR))


print((splicer.readZLZR()))

#==============================================================================
# #==============================================================================
# # 
# arc = 570.
# arctime = 5000.
# splicer.arc(arctime,arc)
# moveZLZR(0,0.1,15,.05)
# #==============================================================================
#==============================================================================

#==============================================================================
# arc = 570.
# arctime = 5000.
# stuffdistance = 20.+10.
# splicer.arc(arctime,arc)
# moveZLZR(0,0.1,stuffdistance,.05)
#==============================================================================
 
arc = 600.
arctime = 2000.
stuffdistance = 20.+10.
splicer.arc(arctime,arc)
#moveZLZR(0,0.1,stuffdistance,.05)
