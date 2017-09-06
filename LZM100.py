# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:56:50 2014

@author: LZM100.00014
"""

#datadir = 'C:\Users\LZM100.00014\Documents\Lanterns\'



import clr



from System.Windows.Forms import Form,Application
import os
from System.IO import File #For saving to files

import time

import numpy as np
from System.Reflection import Assembly

cp = os.getcwd()
Assembly.LoadFile(cp + '\\UsbCoreFsm100.dll') 
Assembly.LoadFile(cp + '\\UsbFsm100Server.dll') 

#need to reimport clr to update the assemblies...
import clr


class ZLZRDanger(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

ACK = 0o6
class Splicer():
    def __init__(self):
        
        c = Form()
        self.connected = False
        def attached(source, args):
            print('Connected to splicer')
            self.connected = True
        def detached(source,args):
            self.connected = False
            print('Disconnected from splicer')

        a = clr.UsbFsm100ServerClass(c.Handle  )

        
        a.Attached += attached
        a.Detached += detached
        self.usb = a      
        self.c = c
        #c.Visible=False
        #c.Show()
        #c.Close()
        Application.DoEvents()  #<--- BOO YA
        #Application.Run(c)  
        print('g')
        #c.Close()
        #a.close()
        
        self.usb.Clear()
        self.threshold = 2000.
        
        self.lastZLZR = ('0','0')
        self.lastarc  = 0,0
        
        
        self.lastmove    = self.readZLZR()
        self.lastvelocity = (0.,0.) #important for moving fast
        self.lastZLZR = self.readZLZR()
        self.lastarc = (0,0)
        
        self.immodeSize = {1:np.array((640,480)),2:np.array((640,480)),3:np.array((486,364))}
        self.exposure = 0.
        
        
        
    def cmd(self,cmd,timeout=5000):
        return self.usb.CommandAndReceiveText(cmd,timeout)
         
    def motorPos(self,motor):
        """ Reads the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP"""
        result = self.cmd('=MTR|'+motor)
        print(result)#,double(result[len(motor)+1:])
        return float(result[len(motor)+1:])

    def moveMotor(self,motor,dist,speed):
        """ Changes the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""
        
        result = self.cmd('&MTRARC|%s,%0.1f,%0.2f' % (motor,dist,speed))
        print(result)#,double(result[len(motor)+1:])
        return result == ACK

    def setExposure(self,xp):
        
        self.cmd('&EXPOSURE=%f'%xp)
        self.exposure = xp


    def setXYSize(self,Mode = 2):
        self.cmd('&IMGSIZEMODE|X=%d|Y=%d' %(Mode,Mode))
        
    def readBP(self):
        if time.time()-self.BPTakenTime  > .5:
            res = self.cmd('=FUNCRES|BRTPRF').split('|')
            print(res)
            BP = np.fromstring(res[1],sep=',')
            self.BPTakenTime = time.time()
            return BP
        return 0
        
    def takeBP(self,STEP=100,AVE=125):
        self.cmd('&BRTPRF|STEP=%d|AVE=%d' %(STEP,AVE))
        self.BPTakenTime = time.time()
        
    def setImageSizeMode(self,X=2,Y=2):
        
        self.cmd('&IMGSIZEMODE|X=%d|Y=%d' % (X,Y))

    def stopSplicerWithoutStageReset(self):
        self.cmd('$STOP')
        
    def zoomout(self):
        splicer.cmd('&OPTZOOM=ZOOMOUT')

    def zoomin(self):
        splicer.cmd('&OPTZOOM=ZOOMIN')


    def getImageSize(self):
        xsize = self.cmd('=IMGSIZE-X')
        #ysize = self.cmd('=IMGSIZE-Y')
        self.imageSize = {}
        self.imageSize['Y'] = np.array([float(s[2:]) for s in splicer.cmd('=IMGSIZE-Y').split('|')])
        self.imageSize['X'] = np.array([float(s[2:]) for s in splicer.cmd('=IMGSIZE-X').split('|')])
        

        k = self.cmd('=IMGSIZEMODE').split('|')
        self.imsmode = {k[0][0]:int(k[0][2]),k[1][0]:int(k[1][2])}
        
        self.immodeSize
        self.scale = {}
        self.scale['Y'] = self.imageSize['Y']/self.immodeSize[self.imsmode['Y']]
        self.scale['X'] = self.imageSize['X']/self.immodeSize[self.imsmode['X']]
        
    def MeasureXC(self,M='Y',col=240):
        #col = 240
        dia = self.cmd('=IMGLINEH-%s-V-%d' % (M,col))
        xc = np.fromstring(dia[9:],sep=',')
        return xc
        
    def Diameter(self,M='X'):
        """Measure diameter of fiber using dumb way
        Make sure to call getImageSize First"""

        def fiberwidth(x):
            f    = np.abs(np.diff(x)) 
            a    = np.nonzero(f>15)
            try:
                return  (a[0][-1]-a[0][0])*self.scale[M][1]
            except:
                return 0. 
        
        col = 240
        dia = self.cmd('=IMGLINEH-%s-V-%d' % (M,col))
        xc = np.fromstring(dia[9:],sep=',')
        return fiberwidth(xc)
        
        return result

    def homeTheta(self):
        TL,TR = self.readTLTR()
        meanAngle = .5*(TL+TR)
        dist = meanAngle % 360
        print(dist)
        return self.spin(-dist,.1)
        
    def CaptureLiveImg(self,FileName):
        
        
        for Cam in 'X','Y':
            b = splicer.usb.CommandAndReceiveBinary('=IMGH-LIVE-%s'%Cam,1000)
    
            try:
                os.makedirs(os.path.dirname(FileName))
            except OSError:
                pass
            print(('SAVING TO PATH',os.path.normpath(FileName+Cam+'.bmp')))
            File.WriteAllBytes(os.path.normpath(FileName+Cam+'.bmp'),b)
        
    def CaptureLiveImg2(self,FileName,Cam='X'):
        
        #CAN LOOP THROUGH THE BYTE ARRAY
        
        b = splicer.usb.CommandAndReceiveBinary('=IMGH-LIVE-%s'%Cam,1000)

        try:
            os.makedirs(os.path.dirname(FileName))
        except OSError:
            pass

        File.WriteAllBytes(os.path.normpath(FileName),b)

        
    def resetTheta(self,mtr_list=['TL','TR']):
        
        TM = self.readTLTR()
        
        print(TM)
        M = [ (360- (m % 360))-110 for m in TM ]
        MM = {'TL':M[0],'TR':M[1]}   
        print(MM)
        for mtr in mtr_list:
            self.moveMotor(mtr,MM[mtr],.05)
        
        
        time.sleep(3)
        TM = self.readTLTR()
        
        print(TM)
        M = [ (360- (m % 360)) for m in TM ]
        MM = {'TL':M[0],'TR':M[1]}   
        print(MM)
        for mtr in mtr_list:
            self.moveMotor(mtr,MM[mtr],.1)
            
            
        #self.cmd("$RESETTH")

    def readTLTR(self):
        TL = self.cmd('=MTR|TL')
        TR = self.cmd('=MTR|TR')
        
        res = float(TL[3:]),float(TR[3:])
        #self.Moving = not( self.lastZLZR == res )
        #self.lastZLZR = res
        return res
        
    def readXY(self):
        TL = self.cmd('=MTR|X')
        TR = self.cmd('=MTR|Y')
        
        res = float(TL[3:]),float(TR[3:])
        #self.Moving = not( self.lastZLZR == res )
        #self.lastZLZR = res
        return res
    
    def readZLZR(self):
        ZL = self.cmd('=MTR|ZL')
        ZR = self.cmd('=MTR|ZR')
        #ARC = self.cmd('=MTR|ARC')
        #print 'arc',ARC
        
        try:
            res = float(ZL[3:]),float(ZR[3:])
            self.Moving = not( self.lastZLZR == res )
            self.lastZLZR = res
      #      print ZL,ZR
        except:
            print('Could not read ZL,ZR',ZL,ZR)
            

        return self.lastZLZR
