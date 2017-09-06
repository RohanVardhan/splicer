# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with 
the left/right mouse buttons. Right click on any plot to show a context menu.
"""


QT_API = 'pyqt'   
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

#==============================================================================
# for errors
#==============================================================================
import traceback

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import matplotlib.pylab as pylab
import pyqtgraph as pg
import sys
from scipy import interpolate
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

from qsciPyWidget import SimplePythonEditor

import taperSections
global splicer

import time



class TaperSection:
    def __init__(self,Len=2,Ys=2000,Ye=1000):
        self.Len = Len #mm
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
        #threshold = abs(threshold)
        self.thresholdL = abs(thresholdL)
        self.thresholdR = abs(thresholdR)
        
        self.vr        = vr
        self.y         = y
        self.xl        = xl

        maxy = np.max(y)    
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
        
        xlxr = interpolate.interp1d(tpt[4],tpt[2]) #xl vs xr  
        vlxr = interpolate.interp1d(tpt[4],tpt[1],fill_value=.1,bounds_error=False) #xl vs xr  
        vrxr = interpolate.interp1d(tpt[4],tpt[3],fill_value=.1,bounds_error=False) #xl vs xr  
        arcxr = interpolate.interp1d(tpt[4],tpt[5],fill_value=arc[0],bounds_error=False) #xl vs xr  
        
        self.tpt = tpt
        self.tpx = tpx
        self.step = step
        self.xlxr = xlxr
        self.vlxr = vlxr
        self.vrxr = vrxr
        self.arcxr = arcxr
        print('init params',xlStart,xrStart)
        

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
        
#        SWPLEFT = QtGui.QPushButton("MoveToStart")
#        SWPLEFT.clicked.connect(self.SWPLEFTClicked)
#        hbox.addWidget(MoveToEnd)
#        MoveToEnd = QtGui.QPushButton("SWPLEFT")
 
 
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

        
#

        self.setLayout(hbox)


        self.show()

    def Arcp10(self):    
        """Add 10 to the arc"""
        self.taper.arcAdd += 10

    def Arcm10(self):    
        """Add 10 to the arc"""
        self.taper.arcAdd -= 10
        
    
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
    def __init__(self, gui, xlStart, xrStart, xrEnd, xlxr, vlxr, vrxr, arcxr, rotation=False, arc=False):
        self.started = False

        #Some basic properties.
        self.xlStart = xlStart
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
#==============================================================================
#         make a little window that shows the prekink menu etc
#==============================================================================

        try:
            self.ptWidget = PerformTaperWidget(self.gui,self)
            print('made the widget')
        except:
             traceback.print_exc(file=sys.stdout)
        
    def Initialize(self):
        splicer.absZLZR(self.xlStart,.5, self.xrStart,.5)
        
    def Begin(self):
        """Begin the tapering procedure"""

        curpos = splicer.readZLZR()
        #check if we are close to initialized point.
        self.xrp = self.xrStart#splicer.lastZLZR
        
        if abs(self.xlStart-curpos[0])+abs(self.xrStart-curpos[1])<500:
            if self.rotation:
                splicer.spin(500000,speed=.1)
            if self.arc:
                splicer.arc(1005, self.arcxr(self.xrStart) )
            #splicer.takeBP()
            self.last_laser_update = time.time()                        
            self.started = True
            
        
    def Update(self):
        if self.started:
            
            
                time_step = 0.5
                
                xnow = splicer.lastZLZR[0]                
                xrp  = splicer.lastZLZR[1]                
                

                vl = self.vlxr(xrp)
                vr  = self.vrxr(xrp)
                arc = self.arcxr(xrp)+self.arcAdd

                #vlstep = 

                try:
                    xerr = self.xlxr(xrp)-xnow
                except:
                    xerr = 0.
     
                vcorr = -xerr*.002
                #if vcorr < 0: vcorr = 0 # Do not slow down the ZL
                
                #if abs(xerr)>10.:
                #    vr*=.9
                if abs(vcorr)>.7:
               
                    vcorr = .7*np.sign(vcorr)
                if xrp >= self.xrEnd:
                #    print 'finished'
                    self.End()
                else: 
                    
                    #vll check
                    #if vcorr <0:
                    if vcorr < 0:
                        #RIGHT STAGE IS TOO SLOW
                        stepR = 300
                        vr*=1.1 # make it 10 % faster
                        splicer.updateZR(stepR,vr)
                        # DO NOT SLOW DOWN VL TOO FAST.
                        if vcorr < -.2: vcorr = -.2
                            
                        vll = vl+vcorr
                        if vll < .01: vll = .01
                        
                    elif vl+vcorr > 1.:
                        #RIGHT STAGE IS TOO FAST
                        print('too fast', end=' ')
                        vll = 1.
                        stepR = .3
                        #GOTTA SLOW ZR DOWN....
                        splicer.updateZR(stepR,vr)
                    else:
                        vll = vl+vcorr
                        stepR = 300
                        
                    

                    #LASER STUFF                    
                    if time.time() - self.last_laser_update > time_step:
                        if xerr>450: xerr = 450
                        splicer.moveZLZR(-500+xerr,vll,+stepR,vr) # overshoot by a little bit
                        
                        if self.arc:
                            splicer.arc(600,arc) #only update every half second

                        bp = None#splicer.MeasureXC()
                        if bp is not None:
                            self.gui.brightprofile.setData( y=bp)
                            #splicer.takeBP()
                        self.last_laser_update = time.time()
                                        
                    
                self.gui.xlp.setData(x = [splicer.lastZLZR[0]],y=[splicer.lastZLZR[1]])

                return 'Tapering Lerr=%f,arc=%f' % (xerr,arc)
        else:
            return 'Initializing'
            
    def End(self):
        self.started = False
        splicer.stop()
        self.ptWidget.close()
#        self.gui.stopFunc()
    
# Class that initiates a measurement,
class MeasureTaper():
    
    def __init__(self,gui,measureStart,measureEnd,extra = 2000.): 
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
        okButton.clicked.connect(self.okClicked)
        
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


        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(MoveThetaButton)
        hbox.addWidget(HomeThetaButton)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)
        hbox.addWidget(taperButton)
        hbox.addWidget(measureButton)
        hbox.addWidget(abortButton)

        vbox = QtGui.QVBoxLayout()
        

        hbox2 = QtGui.QHBoxLayout()
        
        #params = [ScalableGroup(name="Taper Structure", children=[])   ]
        
        #t = ParameterTree(showHeader=False)
        #t.setDragEnabled(True)
        self.text = SimplePythonEditor(self)
        #self.text.setAcceptRichText(True)
        #self.text.setTabStopWidth(10)
        
        self.text.setText(""" #Taper Functions
