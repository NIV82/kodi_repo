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

from utility import tag_list, clean_list

class Anidub:
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
        self.auth_mode = bool(self.addon.getSetting('anidub_auth_mode') == '1')
#========================#========================#========================#
        try: anidub_session = float(self.addon.getSetting('anidub_session'))
        except: anidub_session = 0

        if time.time() - anidub_session > 28800:
            self.addon.setSetting('anidub_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anidub.sid'))
            except: pass
            self.addon.setSetting('anidub_auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('anidub_auth') == 'true'),
            proxy_data=self.proxy_data, portal='anidub')
        # self.auth_post_data = {
        #     'login_name': self.addon.getSetting('anidub_username'),
        #     'login_password': self.addon.getSetting('anidub_password'),
        #     'login': 'submit'}
        self.auth_post_data = 'login_name={}&login_password={}&login=submit'.format(
            self.addon.getSetting('anidub_username'),self.addon.getSetting('anidub_password')
            )
        #self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_post_data = self.auth_post_data


#https://online.anidub.com/

        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anidub.sid' )
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not self.addon.getSetting('anidub_username') or not self.addon.getSetting('anidub_password'):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok(u'Авторизация',u'Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok(u'Авторизация',u'Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting('anidub_auth', str(self.network.auth_status).lower())
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
        current_mirror = 'anidub_mirror_{}'.format(self.addon.getSetting('anidub_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('anidub_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_title_info(self, title):
        info = dict.fromkeys(['series', 'title_ru', 'title_en'], '')

        title = tag_list(title).replace('...','')
        title = title.replace('/ ', ' / ').replace('  ', ' ')
        title = title.replace('|', '/').replace(u' / ',' / ')
        title = title.replace('  [', ' [').replace ('\\', '/')

        v = title.split(' / ', 1)
        
        if len(v) == 1:           
            v = title.split('  ', 1)
            if len(v) == 1:
                title = title.replace('/ ', ' / ')
                v = title.split(' / ', 1)
            if len(v) == 1:
                title = title.replace(' /', ' / ')
                v = title.split(' / ', 1)
               
        try:
            part_pos = v[len(v) - 1][v[len(v) - 1].find(' ['):v[len(v) - 1].find(']')+1]
            v.insert(0, part_pos.replace('[', '').replace(']', '').strip())
            v[len(v) - 1] = v[len(v) - 1].replace(part_pos, '')
        except:
            v.insert(0, '')
        if len(v) == 2:
            v.append('')

        try:
            info['series'] = v[0]
            info['title_ru'] = v[1].capitalize()
            info['title_en'] = v[2].capitalize()
        except:
            pass
        return info
#========================#========================#========================#
    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        if series:
            series = series.strip()
            series = u' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
        
        if '0' in self.addon.getSetting('anidub_titles'):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('anidub_titles'):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('anidub_titles'):
            label = u'{} / {}{}'.format(title[0], title[1], series)

        if 'ERROR-404' in label:
            label = u'[COLOR=red][B]{}[/B][/COLOR]'.format(label)
        return label
#========================#========================#========================#
    def create_image(self, anime_id):
        url = '{}'.format(self.database.get_cover(anime_id))

        if not 'https://' in url:
            url = '{}{}'.format(self.site_url, url.replace('/','',1))

        if '0' in self.addon.getSetting('anidub_covers'):
            return url
        else:
            #local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        context_menu.append((u'[B][COLOR=darkorange]Обновить Базу Данных[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=anidub")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append((u'[B][COLOR=red]Очистить историю[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")'))

        if 'common_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append((u'[B][COLOR=white]Обновить аниме (один тайтл)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anidub")'.format(anime_id)))

        if self.auth_mode:
            if 'common_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
                context_menu.append((u'[B][COLOR=cyan]Добавить в Избранное (сайт)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anidub")'.format(anime_id)))
                context_menu.append((u'[B][COLOR=cyan]Удалить из Избранного (сайт)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_partnode=minus&id={}&portal=anidub")'.format(anime_id)))
        
        context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append((u'[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anidub")'))
        context_menu.append((u'[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=anidub")'))
        context_menu.append((u'[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=anidub")'))
        context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None): 

        li = xbmcgui.ListItem(title)

        if anime_id:
            if cover:
                pass
            else:
                cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)
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

            if size: info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = 'anidub'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_year(self, data):
        data = tag_list(data)

        rep_list = [
            (u'январ', '.01.'),(u'янв', '.01.'),(u'феврал', '.02.'),(u'фев', '.02.'),
            (u'март', '.03.'),(u'апрел', '.04.'),(u'апр','.04.'),(u'май', '.05.'),
            (u'июн', '.06.'),(u'июл', '.07.'),(u'август', '.08.'),(u'авг', '.08.'),
            (u'сентябр', '.09.'),(u'сен', '.09.'),(u'октябр', '.10.'),(u'окт', '.10.'),
            (u'ноябр', '.11.'),(u'декабр', '.12.'),(u'дек', '.12.'),
            (u'Начало показа:',''),(u'по','|'),(',','|'),('-','|'),('..','.')
            ]

        for value in rep_list:
            data = data.replace(value[0], value[1])
        
        s = []
        for i in data:
            if i.isdigit() or i in ('.','|'):
                s.append(i)
        data = ''.join(s)
       
        if not data:
            return
        
        data_array = data.split('|')        

        if len(data_array) == 1:
            aired_on = data_array[0]
            
            if '.' in aired_on[len(aired_on)-1]:
                aired_on = aired_on[:len(aired_on)-1]
                
            return {'aired_on':aired_on,'released_on':''}
        
        if len(data_array) == 2:
            aired_on = data_array[0]
            released_on = data_array[1]

            if '.' in aired_on[len(aired_on)-1]:
                aired_on = aired_on[:len(aired_on)-1]
            
            if '.' in released_on[len(released_on)-1]:
                released_on = released_on[:len(released_on)-1]

            return {'aired_on':aired_on, 'released_on':released_on}

        if len(data_array) > 2:
            return {'aired_on': 'EXCEPTIONS','released_on':'EXCEPTIONS'}
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        html = self.network.get_html2(target_name=url)

        if type(html) == int:
            self.database.add_anime(anime_id=anime_id, title_ru='ERROR-404', title_en='ERROR-404')
            return

        try: html = html.decode(encoding='utf-8', errors='replace')
        except: pass

        if type(html) == int:
            self.database.add_anime(anime_id=anime_id, title_ru='ERROR-404', title_en='ERROR-404')
            return

        html = unescape(html)

        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'released_on', 'genres', 'director', 'writer', 'description', 'dubbing',
                      'translation', 'timing', 'country', 'studios', 'image', 'anime_tid'], '')

        #info['image'] = html[html.find('data-src="')+10:html.find(u'" title="Постер аниме {')]
        image = html[html.find('fposter img-box img-fit">')+25:html.find(u'" title="Постер аниме {')]
        info['image'] = image[image.find('data-src="')+10:]

        title_data = html[html.find('<h1>')+4:html.find('</h1>')]
        info.update(self.create_title_info(title_data))

        description = html[html.find(u'Описание</div>')+14:html.find(u'Рейтинг:</div>')]
        info['description'] = clean_list(tag_list(description))

        data_array = html[html.find('<div class="fmeta fx-row fx-start">'):html.find('<div class="fright-title">')]
        data_array = data_array.splitlines()

        for data in data_array:
            if 'xfsearch/year/' in data:
                info['aired_on'] = tag_list(data)
            if u'Начало показа:</span>' in data:
                inf = self.create_year(data)
                if inf:
                    info.update(inf)
            if 'xfsearch/country/' in data:
                info['country'] = tag_list(data)
            if u'Жанр:</span>' in data:
                info['genres'] = tag_list(data.replace(u'Жанр:</span>', '')).lower()
            if u'Автор оригинала:</span>' in data:
                info['writer'] = tag_list(data.replace(u'Автор оригинала:</span>', ''))
            if u'Режиссер:</span>' in data:
                info['director'] = tag_list(data.replace(u'Режиссер:</span>', ''))
            if u'Перевод:</span>' in data:
                info['translation'] = tag_list(data.replace(u'Перевод:</span>', ''))
            if u'Студия:</span>' in data:
                info['studios'] = tag_list(data.replace(u'Студия:</span>', ''))
            if u'Озвучивание:</span>' in data:
                info['dubbing'] = tag_list(data.replace(u'Озвучивание:</span>', ''))
            if u'Тайминг:</span>' in data:
                info['timing'] = tag_list(data.replace(u'Тайминг:</span>', ''))
            if u'Ссылка на трекер:</span>' in data:
                anime_tid = data[data.find('https://tr.anidub.com/')+22:data.find('.html')]
                info['anime_tid'] = anime_tid.replace('-','')
        
        try:
            self.database.add_anime(
                anime_id = anime_id,
                anime_tid = info['anime_tid'],
                title_ru = info['title_ru'],
                title_en = info['title_en'],
                genres = info['genres'],
                director = info['director'],
                writer = info['writer'],
                description = info['description'],
                dubbing = info['dubbing'],
                translation = info['translation'],
                timing = info['timing'],
                country = info['country'],
                studios = info['studios'],
                aired_on = info['aired_on'],
                released_on = info['released_on'],
                image = info['image'],
                update = update)
        except:
            return 101
        return 
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
        self.create_info(anime_id=self.params['id'], update=True)
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
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
    def exec_favorites_part(self):
        if not self.params['node']:
            self.progress.create('AniDUB', u'Инициализация')

            url = '{}mylists/animefuture/page/{}/'.format(self.site_url,self.params['page'])

            html = self.network.get_html2(target_name=url)

            try: html = html.decode(encoding='utf-8', errors='replace')
            except: pass

            pages = html[html.rfind('<div class="navigation">'):html.rfind('<!--/noindex-->')]
            pages = tag_list(pages).replace(' ','|')

            if pages: last_page = int(pages[pages.rfind('|')+1:])
            else: last_page = -1
                
            data_array = html[html.find('<div class="animelist">')+23:html.rfind('<label for="mlist">')]
            data_array = clean_list(data_array).split('<div class="animelist">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                data = data[data.rfind('<ahref="')+8:data.find('<progress class="proglist"')]

                url = data[data.find(self.site_url)+len(self.site_url):data.find('.html"')]
                anime_id = url[url.rfind('/')+1:url.find('-')]

                title = data[data.find('class="upd-title">')+18:]
                series = title[title.find('[')+1:title.find(']')]

                if self.progress.iscanceled():
                    break
                self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue
                    
                label = self.create_title(anime_id, series)

                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
            self.progress.close()

            if int(self.params['page']) < last_page:
                self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'plus' in self.params['node']:
            try:
                url = '{}mylists/'.format(self.site_url)
                post = 'news_id={}&status_id={}'.format(self.params['id'], self.params['node'])
                self.network.get_html2(target_name=url, post=post)
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]Успешно добавлено[/COLOR]', 5000, self.icon))
            except:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=yellow]Ошибка - 103[/COLOR]', 5000, self.icon))

        if 'minus' in self.params['node']:
            try:
                url = '{}mylists/'.format(self.site_url)
                post = 'news_id={}&status_id={}'.format(self.params['id'], self.params['node'])
                self.network.get_html2(target_name=url, post=post)
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]Успешно удалено[/COLOR]', 5000, self.icon))
            except:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=yellow]Ошибка - 103[/COLOR]', 5000, self.icon))
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
        self.create_line(title=u'[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        if self.auth_mode:
            self.create_line(title=u'[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title=u'[B][COLOR=lime]Аниме[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/'})
        self.create_line(title=u'[B][COLOR=lime]Онгоинги[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/anime_ongoing/'})
        self.create_line(title=u'[B][COLOR=lime]Вышедшие сериалы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/full/'})
        self.create_line(title=u'[B][COLOR=lime]Аниме фильмы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title=u'[B][COLOR=lime]Аниме OVA[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title=u'[B][COLOR=gold]Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B][COLOR=white]Поиск по названию[/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title=u'[B][COLOR=white]Поиск по жанрам[/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title=u'[B][COLOR=white]Поиск по году[/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title=u'[B][COLOR=white]Поиск по алфавиту[/COLOR][/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = self.addon.getSetting('anidub_search').split('|')
            data_array.reverse()

            for data in data_array:
                if not data: continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if 'search' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('anidub_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('anidub_search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if 'genres' in self.params['param']:
            from info import anidub_genres
            for i in anidub_genres:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

        if 'years' in self.params['param']:
            from info import anidub_years
            for i in anidub_years:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

        if 'alphabet' in self.params['param']:
            from info import anidub_alphabet            
            for i in anidub_alphabet:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(quote(i))})  
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('AniDUB', u'Инициализация')

        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        post = ''

        if 'search_part' in self.params['param']:
            url = '{}index.php?do=search'.format(self.site_url)
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(quote(self.params['search_string']), self.params['page'])


        html = self.network.get_html2(url, post=post)
        
        try: html = html.decode(encoding='utf-8', errors='replace')
        except: pass

        if html.find('<div class="th-item">') > -1:
            pages = html[html.rfind('<div class="navigation">'):html.rfind('<!--/noindex-->')]
            pages = tag_list(pages).replace(' ','|')

            if pages: last_page = int(pages[pages.rfind('|')+1:])
            else: last_page = -1

            data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
            data_array = clean_list(data_array).split('<div class="th-item">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                    
                url = data[data.find('th-in" href="')+13:data.find('.html">')]

                if '/manga/' in url or '/ost/' in url or '/podcast/' in url or '/anons_ongoing/' in url or '/games/' in url or '/videoblog/' in url:
                    continue

                anime_id = url[url.rfind('/')+1:url.find('-')]
                
                title = data[data.find('<div class="fx-1">')+18:data.find('</div><span>')]
                info = self.create_title_info(title)

                if self.progress.iscanceled():
                    break
                self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(anime_id, info['series'])

                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
            
            if int(self.params['page']) < last_page:
                if 'search_part' in self.params['param']:
                    self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                        'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
                else:
                    self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                        'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        else:
            self.create_line(title='[COLOR=red][B][ Контент не найден ][/B][/COLOR]', params={'mode': 'main_part'})

        self.progress.close()        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_select_part(self):
        self.create_line(title=u'[B]Онлайн просмотр[/B]', params={'mode': 'online_part', 'id': self.params['id']})
        if self.database.get_tid(self.params['id']):
            self.create_line(title=u'[B]Торрент просмотр[/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            url = '{}index.php?newsid={}'.format(self.site_url, self.params['id'])
            html = self.network.get_html2(url)

            try: html = html.decode(encoding='utf-8', errors='replace')
            except: pass

            data_array = html[html.rfind('<div class="fthree tabs-box">')+29:html.rfind('</span></div></div>')]
            data_array = data_array.split('</span>')

            for data in data_array:
                video_url = data[data.find('span data="')+11:data.find('"">')]
                video_title = data[data.find('"">')+3:]

                try: title = video_title.encode('utf-8')
                except: title = video_title

                self.create_line(title=video_title, params={'mode': 'online_part', 'param': video_url, 'id': self.params['id'],'title':title})

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
            anime_tid = self.database.get_tid(self.params['id'])
            html = self.network.get_html2('https://tr.anidub.com/index.php?newsid={}'.format(anime_tid))
        
            try: html = html.decode(encoding='utf-8', errors='replace')
            except: pass

            html = html[html.find('<div class="torrent_c">')+23:html.rfind(u'Управление')]

            data_array = html.split('</ul-->')

            qa = []
            la = []

            for data in data_array:
                torrent_id = data[data.find('torrent_')+8:data.find('_info\'>')]

                if '<div id="' in data:
                    quality = data[data.find('="')+2:data.find('"><')]
                    qa.append(quality)

                if '<div id=\'torrent_' in data:
                    quality = qa[len(qa) - 1]
                    if u'Серии в торренте:' in data:
                        series = data[data.find(u'Серии в торренте:')+17:data.find(u'Раздают')]
                        series = tag_list(series)
                    
                        qid = '{} - [ {} ]'.format(quality, series)
                    else:
                        qid = quality

                    seed = data[data.find('li_distribute_m">')+17:data.find('</span> <')]
                    peer = data[data.find('li_swing_m">')+12:data.find(u'</span> <span class="sep"></span> Размер:')]
                    size = data[data.find(u'Размер: <span class="red">'):data.find(u'</span> <span class="sep"></span> Скачали')]
                    size = size.replace(u'Размер: <span class="red">', '')

                    label = '[COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(size, qid.upper(), seed, peer)
                    la.append('{}|||{}'.format(label, torrent_id))

            for lb in reversed(la):
                lb = lb.split('|||')
                label = lb[0]
                torrent_id = lb[1]

                self.create_line(title=label, anime_id=self.params['id'], params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id']})

        if self.params['param']:
            url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['param'])            
            
            file_name = '{}_{}'.format(self.params['portal'], self.params['param'])
            full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))
            torrent_file = self.network.get_file(target_name=url, destination_name=full_name)

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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False,  size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], folder=False, size=info['length'])

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
