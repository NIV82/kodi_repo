# -*- coding: utf-8 -*-

import gc
import os
import sys
import time

#import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from utility import get_params

class AnimePortal:
    addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.icon = xbmcvfs.translatePath(AnimePortal.addon.getAddonInfo('icon'))
        self.fanart = xbmcvfs.translatePath(AnimePortal.addon.getAddonInfo('fanart'))

        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon_data_dir = xbmcvfs.translatePath(AnimePortal.addon.getAddonInfo('profile'))
        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.database_dir = os.path.join(self.addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.cookie_dir = os.path.join(self.addon_data_dir, 'cookie')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.params = {
            'mode': 'main_part',
            'param': '',
            'page': '1',
            'sort':'',
            'node': '',
            'portal': 'animeportal'
            }

        args = get_params()
        for a in args:
            self.params[a] = unquote(args[a])

        if not AnimePortal.addon.getSetting('animeportal_proxy'):
            AnimePortal.addon.setSetting('animeportal_proxy', '')
            AnimePortal.addon.setSetting('animeportal_proxy_time', '')

    def create_line(self, title=None, params=None, folder=True):
        from info import animeportal_plot

        li = xbmcgui.ListItem('[B][COLOR=white]{}[/COLOR][/B]'.format(title.upper()))
        li.setArt({"fanart": self.fanart,"icon": self.icon.replace('icon', title)})
        info = {'plot': animeportal_plot[title], 'title': title.upper(), 'tvshowtitle': title.upper()}
        li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems([
            ('[B]{} - Обновить DB[/B]'.format(title.capitalize()), 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal={}")'.format(title))
            ])

        url = '{}?{}'.format(sys.argv[0], urlencode(params))
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_portals(self):
        if 'play_part' in self.params['mode']:
            self.play_part()
        else:
            if 'animeportal' in self.params['portal']:
                portal_list = ('anidub','anilibria','animedia','anistar')

                for portal in portal_list:
                    if AnimePortal.addon.getSetting('use_{}'.format(portal)) == 'true':
                        self.create_line(title=portal, params={'mode': 'main_part', 'portal': portal})
                xbmcplugin.endOfDirectory(int(sys.argv[1]))

            if 'anilibria' in self.params['portal']:
                from anilibria import Anilibria
                self.anilibria = Anilibria(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params)
                self.anilibria.execute()
                del Anilibria

            if 'anidub' in self.params['portal']:
                from anidub import Anidub
                self.anidub = Anidub(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params)
                self.anidub.execute()
                del Anidub
            
            if 'anistar' in self.params['portal']:
                from anistar import Anistar
                self.anistar = Anistar(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params)
                self.anistar.execute()
                del Anistar
            
            if 'animedia' in self.params['portal']:
                from animedia import Animedia
                self.animedia = Animedia(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params)
                self.animedia.execute()
                del Animedia

    def play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])

        if AnimePortal.addon.getSetting(portal_engine) == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(AnimePortal.addon.getSetting('{}_tam'.format(self.params['portal'])))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if AnimePortal.addon.getSetting(portal_engine) == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
        if AnimePortal.addon.getSetting(portal_engine) == '2':
            url = 'file:///{}'.format(url.replace('\\','/'))

            import player
            player.play_t2h(int(sys.argv[1]), 15, url, index, self.addon_data_dir)

if __name__ == "__main__":
    animeportal = AnimePortal()
    animeportal.create_portals()
    del AnimePortal

gc.collect()
