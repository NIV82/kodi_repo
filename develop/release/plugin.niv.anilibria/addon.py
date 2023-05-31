# -*- coding: utf-8 -*-

import gc
import os
import sys
import xbmc 

version = xbmc.getInfoLabel('System.BuildVersion')[:2]
try:
    version = int(version)
except:
    version = 0

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

if __name__ == "__main__":
    if version >= 20:
        import anilibria
        anilibria.start()
    if version == 19:
        import anilibria
        anilibria.start()
    if version <= 18:
        import anilibria
        anilibria.start()
        
gc.collect()