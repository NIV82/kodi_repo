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
        post = {
            "operationName":"fetchReleases",
            "variables":{
                "first": 15,
                #"airedOn": None,
                "airedOn":{"startYear":int(self.addon.getSetting('shiza_year_start')),"endYear":int(self.addon.getSetting('shiza_year_end'))},
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
                "contributor": {"include":[],"exclude":[]},
                "after":""
                },
            "query":"query fetchReleases(\
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
                $after: String\
                ) {\
            releases(\
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
                after: $after\
            ) {\
                edges { node { ...ReleaseCard } }\
                pageInfo { hasNextPage hasPreviousPage startCursor endCursor } }}\
                fragment ReleaseCard on Release {\
                    slug\
                    episodesCount\
                    episodesAired\
                    posters {\
                        preview: resize(width: 360, height: 500) { width height url }\
                        original { width height url }}\
                    episodes {name number videos { embedSource embedUrl }}\
                    torrents {seeders leechers size metadata videoFormat videoQualities file { url }}}"}

        if 'catalog' in self.params['param']:
            post['variables']['orderBy'] = {
                "field":info.shiza_sort[self.addon.getSetting('shiza_sort')],
                "direction":info.shiza_direction[self.addon.getSetting('shiza_direction')]}

            xbmc.log(str(post['variables']['orderBy']), xbmc.LOGFATAL)

