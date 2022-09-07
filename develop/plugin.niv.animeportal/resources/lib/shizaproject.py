# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin

import requests
session = requests.Session()

try:
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
except:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from html import unescape
 
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity',
    'Content-Type': 'application/json'
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    
class Shiza:
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        self.params = params
        self.addon = addon
        self.icon = icon

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        self.proxy_data = self.exec_proxy_data()

        self.site_url = self.create_site_url()
        
        self.authorization = False#self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
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
        from info import shizaproject_categories, shizaproject_season, shizaproject_status, shizaproject_voice_stat, shizaproject_form, shizaproject_genre, shizaproject_sort, shizaproject_direction
        
        post = {
            "operationName":"fetchReleases",
            "variables":{
                "first":18,
                "airedOn":None,
                "query":"",
                "after":"",
                "orderBy":{"field":"PUBLISHED_AT","direction":"DESC"},
                "type":{"include":[],"exclude":[]},
                "status":{"include":[],"exclude":["DRAFT"]},
                "activity":{"include":[],"exclude":["WISH"]},
                "rating":{"include":[],"exclude":[]},
                "season":{"include":[],"exclude":[]},
                "watchlist":{"include":[],"exclude":[]},
                "genre":{"include":[],"exclude":[]},
                "category":{"include":[],"exclude":[]},
                "tag":{"include":[],"exclude":[]},
                "studio":{"include":[],"exclude":[]},
                "staff":{"include":[],"exclude":[]},
                "contributor":{"include":[],"exclude":[]}                
                },
            "query":"query fetchReleases($first: Int, $after: String, $orderBy: ReleaseOrder, $query: String, $tag: ReleaseIDFilter, $category: ReleaseIDFilter, $genre: ReleaseIDFilter, $studio: ReleaseIDFilter, $type: ReleaseTypeFilter, $status: ReleaseStatusFilter, $rating: ReleaseRatingFilter, $airedOn: ReleaseAiredOnRangeFilter, $activity: ReleaseActivityFilter, $season: ReleaseSeasonFilter, $staff: ReleaseIDFilter, $contributor: ReleaseIDFilter, $watchlist: ReleaseWatchlistFilter, $watchlistUserId: ID) {  releases(    first: $first   after: $after   orderBy: $orderBy   query: $query   tag: $tag   category: $category   genre: $genre   studio: $studio   type: $type   status: $status   airedOn: $airedOn   rating: $rating   activity: $activity   season: $season   staff: $staff   contributor: $contributor   watchlist: $watchlist   watchlistUserId: $watchlistUserId ) {   totalCount   edges {     node {       ...ReleaseCard       viewerWatchlist {         id         status         __typename       }       reactionGroups {         count         content         viewerHasReacted         __typename       }       viewerInBlockedCountry       __typename     }     __typename   }   pageInfo {     hasNextPage     hasPreviousPage     startCursor     endCursor     __typename   }   __typename }}fragment ReleasePosterCommon on ImageFile {  id  preview: resize(width: 360, height: 500) {    width    height    url    __typename  }  original {    width    height    url    __typename  }  __typename}fragment ReleaseCard on Release {  id  slug  name  originalName  airedOn  releasedOn  publishedAt  announcement  episodesCount  episodesAired  episodeDuration  season  seasonYear  seasonNumber  status  activity  type  rating  viewCount  score  posters {    ...ReleasePosterCommon    __typename  } episodes {name number videos { embedSource embedUrl }} torrents {seeders leechers size metadata videoFormat videoQualities file { url }} genres {    id    slug    name    __typename  }  viewerWatchlist {    id    status    score    episodes    rewatches    __typename  }  reactionGroups {    count    content    viewerHasReacted    __typename  }  __typename}"}
        
        if 'search_string' in self.params:
            post['variables']['query'] = self.params['search_string']
            
        if 'after' in self.params:
            post['variables']['after'] = self.params['after']

        if self.params['param'] in ('ANNOUNCE','ONGOING','RELEASED','SUSPENDED'):
            post['variables']['status']['include'] = [self.params['param']]
        if self.params['param'] in ('FROZEN','WORK_IN_PROGRESS','COMPLETED','DROPPED'):
            post['variables']['activity']['include'] = [self.params['param']]
        if self.params['param'] in ('Дорамы','Мультфильмы','Разное'):
            post['variables']['category']['include'] = [shizaproject_categories[self.params['param']]]

        if 'catalog' in self.params['param']:
            post['variables']['airedOn'] = {"startYear":int(self.addon.getSetting('shizaproject_year_start')),"endYear":int(self.addon.getSetting('shizaproject_year_end'))}
            
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
            if self.addon.getSetting('shizaproject_genre'):
                post['variables']['genre']['include'] = shizaproject_genre[self.addon.getSetting('shizaproject_genre')]
            
            post['variables']['orderBy'] = {
                "field":shizaproject_sort[self.addon.getSetting('shizaproject_sort')],
                "direction":shizaproject_direction[self.addon.getSetting('shizaproject_direction')]}
        
        import json
        post = json.dumps(post, ensure_ascii=False).encode('utf-8')

        return post
