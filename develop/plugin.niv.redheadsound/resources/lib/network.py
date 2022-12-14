# -*- coding: utf-8 -*-

import sys

try:
    from urllib2 import ProxyHandler, HTTPCookieProcessor, build_opener, Request
    from cookielib import MozillaCookieJar
except:
    from urllib.request import ProxyHandler, HTTPCookieProcessor, build_opener, Request
    from http.cookiejar import MozillaCookieJar
    
class WebTools:
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            # 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            # 'Accept-Charset': 'utf-8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            #'Referer': 'https://redheadsound.ru/'
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
            self.auth_url = ''
            self.auth_post_data = ''
        else:
            self.url_opener = build_opener(self.proxy)

    def get_html(self, url, post=None):
        try:
            post = post.encode(encoding='utf-8')
        except:
            pass

        try:
            request = Request(url=url, data=post, headers=self.headers)
            connection = self.url_opener.open(request)

            data = connection.read()
            connection.close()

            try:
                data = data.decode(encoding='utf-8', errors='replace')
            except:
                pass

            return data
        #except Exception as e:
            #return e
        except:
            return False
        
    def get_bytes(self, url, post=None):
        try:
            post = post.encode(encoding='utf-8')
        except:
            pass

        try:
            request = Request(url=url, data=post, headers=self.headers)
            connection = self.url_opener.open(request)

            data = connection.read()
            connection.close()

            return data
        # except Exception as e:
        #     return e
        except:
            return False
            
        
    # def get_file(self, target_name, post=None, destination_name=None):
    #     if self.auth_usage and not self.auth_check():
    #         return None
            
    #     try:
    #         url = self.url_opener.open(Request(url=target_name, data=post, headers=self.headers))
    #         with open(destination_name, 'wb') as write_file:
    #             write_file.write(url.read())
    #         return destination_name
    #     except HTTPError as error:
    #         return error.code