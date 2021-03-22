# -*- coding: utf-8 -*-

import gc, os, sys, time, json
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

try:
    from urllib import quote_plus, unquote_plus, urlencode, urlopen
except:
    from urllib.parse import quote_plus, unquote_plus, urlencode
    from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility, info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.anilibria')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()
        self.skin_used = xbmc.getSkinDir()

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
        
        self.cookies_dir = os.path.join(self.addon_data_dir, 'cookies')
        if not os.path.exists(self.cookies_dir):
            os.mkdir(self.cookies_dir)

        self.database_dir = os.path.join(self.addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'sort':''}
        self.auth_post_data = {
            'mail': Main.addon.getSetting('login'),
            'passwd': Main.addon.getSetting('password'),
            'fa2code': '',
            'csrf': '1'}

        args = utility.get_params()
        for a in args:
            self.params[a] = unquote_plus(args[a])

        if Main.addon.getSetting('unblock') == '0':
            proxy_data = None
        else:
            proxy_data = self.create_proxy_data()
#================================================
        try: session_time = float(Main.addon.getSetting('session_time'))
        except: session_time = 0

        if time.time() - session_time > 28800:
            Main.addon.setSetting('session_time', str(time.time()))
            try: os.remove(os.path.join(self.cookies_dir, 'anilibria.sid'))
            except: pass
            Main.addon.setSetting('auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(auth_usage=bool(Main.addon.getSetting('auth_mode') == 'true'),
                                auth_status=bool(Main.addon.getSetting('auth') == 'true'),
                                proxy_data=proxy_data)
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.sid_file = os.path.join(self.cookies_dir, 'anilibria.sid' )
        del WebTools