#========================#========================#========================#
    def create_episodes(self, episodes):
        online_array = []

        episodes = episodes.split('"name"')
        episodes.pop(0)

        for ep in episodes:
            episode_name = ep[ep.find(':')+1:]
            episode_name = episode_name[:episode_name.find(',')]
            episode_name = episode_name.replace('"', '').replace('null', '')
            
            episode_num = ep[ep.find('"number":')+9:]#:ep.find(',"videos')]
            episode_num = episode_num[:episode_num.find(',')]
            
            if not episode_name:
                episode_name = 'Episode {}'.format(episode_num)
                
            if '"SIBNET"' in ep:
                episode_url = ep[ep.find('SIBNET","embedUrl":"')+20:]
                episode_url = episode_url[:episode_url.find('"')]
            else:
                episode_name = '[COLOR=red][B]{}[/B][/COLOR]'.format(episode_name)
                episode_url = 'https://'

            online_array.append(u'{}||{}||{}'.format(episode_name,episode_num,episode_url))
        
        episodes_data = u'|||'.join(online_array)

        return episodes_data
#========================#========================#========================#
    def create_torrent(self, torrent):
        seed = torrent[torrent.find('seeders":')+9:torrent.find(',"leechers')]
        leech = torrent[torrent.find('leechers":')+10:torrent.find(',"size')]
        size = torrent[torrent.find('size":"')+7:torrent.find('","metadata')]

        metadata = torrent[torrent.find('metadata":"')+11:torrent.find('","videoFormat')]
            
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

        series = u' | [COLOR=gold]{} из {}[/COLOR]'.format(episodes_aired, episodes_count)

        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{} / {}{}'.format(title[0], title[1], series)

        return label
