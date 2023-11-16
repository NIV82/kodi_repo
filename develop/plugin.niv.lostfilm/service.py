# -*- coding: utf-8 -*-

import os
import sys

import xbmc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import library.manage as manage

if __name__ == '__main__':
    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        manage.auto_update()

        if monitor.waitForAbort(3600):
            break