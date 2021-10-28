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

class Shiza:
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
        
        #self.auth_mode = bool(self.addon.getSetting('shizaproject_auth_mode') == '1')
        self.auth_mode = bool(self.addon.getSetting('{}_auth_mode'.format(self.params['portal'])) == '1')
#========================#========================#========================#
        try: session = float(self.addon.getSetting('{}_session'.format(self.params['portal'])))
        except: session = 0

        if time.time() - session > 28800:
            self.addon.setSetting('{}_session'.format(self.params['portal']), str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal'])))
            except: pass
            self.addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('shizaproject_auth') == 'true'),
            proxy_data=self.proxy_data,
            portal='shizaproject')
        self.auth_post_data = {
            "mail": self.addon.getSetting('shizaproject_username'),
            "passwd": self.addon.getSetting('shizaproject_password')
            }
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = ''
        self.network.sid_file = os.path.join(self.cookie_dir, 'shizaproject.sid')
        del WebTools
#========================#========================#========================#  
        if self.auth_mode:
            if not self.addon.getSetting('{}_username'.format(self.params['portal'])) or not self.addon.getSetting('{}_password'.format(self.params['portal'])):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ВВЕДИТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                    return
                else:
                    self.addon.setSetting('{}_auth'.format(self.params['portal']), str(self.network.auth_status).lower())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
