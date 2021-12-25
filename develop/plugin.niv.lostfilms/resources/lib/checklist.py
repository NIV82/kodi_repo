# -*- coding: utf-8 -*-
import os

import xbmc
def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    return

class CheckList:
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir

    def create_item(self, file_path, code=''):
        code = code.encode(encoding="utf-8", errors="strict")
        
        with open(file_path, 'wb') as write_file:
            write_file.write(code)

        return
    
    def check_item(self, file_path, se_code):
        code = '{}{}'.format(se_code[1],se_code[2])
        
        with open(file_path, 'rb') as read_file:
            item_line = read_file.read()
        item_line = item_line.decode(encoding='utf-8', errors='strict')

        return True if code in item_line else False
    
    def is_watched(self, se_code):
        file_path = os.path.join(self.watch_dir, se_code[0])
        
        if not os.path.isfile(file_path):
            #self.create_item(file_path)
            return False
        else:
            check_status = self.check_item(file_path, se_code)
            return check_status

        
        #return True if check_file else False
    
