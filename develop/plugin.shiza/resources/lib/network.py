# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import cookielib

class WebTools:
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
        'Accept': 'text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Accept-Charset': 'utf-8, utf-16, *;q=0.1',
        'Accept-Encoding': 'identity, *;q=0'
    }

    def __init__(self, use_auth=False, auth_state=False, proxy_data=None):
        self.use_auth = use_auth
        self.download_dir = None
        self.proxy_data = proxy_data

        self.proxy = urllib2.ProxyHandler(self.proxy_data)

        if self.use_auth:
            self.cj = cookielib.MozillaCookieJar()
            self.url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
            self.auth_state = auth_state
            self.sid_file = ''
            self.search_cookie_name = 'authautologin'
            self.auth_url = 'http://shiza-project.com/accounts/login'
            self.auth_post_data = {}
        else:
            self.url_opener = urllib2.build_opener()

    def get_html(self, target, referer='', post=None):
        if self.use_auth:
            if not self.authorization():
                return None

        WebTools.headers['Referer'] = referer

        try:
            url = self.url_opener.open(urllib2.Request(url=target, data=post, headers=WebTools.headers))            
            data = url.read()
            return data        
        except urllib2.HTTPError as err:
            return err.code

    def get_file(self, target, referer='', post=None, dest_name=None):
        if self.use_auth:
            if not self.authorization():
                return None

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
                auth = True if str(self.cj).find(self.search_cookie_name) > -1 else False
            except:
                self.url_opener.open(urllib2.Request(self.auth_url, urllib.urlencode(self.auth_post_data), WebTools.headers))
                auth = True if str(self.cj).find(self.search_cookie_name) > -1 else False
                self.cj.save(self.sid_file)
        else:
            self.url_opener.open(urllib2.Request(self.auth_url, urllib.urlencode(self.auth_post_data), WebTools.headers))
            auth = True if str(self.cj).find(self.search_cookie_name) > -1 else False
            self.cj.save(self.sid_file)
        self.auth_state = auth
        return auth