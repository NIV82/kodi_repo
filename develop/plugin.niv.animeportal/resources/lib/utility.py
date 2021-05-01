# -*- coding: utf-8 -*-
import sys

def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params)-1] == '/'):
			params = params[0:len(params)-2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]
	return param

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
