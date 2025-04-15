# -*- coding: utf-8 -*-

    # import ssl
    # ssl._create_default_https_context = ssl._create_unverified_context

import socket
from urllib.parse import urlencode
from urllib.request import ProxyHandler
from urllib.request import HTTPCookieProcessor
from urllib.request import build_opener
from urllib.request import Request
from urllib.request import urlopen
from http.cookiejar import MozillaCookieJar

socket.setdefaulttimeout(4)

def get_web(url, post=None, bytes=False):
    if post:
        try:
            post = post.encode(encoding='utf-8')
        except:
            pass

    headers = {
        'User-Agent': 'Kodi TV Show scraper by Team Kodi; contact pkscout@kodi.tv',
        'Accept': 'application/json'
        }

    try:
        request = Request(url=url, data=post, headers=headers)
        #request.add_header('User-Agent', 'Kodi TV Show scraper by Team Kodi; contact pkscout@kodi.tv')
        
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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 OPR/46.0.2597.39',
            'Referer' : 'https://redheadsound.studio/'
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

    def get_bytes(self, url=None, post=None):
        """GET BYTE-DATA IMPLEMENTATION"""
        if url is None:
            return None

        if post:
            post = urlencode(post)
            post = post.replace('%27','%22')
            post = post.encode('utf-8')

        try:
            request = Request(url=url, data=post, headers=self.headers)
            connection = self.url_opener.open(request)

            data = connection.read()

            content_encoding = connection.getheader('Content-Encoding')
            content_type = connection.getheader('Content-Type')
            connection_status = connection.status
            connection_reason = connection.reason

            connection.close()

            # if content_encoding == 'br':
            #     try:
            #         data = brotli_dec(data=data)
            #         content_encoding = 'br_decoded'
            #     except Exception as err: # pylint: disable=broad-except
            #         connection_reason = f"br_decode error | {err}"

            # if content_encoding == 'gzip':
            #     try:
            #         data = gzip.decompress(data).decode("utf-8")
            #         content_encoding = 'gzip-encoded'
            #     except Exception as err: # pylint: disable=broad-except
            #         connection_reason = f"gzip-decode error | {err}"

            result = {
                'content_type': content_type,
                'content_encoding': content_encoding,
                'connection_status': connection_status,
                'connection_reason': connection_reason,
                'content': data
            }

            return result
        except Exception as err: # pylint: disable=broad-except
            return err

    # def get_bytes(self, url, post=None):
    #     try:
    #         post = post.encode(encoding='utf-8')
    #     except:
    #         pass

    #     try:
    #         request = Request(url=url, data=post, headers=self.headers)
    #         connection = self.url_opener.open(request)

    #         data = connection.read()
    #         connection.close()

    #         return data
    #     except:
    #         return False

    def get_file(self, url, post=None, destination_name=None):
        try:
            url = self.url_opener.open(Request(url=url, data=post, headers=self.headers))
            with open(destination_name, 'wb') as write_file:
                write_file.write(url.read())
            return destination_name
        except:
            return False