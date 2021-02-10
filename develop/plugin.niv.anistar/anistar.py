# -*- coding: utf-8 -*-

import gc
import os
import sys
import urllib
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility
import info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.anistar')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.site_url = 'https://{}/'.format(Main.addon.getSetting('mirror'))

        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon_data_dir = utility.fs_enc(xbmc.translatePath(Main.addon.getAddonInfo('profile')))
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
        
        self.sid_file = utility.fs_enc(os.path.join(self.cookies_dir, 'anistar.sid' ))

        self.params = {'mode': 'main_part', 'param': '', 'node': '', 'page': '1'}

        args = utility.get_params()
        for a in args:
            self.params[a] = urllib.unquote_plus(args[a])
#================================================
        if self.params['param'] == 'db':
            try: os.remove(os.path.join(self.database_dir, 'anistar.db'))
            except: pass
#================================================
        if Main.addon.getSetting('adult') == 'false':
            try: Main.addon.setSetting('adult_pass', '')
            except: pass
#================================================
        if Main.addon.getSetting('unblock') == '1':
            try: proxy_time = float(Main.addon.getSetting('proxy_time'))
            except: proxy_time = 0
            
            if time.time() - proxy_time > 36000:
                Main.addon.setSetting('proxy_time', str(time.time()))
                proxy_pac = urllib.urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Main.addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}
            else:
                proxy_data = {'https': Main.addon.getSetting('proxy')}
        else:
            proxy_data = None
#================================================
        try: session_time = float(Main.addon.getSetting('session_time'))
        except: session_time = 0

        if time.time() - session_time > 28800:
            Main.addon.setSetting('session_time', str(time.time()))
            try: os.remove(self.sid_file)
            except: pass
            Main.addon.setSetting('auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(auth_usage=bool(Main.addon.getSetting('auth_mode') == 'true'),
                                auth_status=bool(Main.addon.getSetting('auth') == 'true'),
                                proxy_data=proxy_data,
                                auth_url=self.site_url)
        self.network.auth_post_data = {'login_name': Main.addon.getSetting('login'),
                                       'login_password': Main.addon.getSetting('password'),
                                       'login': 'submit'}
        self.network.sid_file = self.sid_file
        del WebTools
