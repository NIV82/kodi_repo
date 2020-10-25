# -*- coding: utf-8 -*-

import os
import urllib
import urllib2

class WebTools:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Accept-Charset': 'UTF-8',
        'Accept': 'text/html',
        'Connection': 'keep-alive'
    }
    
    def __init__(self, proxy_data=None):
        self.proxy_data = proxy_data
        self.download_dir = None        
        self.proxy = urllib2.ProxyHandler(self.proxy_data)
        self.url_opener = urllib2.build_opener(self.proxy)

    def get_html(self, target):
        try:
            url = self.url_opener.open(urllib2.Request(url=target, headers=WebTools.headers))            
            data = url.read()
            return data        
        except urllib2.HTTPError as err:
            return err.code

    def get_file(self, target, dest_name=None):
        if not self.download_dir:
            return None
        try:
            if not dest_name:
                dest_name = os.path.basename(target)
            url = self.url_opener.open(urllib2.Request(url=target, headers=WebTools.headers))
            fl = open(os.path.join(self.download_dir, dest_name), "wb")
            fl.write(url.read())
            fl.close()
            return os.path.join(self.download_dir, dest_name)
        except urllib2.HTTPError as err:
            return err.code