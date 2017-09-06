
# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with 
the left/right mouse buttons. Right click on any plot to show a context menu.
"""
import os
#os.environ['QT_API'] = 'pyqt5'
import PyQt5
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

from PyQt5.QtGui import *
QT_API = 'pyqt'   

datadir = "C:/Users/LZM100.00014/Documents/Lanterns/"
 #for saving


from IPython.qt.console.rich_ipython_widget import RichJupyterWidget as RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

#==============================================================================
# for errors
#==============================================================================
import traceback
from scipy import integrate
from scipy.interpolate import interp1d

import numpy as np
from numpy import hstack
#import matplotlib.pylab as pylab

import sys
from scipy import interpolate
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

from qsciPyWidget import Editor as SimplePythonEditor
from MotorDriveWidget import MoveMotorWidget
import taperSections
global splicer

import time



class TaperSection:
    def __init__(self,Len=2,Ys=2000,Ye=1000):
        self.Len = Len #mm,MM
        self.Ys = Ys
        self.Ye = Ye
        
class PTaper(TaperSection):
    def __init__(self,gamma):
        pass

class Taper:
    def __init__(self):
        pass
    
    def Validate(self):
        pass

class TaperCalculator:    
     def __init__(self, xl, y, vr, arc,  thresholdL=7100,thresholdR=8100,  step = .02,useCurrentPos=True):
     
        self.started = False
        self.measureStarted = False

        self.thresholdL = abs(thresholdL)
        self.thresholdR = abs(thresholdR)
        
        self.vr        = vr
        self.y         = y
        self.xl        = xl

        maxy = y[0] #np.max(y)    
        R = y/maxy  #taper ratio
        dx = xl[1]-xl[0]
        V = sum(R**2*dx)
        
        taper_time = V/vr
        
        t= np.linspace(0,taper_time,10000)
        
        dt = R**2/vr*dx
        
        tt = np.cumsum(dt)
        tt -= tt[0]
        vl = dx/dt
    
        xr = vr*tt    
        
        tt /= 1000.
        
         #calculate the initialization parameters
        if useCurrentPos:
            ZL,ZR = splicer.lastZLZR
            xlStart = ZL
            xrStart = ZR
        else:
            xlStart = -self.thresholdL
            xrStart = -self.thresholdR-max(xr)
        
        self.xlStart = xlStart
       
        self.xrStart = xrStart
        
        
        #fix xL and xR to be in splicer Coordinates
        
        self.endLength = abs(xl[-1]-xl[0])
        self.beginLength = abs(xl[-1]-xl[0])
        
        xl = xlStart-xl
        xr = xrStart+xr
        
        self.xrEnd   = xr[-1] #ending positions
        self.xlEnd   = xl[-1] #starting positions
        print(xl[0],xl[-1],'startend')

        vr = xr*0+vr

        self.tpx = tt, vl, xl, vr, xr, arc 
        
        tnew = np.arange(0, max(tt)-1., step) #0.5 second step.    
    
        #taper parameters vs. time
        tpt = [tnew] + [interpolate.interp1d(tt, par)(tnew+step) for par in self.tpx[1:]]
        
        tpti = [interpolate.interp1d(tt, par) for par in self.tpx[1:]] #interpolators for the taper time vs. dist

                
        tpx = [tnew] + [interpolate.interp1d(tt, par)(tnew) for par in self.tpx[1:]]
        
        xlxr = interpolate.interp1d( tpt[4],  tpt[2] ) #xl vs xr  
        vlxr = interpolate.interp1d( tpt[4],  tpt[1],fill_value=.1,bounds_error=False) #xl vs xr  
        vrxr = interpolate.interp1d( tpt[4],  tpt[3],fill_value=.1,bounds_error=False) #xl vs xr  
        arcxr = interpolate.interp1d( tpt[4], tpt[5],fill_value=arc[0],bounds_error=False) #xl vs xr  
        
        self.tpt = tpt
        self.tpx = tpx
        self.step = step
        self.xlxr = xlxr
        self.vlxr = vlxr
        self.vrxr = vrxr
        self.arcxr = arcxr
        
        print('init params',xlStart,xrStart)
 
        
class TaperCalculator3:    
     def __init__(self, xl, R, start_idx=0, xlstart=0, xrstart=0, step = .1,minratio=0.1,
                  direction=0, feedlength=None,feed=None):
        '''Taper Calculator 2 will have push-pull directions
        xr will always be the material needed to feed the taper
        xl will be the other side of the taper...
        xr must always end on'''

        R = R*1.

        V = integrate.trapz(R**2, x=xl)
        R = np.maximum(R,minratio)
        
        #forward direction...  
        xr = integrate.cumtrapz(1/R**2, x=xl,initial=0)
        V2 = integrate.cumtrapz(R**2, x=xl)
        #V2 is the feed rate.
        lastxl_idx = np.argmax(V2>V)
        ## THIS IS OUR FEED 
            
        self.end_idx   = lastxl_idx
        self.start_idx = start_idx
        
        self.R  = R
        
        if direction ==0:
            #Starting at the front of the taper.. super easy.
            self.xr = xr
            self.xl = xl
        else:
            #starting at the end of the taper.. ... make sure that xr[0]
            
            self.xl = xr-xr[start_idx]
            self.xr = xl-xl[start_idx]

        self.feedLength = abs(xr[lastxl_idx]  - xr[0])
        print(('feeds', V, self.feedLength,abs(xr[-1]  - xr[0])))
        self.taperLength = abs(xl[lastxl_idx] - xl[0])
        
        self.end_idx   = -1
        self.start_idx = 0#start_idx  

class TaperCalculator2:    
     def __init__(self, xl, Ri,startl=1000000000, arc=500, step = .1, minratio=0.1,
                  direction=0, feedlength=None,feed=None):
        '''Taper Calculator 2 will have push-pull directions
        xr will always be the material needed to feed the taper
        xl will be the other side of the taper...
        xr must always end on
        BoUNDARY CONDITIONS BECAUSE OF DUMB INTEGRATION....
        for pulling        
        xl[0] = 0 where the left stage must start for pulling left
        xr[-1] = 0 where the right stage must end 
        for pushing
        xl[-1] = 0 left stage ends at the start of the taper.
        xr[0]  = 0 right stage pushes from end of the taper.
        
        '''
        xl = xl*1.
        dx = xl[1]-xl[0]
        V = integrate.trapz(Ri**2, x=xl)    
        R = np.maximum(Ri,minratio)
    
        idx = np.nonzero(R<1.0)[0]
        if len(idx) == 0:
            print('No Taper!!')
            start_idx=0
            end_idx = len(xl)
        else:
            startl_idx = int(startl/dx)
            start_idx  = np.minimum(idx[0],startl_idx)
            end_idx    = idx[-1]+1
       
    
        if direction == 0:
            ## WE WILL BE TAPERING HALF FORWARDS, HALF BACKWARDS, SO R IS NOW R**2
            #forward direction...  
            xr = integrate.cumtrapz(R**2, dx=dx,initial=0)
            #V2 = integrate.cumtrapz(R**2, x=xl)
    
            #V2 is the feed rate... THis is the lastx idx that we need....
            lastxl_idx = np.minimum(np.argmax(xr>V),end_idx)
            if lastxl_idx ==0:
                lastxl_idx = -1
            
            ee   = lastxl_idx
            ss = start_idx
            
    
            Rt = R[ss:ee]
            xr = xr[ss:ee]
            xl = xl[ss:ee]
            #bc end of taper always same...
            xr -= xr[-1]
    
            
            feedLength = abs(xr[-1]  - xr[0])
            taperLength = abs(xl[-1] - xl[0])
    
        else:
            #first find the last index we need in the taper profile...
            xr = integrate.cumtrapz(R**2, dx=dx,initial=0)
            lastxl_idx = np.minimum(np.argmax(xr>V),end_idx)
            #lastidx can go to 0 if the taper completes
            if lastxl_idx ==0:
                lastxl_idx = -1
                
            #also get the xstart
            xstart = xl[start_idx] 
            
            #We are doing the taper in reverse. Pushing with xl
            xr = xl[lastxl_idx::-1]
            Rt = R[lastxl_idx::-1]
            xl = integrate.cumtrapz(Rt**2, dx=-dx,initial=0)
            #Fix the boundary condition.. LAST x[-1] must be zero...
            xl-=xl[-1]
            xr-=xr[0] 
    
            ee = np.argmin(abs(xl-xstart))
            
            Rt = Rt[:ee]
            xl = xl[:ee]
            xr = xr[:ee]
            
        #save for the tapering process !!!!! 
        self.xl = -xl ##left stage is negative...
        self.xr = xr
        self.R  = R
        self.Rt = Rt
        self.direction = direction
        
        ## should we make interpolators???  
 
 

def makeratios(x,Ri,N,ratio=.8,offset=0.):
    
    '''Makes cascaed tapers assuming each time a ratio'''
    
    results = {}
    prevratio = 1.
    print((N,prevratio))
    x = x*1
    Ri = Ri*1
    print((np.max(Ri),np.min(Ri)))
    

    for i in range(N):
        print(i)
        lastone = False
        
        minratio = ratio**float(i+1)
        print(minratio)
        if minratio<=np.min(Ri):
            minratio = np.min(Ri)
            lastone = True

        idx = Ri<=minratio
        print((len(idx),minratio))

        V  = integrate.cumtrapz(Ri**2, x=x,initial=0)    
         
        start_idx = np.argmax(idx)
        end_idx   = len(idx) - np.argmax(idx[::-1])-1

        gap = V[end_idx]-V[start_idx]
        gapx = gap/(minratio)**2
        print(('feed gap in feed and pull',gap,gapx))

        xm = hstack((x[start_idx], x[start_idx]+gapx))
        xl = x[:(start_idx+1)]
        xr = x[(end_idx):]-x[end_idx]+xm[-1]


        RL = Ri[:(start_idx+1)]
        RR = Ri[(end_idx):]#-x[end_idx]+xm[-1]

        xnn = hstack( (xl,xm,xr) )
        Rnn = hstack( (RL,minratio,minratio,RR))

        
        try:
            _Rnn = interp1d(RL[::-1], xl[::-1])
            start= _Rnn(prevratio)
        except Exception as e:
            print(e)
            print(prevratio)
            print((np.min(RL),np.max(RL)))
            
            start = xl[0]
        try:
            _Rnn = interp1d(RR,xr)
            try:
                stop = _Rnn(prevratio)
            except Exception as e:
                print(e)
                stop = xr[-1]
        except:
            print(('xm',xr))
            stop = xr[-1]
        print(('START AND STOP',start,stop))

#        print('ruightbc',rightbc)

        if i==0:
            xn  = np.linspace(xnn[0],xnn[-1],3000)
        else:
            xn  = np.linspace(start,stop,3000)
        _Rn = interp1d(xnn,Rnn)
        Rn  = _Rn(xn)

        
        results[i] = [xn,Rn/prevratio,0] 
        prevratio = minratio
        if lastone:
            print('oo')
            break

    return results
    


def calctp(xl, Ri,rightbc=None,direction=0):
    '''Taper Calculator 2 will have push-pull directions
    xr will always be the material needed to feed the taper
    xl will be the other side of the taper...
    xr must always end on'''

    xl = xl*1.
    dx = xl[1]-xl[0]
    
    V = integrate.trapz(Ri**2, x=xl)    

    if direction == 0:
        ## WE WILL BE TAPERING HALF FORWARDS, HALF BACKWARDS, SO R IS NOW R**2
        #forward direction...  
        xr = integrate.cumtrapz(Ri**2, dx=dx,initial=0)
        Rt = Ri
        
        if rightbc is not None:
            xlerr = xl[0]-rightbc[0]+rightbc[1]
            xr -= xr[0]-xlerr
        else:
            #initialize me
            xr -= xr[-1] #0 at the end
    else:
        xr = xl[::-1]
        Rt = Ri[::-1]
        xb = xl[0]
        xl = integrate.cumtrapz(Rt**2, dx=-dx,initial=0)
        #Fix the boundary condition.. LAST x[-1] must be zero...
        
        xl-=xl[-1]-xb
        xlerr = xl[0]-rightbc[0]+rightbc[1]
        xr-=xr[0]- xlerr #-shorten 
        

    return xl,xr,Rt  

class TaperCalculator4:    
     def __init__(self,xl,xr,Rt,direction):
        '''Taper Calculator 2 will have push-pull directions
        xr will always be the material needed to feed the taper
        xl will be the other side of the taper...
        xr must always end on
        BoUNDARY CONDITIONS BECAUSE OF DUMB INTEGRATION....
        for pulling        
        xl[0] = 0 where the left stage must start for pulling left
        xr[-1] = 0 where the right stage must end 
        for pushing
        xl[-1] = 0 left stage ends at the start of the taper.
        xr[0]  = 0 right stage pushes from end of the taper.
        
        '''
                        
        #save for the tapering process !!!!! 
        self.xl = -xl ##left stage is negative...
        self.xr = xr
        self.Rt = Rt
        self.direction = direction      
    



class SplicerFunc():
    def __init__(self):
        pass
    def Initiate(self):
        pass
    def Update(self,kill=False):
        pass
    def End(self):
        pass
    
class PerformTaperWidget(QtGui.QWidget):
    def __init__(self,parent,taper):
        super(PerformTaperWidget, self).__init__()
        
        self.taper = taper
        
        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        print('deng')
        
        MoveToEnd = QtGui.QPushButton("MoveToStart")        
        MoveToEnd.clicked.connect(self.MoveToStartClicked)
        
        hbox.addWidget(MoveToEnd)
        MoveToEnd = QtGui.QPushButton("MoveToEnd")
        MoveToEnd.clicked.connect(self.MoveToEndClicked)
        print('deng')        
        hbox.addWidget(MoveToEnd)
            
        print('deng')
        MoveToEnd = QtGui.QPushButton("Arc")
        MoveToEnd.clicked.connect(self.ArcClicked)
        hbox.addWidget(MoveToEnd)

        
        self.arcBit = QtGui.QLineEdit(self)
        self.arcBit.setText('540')        
        hbox.addWidget(self.arcBit)

        self.arcTime = QtGui.QLineEdit(self)
        self.arcTime.setText('1000')
        hbox.addWidget(self.arcTime)

        Arcp10 = QtGui.QPushButton("Arc+10")        
        Arcp10.clicked.connect(self.Arcp10)

        Arcm10 = QtGui.QPushButton("Arc-10")        
        Arcm10.clicked.connect(self.Arcm10)
        hbox.addWidget(Arcp10)
        hbox.addWidget(Arcm10)
        
        Arcp10 = QtGui.QPushButton("V+0.01")        
        Arcp10.clicked.connect(self.vadd)

        Arcm10 = QtGui.QPushButton("V-0.01")        
        Arcm10.clicked.connect(self.vsub)
        
        hbox.addWidget(Arcp10)
        hbox.addWidget(Arcm10)

        
#
        self.modifiers= {'arc':0,'v':0.0}
        self.setLayout(hbox)
        self.show()

    def Arcp10(self):    
        """Add 10 to the arc"""
        self.taper.arcAdd += 10
        self.modifiers['arc'] +=4

    def Arcm10(self):    
        """Add 10 to the arc"""
        self.taper.arcAdd -= 10
        self.modifiers['arc'] -=4
        
    def vadd(self):    
        """Add 10 to the arc"""
        
        self.modifiers['v'] +=0.01

    def vsub(self):    
        """Add 10 to the arc"""
        
        self.modifiers['v'] -=0.01
        
    
    def MoveToEndClicked(self):
        
        ZL,ZR = splicer.readZLZR()
        
        end = self.taper.xrEnd +2500  #Move in past the end of the taper for prekik
        
        dist = end-ZR
        
        print('moving',dist)
        splicer.moveZLZR(-dist,.5, dist,.5)
        
    def MoveToStartClicked(self):
        
        ZL,ZR = splicer.readZLZR()
        
        start = self.taper.xrStart #Move in past the end of the taper for prekik
        
        dist = start-ZR
        
        print('moving',dist)
        splicer.moveZLZR(-dist,.5, dist,.5)

    def ArcClicked(self):
        try:
            arcbit,arctime = int(self.arcBit.text()),int(self.arcTime.text())
            print('arctime','arcbit',arctime,arcbit)
            
            if arcbit > 0 and arcbit < 1023:
                splicer.arc(arctime,arcbit)
        except:
            print('could not arc')
        
        
        
class PerformTaper():
    def __init__(self, gui, xlStart, xlEnd, xrStart, xrEnd, xlxr, vlxr, vrxr,
                 arcxr, name, rotation=False, arc=False,spinspeed=0.1):
        self.started = False
        self.name = name
        #Some basic properties.
        self.xlStart = xlStart
        self.xlEnd = xlEnd
        
        self.xrStart = xrStart
        self.xrEnd = xrEnd
        
        self.xlxr = xlxr
        self.vlxr  =  vlxr
        self.vrxr  =  vrxr
        self.arcxr =  arcxr
        
        #DO ARC?
        self.rotation = rotation
        self.arc = arc
        
        self.gui = gui
        
        self.arcAdd = 0 
        self.spinspeed = spinspeed
#==============================================================================
#         make a little window that shows the prekink menu etc
#==============================================================================

        try:
            self.ptWidget = PerformTaperWidget(self.gui,self)
            print('made the widget')
        except:
             traceback.print_exc(file=sys.stdout)
        
    def Initialize(self):
        splicer.absZLZR(self.xlStart,.8, self.xrStart,.8)
        self.lastVL = 0.
    def Begin(self):
        """Begin the tapering procedure"""

        curpos = splicer.readZLZR()
        #check if we are close to initialized point.
        self.xrp = self.xrStart#splicer.lastZLZR
        
        if abs(self.xlStart-curpos[0])+abs(self.xrStart-curpos[1])<500:
            if self.rotation:
                splicer.spin(-500000,speed=self.spinspeed)  #NEGATIVE SPIN SEEMS TO BE MUCH BETTER THAN POSITIVE
                
            if self.arc:
                print('start  arc', self.arcxr(self.xrStart))
                splicer.arc(2000, self.arcxr(self.xrStart) )
            #splicer.takeBP()
            self.last_laser_update = time.time()    
            self.last_stage_update = time.time()                    
            self.last_bp_update = time.time()        
            self.started = True
            
            self.firstStep = True
            
        
    def Update(self):
        
        #at the end of the taper, we should only update the time step
                
        
        if self.started:
                #should update every xx mss            
            
                
                
                xnow = splicer.lastZLZR[0] #Get our positions               
                xrp  = splicer.lastZLZR[1]  
                
                
                if xrp >=  (self.xrEnd-5.): #within 5micronstop.
                    self.End()

                #what the stage velocities should be.
                vl = self.vlxr(xrp)
                vr  = self.vrxr(xrp)

                CurentRatio = (vl/vr)**.5
                
                arc = self.arcxr(xrp) + self.arcAdd


                time_step = .1/vl**1.5  #WHEN vl is fast, update a lot.

                if vl > .5:
                    time_step = .1
                elif vl > .3:
                    time_step = .2                    
                else:
                    time_step = .4
                
               

                xlstep = -vl*time_step*1000 # vl could be greater than the max.
                xrstep =  vr*time_step*1000

                try:
                    xerr = self.xlxr(xrp)-xnow
                except:
                    xerr = 0.
                
                
                xlstep += xerr
                vl -= xerr*.005
                
                if xerr <-30.:
                    errfactor = 1-abs(xerr)/100.
                    if errfactor < 0:
                        errfactor = 0
                    xrstep*=  errfactor
                    if xrstep < 1.:
                        xrstep =0


        
                #stage dither to slow down the right stage
                # ONLY IF VL IS FAST
                if vl > 1.:
                    if xerr < -30:
                        print('stop')
                        splicer.updateZR(0, 0.01)
                    
                    if xerr > 30:
                        print('start')
                        splicer.updateZR(1, 0.01)
                            

                # if xlstep>0, the right motor is too slow
                if xlstep>0: xlstep = -5. #this will freeze the motor
                vcorr = -xerr*.002

                                    
                
                if time.time() - self.last_stage_update > time_step*.9: #
                    print('time_step',time_step)
                    

                    if vl > 1.: 
                        extra = abs(xlstep/(1000*time_step))
                        #xrstep /= extra*1.
                        #print 'xtra', extra 
                        vl = 1.

                    if vl <0.01 : vl = 0.01
                    if vr > 1.: vr = 1
                    if vr < 0.01: vr = 0.01
                    
                    print('the move')
                    print(xlstep,xrstep,vl,vr)

                    #minimum step can't be less than 1. Must dither here.
                    #if xrstep < 1.:
                    #    xrstep = 1.

                    if vl >.8:
                        #give the left stage a boost to make sure right stage does not
                    #fall behind
                        xlstep*=1.3
                    
                    if self.firstStep:
                        print('xrend',self.xrEnd)
                        xlmove = self.xlEnd-self.xlStart
                        xrmove = self.xrEnd-xrp
                        print('xlm','xrm',xlmove,xrmove)
                        splicer.moveZLZR(xlmove,vl,xrmove,vr) # overshoot by a little bit
                        self.firstStep = False
                        print('first stsep',xlmove)
                    else:
                        #splicer.updateZLZR(xlstep, xrstep) # overshoot by a little bit
                        splicer.updateVLVR(vl, vr) # overshoot by a little bit
                    #
                    

                    if time_step > 0.5 :
                        if time.time()-self.last_bp_update > 5.:
                            
                            bp = splicer.MeasureXC(M='Y',col=10)
                            if bp is not None:
                                self.gui.brightprofile.setData( y=bp)
                            #save a brightness profile
               #             splicer.CaptureLiveImg(datadir+self.name + ('/warm/z%0.2fexp%0.1f.bmp' % (xnow,splicer.exposure)),'Y' )
                       
                    self.last_stage_update = time.time()
            
                if time.time() - self.last_laser_update > 1.5:
                
                    if self.arc:
                            splicer.arc(1800,arc) #only update every half second
                        
                    self.last_laser_update = time.time()
                
                        
                    
                self.gui.xlp.setData(x = [splicer.lastZLZR[0]],y=[splicer.lastZLZR[1]])

                return 'Tapering Lerr=%0.2f, arc=%0.2f, Ratio=%0.2f' % (xerr,arc,CurentRatio)
        else:
            return 'Initializing'
            
    def End(self):
        self.started = False
        splicer.stop()
        self.ptWidget.close()


class MultiTaper():
    def __init__(self, gui, tapers=None,params={}):
        self.started = False
        
        self.tapers = tapers
        self.gui = gui
        self.arcAdd = 0 

        defaults = {'lstart':-4000,
                    'rend':-4000}        
        
        defaults.update(params)
        self.params = defaults
        
    def Initialize(self):
        print('initializing')
        ##... How to calculate teh paths???  ,,,...  
        #total feed length
        xr = self.tapers[0].xr
        feedlength = xr[-1]-xr[0]
        p = self.params
        lstart = p['lstart']
        rstart = p['rend'] - feedlength
        print(('rstart,rend',lstart,rstart))
        print(('feedlength',feedlength))
        self.feedlength = feedlength
        self.start_coords = (lstart,rstart)
        
        splicer.absZLZR(lstart, .5, rstart, .5 )
        
        
        try:
            self.ptWidget = PerformTaperWidget(self.gui,self)
        except:
             traceback.print_exc(file=sys.stdout)
        
    def Begin(self):
        """Begin the tapering procedure"""
        self.started = True

        self.start_coords = splicer.readZLZR()
        
        self.start_offset = self.start_coords[0],self.start_coords[1]+self.feedlength
        print(('start offset',self.start_offset))
        _xl = np.hstack([tp.xl for tp in self.tapers])+self.start_offset[0]
        _xr = np.hstack([tp.xr for tp in self.tapers])+self.start_offset[1]
        print((_xl[0],_xr[0]))
        self.gui.xl.setData(x=_xl,y=_xr) 
        

        def taperg(ct, t, start=(0,0), modifiers = {}):
            
            pushv = ct.vp
            ramp = 100 # ramp speed up and down in 200 micron from start and end
            xl = ct.xl+start[0]
            xr = ct.xr+start[1]
            R  = ct.Rt

            print(('splicer start then taper start',modifiers))
            print(start)
            print((xl[0],xr[0]))
            
            start = xl[0],xr[0]
            
            taper_distl = xl[-1]-xl[0]
            taper_distr = xr[-1]-xr[0]
            
            if ct.direction == 0:
                print('B taper')
                x = xl
                xp = xr
                pp = 0 #pulling indexer
                def updateV(feedv,pushv):
                    splicer.updateVLVR(pushv,feedv)                
            else:
                print('B taper')
                x = xr
                xp = xl
                pp = 1 #pulling indexer
                def updateV(feedv,pushv):
                    splicer.updateVLVR(feedv,pushv)
                    
            dx = x[1]-x[0]                
                
            coords = splicer.readZLZR()
            idx = int(coords[pp]-x[0])/dx

            v   = modifiers.get('v',0)+pushv                
            arc = modifiers.get('arc',0)+ct.arc     
            
            splicer.arc(300000,arc)
            splicer.absZLZR(xl[-1], v, xr[-1], v/R[idx]**2)
            
                
            while True:

                #monitoring the move
                coords = splicer.readZLZR()   
                #DON't DO IT IF WE ARE SO CLOSE...
                if  x[-1] - coords[pp] < -20:    
                    fidx = coords[pp]-x[0]                               
                    idx = int(fidx)/dx
                    
                    
                    cr = R[idx] 
                    v = modifiers.get('v',0)+pushv
                    
                    pusherror = coords[1-pp]-xp[idx]
                    #feedback... 
                    vpushfix = -.005*pusherror*pushv  #push feedback is a percentage
                    vpushfix = sorted((-.01, vpushfix, 0.01))[1]
                    updateV(v+vpushfix,v/cr**2)
                    print(('r',R[idx],v/cr**2,pusherror,vpushfix ))
                    arc = modifiers.get('arc',0)+ct.arc                
                    
                    splicer.arc(300000,arc)
                    yield 'Ratio %f, pusherror %f'% (R[idx],pusherror)
                else:
                    ##LETS ROTATE
                    print(('End of taper, rotating',ct.rot))
                    splicer.spin(-ct.rot,.03)
                    break            
                            
                
            
        ## MAKE THE GENERATOR
        def generator(tapers,modifiers):
            print('making generator')
            #start = 
            #splicer.arc(1500000000,10)
            #splicer.arc(300000,500)
            for ct in tapers:
                #loop through the iterator... need to send it back some useful information...
                b = taperg(ct, time.time(),self.start_offset, modifiers )
                                
                next(b)
                
                while True:
                    try:
                        
                        i =  b.send( time.time())
                        yield i
                    except StopIteration:
                        break
    
                    except Exception as e:
                        print(('Exception',e))
                        splicer.arc(0,0)
                        raise 

            splicer.arc(0,0)
                
        g = generator(self.tapers,self.ptWidget.modifiers)                                        

            
        print('setup one iteration')
        self.oneIteration = g
        
        
    def Update(self):
        
        #at the end of the taper, we should only update the time step
                
        
        if self.started:
             
             try:
                 
                 self.gui.xlp.setData(x = [splicer.lastZLZR[0]],y=[splicer.lastZLZR[1]])
                 return next(self.oneIteration)
             except StopIteration:
                 print('taper done')
                 self.started=False
             except Exception as e:
                 self.started = False
                 print('oops')
                 print(e)
        else:
            return 'Initializing'
            
    def End(self):
        try:
            self.started = False
            splicer.stop()
            self.ptWidget.close()
        except Exception as e:
            print(('warning',e))

    
# Class that initiates a measurement,
class MeasureTaper():
    
    def __init__(self,gui,dist=1000,fname=r'..\tapermeasure\last'): 
        """self.xlEnd-2000,(self.xlStart+2000)
        """

        self.state = 'started'
        
        #Get the distance of the stages

        self.measureStarted = False        
        self.measureMoving = False
        
        self.mx = []
        self.my = []
        self.mmpx = []
        self.mmpy = []

        dist = -dist
        self.dist   = dist
        self.movedir = np.sign(dist)*100.
        
        self.fname = fname
        
        self.gui = gui ## Need the gui to update stuff
        
    def Initiate(self):
        #self.MoveToMeasureStart()
        #time.sleep(.3) 
        print('initiated measurement')
        self.start = splicer.readZLZR()[0]
        self.measureStarted = True        
        self.measureMoving = False
        
        splicer.getImageSize()
        self.imgCounter = 0
        
    def End(self):
        splicer.stop()
        self.measureStarted = False        
        self.measureMoving = False
        
        
        #self.gui.stopFunc()

    def Update(self, kill=False):
        
        if kill:
            self.End()
        
       
        xl,xr = splicer.lastZLZR
        
        if not self.measureStarted:
            pass
            #self.End()
            
        elif not splicer.Moving:
            
            xd = splicer.Diameter('X')    
            xlx,xr = splicer.readZLZR()
            yd = splicer.Diameter('Y')
            
            xly,xr = splicer.readZLZR()

            self.mmpx.append(-(xlx))
            self.mmpy.append(-(xly))

            self.mx.append(xd)
            self.my.append(yd)
            
            self.gui.measureX.setData(x=self.mmpx,y = self.mx)
            self.gui.measureY.setData(x=self.mmpy,y = self.my)
            
            if self.imgCounter %10 == 0:
                filename = self.fname + (('z%0.2fexp%0.1f')%(xl,splicer.exposure))
                print(('saving to',filename))
                time.sleep(1)
                splicer.CaptureLiveImg(filename )
                #splicer.CaptureLiveImg(datadir+self.name + ('/measure/Xz%0.2fexp%0.1f.bmp' % (xl,splicer.exposure)),'X' )
                #self.lastMeasurePic = xl
            self.imgCounter +=1
            
            self.measureMoving = True
            self.lastMeasure = time.time()

            tomove = self.movedir#.(self.dist) #Move 2mm closer
            self.dist -= tomove
            
            print('tomove',tomove)
            splicer.moveZLZR(tomove,.1,-tomove,.1) # We Are Moving
            
            self.lastMeasurePic = 10000000.
            if self.dist/self.movedir < 1.:
                print('finished')
                self.End()
                
            return 'took a frame, moved again'
 
 
class MeasureTaperWithPictures():
    
    def __init__(self,gui,extra = 2000.): 
        """self.xlEnd-2000,(self.xlStart+2000)
        """

        self.state = 'created'
        
        self.measureStarted = False        
        self.measureMoving = False
        
        self.mx = []
        self.my = []
        self.mmpx = []
        self.mmpy = []

        self.extra = extra
        self.measureStart = measureStart#-extra
        self.measureEnd   = measureEnd#+extra

        self.gui = gui ## Need the gui to update stuff
        
    def Initiate(self):
        self.MoveToMeasureStart()
        time.sleep(.3)     
        self.measureStarted = True        
        self.measureMoving = False
        
        splicer.getImageSize()
        
        
    def MoveToMeasureStart(self):

        xl,xr = splicer.lastZLZR
        tomove = (self.measureStart-self.extra)-xl #Move 2mm closer for the measure
        splicer.moveZLZR(tomove,.5,-tomove,.5) # Go to the begining
        
    def End(self):
        splicer.stop()
        self.measureStarted = False        
        self.measureMoving = False
        
        
        #self.gui.stopFunc()

    def Update(self, kill=False):
        
        if kill:
            self.End()
        
       
        xl,xr = splicer.lastZLZR
        
        if not self.measureStarted:
            print('Measurement Ended')
        elif self.measureMoving:

            if splicer.Moving:
             
                ct = time.time()
                if ct- self.lastMeasure > .1:
                    
                    xd = splicer.Diameter('X')    
                    xlx,xr = splicer.readZLZR()
                    yd = splicer.Diameter('Y')
                    
                    xly,xr = splicer.readZLZR()

                    self.mmpx.append(-(xlx-self.measureEnd))
                    self.mmpy.append(-(xly-self.measureEnd))

                    self.mx.append(xd)
                    self.my.append(yd)
                    
                    self.lastMeasure = ct
                    
                    self.gui.measureX.setData(x=self.mmpx,y = self.mx)
                    self.gui.measureY.setData(x=self.mmpy,y = self.my)
                    
                return 'Measuring'   
            else:
                self.End()
        elif not splicer.Moving:
                # start the measure
                print('inside here;')
                self.measureMoving = True
                self.lastMeasure = time.time()

                tomove = (self.measureEnd+self.extra)-xl #Move 2mm closer
                print('tomove',tomove)
                splicer.moveZLZR(tomove,.2,-tomove,.2) # We Are Moving
                time.sleep(.1) # give us a second to initiate the move
                return 'Moving to Measure Start'

        


class TaperDesign(QtGui.QMainWindow):
    
    def __init__(self,taper):
        super(TaperDesign, self).__init__()
        self.taper = taper
        self.initUI()
        
    def initUI(self):
       
        #self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Taper Design')    

        okButton = QtGui.QPushButton("Validate")
        okButton.clicked.connect(self.validateClicked)
        
        cancelButton = QtGui.QPushButton("Initiate")
        cancelButton.clicked.connect(self.InitiateClicked)

        taperButton = QtGui.QPushButton("Taper")
        taperButton.clicked.connect(self.taperClicked)

        abortButton = QtGui.QPushButton("Abort")
        abortButton.clicked.connect(self.abortClicked)
        
        measureButton = QtGui.QPushButton("Measure")
        measureButton.clicked.connect(self.measureClicked)

        HomeThetaButton = QtGui.QPushButton("ThetaReset")
        HomeThetaButton.clicked.connect(self.HomeThetaButtonClicked)

        MoveThetaButton = QtGui.QPushButton("ThetaMOVE")
        MoveThetaButton.clicked.connect(self.MoveThetaButtonClicked)
        
        BDButton = QtGui.QPushButton("Bright")
        BDButton.clicked.connect(self.BD)
        
        self.exposure = QtGui.QLineEdit(self)
        self.exposure.setText('200')

#stopSplicerWithoutStageReset(self)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.exposure)
        hbox.addWidget(BDButton)
        hbox.addWidget(MoveThetaButton)
        
        MoveThetaButton = QtGui.QPushButton("TL")
        MoveThetaButton.clicked.connect(self.MoveThetaLClicked)
        hbox.addWidget(MoveThetaButton)
        MoveThetaButton = QtGui.QPushButton("TR")
        MoveThetaButton.clicked.connect(self.MoveThetaRClicked)
        hbox.addWidget(MoveThetaButton)

        StopSplicer = QtGui.QPushButton("STOPSPLICE")
        StopSplicer.clicked.connect(self.StopSpliceClicked)
        
        
        hbox.addWidget(StopSplicer)        
        hbox.addWidget(HomeThetaButton)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)
        hbox.addWidget(taperButton)
        hbox.addWidget(measureButton)
        hbox.addWidget(abortButton)
        
        button = QtGui.QPushButton("ExecuteCMDs")
        button.clicked.connect(self.RunCMDs)
        hbox.addWidget(button)
            

        vbox = QtGui.QVBoxLayout()
        

        hbox2 = QtGui.QHBoxLayout()
        
        #params = [ScalableGroup(name="Taper Structure", children=[])   ]
        
        #t = ParameterTree(showHeader=False)
        #t.setDragEnabled(True)
        self.text = SimplePythonEditor(self)
        #self.text.setAcceptRichText(True)
        #self.text.setTabStopWidth(10)
        
        self.text.setText(""" #Taper Functions