#========================#========================#========================#
    def create_proxy_data(self):
        if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

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

                try: proxy_pac = proxy_pac.decode('utf-8')
                except: pass
                
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = 'shizaproject_mirror_{}'.format(self.addon.getSetting('shizaproject_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('shizaproject_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_post(self):
        from info import shizaproject_categories, shizaproject_season, shizaproject_status, shizaproject_voice_stat, shizaproject_form, shizaproject_genre, shizaproject_tags, shizaproject_sort, shizaproject_direction
        post = {
            "operationName":"fetchReleases",
            "variables":{
                "first": 15,
                "airedOn":{"startYear":int(self.addon.getSetting('shizaproject_year_start')),"endYear":int(self.addon.getSetting('shizaproject_year_end'))},
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
            post['variables']['category']['include'] = [shizaproject_categories[self.params['param']]]

        if 'catalog' in self.params['param']:
            if self.addon.getSetting('shizaproject_season'):
                post['variables']['season']['include'] = shizaproject_season[self.addon.getSetting('shizaproject_season')]
            if self.addon.getSetting('shizaproject_categories'):
                post['variables']['category']['include'] = shizaproject_categories[self.addon.getSetting('shizaproject_categories')]
            if self.addon.getSetting('shizaproject_status'):
                post['variables']['status']['include'] = shizaproject_status[self.addon.getSetting('shizaproject_status')]
            if self.addon.getSetting('shizaproject_voice_stat'):
                post['variables']['activity']['include'] = shizaproject_voice_stat[self.addon.getSetting('shizaproject_voice_stat')]
            if self.addon.getSetting('shizaproject_form'):
                post['variables']['type']['include'] = shizaproject_form[self.addon.getSetting('shizaproject_form')]
            if self.addon.getSetting('shizaproject_rating'):
                post['variables']['rating']['include'] = self.addon.getSetting('shizaproject_rating')
            if self.addon.getSetting('shizaproject_genre'):
                post['variables']['genre']['include'] = shizaproject_genre[self.addon.getSetting('shizaproject_genre')]
            if self.addon.getSetting('shizaproject_tags'):
                post['variables']['tag']['include'] = shizaproject_tags[self.addon.getSetting('shizaproject_tags')]
            
            post['variables']['orderBy'] = {
                "field":shizaproject_sort[self.addon.getSetting('shizaproject_sort')],
                "direction":shizaproject_direction[self.addon.getSetting('shizaproject_direction')]}

        post = str(post).replace('\'','"').replace('None','null')
        
        if 'search_string' in self.params:
            post = post.replace('"query": ""','"query": "{}"'.format(unquote(self.params['search_string'])))
        return post
#========================#========================#========================#
    def create_episodes(self, episodes):
        online_array = []
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
        url = torrent[torrent.find('url":"')+6:torrent.find('?filename=')]

        torrent_data = u'{}||{}||{}||{}||{}||{}||{}'.format(seed,leech,size,metadata,video_format,quality,url)

        if not '.torrent' in torrent_data:
            torrent_data = ''

        return torrent_data
#========================#========================#========================#
    def create_title(self, anime_id, episodes_count, episodes_aired):        
        title = self.database.get_title(anime_id)

        episodes_aired = episodes_aired.replace('null','0')
        episodes_count = episodes_count.replace('null','XXX')

        series = u' - [COLOR=gold][ Серии: {} из {} ][/COLOR]'.format(episodes_aired, episodes_count)

        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{} / {}{}'.format(title[0], title[1], series)

        return label
#========================#========================#========================#
    def create_image(self, anime_id, url):
        if self.addon.getSetting('shizaproject_covers') == '0':
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
        html = self.network.get_html(self.site_url, post)

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
        return
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=shizaproject")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=shizaproject")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=shizaproject")'.format(anime_id)))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=shizaproject")'))
        context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=shizaproject")'))
        context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=shizaproject")'))    

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
                'director':anime_info[9],#	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                'mpaa':anime_info[5],#	string (PG-13)
                'plot':description,#	string (Long Description)
                'title':title,#	string (Big Fan)
                'duration':anime_info[6],#	integer (245) - duration in seconds
                'studio':anime_info[19],#	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                'writer':anime_info[8],#	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                'tvshowtitle':title,#	string (Heroes)
                'premiered':anime_info[3],#	string (2005-03-04)
                'status':anime_info[1],#	string (Continuing) - status of a TVshow
                'aired':anime_info[3],#	string (2008-12-07)
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = 'shizaproject'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_addon_setting(self):
        self.addon.openSettings()
#========================#========================#========================#
    def exec_update_anime_part(self):
        self.create_info(slug=self.params['id'], update=True)
        xbmc.executebuiltin('Container.Refresh')
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
            xbmc.executebuiltin('Notification({},{},{},{})'.format('База Данных', '[COLOR=lime]УСПЕШНО ЗАГРУЖЕНА[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('База Данных', '[COLOR=gold]ERROR: 100[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Удаление истории', '[COLOR=lime]УСПЕШНО ВЫПОЛНЕНО[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Удаление истории', '[COLOR=gold]ERROR: 102[/COLOR]', 5000, self.icon))
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

        html = self.network.get_html(self.site_url, post)

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

            episodes = data[data.find('"episodes":[')+12:data.find('],"torrents')]
            episodes = self.create_episodes(episodes)

            try: episodes = episodes.encode('utf-8')
            except: pass

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

            if '0' in self.addon.getSetting('shizaproject_covers_quality'):
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
        from info import shizaproject_categories, shizaproject_season, shizaproject_status, shizaproject_voice_stat, shizaproject_form, shizaproject_genre, shizaproject_tags, shizaproject_sort, shizaproject_direction, shizaproject_rating

        shizaproject_year = ['{}'.format(year) for year in range(1970,2022)]

        if not self.params['param']:
            self.create_line(title='Год (начало отрезка): [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_year_start')), params={'mode': 'catalog_part', 'param': 'shizaproject_year_start'})
            self.create_line(title='Год (конец отрезка): [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_year_end')), params={'mode': 'catalog_part', 'param': 'shizaproject_year_end'})  
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_season')), params={'mode': 'catalog_part', 'param': 'shizaproject_season'})            
            self.create_line(title='Категория: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_categories')), params={'mode': 'catalog_part', 'param': 'shizaproject_categories'})
            self.create_line(title='Статус тайтла: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_status')), params={'mode': 'catalog_part', 'param': 'shizaproject_status'})
            self.create_line(title='Статус озвучки: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_voice_stat')), params={'mode': 'catalog_part', 'param': 'shizaproject_voice_stat'})            
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_form')), params={'mode': 'catalog_part', 'param': 'shizaproject_form'})            
            self.create_line(title='Возрастное ограничение: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_rating')), params={'mode': 'catalog_part', 'param': 'shizaproject_rating'})
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_genre')), params={'mode': 'catalog_part', 'param': 'shizaproject_genre'})
            self.create_line(title='Тэги: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_tags')), params={'mode': 'catalog_part', 'param': 'shizaproject_tags'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_sort')), params={'mode': 'catalog_part', 'param': 'shizaproject_sort'})
            self.create_line(title='Направление сортировки: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_direction')), params={'mode': 'catalog_part', 'param': 'shizaproject_direction'})

            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)            
        
        if 'shizaproject_year_start' in self.params['param']:
            result = self.dialog.select('Начало отрезка:', tuple(shizaproject_year))
            self.addon.setSetting(id='shizaproject_year_start', value=tuple(shizaproject_year)[result])        
        if 'shizaproject_year_end' in self.params['param']:
            result = self.dialog.select('Конец отрезка:', tuple(shizaproject_year))
            self.addon.setSetting(id='shizaproject_year_end', value=tuple(shizaproject_year)[result])
        if 'shizaproject_season' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_season.keys()))
            self.addon.setSetting(id='shizaproject_season', value=tuple(shizaproject_season.keys())[result])
        if 'shizaproject_categories' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_categories.keys()))
            self.addon.setSetting(id='shizaproject_categories', value=tuple(shizaproject_categories.keys())[result])
        if 'shizaproject_status' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_status.keys()))
            self.addon.setSetting(id='shizaproject_status', value=tuple(shizaproject_status.keys())[result])
        if 'shizaproject_voice_stat' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_voice_stat.keys()))
            self.addon.setSetting(id='shizaproject_voice_stat', value=tuple(shizaproject_voice_stat.keys())[result])
        if 'shizaproject_form' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_form.keys()))
            self.addon.setSetting(id='shizaproject_form', value=tuple(shizaproject_form.keys())[result])
        if 'shizaproject_rating' in self.params['param']:
            result = self.dialog.select('Сортировка по:', shizaproject_rating)
            self.addon.setSetting(id='shizaproject_rating', value=shizaproject_rating[result])
        if 'shizaproject_genre' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_genre.keys()))
            self.addon.setSetting(id='shizaproject_genre', value=tuple(shizaproject_genre.keys())[result])
        if 'shizaproject_tags' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_tags.keys()))
            self.addon.setSetting(id='shizaproject_tags', value=tuple(shizaproject_tags.keys())[result])
        if 'shizaproject_sort' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_sort.keys()))
            self.addon.setSetting(id='shizaproject_sort', value=tuple(shizaproject_sort.keys())[result])        
        if 'shizaproject_direction' in self.params['param']:
            result = self.dialog.select('Направление сортировки:', tuple(shizaproject_direction.keys()))
            self.addon.setSetting(id='shizaproject_direction', value=tuple(shizaproject_direction.keys())[result])
