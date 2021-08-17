# -*- coding: utf-8 -*-

import gc, os, sys, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

try:
    from urllib import urlencode, quote, unquote
except:
    from urllib.parse import urlencode, quote, unquote

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from info import animeportal_plot, animeportal_data
from utility import get_params, fs_dec, fs_enc

addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

try:
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))
except:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))

# progress = xbmcgui.DialogProgress()
# dialog = xbmcgui.Dialog()

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
    'portal': 'animeportal'
    }

args = get_params()
for a in args:
    params[a] = unquote(args[a])

if not addon.getSetting('animeportal_proxy'):
    addon.setSetting('animeportal_proxy', '')
    addon.setSetting('animeportal_proxy_time', '')

def create_portals():
    if 'animeportal' in params['portal']:
        portal_list = ('anidub','anilibria','animedia','anistar','shizaproject')

        for portal in portal_list:
            if 'true' in addon.getSetting('use_{}'.format(portal)):
                li = xbmcgui.ListItem('[B][COLOR=white]{}[/COLOR][/B]'.format(portal.upper()))
                li.setArt({"fanart": fanart,"icon": icon.replace('icon', portal)})
                info = {'plot': animeportal_plot[portal], 'title': portal.upper(), 'tvshowtitle': portal.upper()}
                li.setInfo(type='video', infoLabels=info)
                url = '{}?{}'.format(sys.argv[0], urlencode({'mode': 'main_part', 'portal': portal}))

                xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    if 'anidub' in params['portal']:
        from anidub import Anidub
        #anidub = Anidub(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
        anidub = Anidub(addon_data_dir, params, addon, icon)
        anidub.execute()
        del Anidub

    if 'anilibria' in params['portal']:
        from anilibria import Anilibria
        #anilibria = Anilibria(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
        anilibria = Anilibria(addon_data_dir, params, addon, icon)
        anilibria.execute()
        del Anilibria
            
    if 'anistar' in params['portal']:
        from anistar import Anistar
        # anistar = Anistar(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
        anistar = Anistar(addon_data_dir, params, addon, icon)
        anistar.execute()
        del Anistar
            
    if 'animedia' in params['portal']:
        from animedia import Animedia
        #animedia = Animedia(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
        animedia = Animedia(addon_data_dir, params, addon, icon)
        animedia.execute()
        del Animedia
        
    if 'shizaproject' in params['portal']:
        from shizaproject import Shiza
        #shiza = Shiza(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
        shiza = Shiza(addon_data_dir, params, addon, icon)
        shiza.execute()
        del Shiza

if __name__ == "__main__":
    create_portals()

gc.collect()
