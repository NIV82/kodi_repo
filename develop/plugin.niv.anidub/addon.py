# -*- coding: utf-8 -*-

import gc
import os
import sys

import xbmcaddon

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

addon = xbmcaddon.Addon(id='plugin.niv.anidub')

if sys.version_info.major > 2:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape


# import network

# def data_print(data):
#     import xbmc
#     xbmc.log(str(data), xbmc.LOGFATAL)

# def parse_proxy():
#     url = addon.getSetting('torrent_unblock_2')
#     #pac_url = addon.getSetting('torrent_unblock_2')
#     #content = urlopen(pac_url)
#     #html = content.read()
#     #content.close()
#     html = network.get_web(url=url)
#     data_print(html)

#     try:
#         html = str(html, encoding='utf-8')
#     except:
#         pass
                
#     proxy = html[html.find('PROXY ')+6:html.find('; DIRECT')]
#     proxy = proxy.strip()

#     return proxy



# parse_proxy()

# x = network.get_web(url=url)

if __name__ == "__main__":
    if '0' in addon.getSetting('mode'):
        import anidub_online
        anidub_online.start()
    if '1' in addon.getSetting('mode'):
        import anidub_torrent
        anidub_torrent.start()

    # if '0' in addon.getSetting('anidub_mode'):
    #     if 'anidub_t' in sys.argv[2]:
    #         import anidub_torrent
    #         anidub_torrent.start()
    #     else:
    #         import anidub_online
    #         anidub_online.start()
    # if '1' in addon.getSetting('anidub_mode'):
    #     if 'anidub_o' in sys.argv[2]:
    #         import anidub_online
    #         anidub_online.start()
    #     else:
    #         import anidub_torrent
    #         anidub_torrent.start()
        
gc.collect()
