# -*- coding: utf-8 -*-

import gc, os, sys, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

try:
    from urllib import urlencode, quote, unquote
except:
    from urllib.parse import urlencode, quote, unquote

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from utility import get_params, fs_dec, fs_enc
from info import animeportal_data, animeportal_plot

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

progress = xbmcgui.DialogProgress()
dialog = xbmcgui.Dialog()

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
    'portal': 'animeportal'
    }

args = get_params()
for a in args:
    params[a] = unquote(args[a])

if not addon.getSetting('animeportal_proxy'):
    addon.setSetting('animeportal_proxy', '')
    addon.setSetting('animeportal_proxy_time', '')

def create_line(title=None, params=None, folder=True):
    li = xbmcgui.ListItem('[B][COLOR=white]{}[/COLOR][/B]'.format(title.upper()))
    li.setArt({"fanart": fanart,"icon": icon.replace('icon', title)})
    info = {'plot': animeportal_plot[title], 'title': title.upper(), 'tvshowtitle': title.upper()}
    li.setInfo(type='video', infoLabels=info)

    url = '{}?{}'.format(sys.argv[0], urlencode(params))
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

def create_portals():
    if 'play_part' in params['mode']:
        play_part()
    elif 'information_part' in params['mode']:
        information_part()
    else:
        if 'animeportal' in params['portal']:
            portal_list = ('anidub','anilibria','animedia','anistar','shizaproject')

            for portal in portal_list:
                if addon.getSetting('use_{}'.format(portal)) == 'true':
                    create_line(title=portal, params={'mode': 'main_part', 'portal': portal})
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if 'anidub' in params['portal']:
            from anidub import Anidub
            anidub = Anidub(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
            anidub.execute()
            del Anidub

        if 'anilibria' in params['portal']:
            from anilibria import Anilibria
            anilibria = Anilibria(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
            anilibria.execute()
            del Anilibria
            
        if 'anistar' in params['portal']:
            from anistar import Anistar
            anistar = Anistar(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
            anistar.execute()
            del Anistar
            
        if 'animedia' in params['portal']:
            from animedia import Animedia
            animedia = Animedia(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
            animedia.execute()
            del Animedia
        
        if 'shizaproject' in params['portal']:
            from shizaproject import Shiza
            shiza = Shiza(images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress)
            shiza.execute()
            del Shiza

def information_part():
    txt = animeportal_data
        
    start = '[{}]'.format(params['param'])
    end = '[/{}]'.format(params['param'])
    data = txt[txt.find(start)+6:txt.find(end)].strip()

    dialog.textviewer('Информация', data)
    return

def play_part():
    url = os.path.join(torrents_dir, '{}.torrent'.format(params['id']))
    index = int(params['index'])
    portal_engine = '{}_engine'.format(params['portal'])

    if addon.getSetting(portal_engine) == '0':
        tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
        engine = tam_engine[int(addon.getSetting('{}_tam'.format(params['portal'])))]
        purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
        item = xbmcgui.ListItem(path=purl)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

    if addon.getSetting(portal_engine) == '1':
        purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
        item = xbmcgui.ListItem(path=purl)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
    if addon.getSetting(portal_engine) == '2':
        url = 'file:///{}'.format(url.replace('\\','/'))

        import player
        player.play_t2h(int(sys.argv[1]), 15, url, index, addon_data_dir)

if __name__ == "__main__":
    create_portals()

gc.collect()
