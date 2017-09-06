# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 21:53:01 2014

@author: LZM100.00014
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In this example, we create a simple
window in PyQt4.

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""

import sys
from PyQt4 import QtGui
import win32gui

def main():
    
    app = QtGui.QApplication(sys.argv)

    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('NICK')
    w.show()
    hWnd = win32gui.FindWindow("NICK", None)
    print(hWnd)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()