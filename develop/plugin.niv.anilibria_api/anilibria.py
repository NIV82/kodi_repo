# -*- coding: utf-8 -*-

import gc, os, sys, time, json
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

try:
    from urllib import urlencode, urlopen, quote, unquote
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility, info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.anilibria')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        try: self.addon_data_dir = utility.fs_enc(xbmc.translatePath(Main.addon.getAddonInfo('profile')))
        except: self.addon_data_dir = xbmcvfs.translatePath(Main.addon.getAddonInfo('profile'))

        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.cache_dir = os.path.join(self.addon_data_dir, 'cache')
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '0', 'limit': '12'}
        
        args = utility.get_params()
        for a in args:
            self.params[a] = unquote(args[a])

        if Main.addon.getSetting('unblock') == '0':
            proxy_data = None
        else:
            proxy_data = self.create_proxy_data()
#================================================
        if not os.path.isfile(os.path.join(self.addon_data_dir, 'api_anilibria.db')):
            self.exec_update_part()
#================================================
        if Main.addon.getSetting("Engine") == '2':
            try:
                xbmcaddon.Addon('script.module.torrent2http')
            except:
                xbmc.executebuiltin('XBMC.Notification("Установка модуля", "script.module.torrent2http", 3000)')
                xbmc.executebuiltin('RunPlugin("plugin://script.module.torrent2http")')
#================================================
        from network import WebTools
        self.network = WebTools(auth_usage=False, auth_status=False, proxy_data=proxy_data)
        del WebTools
#================================================
        from database import DBTools
        self.database = DBTools(os.path.join(self.addon_data_dir, 'api_anilibria.db'))
        del DBTools
#================================================
        if not Main.addon.getSetting('mirror_1'):
            self.exec_mirror_part()
