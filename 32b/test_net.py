# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:56:50 2014

@author: LZM100.00014
"""


import sys

sys.path.append(r'C:\Users\LZM100.00014\splicer_comm')
import clr


clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import Form,Application
c = Form()

from System import Reflection 
full_filename = clr.FindAssembly('UsbFsm100Server') 
clr.AddReference('UsbCoreFsm100')
clr.AddReference('UsbFsm100Server')
#print full_filename
#Reflection.Assembly.LoadFile(full_filename) 


#from clr.System.Reflection import Assembly
#b = clr.AddReference('UsbFsm100Server')
#clr.AddReferenceToFile('UsbFsm100Server.dll')
#from clr.UsbFsm100Server import UsbFsm100ServerClass

#Application.Run(c)
import win32gui


def my_handler(source, args):
        print('my_handler called!')
        
        
hwnd = win32gui.FindWindow("XLMAIN","")
a = clr.UsbFsm100ServerClass( c.Handle )

a.Attached += my_handler
a.Detached += my_handler

a.InitDriver(c.Handle)
print(a.ConnectionStatus)

#import UsbFsm100ServerClass
#from UsbFsm100Server import *
#clr.AddReferenceToFile('UsbFsm100Server.dll') 

#from UsbFsm100Server import UsbFsm100ServerClass
#clr.AddReference('UsbFsm100ServerClass')

#import UsbFsm100Server
#from b import UsbFsm100ServerClass
#import UsbFsm100ServerClass

#from MyNamespace import MyClass
#my_instance = MyClass()
#import 