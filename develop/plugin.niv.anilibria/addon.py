# -*- coding: utf-8 -*-

import gc
import os
import sys
#import xbmc
import xbmcaddon

addon = xbmcaddon.Addon(id='plugin.niv.anilibria')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

if __name__ == "__main__":
    if '0' in addon.getSetting('alv_mode'):
        import alv1
        alv1.start()
        
    if '1' in addon.getSetting('alv_mode'):
        import alv3
        alv3.start()
        
gc.collect()