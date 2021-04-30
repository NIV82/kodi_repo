# -*- coding: utf-8 -*-

import gc
import os
import sys
#import time

#import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

from urllib.parse import urlencode
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import unquote
#from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

class AnimePortal:
    addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.addon_data_dir = xbmcvfs.translatePath(AnimePortal.addon.getAddonInfo('profile'))
        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

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

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = args[a][0]

    def create_checking_portal(self):
        if 'animeportal' in self.params['portal']:
            with open(os.path.join(self.addon_data_dir, 'settings.xml'), 'rb') as read_file:
                data_array = read_file.read()

            data_array = data_array.decode()
            data_array = data_array.splitlines()

            for data in data_array:
                if 'id="use_' in data and '">true</setting>' in data:
                    data = data.replace('<setting id="use_','').strip()
                    portal = data[:data.find('"')]
                    label = '[B][COLOR=white]{}[/COLOR][/B]'.format(portal.upper())

                    xbmcplugin.addDirectoryItem(int(sys.argv[1]), '{}?{}'.format(sys.argv[0], urlencode(
                        {'mode': 'main_part', 'portal': portal})), xbmcgui.ListItem(label), isFolder=True)
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if 'anilibria' in self.params['portal']:
            from anilibria import Anilibria
            self.anilibria = Anilibria()
            self.anilibria.execute()
            del Anilibria

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()

    def exec_main_part(self):
        self.create_checking_portal()
    
    def exec_search_part(self):
        self.create_checking_portal()

    def exec_common_part(self):
        self.create_checking_portal()
    
    def exec_schedule_part(self):
        self.create_checking_portal()
    
    def exec_catalog_part(self):
        self.create_checking_portal()
    
    def exec_select_part(self):
        self.create_checking_portal()
    
    def exec_online_part(self):
        self.create_checking_portal()
    
    def exec_torrent_part(self):
        self.create_checking_portal()

    def exec_clean_part(self):
        self.create_checking_portal()
    
    def exec_update_part(self):
        self.create_checking_portal()
    
    def exec_mirror_part(self):
        self.create_checking_portal()
    
    def exec_favorites_part(self):
        self.create_checking_portal()

    def exec_information_part(self):
        self.create_checking_portal()

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if AnimePortal.addon.getSetting("animeportal_engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(AnimePortal.addon.getSetting("animeportal_tam"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if AnimePortal.addon.getSetting("animeportal_engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
        if AnimePortal.addon.getSetting("animeportal_engine") == '2':
            url = 'file:///{}'.format(url.replace('\\','/'))

            import player
            player.play_t2h(int(sys.argv[1]), 15, url, index, self.addon_data_dir)

if __name__ == "__main__":
    animeportal = AnimePortal()
    animeportal.execute()
    del AnimePortal

gc.collect()