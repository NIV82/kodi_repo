# -*- coding: utf-8 -*-

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
    import sys
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode(sys_enc).encode('utf-8')

def fs_enc(path):
    import sys
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
                series.append([x['path'][-1], i])
                
        series.sort()

        real_index = series[index][1]
    else:
        real_index = 0
    
    return real_index