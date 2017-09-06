# -*- coding: utf-8 -*-
"""
Created on Wed May 11 08:27:37 2016

@author: LZM100.00014
"""

def gentest():
    print('RIGHT BEFORE STARTEd')
    yield 'STARTED'
    
    for i in range(2):
        gotjunk = yield i
        print(gotjunk)
        

b = gentest()
print(('init',b))
i = next(b)
print(i)
while True:
    try:
        i =  b.send('stuff we need to send')
    except StopIteration:
        break
    