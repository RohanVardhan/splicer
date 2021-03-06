# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 14:18:41 2014

@author: LZM100.00014
"""

import pythoncom
class PythonUtilities:
    _public_methods_ = [ 'SplitString' ]
    _reg_progid_ = "PythonDemos.Utilities"
    # NEVER copy the following ID

    # Use"print pythoncom.CreateGuid()" to make a new one.
    _reg_clsid_ = pythoncom.CreateGuid()
    print(_reg_clsid_)
    def SplitString(self, val, item=None):
        import string
        if item != None: item = str(item)
        return string.split(str(val), item)

# Add code so that when this script is run by
# Python.exe,.it self-registers.

if __name__=='__main__':        
    print('Registering Com Server')
    import win32com.server.register
    win32com.server.register.UseCommandLine(PythonUtilities)
