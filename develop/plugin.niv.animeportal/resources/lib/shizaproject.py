# -*- coding: utf-8 -*-

import os, sys, time
import xbmc, xbmcgui, xbmcplugin

try:
    from urllib import urlencode, urlopen, quote, unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen
    from html import unescape

#import info
#from utility import unescape

class Shiza:
    #def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress):
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.params = params
        self.addon = addon
        self.icon = icon.replace('icon', self.params['portal'])

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        
        self.auth_mode = bool(self.addon.getSetting('shiza_auth_mode') == '1')
#========================#========================#========================#
        try: shiza_session = float(self.addon.getSetting('shiza_session'))
        except: shiza_session = 0

        if time.time() - shiza_session > 28800:
            self.addon.setSetting('shiza_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'shiza.sid'))
            except: pass
            self.addon.setSetting('shiza_auth', 'false')
#========================#========================#========================#
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
#========================#========================#========================#  
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
#========================#========================#========================#
        # if not os.path.isfile(os.path.join(self.database_dir, 'shizaproject.db')):
        #     self.exec_update_database_part()
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_database_part()
#========================#========================#========================#
        # from database import ShizaProject_DB
        # self.database = ShizaProject_DB(os.path.join(self.database_dir, 'shizaproject.db'))
        # del ShizaProject_DB
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
#========================#========================#========================#
        # self.shiza_season = {'':'','Весна':'SPRING','Лето':'SUMMER','Осень':'FALL','Зима':'WINTER'}
        # self.shiza_categories = {'':'','Аниме':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzE=','Дорамы':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI=','Мультфильмы':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM=','Разное':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ='}
        # self.shiza_status = {'':'','Анонс':'ANNOUNCE','Онгоинг':'ONGOING','Выпущено':'RELEASED','Приостановлено':'SUSPENDED'}
        # self.shiza_voice_stat = {'':'','Хочучка':'WISH','Заморожено':'FROZEN','В работе':'WORK_IN_PROGRESS','Звершено':'COMPLETED','Брошено':'DROPPED'}
        # self.shiza_form = {'':'','ТВ':'TV','ТВ-спешл':'TV_SPECIAL','Остальное':'OTHER','Фильм':'MOVIE','Короткий Фильм':'SHORT_MOVIE','OVA':'OVA','ONA':'ONA','Музыкальный':'MUSIC'}
        # self.shiza_rating = ('','G','PG','PG_13','R','R_PLUS','RX')
        # self.shiza_genre = {'':'','экшен':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzM=','комедия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzQ=','романтика':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODc=','фэнтези':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzk=','фантастика':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDE=','драма':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njg=','школа':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODg=','сверхъестественное':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTk=','сёнен':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODk=','приключения':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzE=','повседневность':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTY=','сейнен':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMTA=','детектив':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDU=','этти':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzg=','магия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODM=','меха':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODQ=','гарем':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTQ=','военное':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDQ=','космос':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzc=','триллер':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDA=','игры':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njk=','музыка':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzI=','супер сила':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDM=','психологическое':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzA=','демоны':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzU=','ужасы':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODI=','сёдзё':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDI=','исторический':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODE=','спорт':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTA=','вампиры':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTE=','пародия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODU=','боевые искусства':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDg=','полиция':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzY='}
        # self.shiza_direction = {'По убыванию':'DESC','По возрастанию':'ASC'}
        # self.shiza_sort = {'Дате публикации':'PUBLISHED_AT','Дате обновление':'UPDATED_AT','Просмотрам':'VIEW_COUNT','Названию EN':'ORIGINAL_NAME','Названию RU':'NAME','Рейтингу':'SCORE'}
        # self.shiza_tags = {'':'','Дружба':'VGFnOjQ1ODkxNDE0ODg1NjYyNzI0','Повседневность':'VGFnOjQ1ODkxNDE0ODg1NjYyODA3','Кровь':'VGFnOjQ1ODkxNDE0ODg1NjYyODk2','Будущее':'VGFnOjQ1ODkxNDE0ODg5ODU3MDI5','bdrip':'VGFnOjQ1ODkxNDE0ODgxNDY4NDE4','webrip':'VGFnOjQ1ODkxNDE0ODg1NjYyODAw','Школа':'VGFnOjQ1ODkxNDE0ODg1NjYyNzM2','Олдскул':'VGFnOjQ1ODkxNDE0ODg1NjYyNzY1','Магия':'VGFnOjQ1ODkxNDE0ODg1NjYyNzk5','hdtvrip':'VGFnOjQ1ODkxNDE0ODg5ODU3MDM0','Демоны':'VGFnOjQ1ODkxNDE0ODg1NjYyNzQ5','Война':'VGFnOjQ1ODkxNDE0ODg1NjYyODAy','Роботы':'VGFnOjQ1ODkxNDE0ODg1NjYyNzcz','Космос':'VGFnOjQ1ODkxNDE0ODg1NjYyNzI4','Любовь':'VGFnOjQ1ODkxNDE0ODg1NjYyODU0','Вампиры':'VGFnOjQ1ODkxNDE0ODg1NjYyNzMy','Оружие':'VGFnOjQ1ODkxNDE0ODg1NjYyNzMz'}
#========================#========================#========================#
    def create_proxy_data(self):
        #if self.addon.getSetting('anidub_unblock') == '0':
        if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            # try: proxy_pac = str(proxy_pac, encoding='utf-8')
            # except: pass
            try: proxy_pac = proxy_pac.decode('utf-8')
            except: pass
            
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                # try: proxy_pac = str(proxy_pac, encoding='utf-8')
                # except: pass

                try: proxy_pac = proxy_pac.decode('utf-8')
                except: pass
                
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = 'shiza_mirror_{}'.format(self.addon.getSetting('shiza_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('shiza_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        #site_url = '{}graphql'.format(site_url)
        return site_url
#========================#========================#========================#
    def create_post(self):
        from info import shiza_categories, shiza_season, shiza_status, shiza_voice_stat, shiza_form, shiza_genre, shiza_tags, shiza_sort, shiza_direction
        post = {
            "operationName":"fetchReleases",
            "variables":{
                "first": 15,
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

        if 'after' in self.params:
            post['variables']['after'] = self.params['after']

        if self.params['param'] in ('ANNOUNCE','ONGOING','RELEASED','SUSPENDED'):
            post['variables']['status']['include'] = [self.params['param']]
        if self.params['param'] in ('WISH','FROZEN','WORK_IN_PROGRESS','COMPLETED','DROPPED'):
            post['variables']['activity']['include'] = [self.params['param']]
        if self.params['param'] in ('Аниме','Дорамы','Мультфильмы','Разное'):
            post['variables']['category']['include'] = [shiza_categories[self.params['param']]]

        if 'catalog' in self.params['param']:
            if self.addon.getSetting('shiza_season'):
                post['variables']['season']['include'] = shiza_season[self.addon.getSetting('shiza_season')]
            if self.addon.getSetting('shiza_categories'):
                post['variables']['category']['include'] = shiza_categories[self.addon.getSetting('shiza_categories')]
            if self.addon.getSetting('shiza_status'):
                post['variables']['status']['include'] = shiza_status[self.addon.getSetting('shiza_status')]
            if self.addon.getSetting('shiza_voice_stat'):
                post['variables']['activity']['include'] = shiza_voice_stat[self.addon.getSetting('shiza_voice_stat')]
            if self.addon.getSetting('shiza_form'):
                post['variables']['type']['include'] = shiza_form[self.addon.getSetting('shiza_form')]
            if self.addon.getSetting('shiza_rating'):
                post['variables']['rating']['include'] = self.addon.getSetting('shiza_rating')
            if self.addon.getSetting('shiza_genre'):
                post['variables']['genre']['include'] = shiza_genre[self.addon.getSetting('shiza_genre')]
            if self.addon.getSetting('shiza_tags'):
                post['variables']['tag']['include'] = shiza_tags[self.addon.getSetting('shiza_tags')]
            
            post['variables']['orderBy'] = {
                "field":shiza_sort[self.addon.getSetting('shiza_sort')],
                "direction":shiza_direction[self.addon.getSetting('shiza_direction')]}

        post = str(post).replace('\'','"').replace('None','null')
        
        if 'search_string' in self.params:
            post = post.replace('"query": ""','"query": "{}"'.format(unquote(self.params['search_string'])))
            #post['variables']['query'] = unquote(self.params['search_string'])
        return post
#========================#========================#========================#
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

            online_array.append(u'{}||{}||{}'.format(episode_name,episode_num,episode_url))
        
        episodes_data = u'|||'.join(online_array)

        return episodes_data
#========================#========================#========================#
    def create_torrent(self, torrent):
        seed = torrent[torrent.find('seeders":')+9:torrent.find(',"leechers')]
        leech = torrent[torrent.find('leechers":')+10:torrent.find(',"size')]
        size = torrent[torrent.find('size":"')+7:torrent.find('","metadata')]

        metadata = torrent[torrent.find('metadata":"')+11:torrent.find('","videoFormat')]
        metadata = metadata.replace(u'Автор рипа',u'[COLOR=steelblue]Автор рипа[/COLOR]')
        metadata = metadata.replace(u'Видео',u'[COLOR=steelblue]Видео[/COLOR]')
        metadata = metadata.replace(u'Аудио',u'[COLOR=steelblue]Аудио[/COLOR]')
        metadata = metadata.replace(u'Субтитры',u'[COLOR=steelblue]Субтитры[/COLOR]')
        
        video_format = torrent[torrent.find('videoFormat":"')+14:torrent.find('","videoQualities')]
        quality = torrent[torrent.find('videoQualities":["')+18:torrent.find('"],"file')]
        #quality = quality.replace('","','||')
        url = torrent[torrent.find('url":"')+6:torrent.find('?filename=')]

        torrent_data = u'{}||{}||{}||{}||{}||{}||{}'.format(seed,leech,size,metadata,video_format,quality,url)
        return torrent_data
#========================#========================#========================#
    def create_title(self, anime_id, episodes_count, episodes_aired):        
        title = self.database.get_title(anime_id)

        series = u' - [COLOR=gold][ Серии: 1-{} из {} ][/COLOR]'.format(episodes_aired, episodes_count)

        if '0' in self.addon.getSetting('shiza_titles'):
        #if self.addon.getSetting('shiza_titles') == '0':
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('shiza_titles'):
        #if self.addon.getSetting('shiza_titles') == '1':
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('shiza_titles'):
        #if self.addon.getSetting('shiza_titles') == '2':
            label = u'{} / {}{}'.format(title[0], title[1], series)

        return label
#========================#========================#========================#
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
#========================#========================#========================#
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
#========================#========================#========================#
    def create_info(self, slug='', update=False):        
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
        html = self.network.get_html2(self.site_url, post)

        try: html = html.decode(encoding='utf-8', errors='replace')
        except: pass

        html = unescape(html)
        html = html.replace('\\n', '\n').replace('\\"', '"')

        data = html.replace('null','""')

        anime_id = data[data.find('"slug":"')+8:data.find('","malId"')]
        shiki_id = data[data.find('"malId":"')+9:data.find('","name"')]

        title_ru = data[data.find('"name":"')+8:data.find('","originalName"')]
        title_en = data[data.find('"originalName":"')+16:data.find('","description"')]

        plot = data[data.find('"description":"')+15:data.find('","descriptionSource"')]
        plot_source = data[data.find('"descriptionSource":"')+21:data.find('","countries"')]
        if plot_source:
            plot = u'{}\n© {}'.format(plot, plot_source)

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
                title_ru = title_ru,
                title_en = title_en,
                description = plot,
                country = countries,
                aired_on = aired,
                studios = studios,
                genres = genres,
                writer = staff,
                dubbing = ', '.join(contributors['VOICE_ACTING']),
                mastering = ', '.join(contributors['MASTERING']),
                timing = ', '.join(contributors['TIMING']),
                other = ', '.join(contributors['OTHER']),
                translation = ', '.join(contributors['TRANSLATION']),
                editing = ', '.join(contributors['EDITING']),
                update=update
            )
        except:
            return 101
        # try:
        #     self.database.add_anime(
        #         anime_id = anime_id,
        #         shiki_id = shiki_id,
        #         title_ru = title_ru,
        #         title_en = title_en,
        #         plot = plot,
        #         countries = countries,
        #         aired = aired,
        #         studios = studios,
        #         genres = genres,
        #         authors = staff,
        #         dubbing = ', '.join(contributors['VOICE_ACTING']),
        #         mastering = ', '.join(contributors['MASTERING']),
        #         timing = ', '.join(contributors['TIMING']),
        #         other = ', '.join(contributors['OTHER']),
        #         translation = ', '.join(contributors['TRANSLATION']),
        #         editing = ', '.join(contributors['EDITING'])
        #         )
        # except:
        #     return 101

        return
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        context_menu.append(('[B][COLOR=darkorange]Обновить Базу Данных[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=shizaproject")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=red]Очистить историю[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=shizaproject")'))

        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append(('[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=shizaproject")'))
        context_menu.append(('[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=shizaproject")'))
        context_menu.append(('[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=shizaproject")'))
        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))        

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if metadata:
            li.setInfo(type='video', infoLabels={'plot':metadata})

        if anime_id:
            cover = self.create_image(anime_id, cover)

            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})
            # 0     1       2           3           4           5       6       7       8       9           10          11      12          13      14      15          16      17      18      19
            #kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios
            anime_info = self.database.get_anime(anime_id)
            
            description = u'{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(anime_info[10], anime_info[11])
            description = u'{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(description, anime_info[12])
            description = u'{}\n[COLOR=steelblue]Тайминг[/COLOR]: {}'.format(description, anime_info[13])
            description = u'{}\n[COLOR=steelblue]Работа над звуком[/COLOR]: {}'.format(description, anime_info[14])
            description = u'{}\n[COLOR=steelblue]Mastering[/COLOR]: {}'.format(description, anime_info[15])
            description = u'{}\n[COLOR=steelblue]Редактирование[/COLOR]: {}'.format(description, anime_info[16])
            description = u'{}\n[COLOR=steelblue]Другое[/COLOR]: {}'.format(description, anime_info[17])

            info = {
                'genre':anime_info[7], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                'country':anime_info[18],#string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year':anime_info[3],#	integer (2009)
                'episode':anime_info[2],#	integer (4)
                #'season':'',#	integer (1)
                #'sortepisode':'',#	integer (4)
                #'sortseason':'',#	integer (1)
                #'episodeguide':'',#	string (Episode guide)
                #'showlink':'',#	string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])
                #'top250':'',#	integer (192)
                #'setid':'',#	integer (14)
                #'tracknumber':'',#	integer (3)
                #'rating':'',#	float (6.4) - range is 0..10
                #'userrating':'',#	integer (9) - range is 1..10 (0 to reset)
                #'watched':'',#	deprecated - use playcount instead
                #'playcount':'',#	integer (2) - number of times this item has been played
                #'overlay':'',#	integer (2) - range is 0..7. See Overlay icon types for values
                #'cast':'',#	list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole
                #'castandrole':'',#	list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
                'director':anime_info[9],#	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                'mpaa':anime_info[5],#	string (PG-13)
                'plot':description,#	string (Long Description)
                #'plotoutline':'',#	string (Short Description)
                'title':title,#	string (Big Fan)
                #'originaltitle':'',#	string (Big Fan)
                #'sorttitle':'',#	string (Big Fan)
                'duration':anime_info[6],#	integer (245) - duration in seconds
                'studio':anime_info[19],#	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                #'tagline':'',#	string (An awesome movie) - short description of movie
                'writer':anime_info[8],#	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                'tvshowtitle':title,#	string (Heroes)
                'premiered':anime_info[3],#	string (2005-03-04)
                'status':anime_info[1],#	string (Continuing) - status of a TVshow
                #'set':'',#	string (Batman Collection) - name of the collection
                #'setoverview':'',#	string (All Batman movies) - overview of the collection
                #'tag':'',#	string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
                #'imdbnumber':'',#	string (tt0110293) - IMDb code
                #'code':'',#	string (101) - Production code
                'aired':anime_info[3],#	string (2008-12-07)
                #'credits':'',#	string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
                #'lastplayed':'',#	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #'album':'',#	string (The Joshua Tree)
                #'artist':'',#	list (['U2'])
                #'votes':'',#	string (12345 votes)
                #'path':'',#	string (/home/user/movie.avi)
                #'trailer':'',#	string (/home/user/trailer.avi)
                #'dateadded':'',#	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #'mediatype':anime_info[0],#	string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
                #'dbid':'',#	integer (23) - Only add this for items which are part of the local db. You also need to set the correct 'mediatype'!
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = 'shizaproject'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online
        #xbmc.log(str(online), xbmc.LOGNOTICE)

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    # def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None): 
    #     li = xbmcgui.ListItem(title)

    #     if metadata:
    #         li.setInfo(type='video', infoLabels={'plot':metadata})

    #     if anime_id:
    #         #cover = cover
    #         cover = self.create_image(anime_id, cover)

    #         li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
    #                    "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})

    #         anime_info = self.database.get_anime(anime_id)

    #         info = {
    #             'plot': anime_info[0],
    #             'country': anime_info[1],
    #             'year': anime_info[2],
    #             'premiered': anime_info[2],
    #             'studio': anime_info[3],
    #             'genre': anime_info[4],
    #             'writer': anime_info[5],
    #             'director': anime_info[5],
    #             'title': title, 
    #             'tvshowtitle': title}
            
    #         info['plot'] = '{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(info['plot'], anime_info[6])
    #         info['plot'] = '{}\n[COLOR=steelblue]Работа со звуком[/COLOR]: {}'.format(info['plot'], anime_info[7])
    #         info['plot'] = '{}\n[COLOR=steelblue]Работа над таймингом[/COLOR]: {}'.format(info['plot'], anime_info[8])
    #         info['plot'] = '{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(info['plot'], anime_info[10])
    #         info['plot'] = '{}\n[COLOR=steelblue]Редактура[/COLOR]: {}'.format(info['plot'], anime_info[11])
    #         info['plot'] = '{}\n[COLOR=steelblue]Другое[/COLOR]: {}'.format(info['plot'], anime_info[9])

    #         if size:
    #             info['size'] = size

    #         li.setInfo(type='video', infoLabels=info)

    #     li.addContextMenuItems(self.create_context(anime_id))

    #     if folder==False:
    #             li.setProperty('isPlayable', 'true')

    #     params['portal'] = 'shizaproject'
    #     url = '{}?{}'.format(sys.argv[0], urlencode(params))

    #     if online: url = online

    #     xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_addon_setting(self):
        self.addon.openSettings()
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        except: pass

        db_file = os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_{}.db'.format(self.params['portal'])
        try:                
            data = urlopen(db_url)
            chunk_size = 8192
            bytes_read = 0

            try: file_size = int(data.info().getheaders("Content-Length")[0])
            except: file_size = int(data.getheader('Content-Length'))

            self.progress.create(u'Загрузка Базы Данных')
            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                self.progress.close()
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
            pass

    # def exec_update_database_part(self):
    #     try: self.database.end()
    #     except: pass
        
    #     #try: os.remove(os.path.join(self.database_dir, 'anidub.db'))
    #     try: os.remove(os.path.join(self.database_dir, '{}.db'.format(self.params['portal'])))
    #     except: pass

    #     #db_file = os.path.join(self.database_dir, 'anidub.db')
    #     db_file = os.path.join(self.database_dir, '{}.db'.format(self.params['portal']))
    #     #db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anidub.db'
    #     db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/{}.db'.format(self.params['portal'])
    #     try:                
    #         data = urlopen(db_url)
    #         chunk_size = 8192
    #         bytes_read = 0

    #         try: file_size = int(data.info().getheaders("Content-Length")[0])
    #         except: file_size = int(data.getheader('Content-Length'))

    #         self.progress.create('Загрузка Базы Данных')
    #         with open(db_file, 'wb') as write_file:
    #             while True:
    #                 chunk = data.read(chunk_size)
    #                 bytes_read = bytes_read + len(chunk)
    #                 write_file.write(chunk)
    #                 if len(chunk) < chunk_size:
    #                     break
    #                 percent = bytes_read * 100 / file_size
    #                 self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
    #             self.progress.close()
    #         #label_1 = '{} - База Данных'.format(self.params['portal'].upper())
    #         #label_2 = 'База Данных [COLOR=lime]успешно загружена[/COLOR]'
    #         xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
    #             self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
    #         #self.dialog.ok('AniDUB - База Данных','БД успешно загружена')
    #     except:
    #         xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
    #             self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
    #         #self.dialog.ok('AniDUB - База Данных','Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
    #         pass
        
    # def exec_update_database_part(self):
    #     try: self.database.end()
    #     except: pass

    #     try: os.remove(os.path.join(self.database_dir, 'shizaproject.db'))
    #     except: pass

    #     db_file = os.path.join(self.database_dir, 'shizaproject.db')        
    #     db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/shizaproject.db'
    #     try:                
    #         data = urlopen(db_url)
    #         chunk_size = 8192
    #         bytes_read = 0

    #         try: file_size = int(data.info().getheaders("Content-Length")[0])
    #         except: file_size = int(data.getheader('Content-Length'))

    #         self.progress.create('Загрузка Базы Данных')
    #         with open(db_file, 'wb') as write_file:
    #             while True:
    #                 chunk = data.read(chunk_size)
    #                 bytes_read = bytes_read + len(chunk)
    #                 write_file.write(chunk)
    #                 if len(chunk) < chunk_size:
    #                     break
    #                 percent = bytes_read * 100 / file_size
    #                 self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
    #             self.progress.close()
    #         self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
    #     except:
    #         self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
    #         pass
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=lime]успешно выполнено[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=yellow]ERROR: 102[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
    def exec_information_part(self):
        from info import animeportal_data as info
            
        start = '[{}]'.format(self.params['param'])
        end = '[/{}]'.format(self.params['param'])
        data = info[info.find(start)+6:info.find(end)].strip()

        self.dialog.textviewer(u'Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=lime][ Аниме ][/COLOR][/B]', params={'mode': 'anime_part'})
        self.create_line(title='[B][COLOR=yellow][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Дорамы'})
        self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Мультфильмы'})
        self.create_line(title='[B][COLOR=orange][ Кино и ТВ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'Разное'})
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_anime_part(self):
        self.create_line(title='[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part'})
        self.create_line(title='[B][COLOR=lime][ Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'ONGOING'})
        self.create_line(title='[B][COLOR=lime][ В работе ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'WORK_IN_PROGRESS'})
        self.create_line(title='[B][COLOR=lime][ Запланированные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'WISH'})
        self.create_line(title='[B][COLOR=lime][ Завершенные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'COMPLETED'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title=u'[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('shizaproject_search').split('|')
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
                data_array = self.addon.getSetting('shizaproject_search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('shizaproject_search', data_array)

                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create("ShizaProject", u"Инициализация")
        post = self.create_post()

        html = self.network.get_html2(self.site_url, post)

        try: html = html.decode(encoding='utf-8', errors='replace')
        except: pass

        data_array = html.split('{"node":{"slug":"')
        data_array.pop(0)

        i = 0

        for data in data_array:
            data = unescape(data)

            anime_id = data[:data.find('",')]
            episodes_count = data[data.find('episodesCount":')+15:data.find(',"episodesAired')]
            episodes_aired = data[data.find('episodesAired":')+15:data.find(',"posters')]

            poster_data = data[data.find('posters":[{')+11:data.find('"}}],"episodes')]
            poster_preview = poster_data[poster_data.find('https://'):poster_data.find('"},"original')]
            poster_original = poster_data[poster_data.rfind('https://'):]

            #episodes = data[data.find('"episodes":[{')+13:data.find('],"torrents')]
            episodes = data[data.find('"episodes":[')+12:data.find('],"torrents')]
            episodes = self.create_episodes(episodes)

            try: episodes = episodes.encode('utf-8')
            except: pass
            #xbmc.log(str(episodes), xbmc.LOGNOTICE)

            torrent = data[data.find('torrents":[{')+12:data.find('"}}]}}')]
            torrent = self.create_torrent(torrent)

            try: torrent = torrent.encode('utf-8')
            except: pass

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
            if not self.database.anime_in_db(anime_id):
                inf = self.create_info(anime_id)

            label = self.create_title(anime_id, episodes_count, episodes_aired)

            if '0' in self.addon.getSetting('shiza_covers_quality'):
            #if self.addon.getSetting('shiza_covers_quality') == '0':
                cover = poster_preview
            else:
                cover = poster_original

            series = '1-{} / {}'.format(episodes_aired, episodes_count)

            self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part','id': anime_id,'cover':cover,'episodes':episodes,'torrent':torrent,'series':series})

        self.progress.close()

        if 'hasNextPage":true' in html:
            after = html[html.find('endCursor":"')+12:html.rfind('"}')]
            self.create_line(title=u'[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                             'mode': self.params['mode'], 'param': self.params['param'], 'after': after})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        from info import shiza_categories, shiza_season, shiza_status, shiza_voice_stat, shiza_form, shiza_genre, shiza_tags, shiza_sort, shiza_direction, shiza_rating

        shiza_year = ['{}'.format(year) for year in range(1970,2022)]

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
            result = self.dialog.select('Начало отрезка:', tuple(shiza_year))
            self.addon.setSetting(id='shiza_year_start', value=tuple(shiza_year)[result])        
        if 'shiza_year_end' in self.params['param']:
            result = self.dialog.select('Конец отрезка:', tuple(shiza_year))
            self.addon.setSetting(id='shiza_year_end', value=tuple(shiza_year)[result])
        if 'shiza_season' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_season.keys()))
            self.addon.setSetting(id='shiza_season', value=tuple(shiza_season.keys())[result])
        if 'shiza_categories' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_categories.keys()))
            self.addon.setSetting(id='shiza_categories', value=tuple(shiza_categories.keys())[result])
        if 'shiza_status' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_status.keys()))
            self.addon.setSetting(id='shiza_status', value=tuple(shiza_status.keys())[result])
        if 'shiza_voice_stat' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_voice_stat.keys()))
            self.addon.setSetting(id='shiza_voice_stat', value=tuple(shiza_voice_stat.keys())[result])
        if 'shiza_form' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_form.keys()))
            self.addon.setSetting(id='shiza_form', value=tuple(shiza_form.keys())[result])
        if 'shiza_rating' in self.params['param']:
            result = self.dialog.select('Сортировка по:', shiza_rating)
            self.addon.setSetting(id='shiza_rating', value=shiza_rating[result])
        if 'shiza_genre' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_genre.keys()))
            self.addon.setSetting(id='shiza_genre', value=tuple(shiza_genre.keys())[result])
        if 'shiza_tags' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_tags.keys()))
            self.addon.setSetting(id='shiza_tags', value=tuple(shiza_tags.keys())[result])
        if 'shiza_sort' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shiza_sort.keys()))
            self.addon.setSetting(id='shiza_sort', value=tuple(shiza_sort.keys())[result])        
        if 'shiza_direction' in self.params['param']:
            result = self.dialog.select('Направление сортировки:', tuple(shiza_direction.keys()))
            self.addon.setSetting(id='shiza_direction', value=tuple(shiza_direction.keys())[result])
