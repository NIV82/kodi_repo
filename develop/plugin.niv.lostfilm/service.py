# -*- coding: utf-8 -*-

import time
#import sys
#import os

import xbmc

xbmc.log("======================", level=xbmc.LOGFATAL)
xbmc.log("start", level=xbmc.LOGFATAL)
xbmc.log("======================", level=xbmc.LOGFATAL)

#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            break
        xbmc.log("hello addon! %s" % time.time(), level=xbmc.LOGFATAL)