#         "orderBy":{"field":"PUBLISHED_AT","direction":"DESC"},
#         "type":{"include":["TV","TV_SPECIAL","OTHER","MOVIE","SHORT_MOVIE","OVA","ONA","MUSIC"],"exclude":[]},
#         "status":{"include":["ANNOUNCE","ONGOING","RELEASED","SUSPENDED"],"exclude":["DRAFT"]},
#         "activity":{"include":["WISH","FROZEN","WORK_IN_PROGRESS","COMPLETED","DROPPED"],"exclude":[]},
#         "rating":{"include":["G","PG","PG_13","R","R_PLUS","RX"],"exclude":[]},
#         "season":{"include":["SPRING","SUMMER","FALL","WINTER"],"exclude":[]},
#         "watchlist":{"include":[],"exclude":[]},
#         "genre":{"include":["R2VucmU6NDU4OTE0MjEzMzIzMDc5NzM=","R2VucmU6NDU4OTE0MjEzMzIzMDc5NzQ=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODc=","R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzk=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDE=","R2VucmU6NDU4OTE0MjEzMzIzMDc5Njg=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODg=","R2VucmU6NDU4OTE0MjEzMzIzMDc5OTk=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODk=","R2VucmU6NDU4OTE0MjEzMzIzMDc5NzE=","R2VucmU6NDU4OTE0MjEzMzIzMDc5OTY=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMTA=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDU=","R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzg=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODM=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODQ=","R2VucmU6NDU4OTE0MjEzMzIzMDc5OTQ=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDQ=","R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzc=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDA=","R2VucmU6NDU4OTE0MjEzMzIzMDc5Njk=","R2VucmU6NDU4OTE0MjEzMzIzMDc5NzI=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDM=","R2VucmU6NDU4OTE0MjEzMzIzMDc5NzA=","R2VucmU6NDU4OTE0MjEzMzIzMDc5NzU=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODI=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDI=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODE=","R2VucmU6NDU4OTE0MjEzMzIzMDc5OTA=","R2VucmU6NDU4OTE0MjEzMzIzMDc5OTE=","R2VucmU6NDU4OTE0MjEzMzIzMDc5ODU=","R2VucmU6NDU4OTE0MjEzMzIzMDgwMDg=","R2VucmU6NDU4OTE0MjEzMzIzMDc5NzY="],"exclude":[]},
#         "category":{"include":["Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzE=","Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI=","Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM=","Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ="],"exclude":[]},
#         "tag":{"include":["VGFnOjQ1ODkxNDE0ODg1NjYyNzI0","VGFnOjQ1ODkxNDE0ODg1NjYyODA3","VGFnOjQ1ODkxNDE0ODg1NjYyODk2","VGFnOjQ1ODkxNDE0ODg5ODU3MDI5","VGFnOjQ1ODkxNDE0ODgxNDY4NDE4","VGFnOjQ1ODkxNDE0ODg1NjYyODAw","VGFnOjQ1ODkxNDE0ODg1NjYyNzM2","VGFnOjQ1ODkxNDE0ODg1NjYyNzY1","VGFnOjQ1ODkxNDE0ODg1NjYyNzk5","VGFnOjQ1ODkxNDE0ODg5ODU3MDM0","VGFnOjQ1ODkxNDE0ODg1NjYyNzQ5","VGFnOjQ1ODkxNDE0ODg1NjYyODAy","VGFnOjQ1ODkxNDE0ODg1NjYyNzcz","VGFnOjQ1ODkxNDE0ODg1NjYyNzI4","VGFnOjQ1ODkxNDE0ODg1NjYyODU0","VGFnOjQ1ODkxNDE0ODg1NjYyNzMy","VGFnOjQ1ODkxNDE0ODg1NjYyNzMz"],"exclude":[]},
#         "studio":{"include":[],"exclude":[]},"staff":{"include":[],"exclude":[]},
#         "contributor":{"include":[],"exclude":[]}

        if 'after' in self.params:
            post['variables']['after'] = self.params['after']

        if 'search_string' in self.params:
            post['variables']['query'] = unquote(self.params['search_string'])

        if self.params['param'] in ('ANNOUNCE','ONGOING','RELEASED','SUSPENDED'):
            post['variables']['status']['include'] = [self.params['param']]
        if self.params['param'] in ('WISH','FROZEN','WORK_IN_PROGRESS','COMPLETED','DROPPED'):
            post['variables']['activity']['include'] = [self.params['param']]
        if self.params['param'] in ('Аниме','Дорамы','Мультфильмы','Разное'):
            post['variables']['category']['include'] = [info.shiza_categories[self.params['param']]]
        
        post = str(post).replace('\'','"').replace('None','null')
        
        return post

    def create_episodes(self, episodes):
        online_array = []
        #episodes = episodes.split('}]},{')
        episodes = episodes.split(']},{')

        for ep in episodes:
            episode_name = ep[ep.find('"name":"')+8:ep.find('","number"')]
            episode_num = ep[ep.find('"number":')+9:ep.find(',"videos')]
            episode_url = ep[ep.find('SIBNET","embedUrl":"')+20:]
            episode_url = episode_url[:episode_url.find('"')]

            if not 'https://' in episode_url:
                continue

            online_array.append('{}||{}||{}'.format(episode_name,episode_num,episode_url))
        
        episodes_data = '|||'.join(online_array)

        return episodes_data

    def create_torrent(self, torrent):
        seed = torrent[torrent.find('seeders":')+9:torrent.find(',"leechers')]
        leech = torrent[torrent.find('leechers":')+10:torrent.find(',"size')]
        size = torrent[torrent.find('size":"')+7:torrent.find('","metadata')]

        metadata = torrent[torrent.find('metadata":"')+11:torrent.find('","videoFormat')]
        metadata = metadata.replace('Автор рипа','[COLOR=steelblue]Автор рипа[/COLOR]')
        metadata = metadata.replace('Видео','[COLOR=steelblue]Видео[/COLOR]')
        metadata = metadata.replace('Аудио','[COLOR=steelblue]Аудио[/COLOR]')
        metadata = metadata.replace('Субтитры','[COLOR=steelblue]Субтитры[/COLOR]')
        
        video_format = torrent[torrent.find('videoFormat":"')+14:torrent.find('","videoQualities')]
        quality = torrent[torrent.find('videoQualities":["')+18:torrent.find('"],"file')]
        #quality = quality.replace('","','||')
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
# ===========================================================================================
    def create_image(self, anime_id, url):
        if self.addon.getSetting('shiza_covers') == '0':
            return url
        else:
            local_img = '{}_{}'.format(self.params['portal'], url[url.rfind('/')+1:])

            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)
