# -*- coding: utf-8 -*-

import gc
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

if __name__ == "__main__":
    import anilibria
    anilibria.start()
        
gc.collect()