#========================#========================#========================#
    def create_image(self, anime_id, url):            
        if '0' in self.addon.getSetting('shizaproject_covers'):
            return url
        else:
            local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
            
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                
                try:                    
                    data_request = session.get(url=url, proxies=self.proxy_data)
                    with open(file_name, 'wb') as write_file:
                        write_file.write(data_request.content)
                    return file_name
                except:
                    return url
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

        data_request = session.post(url=self.site_url, proxies=self.proxy_data, data=post, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru='anime_id: {}'.format(anime_id),
                title_en='anime_id: {}'.format(anime_id)
                )
            return
        
        html = data_request.text

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
            self.dialog.notification(heading='Инфо-Парсер',message='Ошибка',icon=self.icon,time=3000,sound=False)
        return
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=shizaproject")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=shizaproject")'.format(anime_id)))
            
        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=shizaproject")'))
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=shizaproject")'))
        
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, rating=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if metadata:
            li.setInfo(type='video', infoLabels={'plot':metadata})

        if anime_id:
            cover = self.create_image(anime_id, cover)

            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})
            
            anime_info = self.database.get_anime(anime_id)

            description = anime_info[10] if anime_info[10] else ''
            
            if anime_info[11]:
                description = u'{}\n\n[B]Озвучивание[/B]: {}'.format(anime_info[10], anime_info[11])
            if anime_info[12]:
                description = u'{}\n[B]Перевод[/B]: {}'.format(description, anime_info[12])
            if anime_info[13]:
                description = u'{}\n[B]Тайминг[/B]: {}'.format(description, anime_info[13])
            if anime_info[14]:
                description = u'{}\n[B]Работа над звуком[/B]: {}'.format(description, anime_info[14])
            if anime_info[15]:
                description = u'{}\n[B]Mastering[/B]: {}'.format(description, anime_info[15])
            if anime_info[16]:
                description = u'{}\n[B]Редактирование[/B]: {}'.format(description, anime_info[16])
            if anime_info[17]:
                description = u'{}\n[B]Другое[/B]: {}'.format(description, anime_info[17])
                
            info = {
                'genre':anime_info[7], 
                'country':anime_info[18],
                'year':anime_info[3],
                'episode':anime_info[2],
                'director':anime_info[9],
                'mpaa':anime_info[5],
                'plot':description,
                'title':title,
                'duration':anime_info[6],
                'studio':anime_info[19],
                'writer':anime_info[8],
                'tvshowtitle':title,
                'premiered':anime_info[3],
                'status':anime_info[1],
                'aired':anime_info[3],
                'rating':rating
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
    def exec_proxy_data(self):
        if 'renew' in self.params['param']:
            self.addon.setSetting('{}_proxy'.format(self.params['portal']),'')
            self.addon.setSetting('{}_proxy_time'.format(self.params['portal']),'')

        if 'false' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None
        
        try: proxy_time = float(self.addon.getSetting('{}_proxy_time'.format(self.params['portal'])))
        except: proxy_time = 0
    
        if time.time() - proxy_time > 604800:
            self.addon.setSetting('{}_proxy_time'.format(self.params['portal']), str(time.time()))
            proxy_request = requests.get(url='http://antizapret.prostovpn.org/proxy.pac', headers=headers)

            if proxy_request.status_code == requests.codes.ok:
                proxy_pac = proxy_request.text

                if sys.version_info.major > 2:                    
                    proxy = proxy_pac[proxy_pac.rfind('return "HTTPS')+13:]
                    proxy = proxy[:proxy.find(';')].strip()
                    proxy = 'https://{}'.format(proxy)
                else:
                    proxy = proxy_pac[proxy_pac.rfind('PROXY')+5:]
                    proxy = proxy[:proxy.find(';')].strip()

                self.addon.setSetting('{}_proxy'.format(self.params['portal']), proxy)
                proxy_data = {'https': proxy}
            else:
                proxy_data = None
        else:
            if self.addon.getSetting('{}_proxy'.format(self.params['portal'])):
                proxy_data = {'https': self.addon.getSetting('{}_proxy'.format(self.params['portal']))}
            else:
                proxy_request = requests.get(url='http://antizapret.prostovpn.org/proxy.pac', headers=headers)

                if proxy_request.status_code == requests.codes.ok:
                    proxy_pac = proxy_request.text
                    
                    if sys.version_info.major > 2:                    
                        proxy = proxy_pac[proxy_pac.rfind('return "HTTPS')+13:]
                        proxy = proxy[:proxy.find(';')].strip()
                        proxy = 'https://{}'.format(proxy)
                    else:
                        proxy = proxy_pac[proxy_pac.rfind('PROXY')+5:]
                        proxy = proxy[:proxy.find(';')].strip()

                    self.addon.setSetting('{}_proxy'.format(self.params['portal']), proxy)
                    proxy_data = {'https': proxy}
                else:
                    proxy_data = None

        return proxy_data
#========================#========================#========================#
    def exec_update_anime_part(self):
        self.create_info(slug=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_file_part(self):
        if 'cover_set' in self.params['param']:
            target_url = 'http://getfile.dokpub.com/yandex/get/https://disk.yandex.ru/d/sbeL3-5VPwVs2g'
            target_path = os.path.join(self.images_dir, 'anistar_set.zip')
        else:
            try: self.database.end()
            except: pass
            
            target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_{}.db'.format(self.params['portal'])
            target_path = os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))
        
        try: os.remove(target_path)
        except: pass

        try:
            self.progress_bg.create(u'Загрузка файла')
                             
            data_request = requests.get(target_url, stream=True)
            file_size = int(data_request.headers['Content-Length'])
            with data_request as data:
                bytes_read = 0
                data.raise_for_status()
                with open(target_path, 'wb') as write_file:
                    for chunk in data.iter_content(chunk_size=8192):                        
                        bytes_read = bytes_read + len(chunk)                        
                        write_file.write(chunk)
                        percent = int(bytes_read * 100 / file_size)
                        
                        self.progress_bg.update(percent, u'Загружено: {} MB'.format('{:.2f}'.format(bytes_read/1024/1024.0)))
                        
            self.progress_bg.close()
            self.dialog.notification(heading='Загрузка файла',message='Выполнено',icon=self.icon,time=3000,sound=False)
            
            if 'cover_set' in self.params['param']:
                self.create_image_set(target_path)

        except:
            self.dialog.notification(heading='Загрузка файла',message='Ошибка',icon=self.icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=self.icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=self.icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_information_part(self):
        data = u'[B][COLOR=darkorange]ShizaProject[/COLOR][/B]\n\
    - Суб плагин переведен на библиотеку requests\n\
    - Общая оптимизация, правки'
        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=lime]Онгоинги[/COLOR][/B]', params={'mode': 'common_part', 'param': 'ONGOING'})
        self.create_line(title='[B][COLOR=lime]Завершенные[/COLOR][/B]', params={'mode': 'common_part', 'param': 'COMPLETED'})
        self.create_line(title='[B][COLOR=yellow]Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'Дорамы'})
        self.create_line(title='[B][COLOR=blue]Мультфильмы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'Мультфильмы'})
        self.create_line(title='[B][COLOR=orange]Кино и ТВ[/COLOR][/B]', params={'mode': 'common_part', 'param': 'Разное'})
        self.create_line(title='[B][COLOR=lime]Каталог[/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = self.addon.getSetting('shizaproject_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': data})

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                data_array = self.addon.getSetting('shizaproject_search').split('|')
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                self.addon.setSetting('shizaproject_search', data_array)

                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        self.progress_bg.create("ShizaProject", u"Инициализация")
        post = self.create_post()

        data_request = session.post(url=self.site_url, proxies=self.proxy_data, data=post, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        html = data_request.text
        
        if not '"node":{"' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        data_array = html.split('"node":{"')
        data_array.pop(0)

        i = 0

        for data in data_array:
            data = unescape(data)

            anime_id = data[data.find('slug":"')+7:]
            anime_id = anime_id[:anime_id.find('",')]

            episodes_count = data[data.find('episodesCount":')+15:]
            episodes_count = episodes_count[:episodes_count.find(',')]
            episodes_count = episodes_count
            
            episodes_aired = data[data.find('episodesAired":')+15:]
            episodes_aired = episodes_aired[:episodes_aired.find(',')]
            episodes_aired = episodes_aired

            poster_data = data[data.find('posters":')+9:data.find('"episodes"')]
            
            cover = poster_data[poster_data.rfind('https://'):]
            cover = cover[:cover.find('","')]
            
            episodes = data[data.find('"episodes":[')+12:data.find('],"torrents')]
            episodes = self.create_episodes(episodes)

            try:
                episodes = episodes.encode('utf-8')
            except:
                pass

            torrent = data[data.find('torrents":[{')+12:data.find('"}}]}}')]
            torrent = self.create_torrent(torrent)

            try:
                torrent = torrent.encode('utf-8')
            except:
                pass

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id, episodes_count, episodes_aired)

            series = '1-{} / {}'.format(episodes_aired, episodes_count)

            self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part','id': anime_id,'cover':cover,'episodes':episodes,'torrent':torrent,'series':series})

        self.progress_bg.close()

        if 'hasNextPage":true' in html:
            after = html[html.find('endCursor":"')+12:]
            after = after[:after.find('",')]

            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)            
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'after': after, 'page': (int(self.params['page']) + 1)})
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        from info import shizaproject_categories, shizaproject_season, shizaproject_status, shizaproject_voice_stat, shizaproject_form, shizaproject_genre, shizaproject_sort, shizaproject_direction

        shizaproject_year = ['{}'.format(year) for year in range(1970,2023)]

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
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('shizaproject_genre')), params={'mode': 'catalog_part', 'param': 'shizaproject_genre'})
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
        if 'shizaproject_genre' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_genre.keys()))
            self.addon.setSetting(id='shizaproject_genre', value=tuple(shizaproject_genre.keys())[result])
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
                self.create_line(title=u'[B]Онлайн просмотр[/B]', params={'mode': 'online_part', 'id': self.params['id'], 'episodes':self.params['episodes'], 'cover': self.params['cover']})
            if 'torrent' in self.params:
                self.create_line(title=u'[B]Торрент просмотр[/B]', params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent':self.params['torrent'], 'cover': self.params['cover'], 'series':self.params['series']})
        else:
            self.create_line(title=u'[B][COLOR=red]Онлайн и Торрент ссылки отсутствуют[/COLOR][/B]', params={'mode': self.params['mode']})
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

                if '[COLOR=red]' in episode_title:
                    label = u'[COLOR=red][B]{} - [/B][/COLOR]{}'.format(episode_num, episode_title)
                else:
                    label = u'{} - {}'.format(episode_num, episode_title)

                self.create_line(title=label, anime_id=self.params['id'], cover=cover, params={'mode': 'online_part', 'id': self.params['id'], 'param': data[2], 'title':'[COLOR=gold][ PLAY ][/COLOR]', 'cover': cover})

        if self.params['param']:
            data_request = session.get(url=self.params['param'], proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            html = data_request.text
            
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
            data_request = session.get(url=self.params['param'], proxies=self.proxy_data, headers=headers)

            file_name = 'shizaproject.torrent'
            torrent_file = os.path.join(self.torrents_dir, file_name)
            
            with open(torrent_file, 'wb') as write_file:
                write_file.write(data_request.content)

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
                    self.create_line(title=series[i], params={'mode': 'selector_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], cover=self.params['cover'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], cover=self.params['cover'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_selector_part(self):
        torrent_url = os.path.join(self.torrents_dir, self.params['id'])
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])
        
        if '0' in self.addon.getSetting(portal_engine):
            try:
                tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver', 'torrserver_tam', 'lt2http')
                engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
                purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(torrent_url), index, engine)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=3000,sound=False)

        if '1' in self.addon.getSetting(portal_engine):
            try:
                purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=3000,sound=False)

        if '2' in self.addon.getSetting(portal_engine):
            from utility import torrent2magnet
            url = torrent2magnet(torrent_url)
                        
            try:
                import torrserver_player
                torrserver_player.Player(
                    torrent=url,
                    sort_index=index,
                    host=self.addon.getSetting('{}_ts_host'.format(self.params['portal'])),
                    port=self.addon.getSetting('{}_ts_port'.format(self.params['portal']))
                    )
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=3000,sound=False)