#================================================
    def create_proxy_data(self):
        try: proxy_time = float(Main.addon.getSetting('proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 36000:
            Main.addon.setSetting('proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
            
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
            
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            Main.addon.setSetting('proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if Main.addon.getSetting('proxy'):
                proxy_data = {'https': Main.addon.getSetting('proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Main.addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}
        return proxy_data

    def create_url(self):        
        api_filter = '&filter=id,type,player.series.string'
        api_page = '&after={}'.format(int(self.params['page']) * int(self.params['limit']))
        api_limit = '&limit={}'.format(self.params['limit'])

        if 'search_string' in self.params:
            url = 'http://api.anilibria.tv/api/v2/searchTitles?search={}{}{}{}'.format(
                self.params['search_string'], api_limit, api_filter, api_page)

        if self.params['param'] == 'updated':
            url = 'http://api.anilibria.tv/api/v2/getUpdates{}{}{}'.format(
                api_limit.replace('&','?'), api_filter, api_page)

        if self.params['param'] == 'in_favorites':
            url = 'http://api.anilibria.tv/api/v2/advancedSearch?query={{id}}&order_by={}{}{}&sort_direction=1{}'.format(
                self.params['param'], api_limit, api_filter, api_page)

        if self.params['param'] == 'catalog':
            year = '%20and%20{{season.year}}=={}'.format(Main.addon.getSetting('year')) if Main.addon.getSetting('year') else ''
            genre = '%20and%20"{}"%20in%20{{genres}}'.format(quote(Main.addon.getSetting('genre'))) if Main.addon.getSetting('genre') else ''
            season = '%20and%20{{season.code}}=={}'.format(info.season[Main.addon.getSetting('season')]) if Main.addon.getSetting('season') else ''            
            status = '%20and%20{{status.code}}=={}'.format(info.status[Main.addon.getSetting('status')]) if not Main.addon.getSetting('status') == 'Все'  else ''
            sort = '&order_by={}&sort_direction=1'.format(info.sort[Main.addon.getSetting('sort')])

            url = 'http://api.anilibria.tv/api/v2/advancedSearch?query={{id}}{}{}{}{}{}{}{}{}'.format(
                status, year, genre, season, sort, api_limit, api_filter, api_page)

        return url

    def create_title(self, title, series_cur=None, series_max=None, announce=None):
        if series_max == '0':
            series_max = 'XXX'

        if series_cur:
            res = 'Серии: {} из {}'.format(series_cur, series_max)

            if not series_max:
                res = '{}'.format(series_cur)

            if announce:
                res = '{} ] - [ {}'.format(res, utility.rep_list(announce))

            series = ' - [COLOR=gold][ {} ][/COLOR]'.format(res)

            if xbmc.getSkinDir() == 'skin.aeon.nox.silvo' and self.params['mode'] == 'common_part':
                series = ' - [ {} ]'.format(res)
        else:
            series = ''

        if Main.addon.getSetting('title_mode') == '0':
            label = '{}{}'.format(title[0], series)
        if Main.addon.getSetting('title_mode') == '1':
            label = '{}{}'.format(title[1], series)
        if Main.addon.getSetting('title_mode') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image(self, anime_id):
        url = 'https://static.anilibria.tv/upload/release/350x500/{}.jpg'.format(anime_id)

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                try: local_path = utility.fs_dec(os.path.join(self.images_dir, local_img))
                except: local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                try: file_name = utility.fs_dec(os.path.join(self.images_dir, local_img))
                except: file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)

            li.setArt({
                "thumb": cover,
                "poster": cover,
                "tvshowposter": cover,
                # "banner": cover,
                #"fanart": cover,
                "clearart": cover,
                "clearlogo": cover,
                "landscape": cover,
                "icon": cover
                })

            #genres, voice, translator, editing, decor, timing, year, description
            anime_info = self.database.get_anime(anime_id)

            description = '{}\n\n[COLOR=steelblue]Озвучка:[/COLOR] {}'.format(anime_info[7], anime_info[1])
            description = '{}\n[COLOR=steelblue]Перевод:[/COLOR] {}'.format(description, anime_info[2])
            description = '{}\n[COLOR=steelblue]Редактирование:[/COLOR] {}'.format(description, anime_info[3])
            description = '{}\n[COLOR=steelblue]Оформление:[/COLOR] {}'.format(description, anime_info[4])
            description = '{}\n[COLOR=steelblue]Синхронизация:[/COLOR] {}'.format(description, anime_info[5])  

            info = {
                'genre': anime_info[0], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                #'country': '', #string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year': anime_info[6], #integer (2009)
                #'episode': '', #integer (4)
                #'season': '', #integer (1)
                #'sortepisode': '', #integer (4)
                #'sortseason': '', #integer (1)
                #'episodeguide': '', #string (Episode guide)
                #'showlink': '', #string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])
                #'top250': '', #integer (192)
                #'setid': '', #integer (14)
                #'tracknumber': '', #integer (3)
                #'rating': '', #float (6.4) - range is 0..10
                #'userrating': '', #integer (9) - range is 1..10 (0 to reset)
                #'watched': '', #depreciated - use playcount instead
                #'playcount': '', #integer (2) - number of times this item has been played
                #'overlay': '', #integer (2) - range is 0..7. See Overlay icon types for values
                #'cast': '', #list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole
                #'castandrole': '', #list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
                #'director': '', #string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                #'mpaa': '', #string (PG-13)
                'plot': description, #string (Long Description)
                #'plotoutline': '', #string (Short Description)
                'title': title, #string (Big Fan)
                #'originaltitle': '', #string (Big Fan)
                #'sorttitle': '', #string (Big Fan)
                #'duration': '', #integer (245) - duration in seconds
                #'studio': '', #string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                #'tagline': '', #string (An awesome movie) - short description of movie
                #'writer': '', #string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                'tvshowtitle': title, #string (Heroes)
                #'premiered': '', #string (2005-03-04)
                #'status': '', #string (Continuing) - status of a TVshow
                #'set': '', #string (Batman Collection) - name of the collection
                #'setoverview': '', #string (All Batman movies) - overview of the collection
                #'tag': '', #string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
                #'imdbnumber': '', #string (tt0110293) - IMDb code
                #'code': '', #string (101) - Production code
                #'aired': '', #string (2008-12-07)
                #'credits': '', #string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
                #'lastplayed': '', #string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #'album': '', #string (The Joshua Tree)
                #'artist': '', #list (['U2'])
                #'votes': '', #string (12345 votes)
                #'path': '', #string (/home/user/movie.avi)
                #'trailer': '', #string (/home/user/trailer.avi)
                #'dateadded': '', #string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #'mediatype': '', #string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
                #'dbid': '' #integer (23) - Only add this for items which are part of the local db. You also need to set the correct 'mediatype'! 
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=clean_part")')])
                
        if self.params['mode'] == 'information_part':
            li.addContextMenuItems([('[B]Обновить Базу Данных[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=update_part")')])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):
        api_filter = '&filter=id,names,genres,team,season.year,description'
        url = 'http://api.anilibria.tv/v2/getTitle?id={}{}'.format(anime_id, api_filter)

        html = self.network.get_html(url)

        anime_id = html[html.find(':')+1:html.find(',')]
        title_ru = html[html.find('ru":"')+5:html.find('","en')]
        title_en = html[html.find('en":"')+5:html.find('","alt')]

        genres = html[html.find('genres":[')+9:html.find('],"team')]
        voice = html[html.find('voice":[')+8:html.find('],"translator')]
        translator = html[html.find('translator":[')+13:html.find('],"editing')]        
        editing = html[html.find('editing":[')+10:html.find('],"decor')]
        decor = html[html.find('decor":[')+8:html.find('],"timing')]
        timing = html[html.find('timing":[')+9:html.find(']},"season')]

        year = html[html.find('year":')+6:html.find('},"descrip')]
        description = html[html.find('description":"')+14:html.rfind('"}')]

        try:
            self.database.add_anime(
                anime_id,
                title_ru,
                title_en,
                genres.replace('"','').replace(',', ', '),
                voice.replace('"','').replace(',', ', '),
                translator.replace('"','').replace(',', ', '),
                editing.replace('"','').replace(',', ', '),
                decor.replace('"','').replace(',', ', '),
                timing.replace('"','').replace(',', ', '),
                int(year),
                utility.fix_list(description)
                )
        except:
            return 101

        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        Main.addon.openSettings()

    def exec_mirror_part(self):
        url = 'https://darklibria.it/mirror'
        html = self.network.get_html(url=url)

        nodes = []

        info = html[html.find('success mb-1" href="')+20:html.find('Сделать личное зеркало 2')]
        data_array = info.split('href="')
        for data in data_array:            
            mirror = data[:data.find('" target')]
            nodes.append(mirror)
        
        Main.addon.setSetting('mirror_1', nodes[0])
        Main.addon.setSetting('mirror_2', nodes[1])
        Main.addon.setSetting('mirror_3', nodes[2])
        Main.addon.setSetting('mirror_4', nodes[3])

        return

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.addon_data_dir, 'api_anilibria.db'))
        except: pass        

        db_file = os.path.join(self.addon_data_dir, 'api_anilibria.db')        
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/api_anilibria.db'
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
            Main.addon.setSetting('database', 'true')
        except:
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
            Main.addon.setSetting('database', 'false')
            pass

    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            self.dialog.ok('Поиск','Удаление истории - Выполнено')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=yellow]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated'})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'in_favorites'})
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if not Main.addon.getSetting('search'):
            Main.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = Main.addon.getSetting('search').split('|')
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
                data_array = Main.addon.getSetting('search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                Main.addon.setSetting('search', data_array)

                self.params['mode'] = 'common_part'
                self.execute()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_schedule_part(self):
        self.progress.create("Anilibria", "Инициализация")

        api_filter = '?filter=id,announce,type.series,torrents.series.string'
        url = 'https://api.anilibria.tv/api/v2/getSchedule{}'.format(api_filter)
        html = self.network.get_html(url=url)

        nodes = html.split(']},{')

        i = 0

        for node in nodes:
            day = info.week[i]
            data_array = node[node.find(':[{')+3:].split('},{')
            self.create_line(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(day), params={})
            
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            for data in data_array:
                anime_id = data[data.find(':')+1:data.find(',')]
                
                announce = data[data.find('announce":')+10:data.find(',"type"')]
                announce = announce.replace('"','').replace('null','')
                announce = utility.rep_list(announce)

                series_max = data[data.find('pe":{"series":')+14:data.find('},"torr')]
                series_cur = data[data.find('string":"')+9:data.find('"}')]
                
                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(self.database.get_title(anime_id), series_cur, series_max, announce)
                self.create_line(anime_id=anime_id, title=label, params={'mode': 'select_part', 'id': anime_id})

        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return

    def exec_common_part(self):
        self.progress.create("Anilibria", "Инициализация")

        url = self.create_url()
        html = self.network.get_html(url=url)
#============================================
        xbmc.log(str(url), xbmc.LOGFATAL)
#============================================
        data_array = html.split('},{')

        i = 0
        for data in data_array:
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            anime_id = data[data.find(':')+1:data.find(',')]
            type_code = data[data.find('code":')+6:data.find(',"string')]
            series_max = data[data.find('series":')+8:data.find(',"length')]
            series_cur = data[data.rfind('string":"')+9:data.rfind('"}')]
            
            if type_code == '0':
                series_cur = 'Фильм'
                series_max = None

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.is_anime_in_db(anime_id):
                inf = self.create_info(anime_id)

                if type(inf) == int:
                    self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                    continue
                
            label = self.create_title(self.database.get_title(anime_id), series_cur, series_max, None)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        
        if len(data_array) >= int(self.params['limit']):
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        if Main.addon.getSetting('status') == '':
            Main.addon.setSetting(id='status', value='Все')

        if Main.addon.getSetting('sort') == '':
            Main.addon.setSetting(id='sort', value='Новое')

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('season')), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if self.params['param'] == 'genre':
            result = self.dialog.select('Жанр:', info.genre)
            Main.addon.setSetting(id='genre', value=info.genre[result])
        
        if self.params['param'] == 'year':
            result = self.dialog.select('Год:', info.year)
            Main.addon.setSetting(id='year', value=info.year[result])

        if self.params['param'] == 'season':
            result = self.dialog.select('Сезон:', tuple(info.season.keys()))
            Main.addon.setSetting(id='season', value=tuple(info.season.keys())[result])

        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', tuple(info.sort.keys()))
            Main.addon.setSetting(id='sort', value=tuple(info.sort.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Статус релиза:', tuple(info.status.keys()))
            Main.addon.setSetting(id='status', value=tuple(info.status.keys())[result])

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]anilibria.tv[/COLOR]', data)
        return

    def exec_select_part(self):
        self.create_line(title='[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id']})
        self.create_line(title='[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_online_part(self):
        if not self.params['param']:
            api_filter = '&playlist_type=array&filter=player'
            url = 'https://api.anilibria.tv/api/v2/getTitle?id={}{}'.format(self.params['id'], api_filter)

            html = self.network.get_html(url=url)

            array = {'480p': [], '720p': [], '1080p': []}

            host = html[html.find('host":"')+7:html.find('","series')]
            html = html[html.find('playlist":[{')+12:]

            data_array = html.split('},{')

            for data in data_array:
                name = data[data.find(':')+1:data.find(',')]            
                data = data[data.find('hls":{')+6:data.find('}')].replace('"', '')

                fhd = data[data.find('fhd:')+4:data.find(',hd:')].replace('null', '')            
                hd = data[data.find(',hd:')+4:data.find(',sd:')].replace('null', '')
                sd = data[data.find(',sd:')+4:].replace('null', '')

                if fhd:
                    array['1080p'].append('{}||{}{}'.format(
                        'Серия: {}'.format(name), 'https://{}'.format(host), fhd))
                if hd:
                    array['720p'].append('{}||{}{}'.format(
                        'Серия: {}'.format(name), 'https://{}'.format(host), hd))
                if sd:
                    array['480p'].append('{}||{}{}'.format(
                        'Серия: {}'.format(name), 'https://{}'.format(host), sd))

            for i in array.keys():
                if array[i]:
                    label = '[B]Качество: {}[/B]'.format(i)
                    self.create_line(title=label, params={'mode': 'online_part', 'param': ','.join(array[i]), 'id': self.params['id']})
        
        if self.params['param']:
            data_array = self.params['param'].split(',')
            for data in data_array:
                data = data.split('||')
                self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        if not self.params['param']:
            api_filter = '&filter=torrents&playlist_type=array'
            url = 'https://api.anilibria.tv/api/v2/getTitle?id={}{}'.format(self.params['id'], api_filter)

            html = self.network.get_html(url=url)            
            html = html[html.find('list":[{')+8:]
            
            data_array = html.split(',{')

            for data in data_array:
                torrent_id = data[data.find(':')+1:data.find(',')]
                series = data[data.find('string":"')+9:data.find('"},"quality')]
                quality = data[data.find('lity":{"string":"')+17:data.find('","type')]
                leechers = data[data.find('leechers":')+10:data.find(',"seeders')]            
                seeders = data[data.find('seeders":')+9:data.find(',"downloads')]

                torrent_size = data[data.find('total_size":')+12:data.find(',"url')]
                torrent_size = float('{:.2f}'.format(int(torrent_size)/1024.0/1024/1024))

                label = 'Серии: {} : {} , [COLOR=F0FFD700]{} GB[/COLOR], Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
                    series, quality, torrent_size, seeders, leechers)
                self.create_line(title=label, params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id']})

        if self.params['param']:
            site_url = 'https://www.anilibria.tv/'
            if not Main.addon.getSetting('mirrors') == '0':
                site_url = Main.addon.getSetting('mirror_{}'.format(Main.addon.getSetting('mirrors')))

            full_url = '{}upload/torrents/{}.torrent'.format(site_url, self.params['param'])
            file_name = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['param']))
            torrent_file = self.network.get_file(target_name=full_url, destination_name=file_name)

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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': self.params['param']}, anime_id=self.params['id'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': self.params['param']}, anime_id=self.params['id'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if Main.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Main.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
        if Main.addon.getSetting("Engine") == '2':
            url = 'file:///{}'.format(url.replace('\\','/'))
            import player

            if Main.addon.getSetting('DownloadDirectory') == '':
                download_dir = self.addon_data_dir
            else:
                download_dir = Main.addon.getSetting('DownloadDirectory')
            
            player.play_t2h(int(sys.argv[1]), 15, url, index, download_dir)

if __name__ == "__main__":
    anilibria = Main()
    anilibria.execute()
    del anilibria

gc.collect()
