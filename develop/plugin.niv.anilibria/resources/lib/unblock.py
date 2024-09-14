# -*- coding: utf-8 -*-

try:
    from urllib.request import Request
    from urllib.request import urlopen 
except ImportError: 
    from urllib2 import Request  
    from urllib2 import urlopen
    #from urllib import Request
    #from urllib import urlopen

def get_antizapret_proxy(pac_url=None):
    if pac_url == None:
        pac_url = 'https://p.thenewone.lol:8443/proxy.pac'

    req = Request(pac_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0')

    proxy_pac = urlopen(req).read()

    try:
        proxy_pac = str(proxy_pac, encoding='utf-8')
    except:
        pass

    proxy = proxy_pac[proxy_pac.find('PROXY ')+6:]
    proxy = proxy[:proxy.find('; DIRECT')]
    proxy = proxy.strip()

    return proxy