#        return float(ZL[3:]),float(ZR[3:])

    def moveZLZR(self,dL,sL,dR,sR):
        """ Changes the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()
        
        
        dL = float(dL*10)/10
        dR = float(dR*10)/10
        
        ZLend = ZL+dL
        ZRend = ZR+dR
        if ( ZLend <= -abs(self.threshold)) & ( ZRend <= -abs(self.threshold)):         
            result = self.cmd('&MTRARC|ZL,%0.1f,%0.3f|ZR,%0.1f,%0.3f' % (dL,sL,dR,sR))
            #print 'move'
            if result == ACK:
                return ZLend,ZRend                
            self.lastmove = (ZLend, ZRend)
            #raise 
            #return result == ACK
        else:
            print('NOT MOVING MOTORS')
            ZLm = -abs(self.threshold)-ZL
            ZRm = -abs(self.threshold)-ZR
            raise ZLZRDanger((ZLm,ZRm))
            return 1
    def updateZLZR(self,dL,dR):
        """ Changes the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()
        
        
        dL = float(dL*10)/10
        dR = float(dR*10)/10
        
        ZLend = ZL+dL
        ZRend = ZR+dR
        if ( ZLend <= -abs(self.threshold)) & ( ZRend <= -abs(self.threshold)):         
            result = self.cmd('&MTRARC|ZL,%0.1f,|ZR,%0.1f,' % (dL,dR))
            #print 'move'
            if result == ACK:
                return ZLend,ZRend                
            self.lastmove = (ZLend, ZRend)
            #raise 
            #return result == ACK
        else:
            print('NOT MOVING MOTORS')
            ZLm = -abs(self.threshold)-ZL
            ZRm = -abs(self.threshold)-ZR
            raise ZLZRDanger((ZLm,ZRm))
            return 1            
            
    def updateVLVR(self,sL,sR):
        """ Changes the motor velocity
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()
        
        
        #if ( ZLend <= -abs(self.threshold)) & ( ZRend <= -abs(self.threshold)):         
        result = self.cmd('&MTRARC|ZL,,%0.3f|ZR,,%0.3f' % (sL,sR))
        #print 'move'
        if result == ACK:
            return ZLend,ZRend                
        #self.lastmove = (ZLend, ZRend)
            
    def updateZR(self,dR,sR):
        """ Changes the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()
        
        
