# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import cookielib

class WebTools:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def __init__(self, use_auth=False, auth_state=False, proxy_data=None):
        self.use_auth = use_auth
        self.proxy_data = proxy_data
        self.download_dir = None

        self.proxy = urllib2.ProxyHandler(self.proxy_data)

        if self.use_auth:
            self.cj = cookielib.MozillaCookieJar()
            self.cookie = urllib2.HTTPCookieProcessor(self.cj)            
            self.url_opener = urllib2.build_opener(self.cookie, self.proxy)
            self.auth_state = auth_state
            self.sid_file = ''            
            self.auth_url = 'https://www.anilibria.tv/public/login.php'
            self.auth_post_data = {}
        else:
            self.url_opener = urllib2.build_opener(self.proxy)

    def get_html(self, target, referer='', post=None):
        WebTools.headers['Referer'] = referer

        if self.use_auth:
            if not self.authorization():
                return None
        try:
            url = self.url_opener.open(urllib2.Request(url=target, data=post, headers=WebTools.headers))            
            data = url.read()
            return data        
        except urllib2.HTTPError as err:
            return err.code

    def get_file(self, target, referer='', post=None, dest_name=None):
        if not self.download_dir:
            return None
        WebTools.headers['Referer'] = referer
        try:
            if not dest_name:
                dest_name = os.path.basename(target)
            url = self.url_opener.open(urllib2.Request(url=target, data=post, headers=WebTools.headers))
            fl = open(os.path.join(self.download_dir, dest_name), "wb")
            fl.write(url.read())
            fl.close()
            return os.path.join(self.download_dir, dest_name)
        except urllib2.HTTPError as err:
            return err.code

    def authorization(self):
        if not self.use_auth or self.sid_file == '':
            return False
        
        if self.auth_state:
            try:
                self.cj.load(self.sid_file)
                auth = True
            except:
                data = self.url_opener.open(urllib2.Request(self.auth_url, urllib.urlencode(self.auth_post_data), WebTools.headers))
                response = data.read()
                
                if 'success' in response:
                    auth = True
                    self.cj.save(self.sid_file)
                else:
                    auth = False
        else:
            data = self.url_opener.open(urllib2.Request(self.auth_url, urllib.urlencode(self.auth_post_data), WebTools.headers))
            response = data.read()
            
            if 'success' in response:
                auth = True
                self.cj.save(self.sid_file)
            else:
                auth = False

        self.auth_state = auth
        return auth