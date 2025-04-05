# -*- coding: utf-8 -*-
"""WEB TOOLS"""

import socket
from urllib.request import ProxyHandler
from urllib.request import HTTPCookieProcessor
from urllib.request import build_opener
from urllib.request import Request
from urllib.parse import urlencode
from http.cookiejar import MozillaCookieJar

socket.setdefaulttimeout(3)

class WebTools:
    """WEB TOOLS IMPLEMENTATION"""
    def __init__(self, auth_usage=False, auth_status=False, proxy_data=None):
        self.headers = {
            #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36',
            }
        self.auth_usage = auth_usage
        self.proxy_data = proxy_data

        if self.auth_usage:
            self.mcj = MozillaCookieJar()
            self.url_opener = build_opener(
                HTTPCookieProcessor(self.mcj), ProxyHandler(self.proxy_data))
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
            request = Request(url=url, data=post, headers=self.headers)
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

    def get_file(self, url, post=None, fpath=None):
        """GET BYTE-DATA IMPLEMENTATION"""
        try:
            url = self.url_opener.open(Request(url=url, data=post, headers=self.headers))
            with open(fpath, 'wb') as write_file:
                write_file.write(url.read())
            return fpath
        except Exception as err: # pylint: disable=broad-except
            return err
