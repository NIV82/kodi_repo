# -*- coding: utf-8 -*-
import sys, base64

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)
    
def data_encode(data):
    data = data.encode('utf-8')
    data = base64.b64encode(data)
    data = data.decode('utf-8')
    return data

def data_decode(data):
    data = data.encode('utf-8')
    data = base64.b64decode(data)
    data = data.decode('utf-8')
    data = data.split('|')
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
    
def clean_list(data):
    clean_list = ['\n', '\t', '\r', '\v', '\f', '  ']
    for value in clean_list:
        data = data.replace(value, '')
    return data

def tag_list(data):
    start = data.find('<')
    end = data.find('>')
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '').strip()
        start = data.find('<')
        end = data.find('>')
    return data

def fix_list(data):
    fix_list = [("\\r\\n", '\n'),('\\n', '\n'),('\\"', '"'),('""', '"'),('<br><b>','<br> <b>')]
    for value in fix_list:
        data = data.replace(value[0], value[1])            
    return data

def digit_list(data):
    result = []
    for d in data:
        if d.isdigit():
            result.append(d)
    return ''.join(result)

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

def valid_media(data):
    valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
    
    for i in valid_media:
        if i in data:
            return True
        
    return False
#############################################################################################################################
# def rt(s):
#     try:s=s.decode('utf-8')
#     except: pass
#     if not is_libreelec():
#         try:s=s.decode('windows-1251')
#         except: pass
#     try:s=s.encode('utf-8')
#     except: pass
#     return s

# def is_libreelec():
#     try:
#         if os.path.isfile('/etc/os-release'):
#             f = open('/etc/os-release', 'r')
#             str = f.read()
#             f.close()
#             if "LibreELEC" in str and "Generic" in str: return True
#     except: pass
#     return False

# def READ(fn):
#     if sys.version_info.major > 2:
#         fl = open(fn, "rb")
#         r=fl.read()
#         fl.close()
#     else:
#         fl = xbmcvfs.File(fn)
#         r=fl.read()
#         fl.close()
#     return r

# #def t2m(url):
# def torrent2magnet(url):
#     if sys.version_info.major > 2:
#         from urllib.parse import quote
#     else:
#         from urllib import quote

#     try:
#         import bencode, hashlib
#         if url.startswith('http') or 'file:' in url: r = GET(url, cache = True)
#         else:
#             #r = READ(url)
#             with open(url, 'rb') as read_file:
#                 r = read_file.read()
                
#         metainfo = bencode.bdecode(r)
#         announce=''
#         if 'announce' in metainfo.keys(): announce='&tr='+quote(metainfo['announce'])
#         if 'announce-list' in metainfo.keys():
#             try:
#                 for ans in metainfo['announce-list']:
#                     announce=announce+'&tr='+quote(ans[0])
#             except:
#                 pass
#         infohash = hashlib.sha1(bencode.bencode(metainfo['info'])).hexdigest()
#         magneturi  = 'magnet:?xt=urn:btih:'+str(infohash)+'&dn='+quote(rt(metainfo['info']['name']))+announce
#         return magneturi
#     except Exception as e:
#         data_print(e)
#         if '/itorrents.org/' in url:
#             infohash = mfind(url, '/torrent/','.torrent')
#             if len(infohash)>30: return 'magnet:?xt=urn:btih:'+str(infohash)+'&dn='+str(infohash)
#         return url