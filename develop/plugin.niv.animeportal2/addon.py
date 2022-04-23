# -*- coding: utf-8 -*-

import os
import sys
import gc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import animeportal
    
if __name__ == "__main__":
    animeportal.start()
    
gc.collect()