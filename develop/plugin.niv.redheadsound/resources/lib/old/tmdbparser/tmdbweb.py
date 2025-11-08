# coding: utf-8

import json

try:
    from urllib2 import Request, urlopen
    from urllib2 import URLError
    from urllib import urlencode
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
    from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Kodi Movie scraper by Team Kodi',
    'Accept': 'application/json'
    }

def load_info(url, params=None, default=None, resp_type = 'json', unblock=False):
    if unblock:
        url=url.replace('api.themoviedb.org','api-themoviedb-org.translate.goog')

    theerror = ''
    if params:
        url = url + '?' + urlencode(params)

    req = Request(url, headers=HEADERS)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            theerror = {'error': 'failed to reach the remote site\nReason: {}'.format(e.reason)}
        elif hasattr(e, 'code'):
            theerror = {'error': 'remote site unable to fulfill the request\nError code: {}'.format(e.code)}
        if default is not None:
            return default
        else:
            return theerror
    if resp_type.lower() == 'json':
        resp = json.loads(response.read().decode('utf-8'))
    else:
        resp = response.read().decode('utf-8')

    return resp
