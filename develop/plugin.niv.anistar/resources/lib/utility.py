# -*- coding: utf-8 -*-
import sys

def fs_dec(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode(sys_enc).encode('utf-8')

def fs_enc(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode('utf-8').encode(sys_enc)
        
def clean(data):
    clean_list = ['\n', '\t', '\r', '\v', '\f', '  ']
    for value in clean_list:
        data = data.replace(value, '')
    return data
    
def rep(data):
    rep_list = [('&#8748;',' '), ('&#9651;',' '),('&#9734;',' '),('&#9733;',' '),('&#9825;',' '),('&#333;','o'),
                ('&#215;', 'x'), ('&#8734;', ''), ('&nbsp;', ' '), ('&#8537;', ' '), ('&#9829;', ' '), ('&#936;', ''),
                ('&#252;', 'u'), ('&#215;', ''), ('&#363;', 'u'), ('&#249;', 'u'), ('[email&#160;protected]', 'Idolmaster'),
                ('„', '"'), ('“', '"'), ('&copy;', '©'), ('&nbsp;', ' '), ('&raquo;', '')
                ]
    for value in rep_list:
        data = data.replace(value[0], value[1])
    return data

def tag(data):
    start = data.find('<')
    end = data.find('>')
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '').strip()
        start = data.find('<')
        end = data.find('>')
    return data