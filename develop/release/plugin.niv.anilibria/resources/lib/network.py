# -*- coding: utf-8 -*-

try:
    from urllib2 import ProxyHandler
    from urllib2 import HTTPCookieProcessor
    from urllib2 import build_opener
    from urllib2 import Request
    from urllib2 import urlopen
    from cookielib import MozillaCookieJar
except:
    from urllib.request import ProxyHandler
    from urllib.request import HTTPCookieProcessor
    from urllib.request import build_opener
    from urllib.request import Request
    from urllib.request import urlopen
    from http.cookiejar import MozillaCookieJar

def get_web(url, bytes=False):
    try:
        request = Request(url)
        request.add_header(
            'User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0')
        content = urlopen(request)
        html = content.read()
        content.close()

        if not bytes:
            try:
                html = html.decode(encoding='utf-8', errors='replace')
            except:
                pass

        return html
    except:
        return False

class WebTools:
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None):
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0'}
        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        #     'Accept': '*/*',
        #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'Accept-Charset': 'utf-8',
        #     'Accept-Encoding': 'identity'
        #     }
        self.auth_usage = auth_usage
        self.proxy_data = proxy_data

        if self.auth_usage:
            self.mcj = MozillaCookieJar()
            self.url_opener = build_opener(HTTPCookieProcessor(self.mcj), ProxyHandler(self.proxy_data))
            self.auth_status = auth_status
            self.sid_file = None
            self.auth_url = None
            self.auth_post_data = None
        else:
            self.url_opener = build_opener(ProxyHandler(self.proxy_data))

    def get_html(self, url, post=None):
        if self.auth_usage and not self.auth_check():
            return None

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

    # def auth_check(self):
    #     if self.portal == None:
    #         return False
    #     if 'anidub' in self.portal:
    #         return self.anidub_authorization()
    #     return

    # def anidub_authorization(self):
    #     if not self.auth_usage or not self.sid_file or not self.auth_url:
    #         return False

    #     try:
    #         post_data = bytes(self.auth_post_data, encoding='utf-8')
    #     except:
    #         post_data = self.auth_post_data

    #     if self.auth_status:
    #         try:
    #             self.mcj.load(self.sid_file)
    #             if 'dle_user_id' in str(self.mcj):
    #                 auth = True
    #             else:
    #                 auth = False
    #         except:
    #             self.url_opener.open(Request(self.auth_url, post_data, self.headers))
    #             if 'dle_user_id' in str(self.mcj):
    #                 auth = True
    #             else:
    #                 auth = False
    #             self.mcj.save(self.sid_file)
    #     else:
    #         self.url_opener.open(Request(self.auth_url, post_data, self.headers))
    #         if 'dle_user_id' in str(self.mcj):
    #             auth = True
    #         else:
    #             auth = False
    #         self.mcj.save(self.sid_file)

    #     self.auth_status = auth
        
    #     return auth