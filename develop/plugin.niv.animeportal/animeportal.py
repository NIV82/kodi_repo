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

        if not os.path.isfile(os.path.join(self.addon_data_dir, 'settings.xml')):
            AnimePortal.addon.setSetting('animeportal_engine', '2')

        self.proxy_data = self.create_proxy_data()

    #def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None):
    def create_line(self, title=None, params=None, folder=True):
        from info import animeportal_plot

        li = xbmcgui.ListItem('[B][COLOR=white]{}[/COLOR][/B]'.format(title.upper()))
        li.setArt({"fanart": self.fanart,"icon": self.icon.replace('icon', title)})
        info = {'plot': animeportal_plot[title], 'title': title.upper(), 'tvshowtitle': title.upper()}
        li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems([
            ('[B]{} - Обновить DB[/B]'.format(title.capitalize()), 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal={}")'.format(title))
            ])

        # li.addContextMenuItems([
        #     ('[B]AniDub - Обновить DB[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anidub")'),
        #     ('[B]Anilibria - Обновить DB[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anilibria")'),
        #     ('[B]Anistar - Обновить DB[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anistar")'),
        #     ('[B]Animedia - Обновить DB[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=animedia")')
        #     ])

        url = '{}?{}'.format(sys.argv[0], urlencode(params))
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_checking_portal(self):
        if 'animeportal' in self.params['portal']:
            portal_list = ('anidub','anilibria','animedia','anistar')

            for portal in portal_list:
                if AnimePortal.addon.getSetting('use_{}'.format(portal)) == 'true':
                    self.create_line(title=portal, params={'mode': 'main_part', 'portal': portal})
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if 'anilibria' in self.params['portal']:
            from anilibria import Anilibria
            self.anilibria = Anilibria(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params, self.proxy_data)
            self.anilibria.execute()
            del Anilibria
        
        if 'anidub' in self.params['portal']:
            from anidub import Anidub
            self.anidub = Anidub(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params, self.proxy_data)
            self.anidub.execute()
            del Anidub
        
        if 'anistar' in self.params['portal']:
            from anistar import Anistar
            self.anistar = Anistar(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params, self.proxy_data)
            self.anistar.execute()
            del Anistar
        
        if 'animedia' in self.params['portal']:
            from animedia import Animedia
            self.animedia = Animedia(self.images_dir, self.torrents_dir, self.database_dir, self.cookie_dir, self.params, self.proxy_data)
            self.animedia.execute()
            del Animedia

    def create_proxy_data(self):
        try: proxy_time = float(AnimePortal.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            AnimePortal.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
                
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            AnimePortal.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if AnimePortal.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': AnimePortal.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                AnimePortal.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data

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
    
    def exec_categories_part(self):
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
        # db_name = '{}.db'.format(self.params['node'])
        # db_file = os.path.join(self.database_dir, db_name)

        # try: os.remove(db_file)
        # except: pass        

        # db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/{}'.format(db_name)
        # try:                
        #     data = urlopen(db_url)
        #     chunk_size = 8192
        #     bytes_read = 0

        #     try: file_size = int(data.info().getheaders("Content-Length")[0])
        #     except: file_size = int(data.getheader('Content-Length'))

        #     self.progress.create('Загрузка Базы Данных')
        #     with open(db_file, 'wb') as write_file:
        #         while True:
        #             chunk = data.read(chunk_size)
        #             bytes_read = bytes_read + len(chunk)
        #             write_file.write(chunk)
        #             if len(chunk) < chunk_size:
        #                 break
        #             percent = bytes_read * 100 / file_size
        #             self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
        #         self.progress.close()
        #     self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
        # except:
        #     self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
        #     pass
    
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
