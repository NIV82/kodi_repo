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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            #'Accept': '*/*',
            #'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            #'Accept-Charset': 'utf-8',
            #'Accept-Encoding': 'identity',
            #'Content-Type': 'application/json'
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin':'https://www.lostfilm.tv/',
            'Referer': 'https://www.lostfilm.tv/'
            }
        
        self.auth_usage = auth_usage
        self.proxy_data = proxy_data
        self.proxy = ProxyHandler(self.proxy_data)

        if self.auth_usage:
            self.mcj = MozillaCookieJar()
            self.hcp = HTTPCookieProcessor(self.mcj)
            self.redirect = HTTPCookieProcessor()
                       
            self.url_opener = build_opener(self.hcp, self.proxy)
            self.auth_status = auth_status
            self.sid_file = ''
            self.auth_url = ''
            self.auth_post_data = ''
        else:
            self.url_opener = build_opener(self.proxy)

    def get_html(self, target_name, post=None):
        if self.auth_usage and not self.authorization():
            return None

        try: post = post.encode(encoding='utf-8')
        except: pass

        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))

            try: charset = url.headers.getparam('charset')
            except: charset = url.headers.get_content_charset()

            data = url.read()

            if charset:
                if not 'utf-8' in charset.lower():
                    data = data.decode(charset).encode('utf8')

            try: data = data.decode(encoding='utf-8', errors='replace')
            except: pass

            return data
        # except HTTPError as error:
        #     return error.code
        except HTTPError:
            return False
        
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

    def get_bytes(self, target_name, post=None):
        if self.auth_usage and not self.authorization():
            return None

        try: post = bytes(post, encoding='utf-8')
        except: pass

        try:
            url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))
            data = url.read()
            
            return data
        except HTTPError as error:
            return error.code

    def authorization(self):
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