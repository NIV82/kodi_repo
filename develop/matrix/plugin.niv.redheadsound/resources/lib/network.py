# -*- coding: utf-8 -*-

try:
    from urllib2 import ProxyHandler
    from urllib2 import HTTPCookieProcessor
    from urllib2 import build_opener
    from urllib2 import Request
    from cookielib import MozillaCookieJar
except:
    from urllib.request import ProxyHandler
    from urllib.request import HTTPCookieProcessor
    from urllib.request import build_opener
    from urllib.request import Request
    from http.cookiejar import MozillaCookieJar

class WebTools:
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None):
        self.headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
                    }
        
        self.auth_usage = auth_usage
        self.proxy_data = proxy_data

        self.mcj = MozillaCookieJar()
        self.url_opener = build_opener(HTTPCookieProcessor(self.mcj), ProxyHandler(self.proxy_data))
        self.auth_status = auth_status
        self.sid_file = None
        self.auth_url = None
        self.auth_post_data = None

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
        except:
            return False

    def get_file(self, url, post=None, destination_name=None):
        try:
            url = self.url_opener.open(Request(url=url, data=post, headers=self.headers))
            with open(destination_name, 'wb') as write_file:
                write_file.write(url.read())
            return destination_name
        except:
            return False