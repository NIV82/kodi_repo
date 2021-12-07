# -*- coding: utf-8 -*-
import sys

# def get_params():
# 	param = []
# 	paramstring = sys.argv[2]
# 	if len(paramstring) >= 2:
# 		params = sys.argv[2]
# 		cleanedparams = params.replace('?', '')
# 		if (params[len(params)-1] == '/'):
# 			params = params[0:len(params)-2]
# 		pairsofparams = cleanedparams.split('&')
# 		param = {}
# 		for i in range(len(pairsofparams)):
# 			splitparams = {}
# 			splitparams = pairsofparams[i].split('=')
# 			if (len(splitparams)) == 2:
# 				param[splitparams[0]] = splitparams[1]
# 	return param

# def fs_dec(path):
#     sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
#     return path.decode(sys_enc).encode('utf-8')

# def fs_enc(path):
#     sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
#     return path.decode('utf-8').encode(sys_enc)
    
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
    fix_list = [('\\n', '\n'),('\\"', '"'),('""', '"'),('<br><b>','<br> <b>')]
    for value in fix_list:
        data = data.replace(value[0], value[1])            
    return data

def digit_list(data):
    result = []
    for d in data:
        if d.isdigit():
            result.append(d)
    return ''.join(result)

def rep_list(data, rep_data):
    rep_values = []
    rep_data = rep_data.split(',')

    for i in rep_data:
        i = i.split('|')
        rep_values.append((i[0], i[1]))
    
    for value in rep_values:
        data = data.replace(value[0], value[1])
    
    return data