#========================#========================#========================#
    def exec_select_part(self):
        if 'episodes' in self.params:
            self.create_line(title=u'[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id'], 'episodes':self.params['episodes'], 'cover': self.params['cover']})
        if 'torrent' in self.params:
            self.create_line(title=u'[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent':self.params['torrent'], 'cover': self.params['cover'], 'series':self.params['series']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            try:
                data_array = self.params['episodes'].decode('utf-8')
                data_array = data_array.split('|||')
            except:
                data_array = self.params['episodes'].split('|||')
            #data_array = self.params['episodes'].split('|||')
            cover = self.params['cover']

            for data in data_array:
                data = data.split('||')
                episode_title = data[0]
                episode_num = data[1]
                episode_url = data[2]

                #xbmc.log(str(data[2]), xbmc.LOGNOTICE)

                label = u'{} - {}'.format(episode_num, episode_title)
                #self.create_line(title=label, anime_id=self.params['id'], cover=cover, params={'mode': 'online_part', 'id': self.params['id'], 'param': data[2], 'title':label, 'cover': cover})
                self.create_line(title=label, anime_id=self.params['id'], cover=cover, params={'mode': 'online_part', 'id': self.params['id'], 'param': data[2], 'title':'[COLOR=gold][ PLAY ][/COLOR]', 'cover': cover})

        if self.params['param']:
            html = self.network.get_html2(target_name=self.params['param'])
            
            cover = html[html.find('og:image" content="')+19:html.find('"/><meta property="og:description')]
            
            if 'player.src' in html:
                video_src = html[html.find('player.src([{src: "')+19:html.find(';player.persistvolume')]
                video_src = video_src[:video_src.find('"')]
                play_url = 'https://video.sibnet.ru{}|referer={}'.format(video_src, self.params['param'])
                #xbmc.log(str(play_url), xbmc.LOGNOTICE)

                label = self.params['title']

            if 'class=videostatus><p>' in html:
                status = html[html.find('class=videostatus><p>')+21:html.find('</p></div><script')]
                label = '[COLOR=red][B][ {} ][/B][/COLOR]'.format(status.replace('.',''))
                play_url = ''

            self.create_line(title=label, cover=cover, params={}, anime_id=self.params['id'], online=play_url, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            try:
                data = self.params['episodes'].decode('utf-8')
                data = data.split('||')
            except:
                data = self.params['torrent'].split('||')

            #data = self.params['torrent'].split('||')

            seeders = data[0]
            leechers = data[1]
            torrent_size = '{:.2f}'.format(float(data[2]) / 1024 / 1024 / 1024)
            metadata = data[3].replace('\\n','\n\n')
            video_format = data[4]
            quality = data[5].replace('","',' - ').replace('RESOLUTION_','')
            torrent_url = data[6]

            label = u'Серии: {} - {}, {} , [COLOR=F0FFD700]{} GB[/COLOR], Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
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
#========================#========================#========================#
    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])

        if self.addon.getSetting(portal_engine) == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if self.addon.getSetting(portal_engine) == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)