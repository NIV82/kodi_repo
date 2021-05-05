# -*- coding: utf-8 -*-

from urllib.request import ProxyHandler
from urllib.request import HTTPCookieProcessor
from urllib.request import build_opener
from urllib.request import Request
from urllib.request import HTTPError
from http.cookiejar import MozillaCookieJar

class WebTools:
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None, portal=None):
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
        self.portal = portal

        if self.auth_usage:
            self.mcj = MozillaCookieJar()
            self.hcp = HTTPCookieProcessor(self.mcj)            
            self.url_opener = build_opener(self.hcp, self.proxy)
            self.auth_status = auth_status
            self.sid_file = ''
            self.auth_url = ''
            self.auth_post_data = ''
        else:
            self.url_opener = build_opener(self.proxy)

    def get_html(self, target_name, post=None):
        if self.auth_usage and not self.auth_check():
            return None
            
        try: post = bytes(post, encoding='utf-8')
        except: pass

        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))
            data = url.read()

            try: data = data.decode('cp1251').encode('utf8')
            except: pass

            try: data = str(data, encoding='utf-8')
            except: pass
            
            return data
        except HTTPError as error:
            return error.code


    def get_file(self, target_name, post=None, destination_name=None):
        if self.auth_usage and not self.auth_check():
            return None
            
        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))
            with open(destination_name, 'wb') as write_file:
                write_file.write(url.read())
            return destination_name
        except HTTPError as error:
            return error.code

    def get_bytes(self, target_name, post=None):
        if self.auth_usage and not self.auth_check():
            return None

        try: post = bytes(post, encoding='utf-8')
        except: pass

        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))
            data = url.read()
            
            return data
        except HTTPError as error:
            return error.code

    def auth_check(self):
        if self.portal == None:
            return False
        if self.portal == 'anilibria':
             return self.anilibria_authorization()
        if self.portal == 'anidub':
            return self.anidub_authorization()
        if self.portal == 'anistar':
            return self.anistar_authorization()
        return

    def anilibria_authorization(self):
        if not self.auth_usage or self.sid_file == '':
            return False

        try: post_data = bytes(self.auth_post_data, encoding='utf-8')
        except: post_data = self.auth_post_data

        if self.auth_status:
            try:
                self.mcj.load(self.sid_file)
                auth = True
            except:
                data = self.url_opener.open(Request(self.auth_url, post_data, self.headers))
                response = data.read()

                try: response = str(response, encoding='utf-8')
                except: pass
                
                if 'success' in response:
                    auth = True
                    self.mcj.save(self.sid_file)
                else:
                    auth = False
        else:
            data = self.url_opener.open(Request(self.auth_url, post_data, self.headers))
            response = data.read()
            
            try: response = str(response, encoding='utf-8')
            except: pass

            if 'success' in response:
                auth = True
                self.mcj.save(self.sid_file)
            else:
                auth = False

        self.auth_status = auth
        return auth

    def anidub_authorization(self):
        try: post_data = bytes(self.auth_post_data, encoding='utf-8')
        except: post_data = self.auth_post_data

        if not self.auth_usage or self.sid_file == '' or self.auth_url == '':
            return False

        if self.auth_status:
            try:
                self.mcj.load(self.sid_file)
                auth = True if 'dle_user_id' in str(self.mcj) else False
            except:
                self.url_opener.open(Request(self.auth_url, post_data, self.headers))
                auth = True if 'dle_user_id' in str(self.mcj) else False
                self.mcj.save(self.sid_file)
        else:
            self.url_opener.open(Request(self.auth_url, post_data, self.headers))
            auth = True if 'dle_user_id' in str(self.mcj) else False
            self.mcj.save(self.sid_file)
        self.auth_status = auth
        return auth
    
    def anistar_authorization(self):
        try: post_data = bytes(self.auth_post_data, encoding='utf-8')
        except: post_data = self.auth_post_data

        if not self.auth_usage or self.sid_file == '' or self.auth_url == '':
            return False

        if self.auth_status:
            try:
                self.mcj.load(self.sid_file)
                auth = True if 'dle_user_id' in str(self.mcj) else False
            except:
                self.url_opener.open(Request(self.auth_url, post_data, self.headers))
                auth = True if 'dle_user_id' in str(self.mcj) else False
                self.mcj.save(self.sid_file)
        else:
            self.url_opener.open(Request(self.auth_url, post_data, self.headers))
            auth = True if 'dle_user_id' in str(self.mcj) else False
            self.mcj.save(self.sid_file)
        self.auth_status = auth
        return auth