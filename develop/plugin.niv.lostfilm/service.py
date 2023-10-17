# -*- coding: utf-8 -*-

import os
import sys

import xbmc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import media_library

if __name__ == '__main__':
    xbmc.sleep(10)
    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        media_library.create_update_library()

        if monitor.waitForAbort(3600):
            break