# -*- coding: utf-8 -*-

def clean_tags(data, tag_start='<', tag_end='>'):
    start = data.find(tag_start)
    end = data.find(tag_end)
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '')
        start = data.find(tag_start)
        end = data.find(tag_end)
    return data.strip()
    