#================================================
        if Main.addon.getSetting('auth_mode') == 'true':
            if not Main.addon.getSetting("login") or not Main.addon.getSetting("password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация - Ошибка','Укажите логин и пароль')
                return

            if not self.network.auth_status:
                if not self.network.authorization():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация - Ошибка','Проверьте логин и пароль')
                    return
                else:
                    Main.addon.setSetting("auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'anilibria.db')):
            self.exec_update_part()
#================================================
        from database import DBTools
        if Main.addon.getSetting('database') == 'false':
            os.remove(os.path.join(self.database_dir, 'anilibria.db'))
            Main.addon.setSetting('database', 'true')
        self.database = DBTools(os.path.join(self.database_dir, 'anilibria.db'))
        del DBTools

    def create_viewmode(self):
        skin_used = xbmc.getSkinDir()
        #xbmc.log(str(skin_used), xbmc.LOGFATAL)

        if skin_used == 'skin.aeon.nox.silvo':
            xbmc.executebuiltin('Container.SetViewMode(50)')

            if self.params['mode'] == 'schedule_part':
                xbmc.executebuiltin('Container.SetViewMode(602)')
            if self.params['mode'] == 'common_part':
                xbmc.executebuiltin('Container.SetViewMode(509)')


        if skin_used == 'skin.estuary':
            if self.params['mode'] == 'common_part':# or self.params['param'] == 'search_part':
                xbmc.executebuiltin('Container.SetViewMode(51)')
            else:
                xbmc.executebuiltin('Container.SetViewMode(55)')

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

    def create_title_api(self, title, series):
        if series:
            series = ' - [COLOR=gold][ Серии: {} ][/COLOR]'.format(series)

            if self.skin_used == 'skin.aeon.nox.silvo' and self.params['mode'] == 'common_part':
                series = ' - [ Серии: {} ]'.format(series)                
        else:
            series = ''

        if Main.addon.getSetting('title_mode') == '0':
            label = '{}{}'.format(title[0], series)
        if Main.addon.getSetting('title_mode') == '1':
            label = '{}{}'.format(title[1], series)
        if Main.addon.getSetting('title_mode') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image_api(self, anime_id):
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

    def create_line_api(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image_api(anime_id)

            li.setArt({
                "thumb": cover,
                "poster": cover,
                "tvshowposter": cover,
                # "banner": cover,
                "fanart": cover,
                "clearart": cover,
                "clearlogo": cover,
                "landscape": cover,
                "icon": cover
                })

            anime_info = self.database.get_anime_api(anime_id)
            #genres, voice, translator, editing, decor, timing, year, description

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

            #genres, voice, translator, editing, decor, timing

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part_api' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=clean_part")')])

        if Main.addon.getSetting('auth_mode') == 'true' and self.params['mode'] == 'common_part':
            li.addContextMenuItems([
                ('[B]Добавить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}")'.format(anime_id)),
                ('[B]Удалить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}")'.format(anime_id))
                ])
                
        if self.params['mode'] == 'information_part':
            li.addContextMenuItems([('[B]Обновить Базу Данных[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=update_part")')])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if Main.addon.getSetting('online_mode') == 'true':
            if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info_api(self, anime_id):
        url = 'http://api.anilibria.tv/v2/getTitle?id={}&filter=names,genres,team,season.year,description'.format(anime_id)
        html = self.network.get_json(target_name=url)

        if type(html) == int:
            return html

        data = json.loads(html)        

        title_ru = data['names']['ru']
        title_en = data['names']['en'],
        genres = ', '.join(data['genres']),
        voice = ', '.join(data['team']['voice']),
        translator = ', '.join(data['team']['translator']),
        editing = ', '.join(data['team']['editing']),
        decor = ', '.join(data['team']['decor']),
        timing = ', '.join(data['team']['timing']),
        year = data['season']['year'],
        description = data['description']

        try:
            self.database.add_anime(anime_id, title_ru, title_en, genres, voice, translator, editing, decor, timing, year, description)
        except:
            return 101

        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        self.create_viewmode()
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        Main.addon.openSettings()

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'anilibria.db'))
        except: pass        

        db_file = os.path.join(self.database_dir, 'anilibria.db')        
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anilibria.db'
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
            self.dialog.ok('Anilibria - База Данных','БД успешно загружена')
            Main.addon.setSetting('database', 'true')
        except:
            self.dialog.ok('Anilibria - База Данных','Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
            Main.addon.setSetting('database', 'false')
            pass

    def exec_favorites_part(self):
        url = 'https://www.anilibria.tv/release/{}.html'.format(self.params['id'])

        html = self.network.get_html(target_name=url)

        csrf_token = html[html.find('value=\'{')+7:html.find('}\'>')+1]
        rid = html[html.find('350x500/')+8:html.find('.jpg')]

        fav_url = 'https://www.anilibria.tv/public/favorites.php'
        post = 'rid={}&csrf_token={}'.format(rid, csrf_token)

        try:
            self.network.get_html(target_name=fav_url,post=post)
            self.dialog.ok('Anilibria - Избранное', 'Выполнено')
        except:
            self.dialog.ok('Anilibria - Избранное', 'Ошибка: [COLOR=yellow]103[/COLOR]')
    
    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            self.dialog.ok('Anilibria - Поиск','Удаление истории - Выполнено')
        except:
            self.dialog.ok('Anilibria - Поиск','Удаление истории - [COLOR=yellow]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        # if Main.addon.getSetting('auth_mode') == 'true':
        #     self.create_line_api(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites'})
        self.create_line_api(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part_api'})
        self.create_line_api(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line_api(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated'})
        self.create_line_api(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'in_favorites'})
        self.create_line_api(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        self.create_line_api(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part_api(self):
        if not Main.addon.getSetting('search'):
            Main.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line_api(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part_api', 'param': 'search'})

            data_array = Main.addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line_api(title='{}'.format(data), params={'mode': 'common_part', 'search_string': quote_plus(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote_plus(skbd.getText())
                data_array = Main.addon.getSetting('search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote_plus(self.params['search_string']))
                Main.addon.setSetting('search', data_array)

                self.params['mode'] = 'common_part'
                self.execute()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_schedule_part(self):
        self.progress.create("Anilibria", "Инициализация")

        url = 'https://api.anilibria.tv/v2/getSchedule?filter=id,announce,torrents.series.string'
        html = self.network.get_json(target_name=url)

        if type(html) == int:
            self.create_line_api(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        data_array = json.loads(html)

        i = 0

        for data in data_array:
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            day = info.week[data['day']]
            self.create_line_api(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(day), params={})

            for d in data['list']:
                anime_id = d['id']
                announce = d['announce']                
                series = d['torrents']['series']['string']

                if announce:
                    series = '{} ] - [ {}'.format(series, utility.rep_list(announce))

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db_api(anime_id):
                    inf = self.create_info_api(anime_id)
                    
                    if type(inf) == int:
                        self.create_line_api(title='[B][COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title_api(self.database.get_title_api(anime_id), series)
                self.create_line_api(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        
        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_common_part(self):
        self.progress.create("Anilibria", "Инициализация")

        if 'search_string' in self.params:
            url = 'http://api.anilibria.tv/v2/searchTitles?search={}&limit=24&filter=id,torrents.series.string'.format(
                self.params['search_string'])

        if self.params['param'] == 'updated' or self.params['param'] == 'in_favorites':
            url = 'http://api.anilibria.tv/v2/advancedSearch?query={{id}}&order_by={}&filter=id,torrents.series.string&limit=24&sort_direction=1'.format(
                self.params['param'])
        
        if self.params['param'] == 'catalog':
            year = '%20and%20{{season.year}}=={}'.format(Main.addon.getSetting('year')) if Main.addon.getSetting('year') else ''
            genre = '%20and%20"{}"%20in%20{{genres}}'.format(quote_plus(Main.addon.getSetting('genre'))) if Main.addon.getSetting('genre') else ''
            season = '%20and%20{{season.code}}=={}'.format(info.season[Main.addon.getSetting('season')]) if Main.addon.getSetting('season') else ''
            sort = '&order_by={}&sort_direction=1'.format(info.sort[Main.addon.getSetting('sort')])
            status = '%20and%20{{status.code}}=={}'.format(info.status[Main.addon.getSetting('status')])

            url = 'http://api.anilibria.tv/v2/advancedSearch?query={{id}}{}{}{}{}{}&filter=id,torrents.series.string&limit=24'.format(
                year, genre, season, status, sort)

            xbmc.log(str(url), xbmc.LOGFATAL)

        html = self.network.get_json(target_name=url)

        data_array = json.loads(html)

        i = 0

        for data in data_array:
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            anime_id = data['id']
            series = data['torrents']['series']['string']

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.is_anime_in_db_api(anime_id):
                inf = self.create_info_api(anime_id)

                if type(inf) == int:
                    self.create_line_api(title='[B][COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                    continue

            label = self.create_title_api(self.database.get_title_api(anime_id), series)
            self.create_line_api(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        if Main.addon.getSetting('status') == '':
            Main.addon.setSetting(id='status', value='Все Релизы')

        if Main.addon.getSetting('sort') == '':
            Main.addon.setSetting(id='sort', value='Новое')

        if self.params['param'] == '':
            self.create_line_api(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line_api(title='Год: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line_api(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('season')), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line_api(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line_api(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line_api(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
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
            self.create_line_api(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line_api(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line_api(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line_api(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})
            self.create_line_api(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]anilibria.tv[/COLOR]', data)
        return

    def exec_select_part(self):
        html = self.network.get_html('https://www.anilibria.tv/release/{}.html'.format(self.params['id']))
        
        if Main.addon.getSetting('online_mode') == 'false':
            data_array = html[html.find('<td id="torrentTableInfo'):html.rfind('Cкачать</a>')+17]
            data_array = data_array.split('</tr>')

            for data in data_array:
                torrent_title = data[data.find('tcol1">')+7:data.find('</td>')]
                torrent_stat = data[data.find('alt="dl"> ')+10:data.rfind('<td id')]
                torrent_stat = utility.tag_list(torrent_stat).replace('  ', '|').split('|')
                
                torrent_url = data[data.find('TableInfo')+9:data.find('" class="')]

                label = '{} , [COLOR=F0FFD700]{}[/COLOR], Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
                    torrent_title, torrent_stat[0], torrent_stat[1], torrent_stat[2])
                
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'])
        else:
            info = dict.fromkeys(['title','sd', 'mid', 'hd', 'id'], '')
            data_array = html[html.find('[{')+2:html.find('},]')]
            data_array = data_array.split('},{')

            sd = []
            mid = []
            hd = []

            for data in data_array:
                data = data.split(',')

                for d in data:
                    if 'title' in d:
                        info['title'] = d[d.find(':\'')+2:d.rfind('\'')]
                    if '[480p]' in d:
                        d = d[d.find('[480p]//')+8:d.find('m3u8')+4]
                        info['sd'] = 'https://{}'.format(d)
                        sd.append('{}|{}'.format(info['title'], info['sd']))
                    if '[720p]' in d:
                        d = d[d.find('[720p]//')+8:d.find('m3u8')+4]
                        info['mid'] = 'https://{}'.format(d)
                        mid.append('{}|{}'.format(info['title'], info['mid']))
                    if '[1080p]' in d:
                        d = d[d.find('[1080p]//')+9:d.find('m3u8')+4]
                        info['hd'] = 'https://{}'.format(d)
                        hd.append('{}|{}'.format(info['title'], info['hd']))

            if info['sd']:
                label = 'Качество: [COLOR=F020F0F0]480p[/COLOR]' 
                self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(sd)}, anime_id=self.params['id'])
            if info['mid']:
                label = 'Качество: [COLOR=F020F0F0]720p[/COLOR]'
                self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(mid)}, anime_id=self.params['id'])
            if info['hd']:
                label = 'Качество: [COLOR=F020F0F0]1080p[/COLOR]'
                self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(hd)}, anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        url = 'https://www.anilibria.tv/public/torrent/download.php?id={}'.format(self.params['torrent_url'])
        file_id = self.params['torrent_url']
        file_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_id))
        torrent_file = self.network.get_file(target_name=url, destination_name=file_name)

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
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_id}, anime_id=self.params['id'], folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_id}, anime_id=self.params['id'], folder=False, size=info['length'])
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def exec_online_part(self):        
        data_array = self.params['param'].split('|||')

        for data in data_array:
            data = data.split('|')            
            self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if Main.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Main.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote_plus(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote_plus(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

if __name__ == "__main__":
    anilibria = Main()
    anilibria.execute()
    del anilibria

gc.collect()
