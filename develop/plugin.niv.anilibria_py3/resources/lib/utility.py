# -*- coding: utf-8 -*-
import sys

def clean(data):
    clean_list = ['\n', '\t', '\r', '\v', '\f', '  ']
    for value in clean_list:
        data = data.replace(value, '')
    return data
    
def rep(data):
    rep_list = [('&amp;', '&'), ('&laquo;', '"'), ('&raquo;', '"'), ('&nbsp;', ' '), ('&mdash;', '-'), ('&ndash;', '-'),
                ('&hellip;', '...'), ('&copy;', '©'), ('&quot;', '"'), ('&apos;', '\''), ('&gt;', '>'), ('&lt;', '<'),
                ('&#8217;', '\''), ('&#8220;','“'), ('&#8221;','”'), ('&#039;', '\''), ('&#34;', '"'), ('&#39;', '\''), 
                ('‑', '-'), ('&ldquo;', '"'), ('&rdquo;', '"')]
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

def rbr(data):
    start = data.find('(')
    end = data.find(')')
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '').strip()
        start = data.find('(')
        end = data.find(')')
    return data

def sbr(data):
    start = data.find('[')
    end = data.find(']')
    while start < end and start > -1:
        data = data.replace(data[start:end+1], '').strip()
        start = data.find('[')
        end = data.find(']')
    return data