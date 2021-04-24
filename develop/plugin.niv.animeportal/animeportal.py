# -*- coding: utf-8 -*-

import gc
import os
import sys
#import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

from urllib.parse import urlencode
# from urllib.parse import quote
from urllib.parse import unquote
#from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility

class AnimePortal:
    addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.addon_data_dir = xbmcvfs.translatePath(AnimePortal.addon.getAddonInfo('profile'))
        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.params = {
            'mode': 'main_part',
            'param': '',
            'page': '1',
            'sort':'',
            'node': '',
            'portal': 'animeportal'
            }

        args = utility.get_params()
        for a in args:
            self.params[a] = unquote(args[a])

    def create_print(self, data):
        xbmc.log(str(data), xbmc.LOGFATAL)
        return

    def create_checking_portal(self):
        if 'animeportal' in self.params['portal']:
            with open(os.path.join(self.addon_data_dir, 'settings.xml'), 'rb') as read_file:
                data_array = read_file.read()

            data_array = data_array.decode()
            data_array = data_array.splitlines()

            for data in data_array:
                if 'id="use_' and '">true</setting>' in data:
                    portal = data[data.find('use_')+4:data.find('">true')].strip()
                    label = '[B][COLOR=white]{}[/COLOR][/B]'.format(portal.upper())

                    xbmcplugin.addDirectoryItem(int(sys.argv[1]), '{}?{}'.format(sys.argv[0], urlencode(
                        {'mode': 'main_part', 'portal': portal})), xbmcgui.ListItem(label), isFolder=True)
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if 'anilibria' in self.params['portal']:
            from anilibria.anilibria import Anilibria
            self.anilibria = Anilibria()
            self.anilibria.execute()
            del Anilibria


    def execute(self):
        #self.create_print(self.params)
        getattr(self, 'exec_{}'.format(self.params['mode']))()

    def exec_main_part(self):
        self.create_checking_portal()
    
    def exec_search_part(self):
        self.create_checking_portal()
        #if 'anilibria' in self.params['portal']:
            #self.anilibria.execute()

    def exec_common_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_schedule_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_catalog_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_select_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_online_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_torrent_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_play_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_clean_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_update_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()
    
    def exec_mirror_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()

    def exec_information_part(self):
        self.create_checking_portal()
        # if 'anilibria' in self.params['portal']:
        #     self.anilibria.execute()

if __name__ == "__main__":
    animeportal = AnimePortal()
    animeportal.execute()
    del AnimePortal

gc.collect()
