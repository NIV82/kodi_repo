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

class Anistar:
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

        if self.addon.getSetting('anistar_adult') == 'false':
            try: self.addon.setSetting('anistar_adult_pass', '')
            except: pass

        #self.proxy_data = self.create_proxy_data()
        self.proxy_data = None
        self.site_url = self.create_site_url()
        #self.auth_mode = bool(self.addon.getSetting('anistar_auth_mode') == '1')
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
            auth_status=bool(self.addon.getSetting('anistar_auth') == 'true'),
            proxy_data=self.proxy_data,
            portal='anistar')
        self.auth_post_data = {
            'login_name': self.addon.getSetting('anistar_username'),
            'login_password': self.addon.getSetting('anistar_password'),
            'login': 'submit'}
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anistar.sid')
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not self.addon.getSetting('{}_username'.format(self.params['portal'])) or not self.addon.getSetting('{}_password'.format(self.params['portal'])):
                self.params['mode'] = 'addon_setting'
                self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
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
    # def create_proxy_data(self):
    #     if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
    #         return None

    #     try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
    #     except: proxy_time = 0

    #     if time.time() - proxy_time > 86400:
    #         self.addon.setSetting('animeportal_proxy_time', str(time.time()))
    #         proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

    #         try: proxy_pac = proxy_pac.decode('utf-8')
    #         except: pass
            
    #         proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
    #         self.addon.setSetting('animeportal_proxy', proxy)
    #         proxy_data = {'https': proxy}
    #     else:
    #         if self.addon.getSetting('animeportal_proxy'):
    #             proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
    #         else:
    #             proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

    #             try: proxy_pac = proxy_pac.decode('utf-8')
    #             except: pass
                
    #             proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
    #             self.addon.setSetting('animeportal_proxy', proxy)
    #             proxy_data = {'https': proxy}

    #     return proxy_data
#========================#========================#========================#
    def create_site_url(self):
        site_url = self.addon.getSetting('anistar_mirror_0')
        current_mirror = 'anistar_mirror_{}'.format(self.addon.getSetting('anistar_mirror_mode'))        

        if not self.addon.getSetting(current_mirror):
            try:
                self.exec_mirror_part()
                site_url = '{}'.format(self.addon.getSetting('anistar_mirror'))
            except:
                site_url = self.addon.getSetting('anistar_mirror_0')
        else:
            site_url = '{}'.format(self.addon.getSetting(current_mirror))
        return site_url
