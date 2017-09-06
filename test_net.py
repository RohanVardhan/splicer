# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:56:50 2014

@author: LZM100.00014
"""


import sys
sys.path.append(r'C:\Users\LZM100.00014\splicer_comm')
import clr
import System
from System import Reflection 
from System.Windows.Forms import Form,Application


Reflection.Assembly.LoadFile(r'C:\Users\LZM100.00014\splicer_comm\UsbCoreFsm100.dll') 
Reflection.Assembly.LoadFile(r'C:\Users\LZM100.00014\splicer_comm\UsbFsm100Server.dll') 

class ZLZRDanger(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

ACK = 0o6
class splicer():
    def __init__(self):
        
        c = Form()

        def attached(source, args):
            print('my_handler called!')
        def detached(source,args):
            print('Detatched')

        a = clr.UsbFsm100ServerClass(c.Handle  )

        
        a.Attached += attached
        a.Detached += detached
        self.usb = a      
        
        Application.Run(c)   
        
        self.threshold = 10000.
        
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
        
        result = self.cmd('&MTRARC|%s,%f0.1,%f0.2' % (motor,dist,speed))
        print(result)#,double(result[len(motor)+1:])
        return result == ACK

    def homeTheta(self):
        TL,TR = self.readTLTR()
        meanAngle = .5*(TL+TR)
        dist = meanAngle % 360
        print(dist)
        return self.spin(-dist,.1)

    def readTLTR(self):
        TL = self.cmd('=MTR|TL')
        TR = self.cmd('=MTR|TR')
        return float(TL[3:]),float(TR[3:])
    
    def readZLZR(self):
        ZL = self.cmd('=MTR|ZL')
        ZR = self.cmd('=MTR|ZR')
        return float(ZL[3:]),float(ZR[3:])

    
    def moveZLZR(self,dL,sL,dR,sR):
        """ Changes the motor position
        motors can be X, Y, ZL, ZR, TL, TR, ZSWP
        ZL,ZR can be -1800000 to 1800000 at .1, speed is 0.01 to 0.1
        X,Y, Step is .1"""        
        #Should Never Move the motor if it is less than the threshold.        
        ZL,ZR = self.readZLZR()
        
        ZLend = ZL+dL
        ZRend = ZR+dR
        if ( ZLend <= -abs(self.threshold)) & ( ZRend <= -abs(self.threshold)):         
            result = self.cmd('&MTRARC|ZL,%f0.1,%f0.3|ZR,%f0.1,%f0.3' % (dL,sL,dR,sR))
            if result == ACK:
                return ZLend,ZRend                
            raise 
            #return result == ACK
        else:
            print('NOT MOVING MOTORS')
            ZLm = -abs(self.threshold)-ZL
            ZRm = -abs(self.threshold)-ZR
            raise ZLZRDanger((ZLm,ZRm))
            return 1

    def spin(self,dist,speed=.01):
        """spin motors"""
        speed = abs(speed) # no monkey business
        if speed > .15: speed = .15
        result = self.cmd('&MTRARC|TL,%f0.1,%f0.3|TR,%f0.1,%f0.3' % (dist,speed,dist,speed))
        return result == ACK

    def arc(self,dur,bit):
        """arc laser for dur, with power bit"""
        result = self.cmd('&MTRARC|ARC,%d,%dBIT' %(dur,bit))
        return result == ACK

    
    def stop(self):
        self.cmd('&MTRARC|STOP')
        
    def stopSpin(self):
        """spin motors"""
        result = self.cmd('&MTRARC|TL,0|TR,0' % (dist,speed,dist,speed))
        return result == ACK

a = splicer()



