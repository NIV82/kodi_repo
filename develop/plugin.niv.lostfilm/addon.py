# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import lostfilm

if __name__ == '__main__':
    lostfilm.start()

#import gc
#import os
#import sys
#import xbmc 

# version = xbmc.getInfoLabel('System.BuildVersion')[:2]
# try:
#     version = int(version)
# except:
#     version = 0

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

# if __name__ == "__main__":
#     if version >= 20:
#         import lostfilm_nexus
#         lostfilm_nexus.start()
#     if version == 19:
#         import lostfilm_matrix
#         lostfilm_matrix.start()
#     if version <= 18:
#         import lostfilm_leia
#         lostfilm_leia.start()
        
#gc.collect()