#========================#========================#========================#
    def create_title_info(self, title):
        info = dict.fromkeys(['title_ru', 'title_en'], '')

        alphabet=set(u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')

        #title = unescape(title)
        title = tag_list(title)
        title = title.replace('|', '/')
        title = title.replace('\\', '/')
        
        v = title.split('/', 1)

        if len(v) == 1:
            v.append('')

        if alphabet.isdisjoint(v[0].lower()): #если v[0] не ru
            if not alphabet.isdisjoint(v[1].lower()): #если v[1] ru
                v.reverse()

        # if v[1].find('/') > -1:
        #     v[1] = v[1][:v[1].find('/')]

# доделать обработку v[1] - разделить еще раз, выбрать английскую часть , остальное выкинуть

        try:
            info['title_ru'] = v[0].strip().capitalize()
            info['title_en'] = v[1].strip().capitalize()
        except: pass
        
        return info
#========================#========================#========================#
    def create_title(self, title, series):
        if series:
            series = u' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''

        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{} / {}{}'.format(title[0], title[1], series)
            
        return label
#========================#========================#========================#
    def create_image(self, anime_id):
        url = '{}uploads/posters/{}/original.jpg'.format(self.site_url, anime_id)

        if self.addon.getSetting('anistar_covers') == '0':
            return url
        else:
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
        
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=anistar")'))
        context_menu.append(('[COLOR=darkorange]Обновить Зеркала[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anistar")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anistar")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anistar")'.format(anime_id)))

        if self.auth_mode and not self.params['param'] == '':
            context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anistar")'.format(anime_id)))
            context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anistar")'.format(anime_id)))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anistar")'))
        context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=anistar")'))
        context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=anistar")'))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            if cover:
                pass
            else:
                cover = self.create_image(anime_id)
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

        params['portal'] = 'anistar'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, data, schedule=False, update=False):
        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'author', 'plot'], '')

        if schedule:
            url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
            data = self.network.get_html(target_name=url)

            try: data = data.decode(encoding='utf-8', errors='replace')
            except: pass

            data = unescape(data)

            title_data = data[data.find('<h1'):data.find('</h1>')]
        else:
            title_data = data[data.find('>')+1:data.find('</a>')]
        
        info.update(self.create_title_info(title_data))

        genre = data[data.find('<p class="tags">')+16:data.find('</a></p>')]
        genre = genre.replace(u'Новинки(онгоинги)', '').replace(u'Аниме', '')
        genre = genre.replace(u'Категория:', '').replace(u'Хентай', '')
        genre = genre.replace(u'Дорамы', '').replace('></a>,','>')
        info['genre'] = tag_list(genre)

        if u'Новости сайта' in info['genre']:
            if u'<li><b>Жанр: </b>' in data:
                pass
            else:
                return 999

        data_array = data[data.find('news_text">')+11:data.find('<div class="descripts"')]
        data_array = data_array.splitlines()

        for line in data_array:
            if u'Год выпуска:' in line:
                for year in range(1950, 2030, 1):
                    if str(year) in line:
                        info['year'] = year
            if u'Режиссёр:' in line:
                line = line.replace(u'Режиссёр:','')
                info['director'] = tag_list(line)
            if u'Автор оригинала:' in line:
                line = line.replace(u'Автор оригинала:','')
                info['author'] = tag_list(line)

        if schedule:
            plot = data[data.find('description">')+13:data.find('<div class="descripts">')]
        else:
            plot = data[data.find('<div class="descripts">'):data.rfind('<div class="clear"></div>')]

        if '<p class="reason">' in plot:
            plot = plot[:plot.find('<p class="reason">')]

        plot = clean_list(plot)

        if '<div class="title_spoiler">' in plot:
            spoiler = plot[plot.find('<div class="title_spoiler">'):plot.find('<!--spoiler_text_end-->')]
            spoiler = spoiler.replace('</div>', ' ').replace('"','')
            spoiler = spoiler.replace('#', '\n#')
            spoiler = tag_list(spoiler)

            plot = plot[:plot.find('<!--dle_spoiler')]
            plot = tag_list(plot)
            info['plot'] = u'{}\n\n{}'.format(plot, spoiler)
        else:
            info['plot'] = tag_list(plot)
        
        try:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru = info['title_ru'],
                title_en = info['title_en'],                
                aired_on = info['year'],
                genres = info['genre'],
                director = info['director'],
                writer = info['author'],
                description = info['plot'],
                update = update
            )
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
        self.create_info(anime_id=self.params['id'], update=True, schedule=True, data=None)
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

            self.progress_bg.create(u'Загрузка Базы Данных')
            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress_bg.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
            self.progress_bg.close()
            self.dialog.notification(heading='База Данных',message='ЗАГРУЖЕНА',icon=self.icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='База Данных',message='ОШИБКА',icon=self.icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_mirror_part(self):

        proxy_data = {'https': 'proxy-nossl.antizapret.prostovpn.org:29976'}

        from network import WebTools
        self.net = WebTools(proxy_data=proxy_data, portal=self.params['portal'])
        del WebTools

        current_mirror = 'anistar_mirror_{}'.format(self.addon.getSetting('anistar_mirror_mode'))
        site_url = self.addon.getSetting('anistar_mirror_0')

        try:
            ht = self.net.get_html(target_name=site_url)
            
            actual_url = ht[ht.find('<center><h3><b><u>'):ht.find('</span></a></u></b></h3></center>')]
            actual_url = tag_list(actual_url).lower()
            actual_url = 'https://{}/'.format(actual_url)
            
            self.dialog.notification(heading='УСПЕШНО',message='Применяем новый адрес:\n[COLOR=blue]{}[/COLOR]'.format(actual_url),icon=self.icon,time=5000,sound=False)
        except:
            actual_url = site_url
            self.dialog.notification(heading='ОШИБКА',message='Применяем базовый адрес:\n[COLOR=blue]{}[/COLOR]'.format(actual_url),icon=self.icon,time=5000,sound=False)

        self.addon.setSetting(current_mirror, actual_url)
#========================#========================#========================#
    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&skin=new36'.format(self.site_url, self.params['id'], self.params['node'])

        if 'plus' in self.params['node']:
            try:
                self.network.get_html(target_name=url)
                self.dialog.notification(heading='Избранное',message='УСПЕШНО ДОБАВЛЕНО',icon=self.icon,time=5000,sound=False)
            except:
                self.dialog.notification(heading='Избранное',message='ОШИБКА',icon=self.icon,time=5000,sound=False)

        if 'minus' in self.params['node']:
            try:
                self.network.get_html(target_name=url)
                self.dialog.notification(heading='Избранное',message='УСПЕШНО УДАЛЕНО',icon=self.icon,time=5000,sound=False)
            except:
                self.dialog.notification(heading='Избранное',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            self.dialog.notification(heading='Поиск',message='УСПЕШНО УДАЛЕНО',icon=self.icon,time=5000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
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
        if self.auth_mode:
            self.create_line(title=u'[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title=u'[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title=u'[B][COLOR=lime][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title=u'[B][COLOR=lime][ Категории ][/COLOR][/B]', params={'mode': 'categories_part'})
        self.create_line(title=u'[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'new/'})
        self.create_line(title=u'[B][COLOR=lime][ RPG ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'rpg/'})
        self.create_line(title=u'[B][COLOR=lime][ Скоро ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'next/'})        
        if '1' in self.addon.getSetting('anistar_adult'):
            from info import anistar_ignor_list
            if self.addon.getSetting('anistar_adult_pass') in anistar_ignor_list:
                self.create_line(title=u'[B][COLOR=lime][ Хентай ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'hentai/'})
        self.create_line(title=u'[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorams/'})
        self.create_line(title=u'[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'cartoons/'})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title=u'[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})

            data_array = self.addon.getSetting('anistar_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                
                try: self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data.decode('utf8').encode('cp1251'))})
                except: self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data.encode('cp1251'))})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                search_string = skbd.getText()
                
                try: self.params['search_string'] = quote(search_string.decode('utf8').encode('cp1251'))
                except: self.params['search_string'] = quote(search_string.encode('cp1251'))

                data_array = self.addon.getSetting('anistar_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(search_string))
                self.addon.setSetting('anistar_search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if 'genres' in self.params['param']:
            from info import anistar_genres2

            for k, i in anistar_genres2.items():
                label = '{}'.format(i)
                self.create_line(title=label, params={'mode': 'common_part', 'param': 'genres', 'node': '{}'.format(k)})

        if 'years' in self.params['param']:
            from info import anistar_years
            for i in anistar_years:
                label = '{}'.format(i)
                # self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&type=year&r=anime&xf={}'.format(i)})
                self.create_line(title=label, params={'mode': 'common_part','param':'years', 'node': '{}'.format(i)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_categories_part(self):
        from info import anistar_genres

        for data in anistar_genres:
            label = '[B][COLOR=white]{}[/COLOR][/B]'.format(data[1])
            self.create_line(title=label, params={'mode': 'common_part', 'param': '{}'.format(data[0])})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        html = self.network.get_html(
            target_name='{}{}'.format(self.site_url, 'raspisanie-vyhoda-seriy-ongoingov.html'))

        html = unescape(html)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return
        
        self.progress_bg.create("AniStar", "Инициализация")
        
        week_title = []

        today_title = html[html.find('<span>[')+7:html.find(']</span>')]
        today_title = u'{} - {}'.format(u'Сегодня', today_title)

        call_list = html[html.find('<div class=\'cal-list\'>'):html.find('<div id="day1')]
        week_list = u'{}{}'.format(today_title, call_list).replace('<span>',' - ')        
        week_list = tag_list(week_list)
        week_list = week_list.splitlines()

        for day in week_list:
            week_title.append(day)

        data_array = html[html.find('<div class="news-top">'):html.find('function calanime')]
        data_array = data_array.replace(call_list, '')
        data_array = data_array.split('<div id="day')

        w = 0
        i = 0

        for array in data_array:
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            array = array.split('<div class="top-w" >')
            array.pop(0)

            day_title = u'{}'.format(week_title[w])
            self.create_line(title=u'[B][COLOR=lime]{}[/COLOR][/B]'.format(day_title), params={})

            self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            for data in array:
                anime_id = data[data.find(self.site_url):data.find('.html">')].replace(self.site_url, '')
                anime_id = anime_id[:anime_id.find('-')]                
                series = ''

                if '<smal>' in data:
                    series = data[data.find('<smal>')+6:data.find('</smal>')]
                else:
                    series = data[data.find('<div class="timer_cal">'):]
                    series = tag_list(series)

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id, data=None, schedule=True)

                label = self.create_title(self.database.get_title(anime_id), series)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

            w = w + 1
        self.progress_bg.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        from info import anistar_ignor_list

        self.progress_bg.create("AniStar", u"Инициализация")
        
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        post = ''

        if 'genre' in self.params['param']:
            from info import anistar_genres2

            url = '{}index.php?cstart={}&do=xfsearch&xf={}'.format(
                self.site_url, self.params['page'], quote(anistar_genres2[self.params['node']])
                )

        if 'years' in self.params['param']:
            xbmc.log(str(self.params['node']), xbmc.LOGFATAL)
            url = '{}index.php?cstart={}&do=xfsearch&type=year&r=anime&xf={}'.format(
                self.site_url, self.params['page'], self.params['node']
                )

        if self.params['param'] == 'search_part':
            url = self.site_url
            post = 'do=search&subaction=search&search_start={}&full_search=1&story={}&catlist%5B%5D=39&catlist%5B%5D=113&catlist%5B%5D=76'.format(
                self.params['page'], self.params['search_string'])

        html = self.network.get_html(target_name=url, post=post)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return   
        
        data_array = html[html.find('title_left">')+12:html.rfind('<div class="panel-bottom-shor">')]
        data_array = data_array.split('<div class="title_left">')

        if self.params['param'] == 'search_part':
            data_array.pop(0)

        if len(data_array) < 1:
            self.create_line(title=u'[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return   

        i = 0

        for data in data_array:
            data = unescape(data)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if u'/m/">Манга</a>' in data:
                continue

            if u'/hentai/">Хентай</a>' in data:
                if not self.addon.getSetting('anistar_adult_pass') in anistar_ignor_list:
                    continue

            anime_id = data[data.find(self.site_url):data.find('">')].replace(self.site_url, '')
            anime_id = anime_id.replace('index.php?newsid=', '').split('-',1)[0]

            series = ''
            if '<p class="reason">' in data:
                series = data[data.find('<p class="reason">')+18:data.rfind('</p>')]

            if anime_id in anistar_ignor_list:
                continue

            self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                inf = self.create_info(anime_id, data)

                if type(inf) == int:
                    if not inf == 999:
                        self.create_line(title='[B][ [COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                    continue

            label = self.create_title(self.database.get_title(anime_id), series)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        self.progress_bg.close()

        if 'button_nav r"><a' in html:
            if 'search_part' in self.params['param']:
                self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                                 'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
            else:
                self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        self.create_line(title=u'[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id']})
        self.create_line(title=u'[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            video_url = '{}test/player2/videoas.php?id={}'.format(self.site_url, self.params['id'])
            html = self.network.get_html(target_name=video_url)

            html = unescape(html)

            data_array = html[html.find('playlst=[')+9:html.find('];')]
            data_array = data_array.split('{')
            data_array.pop(0)

            array = {'480p [multi voice]': [],'720p [multi voice]': [],'480p [single voice]': [],'720p [single voice]': []}

            for data in data_array:
                title = data[data.find('title:"')+7:data.find('",')]
                file_data =  data[data.find('php?360=')+4:data.rfind('",')]

                sd_url = file_data[file_data.find('360=')+4:file_data.find('.m3u8')+5]
                hd_url = sd_url.replace('360', '720')

                if u'Многоголосая озвучка' in title:
                    array['480p [multi voice]'].append(u'{}|{}'.format(title, sd_url))
                    array['720p [multi voice]'].append(u'{}|{}'.format(title, hd_url))
                else:
                    array['480p [single voice]'].append(u'{}|{}'.format(title, sd_url))
                    array['720p [single voice]'].append(u'{}|{}'.format(title, hd_url))
            
            for i in array.keys():
                if array[i]:
                    array_info = '|||'.join(array[i])

                    try: array_info = array_info.encode('utf-8')
                    except: pass

                    label = '[B]Качество: {}[/B]'.format(i)
                    label = label.replace('480p','[COLOR=gold]480p[/COLOR]')
                    label = label.replace('720p','[COLOR=gold]720p[/COLOR]')
                    label = label.replace('[single voice]','[COLOR=blue][single voice][/COLOR]')
                    label = label.replace('[multi voice]','[COLOR=lime][multi voice][/COLOR]')

                    self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': array_info}, anime_id=self.params['id'])

        if self.params['param']:
            data_array = unquote(self.params['param']).split('|||')

            for data in data_array:
                data = data.split('|')

                self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            html = self.network.get_html('{}index.php?newsid={}'.format(self.site_url, self.params['id']))

            if not '<div class="title">' in html:
                self.create_line(title=u'Контент не обнаружен', params={})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            data_array = html[html.find('<div class="title">')+19:html.rfind('<div class="bord_a1">')]
            data_array = data_array.split('<div class="title">')

            for data in data_array:
                torrent_url = data[data.find('gettorrent.php?id=')+18:data.find('">')]

                data = clean_list(data).replace('<b>','|').replace('&nbsp;','')            
                data = tag_list(data).split('|')

                torrent_title = data[0][:data[0].find('(')].strip()
                torrent_seed = data[1].replace(u'Раздают:', '').strip()
                torrent_peer = data[2].replace(u'Качают:', '').strip()
                torrent_size = data[4].replace(u'Размер:', '').strip()

                label = u'{} , [COLOR=yellow]{}[/COLOR], Сидов: [COLOR=green]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                    torrent_title, torrent_size, torrent_seed, torrent_peer)
                    
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'param': torrent_url},  anime_id=self.params['id'])

        if self.params['param']:
            url = '{}engine/gettorrent.php?id={}'.format(self.site_url, self.params['param'])

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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False, size=size[i])
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