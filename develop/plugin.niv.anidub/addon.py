# -*- coding: utf-8 -*-

import gc
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import anidub_online

if __name__ == "__main__":
    anidub_online.start()

gc.collect()
