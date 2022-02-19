# -*- coding: utf-8 -*-

import gc, os, sys, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

try:
    from urllib import urlencode, quote, unquote
    from urlparse import parse_qs
except:
    from urllib.parse import urlencode, quote, unquote, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from info import animeportal_plot, animeportal_data
from utility import fs_dec, fs_enc

addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    
try:
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))
except:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))

if not os.path.exists(addon_data_dir):
    os.makedirs(addon_data_dir)

images_dir = os.path.join(addon_data_dir, 'images')
if not os.path.exists(images_dir):
    os.mkdir(images_dir)

torrents_dir = os.path.join(addon_data_dir, 'torrents')
if not os.path.exists(torrents_dir):
    os.mkdir(torrents_dir)

database_dir = os.path.join(addon_data_dir, 'database')
if not os.path.exists(database_dir):
    os.mkdir(database_dir)

cookie_dir = os.path.join(addon_data_dir, 'cookie')
if not os.path.exists(cookie_dir):
    os.mkdir(cookie_dir)

params = {
    'mode': 'main_part',
    'param': '',
    'page': '1',
    'sort':'',
    'node': '',
    'limit': '12',
    'portal': 'animeportal',
    'portal_mode': ''
    }

args = parse_qs(sys.argv[2][1:])
for a in args:
    params[a] = unquote(args[a][0])            
#=======================================================================================
if not addon.getSetting('animeportal_proxy'):
    addon.setSetting('animeportal_proxy', '')
    addon.setSetting('animeportal_proxy_time', '')
#=======================================================================================
if 'animeportal' in params['portal']:
    portal_list = ('anidub','anilibria','animedia','anistar','shizaproject')

    for portal in portal_list:
        if 'true' in addon.getSetting('use_{}'.format(portal)):
            li = xbmcgui.ListItem('[B][COLOR=white]{}[/COLOR][/B]'.format(portal.upper()))
            li.setArt({"fanart": fanart,"icon": icon.replace('icon', portal)})
            info = {'plot': animeportal_plot[portal], 'title': portal.upper(), 'tvshowtitle': portal.upper()}
            li.setInfo(type='video', infoLabels=info)
            url = '{}?{}'.format(sys.argv[0], urlencode({'mode': 'main_part', 'portal': portal}))

            if 'animedia' in portal:
                li.addContextMenuItems(
                    [('[COLOR=white]Обновить Зеркало[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?node=actual_url&portal=animedia")')]
                    )

            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if 'anidub' in params['portal']:
    if '0' in addon.getSetting('anidub_mode'):
        from anidub_o import Anidub
        anidub = Anidub(addon_data_dir, params, addon, icon)
        anidub.execute()
        del Anidub
    else:
        from anidub_t import Anidub
        anidub = Anidub(addon_data_dir, params, addon, icon)
        anidub.execute()
        del Anidub
    
if 'anilibria' in params['portal']:
    from anilibria import Anilibria
    anilibria = Anilibria(addon_data_dir, params, addon, icon)
    anilibria.execute()
    del Anilibria
            
if 'anistar' in params['portal']:
    from anistar import Anistar
    anistar = Anistar(addon_data_dir, params, addon, icon)
    anistar.execute()
    del Anistar
            
if 'animedia' in params['portal']:
    if 'actual_url' in params['node']:
        addon.setSetting('animedia_auth', 'false')
        addon.setSetting('animedia_mirror_1', '')
    
    from animedia import Animedia
    animedia = Animedia(addon_data_dir, params, addon, icon)
    animedia.execute()
    del Animedia
        
if 'shizaproject' in params['portal']:
    from shizaproject import Shiza
    shiza = Shiza(addon_data_dir, params, addon, icon)
    shiza.execute()
    del Shiza

# if 'play_part' in params['portal_mode']:
#     torrents_dir = os.path.join(addon_data_dir, 'torrents')
    
#     url = os.path.join(torrents_dir, '{}.torrent'.format(params['id']))
#     index = int(params['index'])
#     portal_engine = '{}_engine'.format(params['portal'])

#     if '0' in addon.getSetting(portal_engine):
#         tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
#         engine = tam_engine[int(addon.getSetting('{}_tam'.format(params['portal'])))]
#         purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
#         item = xbmcgui.ListItem(path=purl)
#         xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

#     if '1' in addon.getSetting(portal_engine):
#         purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
#         item = xbmcgui.ListItem(path=purl)
#         xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
gc.collect()
