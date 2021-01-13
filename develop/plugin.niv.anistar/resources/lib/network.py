# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import cookielib

class WebTools:
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Charset': 'utf-8',
            'Accept-Encoding': 'identity'
            }

        self.auth_usage = auth_usage
        self.proxy_data = proxy_data
        self.proxy = urllib2.ProxyHandler(self.proxy_data)

        if self.auth_usage:
            self.mcj = cookielib.MozillaCookieJar()
            self.hcp = urllib2.HTTPCookieProcessor(self.mcj)            
            self.url_opener = urllib2.build_opener(self.hcp, self.proxy)
            self.auth_status = auth_status
            self.sid_file = ''
            self.auth_url = ''
            self.auth_post_data = {}
        else:
            self.url_opener = urllib2.build_opener(self.proxy)

    def get_html(self, target_name, post=None):
        # if self.auth_usage and not self.authorization():
        #     return None
        try:
            url = self.url_opener.open(urllib2.Request(url=target_name, data=post, headers=self.headers))            
            data = url.read()
            data = data.decode('cp1251').encode('utf8')
            return data
        except urllib2.HTTPError as err:
            return err.code

    def get_file(self, target_name, post=None, destination_name=None):
        # if self.auth_usage and not self.authorization():
        #     return None
        try:
            url = self.url_opener.open(urllib2.Request(url=target_name, data=post, headers=self.headers))
            with open(destination_name, 'wb') as write_file:
                write_file.write(url.read())
            return destination_name
        except urllib2.HTTPError as err:
            return err.code