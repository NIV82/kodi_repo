# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
#import xbmcaddon
#import xbmcvfs

from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
from urllib.request import urlopen
from html import unescape

import info
import utility

class Shiza:
    def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params, addon):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()
        self.addon = addon
        self.images_dir = images_dir
        self.torrents_dir = torrents_dir
        self.database_dir = database_dir
        self.cookie_dir = cookie_dir
        self.params = params

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        
        import xbmc
        xbmc.log(str(self.site_url), xbmc.LOGFATAL)

        self.auth_mode = bool(self.addon.getSetting('shiza_auth_mode') == '1')
#================================================
        try: shiza_session = float(self.addon.getSetting('shiza_session'))
        except: shiza_session = 0

        if time.time() - shiza_session > 28800:
            self.addon.setSetting('shiza_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'shiza.sid'))
            except: pass
            self.addon.setSetting('shiza_auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('shiza_auth') == 'true'),
            proxy_data=self.proxy_data,
            portal='shiza')
        self.auth_post_data = {
            "mail": self.addon.getSetting('shiza_username'),
            "passwd": self.addon.getSetting('shiza_password')
            }
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = ''
        self.network.sid_file = os.path.join(self.cookie_dir, 'shiza.sid')
        del WebTools
#================================================  
        if self.auth_mode:
            if not self.addon.getSetting("shiza_username") or not self.addon.getSetting("shiza_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting("shiza_auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'shizaproject.db')):
            self.exec_update_part()
#================================================
        from database import ShizaProject_DB
        self.database = ShizaProject_DB(os.path.join(self.database_dir, 'shizaproject.db'))
        del ShizaProject_DB