#===========================================================================================
    def create_contributors(self, data):
        info = {'VOICE_ACTING':[],'EDITING':[], 'MASTERING':[],'TIMING':[],'TRANSLATION':[], 'OTHER':[]}

        data = data.replace(',{"tasks":','|').replace('{"tasks":[','')

        clean_item = ('"type":"','"user":{"','FEMALE_','MALE_','"','{',']','\n','}},','}','[')

        for item in clean_item:
            data = data.replace(item,'')

        data = data.split('|')
        
        if len(data) == 1:
            i = data[0]
            user = i[i.find('username:')+9:]

            if 'VOICE_ACTING' in i or 'EDITING' in i or 'MASTERING' in i or 'TIMING' in i or 'TRANSLATION' in i:
                for val in ('VOICE_ACTING', 'EDITING','MASTERING', 'TIMING', 'TRANSLATION'):
                    if val in i:
                        info[val].append(user)
            else:
                info['OTHER'].append(user)
        else:
            for i in data:                
                user = i[i.find('username:')+9:]

                if 'VOICE_ACTING' in i or 'EDITING' in i or 'MASTERING' in i or 'TIMING' in i or 'TRANSLATION' in i:
                    for val in ('VOICE_ACTING', 'EDITING','MASTERING', 'TIMING', 'TRANSLATION'):
                        if val in i:
                            info[val].append(user)
                            i = i.replace(val,'')
                else:
                    info['OTHER'].append(user)
            
        return info

    def create_info(self, slug=''):        
        post = {
            "operationName":"fetchRelease",
            "variables":{"slug":"{}".format(slug)},
            "query":"query fetchRelease($slug: String!) {\
                release(slug: $slug) {\
                slug\
                malId\
                name\
                originalName\
                description\
                descriptionSource\
                countries\
                airedOn\
                studios { name }\
                genres { name }\
                staff { person { name } }\
                contributors { tasks { type } user { username } }}}"
                }
        
        post = str(post).replace('\'','"').replace('None','null')
        html = self.network.get_html(self.site_url, post)

        html = html.replace('\\n', '\n').replace('\\"', '"')

        data = unescape(html).replace('null','""')

        anime_id = data[data.find('"slug":"')+8:data.find('","malId"')]
        shiki_id = data[data.find('"malId":"')+9:data.find('","name"')]

        title_ru = data[data.find('"name":"')+8:data.find('","originalName"')]
        title_en = data[data.find('"originalName":"')+16:data.find('","description"')]

        plot = data[data.find('"description":"')+15:data.find('","descriptionSource"')]
        plot_source = data[data.find('"descriptionSource":"')+21:data.find('","countries"')]
        if plot_source:
            plot = '{}\n© {}'.format(plot, plot_source)

        countries = data[data.find('"countries":[')+13:data.find('],"airedOn"')]
        countries = countries.replace('"','')

        aired = data[data.find('"airedOn":"')+11:data.find('","studios"')]
            
        studios = data[data.find('"studios":[')+11:data.find('],"genres"')]
        studios = studios.replace('"person":','').replace('"name":','').replace('"','').replace('{','').replace('}','')

        genres = data[data.find('"genres":[')+10:data.find('],"staff"')]
        genres = genres.replace('"person":','').replace('"name":','').replace('"','').replace('{','').replace('}','')

        staff = data[data.find('"staff":[')+9:data.find('],"contributors"')]
        staff = staff.replace('"person":','').replace('"name":','').replace('"','').replace('{','').replace('}','')

        contributors = data[data.find('"contributors":')+15:]
        contributors = self.create_contributors(contributors)

        try:
            self.database.add_anime(
                anime_id = anime_id,
                shiki_id = shiki_id,
                title_ru = title_ru,
                title_en = title_en,
                plot = plot,
                countries = countries,
                aired = aired,
                studios = studios,
                genres = genres,
                authors = staff,
                dubbing = ', '.join(contributors['VOICE_ACTING']),
                mastering = ', '.join(contributors['MASTERING']),
                timing = ', '.join(contributors['TIMING']),
                other = ', '.join(contributors['OTHER']),
                translation = ', '.join(contributors['TRANSLATION']),
                editing = ', '.join(contributors['EDITING'])
                )
        except:
            return 101
        return

    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None): 
        li = xbmcgui.ListItem(title)

        if metadata:
            li.setInfo(type='video', infoLabels={'plot':metadata})

        if anime_id:
            #cover = cover
            cover = self.create_image(anime_id, cover)

            li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
                       "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})

            anime_info = self.database.get_anime(anime_id)

            info = {
                'plot': anime_info[0],
                'country': anime_info[1],
                'year': anime_info[2],
                'premiered': anime_info[2],
                'studio': anime_info[3],
                'genre': anime_info[4],
                'writer': anime_info[5],
                'director': anime_info[5],
                'title': title, 
                'tvshowtitle': title}
            
            info['plot'] = '{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(info['plot'], anime_info[6])
            info['plot'] = '{}\n[COLOR=steelblue]Работа со звуком[/COLOR]: {}'.format(info['plot'], anime_info[7])
            info['plot'] = '{}\n[COLOR=steelblue]Работа над таймингом[/COLOR]: {}'.format(info['plot'], anime_info[8])
            info['plot'] = '{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(info['plot'], anime_info[10])
            info['plot'] = '{}\n[COLOR=steelblue]Редактура[/COLOR]: {}'.format(info['plot'], anime_info[11])
            info['plot'] = '{}\n[COLOR=steelblue]Другое[/COLOR]: {}'.format(info['plot'], anime_info[9])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=shizaproject")')])

        # if self.auth_mode and self.params['mode'] == 'common_part':
        #     li.addContextMenuItems([
        #         ('[B]Добавить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_add&portal=shizaproject")'.format(anime_id)),
        #         ('[B]Удалить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_del&portal=shizaproject")'.format(anime_id))
        #         ])

        if self.params['mode'] == 'information_part':
            li.addContextMenuItems([('[B]Обновить Базу Данных[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=shizaproject")')])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = 'shizaproject'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

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

    def exec_clean_part(self):
        try:
            self.addon.setSetting('shiza_search', '')
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]Успешно выполнено[/COLOR]')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})

        self.create_line(title='[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part'}) #https://shiza-project.com/releases?orderBy=PUBLISHED_AT
        #self.create_line(title='[B][COLOR=lime][ Все ][/COLOR][/B]', params={'mode': 'common_part', 'param': ''})
        self.create_line(title='[B][COLOR=lime][ Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'ONGOING'}) #https://shiza-project.com/releases?statuses=ONGOING
        self.create_line(title='[B][COLOR=lime][ В работе ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'WORK_IN_PROGRESS'}) #https://shiza-project.com/releases?activities=WORK_IN_PROGRESS
        self.create_line(title='[B][COLOR=lime][ Запланированные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'WISH'}) #https://shiza-project.com/releases?activities=WISH
        self.create_line(title='[B][COLOR=lime][ Завершенные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'COMPLETED'}) #https://shiza-project.com/releases?activities=COMPLETED

        #self.create_line(title='[B][COLOR=yellow][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI='}) #https://shiza-project.com/releases?statuses=%21DRAFT&categories=Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI%3D
        self.create_line(title='[B][COLOR=yellow][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Дорамы'})

        #self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM='}) #https://shiza-project.com/releases?statuses=%21DRAFT&categories=Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM%3D
        self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Мультфильмы'})

        #self.create_line(title='[B][COLOR=orange][ Кино и ТВ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ='}) #https://shiza-project.com/releases?statuses=%21DRAFT&categories=Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ%3D
        self.create_line(title='[B][COLOR=orange][ Кино и ТВ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Разное'})

        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})

        #('Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzE=','Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI=','Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM=','Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ=')
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('shiza_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('shiza_search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('shiza_search', data_array)

                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_common_part(self):
        self.progress.create("ShizaProject", "Инициализация")
        post = self.create_post()

        html = self.network.get_html(self.site_url, post)
        
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

            #episodes = data[data.find('"episodes":[{')+13:data.find('],"torrents')]
            episodes = data[data.find('"episodes":[')+12:data.find('],"torrents')]
            episodes = self.create_episodes(episodes)
            
            torrent = data[data.find('torrents":[{')+12:data.find('"}}]}}')]
            torrent = self.create_torrent(torrent)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
            if not self.database.is_anime_in_db(anime_id):
                inf = self.create_info(anime_id)

            label = self.create_title(anime_id, episodes_count, episodes_aired)

            if self.addon.getSetting('shiza_covers_quality') == '0':
                cover = poster_preview
            else:
                cover = poster_original

            series = '1-{} / {}'.format(episodes_aired, episodes_count)

            self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part','id': anime_id,'cover':cover,'episodes':episodes,'torrent':torrent,'series':series})

        self.progress.close()

        if 'hasNextPage":true' in html:
            after = html[html.find('endCursor":"')+12:html.rfind('"}')]
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                             'mode': self.params['mode'], 'param': self.params['param'], 'after': after})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):        
        if not self.params['param']:
            self.create_line(title='Год (начало отрезка): [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_year_start')), params={'mode': 'catalog_part', 'param': 'shiza_year_start'})
            self.create_line(title='Год (конец отрезка): [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_year_end')), params={'mode': 'catalog_part', 'param': 'shiza_year_end'})  
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_season')), params={'mode': 'catalog_part', 'param': 'shiza_season'})            
            self.create_line(title='Категория: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_categories')), params={'mode': 'catalog_part', 'param': 'shiza_categories'})
            self.create_line(title='Статус тайтла: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_status')), params={'mode': 'catalog_part', 'param': 'shiza_status'})
            self.create_line(title='Статус озвучки: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_voice_stat')), params={'mode': 'catalog_part', 'param': 'shiza_voice_stat'})            
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_form')), params={'mode': 'catalog_part', 'param': 'shiza_form'})            
            self.create_line(title='Возрастное ограничение: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_rating')), params={'mode': 'catalog_part', 'param': 'shiza_rating'})
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_genre')), params={'mode': 'catalog_part', 'param': 'shiza_genre'})
            self.create_line(title='Тэги: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_tags')), params={'mode': 'catalog_part', 'param': 'shiza_tags'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_sort')), params={'mode': 'catalog_part', 'param': 'shiza_sort'})
            self.create_line(title='Направление сортировки: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shiza_direction')), params={'mode': 'catalog_part', 'param': 'shiza_direction'})

            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)            
        
        if 'shiza_year_start' in self.params['param']:
            result = self.dialog.select('Начало отрезка:', info.shiza_year)
            self.addon.setSetting(id='shiza_year_start', value=info.shiza_year[result])        
        if 'shiza_year_end' in self.params['param']:
            result = self.dialog.select('Конец отрезка:', info.shiza_year)
            self.addon.setSetting(id='shiza_year_end', value=info.shiza_year[result])
        if 'shiza_season' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_season.keys()))
            self.addon.setSetting(id='shiza_season', value=tuple(info.shiza_season.keys())[result])
        if 'shiza_categories' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_categories.keys()))
            self.addon.setSetting(id='shiza_categories', value=tuple(info.shiza_categories.keys())[result])
        if 'shiza_status' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_status.keys()))
            self.addon.setSetting(id='shiza_status', value=tuple(info.shiza_status.keys())[result])
        if 'shiza_voice_stat' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_voice_stat.keys()))
            self.addon.setSetting(id='shiza_voice_stat', value=tuple(info.shiza_voice_stat.keys())[result])
        if 'shiza_form' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_form.keys()))
            self.addon.setSetting(id='shiza_form', value=tuple(info.shiza_form.keys())[result])
        if 'shiza_rating' in self.params['param']:
            result = self.dialog.select('Сортировка по:', info.shiza_rating)
            self.addon.setSetting(id='shiza_rating', value=info.shiza_rating[result])
        if 'shiza_genre' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_genre.keys()))
            self.addon.setSetting(id='shiza_genre', value=tuple(info.shiza_genre.keys())[result])
        if 'shiza_tags' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_tags.keys()))
            self.addon.setSetting(id='shiza_tags', value=tuple(info.shiza_tags.keys())[result])
        if 'shiza_sort' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(info.shiza_sort.keys()))
            self.addon.setSetting(id='shiza_sort', value=tuple(info.shiza_sort.keys())[result])        
        if 'shiza_direction' in self.params['param']:
            result = self.dialog.select('Направление сортировки:', tuple(info.shiza_direction.keys()))
            self.addon.setSetting(id='shiza_direction', value=tuple(info.shiza_direction.keys())[result])

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.shiza_data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]shiza-project.com[/COLOR]', data)
        return

    def exec_select_part(self):
        if 'episodes' in self.params:
            self.create_line(title='[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id'], 'episodes':self.params['episodes'], 'cover': self.params['cover']})
        if 'torrent' in self.params:
            self.create_line(title='[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent':self.params['torrent'], 'cover': self.params['cover'], 'series':self.params['series']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    
    def exec_online_part(self):
        if not self.params['param']:
            data_array = self.params['episodes'].split('|||')
            cover = self.params['cover']

            for data in data_array:
                data = data.split('||')
                episode_title = data[0]
                episode_num = data[1]
                episode_url = data[2]

                label = '{} - {}'.format(episode_num, episode_title)
                self.create_line(title=label, anime_id=self.params['id'], cover=cover, params={'mode': 'online_part', 'id': self.params['id'], 'param': data[2], 'title':label, 'cover': cover})

        if self.params['param']:
            html = self.network.get_html(target_name=self.params['param'])
            
            cover = html[html.find('og:image" content="')+19:html.find('"/><meta property="og:description')]
            
            if 'player.src' in html:
                video_src = html[html.find('player.src([{src: "')+19:html.find(';player.persistvolume')]
                video_src = video_src[:video_src.find('"')]
                play_url = 'https://video.sibnet.ru{}|referer={}'.format(video_src, self.params['param'])

                label = self.params['title']

            if 'class=videostatus><p>' in html:
                status = html[html.find('class=videostatus><p>')+21:html.find('</p></div><script')]
                label = '[COLOR=red][B][ {} ][/B][/COLOR]'.format(status.replace('.',''))
                play_url = ''

            self.create_line(title=label, cover=cover, params={}, anime_id=self.params['id'], online=play_url, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        if not self.params['param']:
            data = self.params['torrent'].split('||')

            seeders = data[0]
            leechers = data[1]
            torrent_size = '{:.2f}'.format(float(data[2]) / 1024 / 1024 / 1024)
            metadata = data[3].replace('\\n','\n\n')
            video_format = data[4]
            quality = data[5].replace('","',' - ').replace('RESOLUTION_','')
            torrent_url = data[6]

            label = 'Серии: {} - {}, {} , [COLOR=F0FFD700]{} GB[/COLOR], Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
                self.params['series'], video_format, quality, torrent_size, seeders, leechers)

            self.create_line(title=label, metadata=metadata, params={'mode': 'torrent_part', 'param': torrent_url, 'id': self.params['id'],'cover':self.params['cover']})
        
        if self.params['param']:
            full_url = self.params['param']
            file_name = '{}_{}'.format(self.params['portal'], full_url[full_url.rfind('/')+1:full_url.rfind('.')])
            full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))
           
            torrent_file = self.network.get_file(target_name=full_url, destination_name=full_name)

            import bencode
            
            with open(torrent_file, 'rb') as read_file:
                torrent_data = read_file.read()

            torrent = bencode.bdecode(torrent_data)

            info = torrent['info']
            series = {}
            size = {}

            if 'files' in info:
                for i, x in enumerate(info['files']):
                    size[i] = x['length']
                    series[i] = x['path'][-1]
                for i in sorted(series, key=series.get):
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], cover=self.params['cover'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], cover=self.params['cover'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
