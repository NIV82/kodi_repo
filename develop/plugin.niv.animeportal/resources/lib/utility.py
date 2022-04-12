# -*- coding: utf-8 -*-
import sys, base64

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

# def clean_tags(data, tag_start, tag_end):
#     start = data.find(tag_start)
#     end = data.find(tag_end)
#     while start < end and start > -1:
#         data = data.replace(data[start:end+1], '').strip()
#         start = data.find(tag_start)
#         end = data.find(tag_end)
#     return data

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