#================================================
    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        # if anime_id:
        #     cover = self.create_image(anime_id)

        #     li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
        #                "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})

        #     anime_info = self.database.get_anime(anime_id)

        #     info = {'genre': anime_info[0],'year': anime_info[2],'plot': anime_info[3],'title': title, 'tvshowtitle': title}
        #     info['plot'] = '{}\n\n[COLOR=steelblue]Над релизом работали[/COLOR]: {}'.format(info['plot'], anime_info[1])

        #     if size:
        #         info['size'] = size

        #     li.setInfo(type='video', infoLabels=info)

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = 'shizaproject'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_proxy_data(self):
        if self.addon.getSetting('shiza_unblock') == '0':
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
                
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#================================================
    def create_site_url(self):
        current_mirror = 'shiza_mirror_{}'.format(self.addon.getSetting('shiza_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('shiza_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        #site_url = '{}graphql'.format(site_url)
        return site_url

    def create_post(self):
        query_fetch_releases = 'query fetchReleases(\
            $first: Int,\
            $airedOn: ReleaseAiredOnRangeFilter,\
            $query: String,\
            $orderBy: ReleaseOrder,\
            $type: ReleaseTypeFilter,\
            $status: ReleaseStatusFilter,\
            $activity: ReleaseActivityFilter,\
            $rating: ReleaseRatingFilter,\
            $season: ReleaseSeasonFilter,\
            $genre: ReleaseIDFilter,\
            $category: ReleaseIDFilter,\
            $tag: ReleaseIDFilter,\
            $studio: ReleaseIDFilter,\
            $staff: ReleaseIDFilter,\
            $contributor: ReleaseIDFilter,\
            $after: String)'

        query_releases = '{releases(\
            first: $first\
            airedOn: $airedOn\
            query: $query\
            orderBy: $orderBy\
            type: $type\
            status: $status\
            activity: $activity\
            rating: $rating\
            season: $season\
            genre: $genre\
            category: $category\
            tag: $tag\
            studio: $studio\
            staff: $staff\
            contributor: $contributor\
            after: $after)'

        query_edges = '{edges {node {slug\
                episodesCount\
                episodesAired\
                posters {\
                    preview: resize(width: 360, height: 500) { width height url }\
                    original { width height url }}\
                episodes {name number videos { embedSource embedUrl }}\
                torrents {seeders leechers size metadata videoFormat videoQualities file { url }}}}'

        query_page_info = 'pageInfo {startCursor endCursor}}}'

        post = {
            "operationName":"fetchReleases",
            "variables": {
                "first": 3, 
                "airedOn": None, 
                "query": "", 
                "orderBy":     {"field": "PUBLISHED_AT","direction":"DESC"},
                "type":        {"include":[],"exclude":[]},
                "status":      {"include":[],"exclude":["DRAFT"]},
                "activity":    {"include":[],"exclude":[]},
                "rating":      {"include":[],"exclude":[]},
                "season":      {"include":[],"exclude":[]},
                "genre":       {"include":[],"exclude":[]},
                "category":    {"include":[],"exclude":[]},
                "tag":         {"include":[],"exclude":[]},
                "studio":      {"include":[],"exclude":[]},
                "staff":       {"include":[],"exclude":[]},
                "contributor": {"include":[],"exclude":[]}
                },
            "query":'{}{}{}{}'.format(query_fetch_releases,query_releases,query_edges,query_page_info)
            }

        if self.params['param'] in ('ANNOUNCE','ONGOING','RELEASED','SUSPENDED'):
            post['variables']['status']['include'] = [self.params['param']]
        if self.params['param'] in ('WISH','FROZEN','WORK_IN_PROGRESS','COMPLETED','DROPPED'):
            post['variables']['activity']['include'] = [self.params['param']]
        if self.params['param'] in info.shiza_categories.values():
            post['variables']['category']['include'] = [self.params['param']]

        post = str(post).replace('\'','"').replace('None','null')
        return post


        
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        self.addon.openSettings()

    def exec_update_part(self):
        try: self.database.end()
        except: pass

        try: os.remove(os.path.join(self.database_dir, 'shizaproject.db'))
        except: pass

        db_file = os.path.join(self.database_dir, 'shizaproject.db')        
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/shizaproject.db'
        try:                
            data = urlopen(db_url)
            chunk_size = 8192
            bytes_read = 0

            try: file_size = int(data.info().getheaders("Content-Length")[0])
            except: file_size = int(data.getheader('Content-Length'))

            self.progress.create('Загрузка Базы Данных')
            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                self.progress.close()
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
        except:
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
            pass

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})

        self.create_line(title='[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': ''}) #https://shiza-project.com/releases?orderBy=PUBLISHED_AT
        #self.create_line(title='[B][COLOR=lime][ Все ][/COLOR][/B]', params={'mode': 'common_part', 'param': ''})
        self.create_line(title='[B][COLOR=lime][ Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'ONGOING'}) #https://shiza-project.com/releases?statuses=ONGOING
        self.create_line(title='[B][COLOR=lime][ В работе ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'WORK_IN_PROGRESS'}) #https://shiza-project.com/releases?activities=WORK_IN_PROGRESS
        self.create_line(title='[B][COLOR=lime][ Запланированные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'WISH'}) #https://shiza-project.com/releases?activities=WISH
        self.create_line(title='[B][COLOR=lime][ Завершенные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'COMPLETED'}) #https://shiza-project.com/releases?activities=COMPLETED
        #self.create_line(title='[B][COLOR=lime][ Приостановленные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/suspended'})
        #self.create_line(title='[B][COLOR=lime][ Рекомендуемые ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'releases/top'})

        self.create_line(title='[B][COLOR=yellow][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI='}) #https://shiza-project.com/releases?statuses=%21DRAFT&categories=Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI%3D
        self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM='}) #https://shiza-project.com/releases?statuses=%21DRAFT&categories=Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM%3D
        self.create_line(title='[B][COLOR=orange][ Кино и ТВ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ='}) #https://shiza-project.com/releases?statuses=%21DRAFT&categories=Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ%3D        
        
        #self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    
    def create_episodes(self, episodes):
        online_array = []        
        episodes = episodes.split('},{')

        for ep in episodes:
            if not '"name"' in ep:
                continue
            episode_name = ep[ep.find('"name":"')+8:ep.find('","number"')]
            episode_num = ep[ep.find('"number":')+9:ep.find(',"videos')]
            episode_url = ep[ep.find('embedUrl":"'):ep.rfind('"}')]

            if not episode_url:
                continue
            
            online_array.append('{}||{}||{}'.format(episode_name,episode_num,episode_url))
        
        episodes_data = '|||'.join(online_array)

        return episodes_data

    def create_torrent(self, torrent):
        seed = torrent[torrent.find('seeders":')+9:torrent.find(',"leechers')]
        leech = torrent[torrent.find('leechers":')+10:torrent.find(',"size')]
        size = torrent[torrent.find('size":"')+7:torrent.find('","metadata')]
        metadata = torrent[torrent.find('metadata":"')+11:torrent.find('","videoFormat')]
        video_format = torrent[torrent.find('videoFormat":"')+14:torrent.find('","videoQualities')]
        quality = torrent[torrent.find('videoQualities":["')+18:torrent.find('"],"file')]
        quality = quality.replace('","','||')
        url = torrent[torrent.find('url":"')+6:torrent.find('?filename=')]

        torrent_data = '{}||{}||{}||{}||{}||{}||{}'.format(seed,leech,size,metadata,video_format,quality,url)
        return torrent_data

    def create_title(self, anime_id, episodes_count, episodes_aired):        
        title = self.database.get_title(anime_id)

        series = ' - [COLOR=gold][ Серии: 1-{} из {} ][/COLOR]'.format(episodes_aired, episodes_count)
      
        if self.addon.getSetting('shiza_titles') == '0':
            label = '{}{}'.format(title[0], series)
        if self.addon.getSetting('shiza_titles') == '1':
            label = '{}{}'.format(title[1], series)
        if self.addon.getSetting('shiza_titles') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)

        return label

    def exec_common_part(self):
        self.progress.create("ShizaProject", "Инициализация")
        post = self.create_post()

        html = self.network.get_html(self.site_url, post)

        after = html[html.find('endCursor":"')+12:html.rfind('"}')]

        data_array = html.split('{"node":{"slug":"')
        data_array.pop(0)

        i = 0

        for data in data_array:
            anime_id = data[:data.find('",')]
            episodes_count = data[data.find('episodesCount":')+15:data.find(',"episodesAired')]
            episodes_aired = data[data.find('episodesAired":')+15:data.find(',"posters')]

            poster_data = data[data.find('posters":[{')+11:data.find('"}}],"episodes')]
            poster_preview = poster_data[poster_data.find('https://'):poster_data.find('"},"original')]
            poster_original = poster_data[poster_data.rfind('https://'):]

            episodes = data[data.find('"episodes":[{')+13:data.find('],"torrents')]
            episodes = self.create_episodes(episodes)

            torrent = data[data.find('torrents":[{')+12:data.find('"}}]}}')]
            torrent = self.create_torrent(torrent)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
            if not self.database.is_anime_in_db(anime_id):
                #inf = self.create_info(anime_id)
                label = '[B][COLOR=red][ {} ][/COLOR] - not in base[/B]'.format(anime_id)
                self.create_line(label, params={})
                continue

            label = self.create_title(anime_id, episodes_count, episodes_aired)
            self.create_line(label,params={})

        self.progress.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)