SD = 1680 #Start Diameter
ED = 1490 #end Diameter

Waist = 1000.

taper.startArc = 530.
taper.waistAdd = 0.
taper.vr = 0.05

taper += linear(3000,SD,Waist)
taper += linear(3000,Waist,Waist)
taper += linear(2000,Waist,ED)
taper += linear(25000,ED,ED)
taper += parabolic(4000,ED,SD)""")



        vbox1 = QtGui.QVBoxLayout()
        
        vbox1.addWidget(self.text)

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
        
        self.fps = 0
        self.previoustime = time.time()
        
        self.started = False
        self.ex = ''
        self.processClass = SplicerFunc()
        self.Measurement  = None
        self.taperProcess = None
        
    def okClicked(self):
        ts = taperSections
        d = {'np':np,'linear':ts.linear,'parabolic':ts.parabolic,'taper':ts.Taper(), 'newTaper':ts.Taper}
        exec(str(self.text.text()), d)
        
        self.taperfunc = d['taper']
        
        x,y,arc,vr = self.taperfunc.evaluate()
        self.y.setData(x=x,y=y)
        self.arc.setData(x=x,y=arc)
        
        tp = TaperCalculator(x,y,vr,arc,useCurrentPos = not self.taperfunc.moveZ )
        
        tt, vl, xl,vr, xr,arc = tp.tpt
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

    def startFunc(self,func):
        self.processClass.End()
        self.processClass = func
        
    def stopFunc(self):

        self.processClass.End()
        
        self.processClass = SplicerFunc()
    
    def InitiateClicked(self):
        
        #This is where we can make the taper

        
        tp = self.taper
        print(self.doRotate.isChecked())
        self.taperProcess = PerformTaper(self,tp.xlStart,tp.xrStart,tp.xrEnd,tp.xlxr,tp.vlxr,tp.vrxr,tp.arcxr,self.doRotate.isChecked(),self.doArc.isChecked())        
        self.startFunc(self.taperProcess)        
        self.taperProcess.Initialize()
        

    def HomeThetaButtonClicked(self):
        splicer.resetTheta()      
    
    def MoveThetaButtonClicked(self):
        #splicer.resetTheta()  
        splicer.spin(10, .05)
        #time.sleep(1)
        #splicer.spin(-100, .05)
        #splicer.cmd('$RESETTH')

    def taperClicked(self):
        
        self.taperProcess.Begin()
        
    def abortClicked(self):
        splicer.stop()        
        self.processClass.End()
        self.processClass = SplicerFunc()
   
    def measureClicked(self):

        print(self.taper.xlEnd,self.taper.xlStart)
        self.Measurement =  MeasureTaper(self, self.taper.xlEnd, self.taper.xlStart,2000)
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
            self.statusBar().showMessage("XL=%0.1f,XR=%0.1f, fps%0.5f, Moving %s,%s" % (a[0],a[1], self.fps, moving,status))
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

