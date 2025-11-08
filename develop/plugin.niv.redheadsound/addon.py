# -*- coding: utf-8 -*-

import gc
import os
import sys
#import httpx

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
#sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'resources/lib', 'external_libraries'))

import redheadsound 
if __name__ == "__main__":
    redheadsound.start()
        
gc.collect()