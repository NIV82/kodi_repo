# -*- coding: utf-8 -*-
import sys

def clean_list(data):
    clean_list = ['\n', '\t', '\r', '\v', '\f', '  ']
    for value in clean_list:
        data = data.replace(value, '')
    return data

def clean_tags(data, tag_start, tag_end):
    start = data.find(tag_start)
    end = data.find(tag_end)
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '').strip()
        start = data.find(tag_start)
        end = data.find(tag_end)
    return data

# def fs_dec(path):
#     sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
#     return path.decode(sys_enc).encode('utf-8')

# def fs_enc(path):
#     sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
#     return path.decode('utf-8').encode(sys_enc)

def fs_dec(path):
    try:
        sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
        return path.decode(sys_enc).encode('utf-8')
    except:
        return path

def fs_enc(path):
    import xbmc
    path=xbmc.translatePath(path)
    
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    
    try:
        path2=path.decode('utf-8')
    except:
        pass
    
    try:
        path2=path2.encode(sys_enc)
    except:
        try:
            path2=path2.encode(sys_enc)
        except:
            path2=path
            
    return path2