#        dL = float(dL*10)/10
        dR = float(dR*10)/10
        
#        ZLend = ZL+dL
        ZRend = ZR+dR
        if (  ZRend <= -abs(self.threshold)):         
            result = self.cmd('&MTRARC|ZR,%0.1f,%0.3f' % (dR,sR))
        else:
            return 1

    def updateZL(self,dR,sR):
        """ Changes the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()
        
        
#        dL = float(dL*10)/10
        dR = float(dR*10)/10
        
#        ZLend = ZL+dL
        ZRend = ZR+dR
        if (  ZRend <= -abs(self.threshold)):         
            result = self.cmd('&MTRARC|ZL,%0.1f,%0.3f' % (dR,sR))
        else:
            return 1

            
    def absZLZR(self,L,sL,R,sR):
        """ Changes the motor position to absolutep position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()

#        dL = round(dL*10)/10
#        dR = round(dR*10)
        dL = round((L-ZL)*10)/10
        dR = round((R-ZR)*10)/10
        #dL = float( '%0.1f' % (L-ZL))
        #dR = float( '%0.1f' % (R-ZR)      )
        # THESE NEED TO BE ROUNDED
        
        #print 'absolute move DL,DR',dL,dR,ZL,ZR
        ZLend = ZL+dL
        ZRend = ZR+dR
        if ( ZLend <= -abs(self.threshold)) & ( ZRend <= -abs(self.threshold)):   
            result = self.cmd('&MTRARC|ZL,%0.1f,%0.3f|ZR,%0.1f,%0.3f' % (dL,sL,dR,sR))
            
            self.lastmove = (ZLend, ZRend)
            #print 'lastmove',self.lastmove
            #print result
            #if result == ACK:
            return ZLend,ZRend                
            #raise 
            #return result == ACK
        else:
            print('NOT MOVING MOTORS')
            ZLm = -abs(self.threshold)-ZL
            ZRm = -abs(self.threshold)-ZR
            raise ZLZRDanger((ZLm,ZRm))
            return 1

    def spin(self,dist,speed=.01):
        """spin motors 
        speed is always positive
        distance can be negative"""
        speed = abs(speed) # no monkey business
        if speed > .15: speed = .15
        result = self.cmd('&MTRARC|TL,%0.1f,%0.3f|TR,%0.1f,%0.3f' % (dist,speed,dist,speed))
        return result == ACK
    def spinL(self,dist,speed=.01):
        """spin motors 
        speed is always positive
        distance can be negative"""
        speed = abs(speed) # no monkey business
        if speed > .15: speed = .15
        result = self.cmd('&MTRARC|TL,%0.1f,%0.3f' % (dist,speed))
        return result == ACK
    def spinR(self,dist,speed=.01):
        """spin motors 
        speed is always positive
        distance can be negative"""
        speed = abs(speed) # no monkey business
        if speed > .15: speed = .15
        result = self.cmd('&MTRARC|TR,%0.1f,%0.3f' % (dist,speed))
        return result == ACK

    def arc(self,dur,bit):
        """arc laser for dur, with power bit"""
        #print 'arc cmd', '&MTRARC|ARC,%d,%dBIT' %(dur,bit)
        
        result = self.cmd('&MTRARC|ARC,%d,%dBIT' %(dur,bit))
        self.lastarc = (dur,bit) ## KEEP TRACK FOR RECORDING THE TAPER
        return result == ACK

    def arcP(self,bit):
        """only change the arc bit"""
        #print 'arc cmd', '&MTRARC|ARC,%d,%dBIT' %(dur,bit)
        
        result = self.cmd('&MTRARC|ARC,,%dBIT' %(bit))
        dur = self.lastarc[0]
        self.lastarc = (dur,bit) ## KEEP TRACK FOR RECORDING THE TAPER
        return result == ACK

    
    def stop(self):
        self.cmd('&MTRARC|STOP')
        
    def stopSpin(self):
        """spin motors"""
        result = self.cmd('&MTRARC|TL,0|TR,0' % (dist,speed,dist,speed))
        return result == ACK

splicer = Splicer()



