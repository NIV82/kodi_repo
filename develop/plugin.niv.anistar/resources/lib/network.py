# -*- coding: utf-8 -*-

import socket
from urllib.request import ProxyHandler
from urllib.request import HTTPCookieProcessor
from urllib.request import build_opener
from urllib.request import Request
from urllib.request import urlopen
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlencode

socket.setdefaulttimeout(3)

# def data_print(data):
#     import xbmc
#     xbmc.log(str(data), xbmc.LOGFATAL)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 OPR/46.0.2597.39',
}

def set_headers(headers):
    HEADERS.clear()
    HEADERS.update(headers)

class WebTools:
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None):
        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 OPR/46.0.2597.39',
        #     }
        #self.headers.update(headers)
        #data_print(self.headers)

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

    def get_bytes(self, url=None, post=None):
        """GET BYTE-DATA IMPLEMENTATION"""
        if url is None:
            return None

        if post:
            post = urlencode(post)
            post = post.replace('%27','%22')
            post = post.encode('utf-8')

        try:
            # request = Request(url=url, data=post, headers=self.headers)
            request = Request(url=url, data=post, headers=HEADERS)
            connection = self.url_opener.open(request)

            data = connection.read()

            content_encoding = connection.getheader('Content-Encoding')
            content_type = connection.getheader('Content-Type')
            connection_status = connection.status
            connection_reason = connection.reason

            connection.close()

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

    def get_file(self, url, post=None, destination_name=None):
        try:
            # url = self.url_opener.open(Request(url=url, data=post, headers=self.headers))
            url = self.url_opener.open(Request(url=url, data=post, headers=HEADERS))
            with open(destination_name, 'wb') as write_file:
                write_file.write(url.read())
            return destination_name
        except:
            return False