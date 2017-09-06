# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 17:41:44 2014

@author: LZM100.00014
"""

import numpy as np

class Taper(object):
    def __init__(self,*sections):
        self.x = None
        self.y = None
        self.arc = None
        self.startArc = 500.

        self.arcMax = 800
        self.arcMin = 20
        
        self.waistAdd = 0
        self.vr = .05

        self.moveZ = True
        self.LStart = 8100
        self.RStart = 9100        
        self.taper_exp = 1.
        
        for i in sections:
            self += i
        
    def __add__(self,section):
        print('adding section',self.x,self.y,section.x,section.y)
        if self.x is None:
            self.x = section.x
            self.y = section.y
        else:
            dx = 2*self.x[-1]-self.x[-2]
            self.x = np.hstack( (self.x,section.x+dx) )
            self.y = np.hstack( (self.y,section.y) )
        return self
    
    def evaluate(self):
        print(self.x,self.y)
        OD = np.max(self.y)
        ID = np.min(self.y)
        
        #self.x = np.arange(len(self.x),dtype=float)
        if self.arc is None:
            #0/0
            arc = (self.startArc +
                     ((OD-self.y)/
                      (OD-ID))**self.taper_exp
                      *self.waistAdd)
            arc[np.nonzero(arc>self.arcMax)] = self.arcMax 
            arc[np.nonzero(arc<self.arcMin)] = self.arcMin
            
        else:
            arc = self.arc
        #self.vr = self.vr + self.x*0        
        #print self.x,self.y,self.arc,self.vr
        return self.x, self.y, arc, self.vr

class TaperSection(object):
    def __init__(self,length,ys,ye):
        x = np.arange(length,dtype=float)
        self.x = x
        self.tp = x/float(length)
        
    def __add__(self,section):
        a = Taper(self)
        a += section
        return a
        
        
class linear(TaperSection):
    def __init__(self,length,ys,ye):
        super(linear,self).__init__(length,ys,ye)
        y = ys-(ys-ye)*self.tp
        
        self.y = y
        
class sinewave(TaperSection):
    def __init__(self,periods,period,ys,ye,phase=0.):
        length = periods*period
        super(sinewave,self).__init__(length,0,0)
        ratio = ys-ye
        y = (1-np.cos(self.x*2*np.pi/period+phase))*ratio/2+ye
        
        
        self.y = y
        

class parabolic(TaperSection):
    def __init__(self,length,ys,ye,gamma=2.3): 
        super(parabolic,self).__init__(length,ys,ye)
        y = ys-(ys-ye)*(1-(1-self.tp)**gamma)

        self.y = y
        