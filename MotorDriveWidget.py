# -*- coding: utf-8 -*-
"""
Created on Wed Dec 31 09:30:29 2014

@author: LZM100.00014
"""

from pyqtgraph.Qt import QtGui, QtCore

class MoveMotorWidget(QtGui.QWidget):
    def __init__(self,splicer=None):
        super(MoveMotorWidget, self).__init__()
        
        self.splicer = splicer
        self.taper = None
        
        
        hbox = QtGui.QGridLayout()
        hbox2 = QtGui.QHBoxLayout()

        ## add buttons
        button = QtGui.QPushButton("<")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,3,2)

        ## add buttons
        button = QtGui.QPushButton("<<")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,3,1)

        ## add buttons
        button = QtGui.QPushButton(">")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,3,5)

        ## add buttons
        button = QtGui.QPushButton(">>")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,3,6)

        ## add buttons
        button = QtGui.QPushButton("^")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,2,3)

        ## add buttons
        button = QtGui.QPushButton("^^")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,1,3)
        
                ## add buttons
        button = QtGui.QPushButton("-")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,5,3)

        ## add buttons
        button = QtGui.QPushButton("--")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,6,3)

#==============================================================================
# ZMOTOR
#==============================================================================

                ## add buttons
        button = QtGui.QPushButton("ZL-")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,7,2)

        ## add buttons
        button = QtGui.QPushButton("ZL--")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,7,1)
        


                ## add buttons
        button = QtGui.QPushButton("ZL+")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,7,4)

        ## add buttons
        button = QtGui.QPushButton("ZL++")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,7,5)
        
                ## add buttons
        button = QtGui.QPushButton("ZR-")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,8,2)

        ## add buttons
        button = QtGui.QPushButton("ZR--")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,8,1)
        


                ## add buttons
        button = QtGui.QPushButton("ZR+")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,8,4)

        ## add buttons
        button = QtGui.QPushButton("ZR++")        
        button.clicked.connect(self.motorMove)
        hbox.addWidget(button,8,5)
        
        
        
        
        self.setLayout(hbox2) 
        
        hbox2.addLayout(hbox)
#==============================================================================
#         MTR GRID OVER
#==============================================================================
        zb = QtGui.QGridLayout()

        button = QtGui.QPushButton("1")        
        button.clicked.connect(self.ZB)
        zb.addWidget(button,1,1)
        self.setLayout(hbox2) 
        
        button = QtGui.QPushButton("2")        
        button.clicked.connect(self.ZB)
        zb.addWidget(button,1,2)
        self.setLayout(hbox2) 
        
        button = QtGui.QPushButton("3")        
        button.clicked.connect(self.ZB)
        zb.addWidget(button,1,3)
        self.setLayout(hbox2) 
        
        button = QtGui.QPushButton("zoomin")        
        button.clicked.connect(self.splicer.zoomin)
        zb.addWidget(button,2,2)
        
        button = QtGui.QPushButton("zoomout")        
        button.clicked.connect(self.splicer.zoomout)
        zb.addWidget(button,2,1)
        
        button = QtGui.QPushButton("STOP")        
        button.clicked.connect(self.splicer.stopSplicerWithoutStageReset)
        zb.addWidget(button,2,3)


        hbox2.addLayout(zb)        
        self.setLayout(hbox2) 
       # self.setLayout(hbox2) 


        self.show()
        
    def ZB(self):
        button_text =str(self.sender().text())
        print(button_text)
        self.splicer.cmd('&IMGSIZEMODE|X=%s|Y=%s'%(button_text,button_text))        
        
    def motorMove(self):
        button_text =str(self.sender().text())
        print(button_text)
        
        mtrdict = {'<':'&MTRARC|X, -0.5, 0.01',
                   '<<':'&MTRARC|X, -5.0, 0.01',
                   '>':'&MTRARC|X, 0.5, 0.01',
                   '>>':'&MTRARC|X, 5.0, 0.01',
                   '^':'&MTRARC|Y, 0.5, 0.01',
                   '^^':'&MTRARC|Y, 5.0, 0.01',
                   '-':'&MTRARC|Y, -0.5, 0.01',
                   '--':'&MTRARC|Y, -5.0, 0.01',
                   'ZL-':'&MTRARC|ZL, -1, 0.01',
                   'ZL--':'&MTRARC|ZL, -5.0, 0.01',
                   'ZL+':'&MTRARC|ZL, 1, 0.01',
                   'ZL++':'&MTRARC|ZL, 5.0, 0.01',
                   'ZR-':'&MTRARC|ZR, -1, 0.01',
                   'ZR--':'&MTRARC|ZR, -5.0, 0.01',
                   'ZR+':'&MTRARC|ZR, 1, 0.01',
                   'ZR++':'&MTRARC|ZR, 5.0, 0.01',}
                   
                   
        

        self.splicer.cmd(mtrdict[button_text])
            
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    from  LZM100 import splicer
    w = MoveMotorWidget(splicer)
    
    w.show()
    
    sys.exit(app.exec_())