SD = 1190 #Start Diameter
ED = 800 #end Diameter

Waist = 1000.

taper.startArc = 500.
taper.waistAdd = 0.
taper.vr= 0.03

taper += linear(3000,SD,SD)
taper += linear(10000,SD,ED)
taper += linear(20000,ED,ED)
taper += linear(5000,ED,SD)

#multitaper = True
ARC = 560.
ROT = 60.
N   = 5

taper.name='ff'""")


        
        vbox1 = QtGui.QVBoxLayout()
        
        vbox1.addWidget(self.text)


        self.runcmds = SimplePythonEditor(self)
        
        self.runcmds.setText("""'''Instructions
        arc(duration in ms, bit between 0 and 1024)
        moveZLZR(ZL distance in micron 0.1 to,ZL speed,ZR distance in micron, ZR Speed)
        zoomin()
        zoomout()
        '''""")

        vbox1.addWidget(self.runcmds)

        hbox3 = QtGui.QHBoxLayout()
        self.doArc = QtGui.QCheckBox('Arc', self)
        self.doRotate = QtGui.QCheckBox('Rotate', self)
        self.controlSplicer = QtGui.QCheckBox('Control Splicer', self)
        hbox3.addWidget(self.doArc)
        hbox3.addWidget(self.doRotate)
        hbox3.addWidget(self.controlSplicer)
        vbox1.addLayout(hbox3)        
        hbox2.addLayout(vbox1)
        vboxPlots = QtGui.QVBoxLayout()       
        p1 = pg.PlotWidget(self,title='Taper Profile',xlabel='xl ($\mu$m)')
        p1.setLabel('left', "OD", units='micron')
        p1.setLabel('bottom', "ZL",  units='micron')        
        
        self.p1 = p1
        self.y = p1.plot()
        self.measureX = p1.plot(pen = (0,255,0))
        self.measureY = p1.plot(pen = (0,0,255))
        

        self.arc = p1.plot(pen=(255,0,0))
        
        self.brightprofileWindow = pg.PlotWidget(title='Brightness Profile')
        
        self.brightprofileWindow.show()
        
        self.brightprofile = self.brightprofileWindow.plot()
        
        vboxPlots.addWidget(p1,stretch=.8)
        p2 = pg.PlotWidget(self,title='Motor Velocity')
        p2.setLabel('left', "Velocity", units='mm/s')
        p2.setLabel('bottom', "Time",  units='s')
        
        self.p2 = p2
        self.vl = p2.plot()
        self.vr = p2.plot(pen=(255,0,0))
        vboxPlots.addWidget(p2,stretch=.8)

        p3 = pg.PlotWidget(self,title='xl,xr')
        self.p3 = p3
        self.xl = p3.plot()
        self.xr = p3.plot(   pen=(255,0,0))
        self.xlp = p3.plot(  pen=None, symbolBrush=(255,0,0), symbolPen='w')
        #self.xrp = p3.plot(np.random.normal(size=1), pen=None, symbolBrush=(255,0,0), symbolPen='w')
        p3.setLabel('left', "XR", units='micron')
        p3.setLabel('bottom', "XL",  units='MICRON')
        
        vboxPlots.addWidget(p3,stretch=.8)
        hbox2.addLayout(vboxPlots)

        
        
        vbox.addLayout(hbox2)        
        #vbox.addStretch(1)
        vbox.addLayout(hbox)

        #self.setLayout(vbox)        

        self.main_widget = QtGui.QWidget(self)
        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)


        self.timer = QtCore.QBasicTimer()
        self.timer.start(1, self) #check stuff every 130 ms, update stage every 150ms
        
        self.statusBar().showMessage("System Status | Normal")
        
        self.show()
        
        
        self.mtwidget = MoveMotorWidget(splicer)
        self.fps = 0
        self.previoustime = time.time()
        
        self.started = False
        self.ex = ''
        self.processClass = SplicerFunc()
        self.Measurement  = None
        self.taperProcess = None
    def RunCMDs(self):   
        txt = self.runcmds.text2()


        def moveZLZR(dL,sL,dR,sR):
            result = splicer.cmd('&MTRARC|ZL,%0.1f,%0.3f|ZR,%0.1f,%0.3f' % (dL,sL,dR,sR))
            
        d = {'splicer':splicer,'moveZLZR':moveZLZR,'arc':splicer.arc,'zoomin':splicer.zoomin,'zoomout':splicer.zoomout}
        try:
            
            exec(str(txt), d)
        except Exception as e:

            print(e)
            #QtGui.QMessageBox.
            QtGui.QMessageBox.information(self, 'Validation ERROR', str(e), QtGui.QMessageBox.Cancel)        
        
    def validateClicked(self):
        '''validating'''

        ts = taperSections
        taper = ts.Taper()
        d = {'np':np, 'linear':ts.linear,'sine':ts.sinewave,'parabolic':ts.parabolic,'taper':taper, 'newTaper':ts.Taper}

        try:
            glb = { }
            #loc = locals()
            
            exec( self.text.text2(), {},d)
            
            print('exectuing-----------------')
            #print(str(self.text.text2()))
            print(type(self.text.text2()))
            print(d.keys(),d['taper'].name,glb.keys())
            
        except Exception as e:

            print(e)
            #QtGui.QMessageBox.
            QtGui.QMessageBox.information(self, 'Validation ERROR', str(e), QtGui.QMessageBox.Cancel)
      
        if 'multitaper' in d:
            print('doing a multitaper')
            self.taperfunc = d['taper']
            d['name'] = 'NO NAME'
            
            
            
            xi, yi, _arc, vr = self.taperfunc.evaluate()

            #N = 5000
            x = np.linspace(xi[0],xi[-1],5000)
            y_ = interpolate.interp1d(xi,yi)
            y = y_(x)
            R = y/np.max(y)
            
            self.y.setData(x=x, y=y)
            #print(x,y)
            
            ##produce the tapers!!!
            tapers = []

            NN = d.get('N',5)
            arc = d.get('ARC',500)
            ROT = d.get('ROT',0)
            vp = d.get('VPUSH',0.3)
            ratio = d.get('RATIO',0.95)
            offset = d.get('OFFSET',0.0)
            
            taper_profiles = makeratios(x,R,NN,ratio=ratio,offset=offset)
            prevend = None
            
            for i,bb in list(taper_profiles.items()):
                print(i)
                x2,Rn,rbc = bb
                xl,xr,Rt  = calctp(x2,Rn,rightbc = prevend,direction=i%2)
                if i > 0 :
                    l = np.linspace(prevend[0],xl[0],1000)
                    r = np.linspace(prevend[1],xr[0],1000)
                    Rb = np.ones(1000)
                    tp = TaperCalculator4(l, r,Rb,(i)%2)
                    tp.arc = arc
                    tp.rot = 0
                    tp.vp  = vp
                    tapers.append(tp)
                    
                tp = TaperCalculator4(xl, xr,Rt,i%2)
                #make the connector
                
                tp.arc = arc
                tp.rot = ROT*((i+1)%2)
                tp.vp  = vp
                tapers.append(tp)
                prevend = xl[-1],xr[-1]            
            
            win = pg.GraphicsWindow(title="Tapering Profile")
            win.resize(1000,600)
            win.setWindowTitle('Tapering Profiles')
            p2 = win.addPlot()
            p3 = win.addPlot()
            RR = 1.
            xrcarry = 0
            
            for k,tp in enumerate(tapers):
                RR = tp.Rt
                p2.plot(x=tp.xl, y=tp.Rt,    pen = pg.intColor(k))
                p3.plot(x=tp.xl, y=tp.xr, pen = pg.intColor(k))
                
            ##MASTER STACK
            xl = np.hstack([tp.xl for tp in tapers])
            xr = np.hstack([tp.xr for tp in tapers])
            self.xl.setData(x=xl,y=xr) 
            self.dummy_=win            
            self.tapers = tapers
            
            self.taperProcess = MultiTaper(self,tapers)        
            self.startFunc(self.taperProcess) 
            
        else:
            self.taperfunc = d['taper']
            spinspeed = d.get('spinspeed',0.1)
            
            x,y,_arc,vr = self.taperfunc.evaluate()
            tp = TaperCalculator(x, 
                                 y, 
                                 vr, 
                                 _arc, 
                                 useCurrentPos = not self.taperfunc.moveZ,
                                 thresholdL = self.taperfunc.LStart,
                                 thresholdR = self.taperfunc.RStart )
            
            tt, vl, xl,vr, xr,arc = tp.tpt
    
            self.y.setData(x=x, y=y)
            self.arc.setData(x=x, y=_arc)        
            
            self.vl.setData(x=tt, y=vl)        
            self.vr.setData(x=tt, y=vr)
            
            self.xl.setData(x=xl,y=xr)       
            #Let calculate predicted XL XR based on velocity + time.
            xlp = np.cumsum(np.diff(vl)/np.diff(tt))
            xrp = np.cumsum(np.diff(vr)/np.diff(tt))
            self.xr.setData(x=xlp,y=xrp)       
            #self.xr.setData(x=tt,y=xr)
            print(min(np.diff(tt)),max(np.diff(tt)))        
            self.taper = tp
            
            self.taperProcess = PerformTaper(self,
                                 tp.xlStart,
                                 tp.xlEnd,
                                 tp.xrStart,
                                 tp.xrEnd,
                                 tp.xlxr,
                                 tp.vlxr,
                                 tp.vrxr,
                                 tp.arcxr, 
                                 self.taperfunc.name,
                                 self.doRotate.isChecked(),
                                 self.doArc.isChecked(),
                                 spinspeed)        
                                 
            self.startFunc(self.taperProcess)        


    def startFunc(self,func):
        self.processClass.End()
        self.processClass = func
        
    def stopFunc(self):

        self.processClass.End()
        
        self.processClass = SplicerFunc()
    
    def InitiateClicked(self):
        
        #This is where we can make the taper

        for i in range(3):
            splicer.usb.ReceiveText(500)
        splicer.stopSplicerWithoutStageReset()
        #splicer.usb.ReceiveText(500)
#        self.taperProcess = PerformTaper(self,
#                                         tp.xlStart,
#                                         tp.xlEnd,
#                                         tp.xrStart,
#                                         tp.xrEnd,
#                                         tp.xlxr,
#                                         tp.vlxr,
#                                         tp.vrxr,
#                                         tp.arcxr, 
#                                         self.taperfunc.name,
#                                         self.doRotate.isChecked(),
#                                         self.doArc.isChecked())        
#        self.startFunc(self.taperProcess)        
        self.taperProcess.Initialize()
        
    def BD(self):
        print('biorhgt clicked')
        exposure = int(self.exposure.text())
        print(exposure)
            
        if exposure > 1 and exposure < 200:
                splicer.setExposure(exposure)

        pass
    
    def HomeThetaButtonClicked(self):
        splicer.resetTheta()      
    
    def MoveThetaButtonClicked(self):
        #splicer.resetTheta()  
        splicer.spin(-10, .05)
        #time.sleep(1)
        #splicer.spin(-100, .05)
        #splicer.cmd('$RESETTH')
        
    def StopSpliceClicked(self):
        splicer.stopSplicerWithoutStageReset()        
        #splicer.cmd('$XY')
    def MoveThetaRClicked(self):
        splicer.cmd('&MTRARC|TR,%0.1f,%0.3f'%(-10,.05))


    def MoveThetaLClicked(self):
        splicer.cmd('&MTRARC|TL,%0.1f,%0.3f'%(-10,.05))

    def taperClicked(self):
        
        self.taperProcess.Begin()
        
    def abortClicked(self):
        splicer.stop()        
        self.processClass.End()
        self.processClass = SplicerFunc()
   
    def measureClicked(self):


        #PRINT WE NEED SOME AWESOME STUFF
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Enter Directory Prefix for Saving:',text='..\measurements\\taper1')
        
        if ok:
            fname = str(text)
            
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Enter Measurement Distance',text='-5000')
        
        if ok:
            dist = float(text)
            
            self.Measurement =  MeasureTaper(self, dist, fname)
            self.Measurement.Initiate()
        
            self.startFunc(self.Measurement)
        
        
    def timerEvent(self, e):
        # Loop where we control the splicer.
        if splicer.connected & self.controlSplicer.isChecked():
            a = splicer.readZLZR()
            status = self.processClass.Update()
            ct = time.time()
            
            self.fps = self.fps*.8 + .2*(ct-self.previoustime)
            self.previoustime = ct
            
            moving = splicer.Moving
            self.statusBar().showMessage("XL=%0.1f,XR=%0.1f, fps%0.5f, lastARC %s Moving %s,%s" % (a[0],a[1], self.fps, repr(splicer.lastarc), moving,status))
        else:
            self.statusBar().showMessage("Disconnected")
            


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
        
    def initUI(self):
       
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Absolute')    
        self.show()
  

   
def main():
    
    
    #LETS ALSO DO SOME IPYTHOPN PARRALLEL STUFF
    
    

    global splicer
    app = guisupport.get_app_qt4()
    from  LZM100 import splicer
    # Create an in-process kernel
    # >>> print_process_id()
    # will print the same process ID as the main process
    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = 'qt4'
    kernel.shell.push({'splicer': splicer})

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()
        app.exit()

    control = RichIPythonWidget()
    control.kernel_manager = kernel_manager
    control.kernel_client = kernel_client
    control.exit_requested.connect(stop)
    control.show()
    
    #app = QtGui.QApplication(sys.argv)
    #ex = Example()
    b = TaperDesign(Taper())
    sys.exit(app.exec_())

main()

