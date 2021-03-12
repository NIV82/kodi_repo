# -*- coding: utf-8 -*-

try:
    from urllib2 import ProxyHandler, HTTPCookieProcessor, build_opener, Request, HTTPError
    from cookielib import MozillaCookieJar
except:
    from urllib.request import ProxyHandler, HTTPCookieProcessor, build_opener, Request, HTTPError
    from http.cookiejar import MozillaCookieJar

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
        self.proxy = ProxyHandler(self.proxy_data)

        if self.auth_usage:
            self.mcj = MozillaCookieJar()
            self.hcp = HTTPCookieProcessor(self.mcj)            
            self.url_opener = build_opener(self.hcp, self.proxy)
            self.auth_status = auth_status
            self.sid_file = ''
            self.search_cookie_name = 'dle_user_id'
            self.auth_url = 'https://tr.anidub.com/'
            self.auth_post_data = ''
        else:
            self.url_opener = build_opener(self.proxy)

    def get_html(self, target_name, post=None):
        if self.auth_usage and not self.authorization():
            return None
        
        try: post = bytes(post, encoding='utf-8')
        except: pass

        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))            
            data = url.read()

            try: data = str(data, encoding='utf-8')
            except: pass

            return data        
        except HTTPError as error:
            return error.code

    def get_file(self, target_name, post=None, destination_name=None):
        if self.auth_usage and not self.authorization():
            return None
        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))
            with open(destination_name, 'wb') as write_file:
                write_file.write(url.read())                
            return destination_name
        except HTTPError as error:
            return error.code

    def authorization(self):
        try: post_data = bytes(self.auth_post_data, encoding='utf-8')
        except: post_data = self.auth_post_data

        if not self.auth_usage or self.sid_file == '' or self.auth_url == '':
            return False

        if self.auth_status:
            try:
                self.mcj.load(self.sid_file)
                auth = True if not str(self.mcj).find(self.search_cookie_name) == -1 else False
            except:
                self.url_opener.open(Request(self.auth_url, post_data, self.headers))
                auth = True if not str(self.mcj).find(self.search_cookie_name) == -1 else False
                self.mcj.save(self.sid_file)
        else:
            self.url_opener.open(Request(self.auth_url, post_data, self.headers))
            auth = True if not str(self.mcj).find(self.search_cookie_name) == -1 else False
            self.mcj.save(self.sid_file)
        self.auth_status = auth
        return auth