# -*- coding: utf-8 -*-
import sys, base64

def clean_list(data):
    clean_list = ['\n', '\t', '\r', '\v', '\f', '  ']
    for value in clean_list:
        data = data.replace(value, '')
    return data

def clean_tags(data, tag_start='<', tag_end='>'):
    start = data.find(tag_start)
    end = data.find(tag_end)
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '').strip()
        start = data.find(tag_start)
        end = data.find(tag_end)
    return data

def fs_dec(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode(sys_enc).encode('utf-8')

def fs_enc(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode('utf-8').encode(sys_enc)

def get_index(torrent_file, index):    
    valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
    
    with open(torrent_file, 'rb') as read_file:
        torrent_data = read_file.read()
    
    import bencode
    torrent = bencode.bdecode(torrent_data)

    series = []

    if 'files' in torrent['info']:
        for i, x in enumerate(torrent['info']['files']):            
            extension = x['path'][-1][x['path'][-1].rfind('.'):]

            if extension in valid_media:
                # if 'Ghostfacers.Promo' in x['path'][-1]:
                #     continue                
                series.append([x['path'][-1], i])
                
        series.sort()

        real_index = series[index][1]
    else:
        real_index = 0
    
    return real_index

def is_libreelec():
    import os
    try:
        if os.path.isfile('/etc/os-release'):
            f = open('/etc/os-release', 'r')
            str = f.read()
            f.close()
            if "LibreELEC" in str and "Generic" in str:
                return True
    except: pass
    return False

def rt(s):
    try:
        s=s.decode('utf-8')
    except:
        pass
    
    if not is_libreelec():
        try:
            s=s.decode('windows-1251')
        except:
            pass

    try:
        s=s.encode('utf-8')
    except:
        pass
    
    return s

def torrent2magnet(torrent_file):
    import hashlib, bencode
        
    if sys.version_info.major > 2:
        from urllib.parse import quote
    else:
        from urllib import quote
    
    with open(torrent_file, 'rb') as read_file:
        torrent_data = read_file.read()

    metainfo = bencode.bdecode(torrent_data)

    announce=''
    if 'announce' in metainfo.keys():
        announce = '&tr={}'.format(quote(metainfo['announce']))
    if 'announce-list' in metainfo.keys():
        try:
            for data in metainfo['announce-list']:
                announce = '{}&tr={}'.format(announce, quote(data[0]))
        except:
            pass
        
    infohash = hashlib.sha1(bencode.bencode(metainfo['info'])).hexdigest()
    magneturi = 'magnet:?xt=urn:btih:{}&dn={}{}'.format(infohash, quote(rt(metainfo['info']['name'])),announce)
    
    return magneturi