#========================#========================#========================#
    def exec_select_part(self):
        if 'episodes' in self.params or 'torrent' in self.params:
            if 'episodes' in self.params:
                self.create_line(title=u'[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id'], 'episodes':self.params['episodes'], 'cover': self.params['cover']})
            if 'torrent' in self.params:
                self.create_line(title=u'[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent':self.params['torrent'], 'cover': self.params['cover'], 'series':self.params['series']})
        else:
            self.create_line(title=u'[B][COLOR=red][ Онлайн и Торрент ссылки отсутствуют ][/COLOR][/B]', params={'mode': self.params['mode']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            try:
                data_array = self.params['episodes'].decode('utf-8')
                data_array = data_array.split('|||')
            except:
                data_array = self.params['episodes'].split('|||')
            cover = self.params['cover']

            for data in data_array:
                data = data.split('||')
                episode_title = data[0]
                episode_num = data[1]
                episode_url = data[2]

                label = u'{} - {}'.format(episode_num, episode_title)
                self.create_line(title=label, anime_id=self.params['id'], cover=cover, params={'mode': 'online_part', 'id': self.params['id'], 'param': data[2], 'title':'[COLOR=gold][ PLAY ][/COLOR]', 'cover': cover})

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
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            try:
                data = self.params['episodes'].decode('utf-8')
                data = data.split('||')
            except:
                data = self.params['torrent'].split('||')

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

        if '0' in self.addon.getSetting(portal_engine):
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')            
            engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if '1' in self.addon.getSetting(portal_engine):
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)