#================================================
        if Main.addon.getSetting('auth_mode') == 'true':
            if not Main.addon.getSetting("login") or not Main.addon.getSetting("password"):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('XBMC.Notification(Авторизация, Укажите логин и пароль)')            
                return

            if not self.network.auth_status:
                if not self.network.authorization():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('XBMC.Notification(Ошибка, Проверьте логин и пароль)')
                    return
                else:
                    Main.addon.setSetting("auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'anistar.db')):
            db_file = os.path.join(self.database_dir, 'anistar.db')
            db_url = 'https://github.com/NIV82/kodi_repo/raw/main/release/plugin.niv.anistar/anistar.db'
            try:                
                data = urllib.urlopen(db_url)
                chunk_size = 8192
                bytes_read = 0
                file_size = int(data.info().getheaders("Content-Length")[0])
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
                xbmc.executebuiltin('XBMC.Notification(База Данных, [B]БД успешно загружена[/B])')
                Main.addon.setSetting('database', 'true')
            except:
                xbmc.executebuiltin('XBMC.Notification(База Данных, Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
                Main.addon.setSetting('database', 'false')
                pass
#================================================
        from database import DBTools
        if Main.addon.getSetting('database') == 'false':
            try: os.remove(os.path.join(self.database_dir, 'anistar.db'))
            except: pass
            Main.addon.setSetting('database', 'true')
        self.database = DBTools(os.path.join(self.database_dir, 'anistar.db'))
        del DBTools
#================================================
    def create_match_ru(self, text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')):
        return not alphabet.isdisjoint(text.lower())

    def create_title_info(self, title):
        info = dict.fromkeys(['title_ru', 'title_en'], '')

        title = utility.rep_list(title)
        title = utility.tag_list(title)
        title = title.replace('|', '/')
        title = title.replace('\\', '/')
        
        v = title.split('/', 1)

        if not self.create_match_ru(v[0]):
            if self.create_match_ru(v[1]):
                v.reverse()
       
        if len(v) == 1:
            v.append('')

        # if v[1].find('/') > -1:
        #     v[1] = v[1][:v[1].find('/')]

        try:
            info['title_ru'] = v[0].strip().capitalize()
            info['title_en'] = v[1].strip().capitalize()
        except:
            pass
        
        return info

    def create_title(self, title, series):
        if series:
            series = ' - [COLOR=gold][ {} ][/COLOR]'.format(series)
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
        url = '{}uploads/posters/{}/original.jpg'.format(self.site_url, anime_id)

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                return utility.fs_dec(os.path.join(self.images_dir, local_img))
            else:
                file_name = utility.fs_dec(os.path.join(self.images_dir, local_img))
                return self.network.get_file(target_name=url, destination_name=file_name)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)
            info = {'title': title, 'year': anime_info[0], 'genre': anime_info[1], 'director': anime_info[2], 'writer': anime_info[3], 'plot': anime_info[4]}

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)
        
        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.anistar/?mode=clean_part")')])
        else:
            li.addContextMenuItems([('[B]Добавить Избранное (anistar)[/B]', 'Container.Update("plugin://plugin.niv.anistar/?mode=favorites_part&node=plus&id={}")'.format(anime_id)), 
                                    ('[B]Удалить Избранное (anistar)[/B]', 'Container.Update("plugin://plugin.niv.anistar/?mode=favorites_part&node=minus&id={}")'.format(anime_id))])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urllib.urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_schedule_info(self, anime_id):
        url = '{}index.php?newsid={}'.format(self.site_url,anime_id)
        html = self.network.get_html(target_name=url)

        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'author', 'plot'], '')
       
        title_data = html[html.find('<h1'):html.find('</h1>')]        
        info.update(self.create_title_info(title_data))

        genre = html[html.find('<p class="tags">')+16:html.find('</a></p>')]
        genre = genre.replace('Новинки(онгоинги)', '').replace('Аниме', '')
        genre = genre.replace('Категория:', '').replace('Хентай', '')
        genre = genre.replace('Дорамы', '').replace('></a>,','>')            
        info['genre'] = utility.tag_list(genre)

        if 'Новости сайта' in info['genre']:
            return 'advertising'

        data_array = html[html.find('news_text">')+11:html.find('<div class="descripts"')]
        data_array = data_array.splitlines()

        for line in data_array:
            if 'Год выпуска:' in line:
                for year in range(1996, 2030, 1):
                    if str(year) in line:                        
                        info['year'] = year
            if 'Режиссёр:' in line:
                line = line.replace('Режиссёр:','')
                info['director'] = utility.tag_list(line)
            if 'Автор оригинала:' in line:
                line = line.replace('Автор оригинала:','')
                info['author'] = utility.tag_list(line)

        plot = html[html.find('description">')+13:html.find('<div class="descripts">')]

        if plot.find('<p class="reason">') > -1:
            plot = plot[:plot.find('<p class="reason">')]
        
        plot = utility.clean_list(plot)
        plot = utility.rep_list(plot)        

        if plot.find('<div class="title_spoiler">') > -1:
            spoiler = plot[plot.find('<div class="title_spoiler">'):plot.find('<!--spoiler_text_end-->')]
            spoiler = spoiler.replace('</div>', ' ').replace('"','')
            spoiler = spoiler.replace('#', '\n#')
            spoiler = utility.tag_list(spoiler)

            plot = plot[:plot.find('<!--dle_spoiler')]
            plot = utility.tag_list(plot)
            info['plot'] = '{}\n\n{}'.format(plot, spoiler)
        else:
            info['plot'] = utility.tag_list(plot)

        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['year'], info['genre'], info['director'], info['author'], info['plot'])
        except:
            xbmc.executebuiltin('XBMC.Notification(Ошибка парсера, ERROR: 101 - [ADD])')
            return 101
        return

    def create_info(self, anime_id, data):
        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'author', 'plot'], '')

        title_data = data[data.find('">')+2:data.find('</a>')]
        info.update(self.create_title_info(title_data))

        genre = data[data.find('<p class="tags">')+16:data.find('</a></p>')]
        genre = genre.replace('Новинки(онгоинги)', '').replace('Аниме', '')
        genre = genre.replace('Категория:', '').replace('Хентай', '')
        genre = genre.replace('Дорамы', '').replace('></a>,','>')
        genre = utility.rep_list(genre)
        info['genre'] = utility.tag_list(genre)

        if 'Новости сайта' in info['genre']:
            return 'advertising'

        data_array = data[data.find('news_text">')+11:data.find('<div class="descripts"')]
        data_array = data_array.splitlines()

        for line in data_array:
            if 'Год выпуска:' in line:
                for year in range(1950, 2030, 1):
                    if str(year) in line:
                        info['year'] = year
            if 'Режиссёр:' in line:
                line = line.replace('Режиссёр:','')
                info['director'] = utility.tag_list(line)
            if 'Автор оригинала:' in line:
                line = line.replace('Автор оригинала:','')
                info['author'] = utility.tag_list(line)

        plot = data[data.find('<div class="descripts">'):data.rfind('<div class="clear"></div>')]

        if plot.find('<p class="reason">') > -1:
            plot = plot[:plot.find('<p class="reason">')]
        
        plot = utility.clean_list(plot)
        plot = utility.rep_list(plot)

        if plot.find('<div class="title_spoiler">') > -1:
            spoiler = plot[plot.find('<div class="title_spoiler">'):plot.find('<!--spoiler_text_end-->')]
            spoiler = spoiler.replace('</div>', ' ').replace('"','')
            spoiler = spoiler.replace('#', '\n#')
            spoiler = utility.tag_list(spoiler)

            plot = plot[:plot.find('<!--dle_spoiler')]
            plot = utility.tag_list(plot)
            info['plot'] = '{}\n\n{}'.format(plot, spoiler)
        else:
            info['plot'] = utility.tag_list(plot)

        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['year'], info['genre'], info['director'], info['author'], info['plot'])
        except:
            xbmc.executebuiltin('XBMC.Notification(Ошибка парсера, ERROR: 101 - [ADD])')
            return 101
        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        Main.addon.openSettings()
    
    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&skin=new36'.format(self.site_url, self.params['id'], self.params['node'])

        try:
            self.network.get_html(target_name=url)
            xbmc.executebuiltin("XBMC.Notification(Избранное, Готово)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Избранное, ERROR: 103)")

        xbmc.executebuiltin('Container.Refresh')

    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, Успешно выполнено)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, [COLOR=yellow]ERROR: 102[/COLOR])")
            pass
        xbmc.executebuiltin('Container.Refresh')

    def exec_main_part(self):
        if Main.addon.getSetting('auth_mode') == 'true':
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=lime][ Аниме ][/COLOR][/B]', params={'mode': 'catalog_part'})
        self.create_line(title='[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorams/'})
        self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'cartoons/'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=white][ Категории ][/COLOR][/B]', params={'mode': 'categories_part'})
        self.create_line(title='[B][COLOR=white][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'new/'})
        self.create_line(title='[B][COLOR=white][ RPG ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'rpg/'})
        self.create_line(title='[B][COLOR=white][ Скоро ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'next/'})        
        if Main.addon.getSetting('adult') == 'true':
            if Main.addon.getSetting('adult_pass') in info.ignor_list:
                self.create_line(title='[B][COLOR=white][ Хентай ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'hentai/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})            
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})
            self.create_line(title='= = = = = = = = = = = = = = = = = = = =', params={}, folder=False)
            self.create_line(title='[B][COLOR=white][ Обновление Базы Данных ][/COLOR][/B]', params={'mode': 'main_part', 'param': 'db'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)      
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]anistar.org[/COLOR]', data)
        return

    def exec_search_part(self):
        if not Main.addon.getSetting('search'):
            Main.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title='[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})

            data_array = Main.addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': urllib.quote(data.decode('utf8').encode('cp1251'))})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                search_string = skbd.getText()
                self.params['search_string'] = urllib.quote(search_string.decode('utf8').encode('cp1251'))

                data_array = Main.addon.getSetting('search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), urllib.unquote(search_string))
                Main.addon.setSetting('search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if self.params['param'] == 'genres':
            data = info.categories

        if self.params['param'] == 'years':
            data = info.years

        if self.params['param'] == 'genres':
            for i in data:
                label = '{}'.format(i[1])
                self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&xf={}'.format(urllib.quote_plus(i[1]))})

        if self.params['param'] == 'years':
            for i in data:
                label = '{}'.format(i)
                self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&type=year&r=anime&xf={}'.format(i)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_categories_part(self):
        data_array = info.categories

        for data in data_array:
            label = '[B][COLOR=white]{}[/COLOR][/B]'.format(data[1])
            self.create_line(title=label, params={'mode': 'common_part', 'param': '{}'.format(data[0])})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_schedule_part(self):
        self.progress.create("AniStar", "Инициализация")

        url = '{}{}'.format(self.site_url, 'raspisanie-vyhoda-seriy-ongoingov.html')
        html = self.network.get_html(target_name=url)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return  

        week_title = []

        today_title = html[html.find('<span>[')+7:html.find(']</span>')]
        today_title = '{} - {}'.format('Сегодня', today_title)

        call_list = html[html.find('<div class=\'cal-list\'>'):html.find('<div id="day1')]
        week_list = '{}{}'.format(today_title, call_list).replace('<span>',' - ')        
        week_list = utility.tag_list(week_list)
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

            day_title = '{}'.format(week_title[w])
            self.create_line(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(day_title), params={})
            
            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            for data in array:
                anime_id = data[data.find(self.site_url):data.find('.html">')].replace(self.site_url, '')
                anime_id = anime_id[:anime_id.find('-')]                
                series = ''

                if data.find('<smal>') > -1 :
                    series = data[data.find('<smal>')+6:data.find('</smal>')]
                else:
                    series = data[data.find('<div class="timer_cal">'):]
                    series = utility.tag_list(series)

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_schedule_info(anime_id)

                label = self.create_title(self.database.get_title(anime_id), series)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

            w = w + 1
        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_common_part(self):
        self.progress.create("AniStar", "Инициализация")
        
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        post = ''
        
        if 'xfsearch' in self.params['param']:
            url = '{}index.php?cstart={}{}'.format(self.site_url, self.params['page'], self.params['param'])

        if self.params['param'] == 'search_part':
            url = self.site_url
            post = 'do=search&subaction=search&search_start={}&full_search=1&story={}&catlist%5B%5D=39&catlist%5B%5D=113&catlist%5B%5D=76'.format(
                self.params['page'], self.params['search_string'])

        html = self.network.get_html(target_name=url, post=post)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return   
        
        data_array = html[html.find('title_left">')+12:html.rfind('<div class="panel-bottom-shor">')]
        data_array = data_array.split('<div class="title_left">')

        if self.params['param'] == 'search_part':
            data_array.pop(0)

        if len(data_array) > 0:
            i = 0
            for data in data_array:
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                if data.find('/m/">Манга</a>') > -1:
                    continue

                if data.find('/hentai/">Хентай</a>') > -1:
                    if not Main.addon.getSetting('adult_pass') in info.ignor_list:
                        continue

                anime_id = data[data.find(self.site_url):data.find('">')].replace(self.site_url, '')
                if 'index.php?newsid=' in anime_id:
                    anime_id = anime_id.replace('index.php?newsid=', '').strip()
                else:
                    anime_id = anime_id[:anime_id.find('-')]
                
                series = ''
                if data.find('<p class="reason">') > -1:
                    series = data[data.find('<p class="reason">')+18:data.rfind('</p>')]

                if anime_id in info.ignor_list:
                    continue

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id, data)

                    if inf == 'advertising':
                        continue

                    if type(inf) == int:
                        self.create_line(title='[B][ [COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(self.database.get_title(anime_id), series)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})

        self.progress.close()
        
        if html.find('button_nav r"><a') > -1:
            if self.params['param'] == 'search_part':
                self.create_line(title='[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
                                 'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
            else:
                self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_select_part(self):
        html = self.network.get_html('{}index.php?newsid={}'.format(self.site_url, self.params['id']))

        if html.find('<div class="title">') > -1:
            data_array = html[html.find('<div class="title">')+19:html.rfind('<div class="bord_a1">')]
            data_array = data_array.split('<div class="title">')

            for data in data_array:
                torrent_url = data[data.find('gettorrent.php?id=')+18:data.find('">')]

                data = utility.clean_list(data).replace('<b>','|').replace('&nbsp;','')            
                data = utility.tag_list(data).split('|')

                torrent_title = data[0][:data[0].find('(')].strip()
                torrent_seed = data[1].replace('Раздают:', '').strip()
                torrent_peer = data[2].replace('Качают:', '').strip()
                torrent_size = data[4].replace('Размер:', '').strip()

                label = '{} , [COLOR=yellow]{}[/COLOR], Сидов: [COLOR=green]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                    torrent_title, torrent_size, torrent_seed, torrent_peer)
                
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'])
                
        else:
            self.create_line(title='Контент не обнаружен', params={})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        url = '{}engine/gettorrent.php?id={}'.format(self.site_url, self.params['torrent_url'])
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

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if Main.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Main.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(urllib.quote_plus(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(urllib.quote_plus(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        xbmc.executebuiltin("Container.Refresh")

if __name__ == "__main__":
    anistar = Main()
    anistar.execute()
    del anistar

gc.collect()