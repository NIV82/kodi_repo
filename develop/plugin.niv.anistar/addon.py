# -*- coding: utf-8 -*-

import gc
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import anistar

if __name__ == "__main__":
    anistar.start()

gc.collect()
