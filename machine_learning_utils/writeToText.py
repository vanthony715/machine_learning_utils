#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: avasquez
"""
import os

class WriteToText:
    
    '''Writes and saves to text file'''
    
    def __init__(self, filename, obj, desc = None):
        self.filename = filename
        self.desc = desc
        self.obj = obj

    def removeFile(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        else:
            pass
    
    def writeToFile(self):
        with open(self.filename, 'a') as f:
            if self.desc:
                f.write(self.desc)
                f.write('\n')
            f.write(self.obj)
                
        