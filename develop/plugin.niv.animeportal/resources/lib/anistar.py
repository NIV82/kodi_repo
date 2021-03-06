# -*- coding: utf-8 -*-

import os, sys, time
import xbmc, xbmcgui, xbmcplugin

try:
    from urllib import urlencode, urlopen, quote, unquote
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen

import info
from utility import tag_list, unescape, clean_list

class Anistar:
    def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress):
        self.progress = progress
        self.dialog = dialog
        self.addon = addon
        self.images_dir = images_dir
        self.torrents_dir = torrents_dir
        self.database_dir = database_dir
        self.cookie_dir = cookie_dir
        self.params = params

        if self.addon.getSetting('anistar_adult') == 'false':
            try: self.addon.setSetting('anistar_adult_pass', '')
            except: pass

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('anistar_auth_mode') == '1')
#================================================
        try: anistar_session = float(self.addon.getSetting('anistar_session'))
        except: anistar_session = 0

        if time.time() - anistar_session > 28800:
            self.addon.setSetting('anistar_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anistar.sid'))
            except: pass
            self.addon.setSetting('anistar_auth', 'false')
#================================================
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
#================================================
        if self.auth_mode:
            if not self.addon.getSetting("anistar_username") or not self.addon.getSetting("anistar_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting("anistar_auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'anistar.db')):
            self.exec_update_part()
#================================================
        from database import Anistar_DB
        self.database = Anistar_DB(os.path.join(self.database_dir, 'anistar.db'))
        del Anistar_DB
#================================================
        self.anistar_categories=[('thriller/','Боевик'),('vampires/','Вампиры'),('ani-garem/','Гарем'),('detective/','Детектив'),('drama/','Драма'),('history/','История'),('cyberpunk/','Киберпанк'),('comedy/','Комедия'),('maho-shoujo/','Махо-седзе'),('fur/','Меха'),('parodies/','Пародии'),('senen/','Сёнен'),('sports/','Спорт'),('mysticism/','Мистика'),('music/','Музыкальное'),('everyday-life/','Повседневность'),('adventures/','Приключения'),('romance/','Романтика'),('shoujo/','Сёдзе'),('senen-ay/','Сёнен-ай'),('horror/','Триллер'),('horor/','Ужасы'),('fantasy/','Фантастика'),('fentezi/','Фэнтези'),('school/','Школа'),('echchi-erotic/','Эччи'),('action/','Экшен'),('metty/','Этти'),('seinen/','Сейнен'),('demons/','Демоны'),('magic/','Магия'),('super-power/','Супер сила'),('military/','Военное'),('kids/','Детское'),('supernatural/','Сверхъестественное'),('psychological/','Психологическое'),('historical/','Исторический'),('samurai/','Самураи'),('martial-arts/','Боевые искусства'),('police/','Полиция'),('space/','Космос'),('game/','Игры'),('josei/','Дзёсэй'),('shoujo-ai/','Сёдзе Ай')]
        self.anistar_ignor_list = ['7013','6930','6917','6974','6974','4106','1704','1229','1207','1939','1954','2282','4263','4284','4288','4352','4362','4422','4931','5129','5130','5154','5155','6917','6928','6930','6932','6936','6968','6994','7013','7055','3999','4270','4282','4296','4300','4314','4348','4349','4364','4365','4366','4367','4368','4369','4374','4377','4480','4493','4556','6036','3218','3943','3974','4000','4091']
#================================================
    def create_proxy_data(self):
        if self.addon.getSetting('anistar_unblock') == '0':
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

    def create_title_info(self, title):
        info = dict.fromkeys(['title_ru', 'title_en'], '')

        alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')

        title = unescape(title)
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

    def create_title(self, title, series):
        if series:
            series = ' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
        
        if self.addon.getSetting('anistar_titles') == '0':
            label = '{}{}'.format(title[0], series)
        if self.addon.getSetting('anistar_titles') == '1':
            label = '{}{}'.format(title[1], series)
        if self.addon.getSetting('anistar_titles') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image(self, anime_id):
        url = '{}uploads/posters/{}/original.jpg'.format(self.site_url, anime_id)

        if self.addon.getSetting('anistar_covers') == '0':
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

    def create_context(self, anime_id):
        context_menu = []
        
        context_menu.append(('[B][COLOR=darkorange]Обновить Базу Данных[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anistar")'))
        context_menu.append(('[B][COLOR=darkorange]Обновить Зеркала[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anistar")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=red]Очистить историю[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anistar")'))

        if self.auth_mode and not self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=white]Добавить FAV (сайт)[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anistar")'.format(anime_id)))
            context_menu.append(('[B][COLOR=white]Удалить FAV (сайт)[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anistar")'.format(anime_id)))

        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append(('[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anistar")'))
        context_menu.append(('[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=anistar")'))
        context_menu.append(('[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=anistar")'))
        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))

        return context_menu

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)
            info = {'title': title, 'year': anime_info[0], 'genre': anime_info[1], 'director': anime_info[2], 'writer': anime_info[3], 'plot': anime_info[4]}

            if size: info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = 'anistar'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = unquote(online)

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id, data, schedule=False):
        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'author', 'plot'], '')

        if schedule:
            url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
            data = self.network.get_html(target_name=url)
            title_data = data[data.find('<h1'):data.find('</h1>')]
        else:
            title_data = data[data.find('>')+1:data.find('</a>')]
        
        info.update(self.create_title_info(title_data))

        genre = data[data.find('<p class="tags">')+16:data.find('</a></p>')]
        genre = genre.replace('Новинки(онгоинги)', '').replace('Аниме', '')
        genre = genre.replace('Категория:', '').replace('Хентай', '')
        genre = genre.replace('Дорамы', '').replace('></a>,','>')
        info['genre'] = tag_list(genre)

        if 'Новости сайта' in info['genre']:
            if '<li><b>Жанр: </b>' in data: pass
            else: return 999

        data_array = data[data.find('news_text">')+11:data.find('<div class="descripts"')]
        data_array = data_array.splitlines()

        for line in data_array:
            if 'Год выпуска:' in line:
                for year in range(1950, 2030, 1):
                    if str(year) in line:
                        info['year'] = year
            if 'Режиссёр:' in line:
                line = line.replace('Режиссёр:','')
                info['director'] = tag_list(line)
            if 'Автор оригинала:' in line:
                line = line.replace('Автор оригинала:','')
                info['author'] = tag_list(line)

        if schedule:
            plot = data[data.find('description">')+13:data.find('<div class="descripts">')]
        else:
            plot = data[data.find('<div class="descripts">'):data.rfind('<div class="clear"></div>')]

        if '<p class="reason">' in plot:
            plot = plot[:plot.find('<p class="reason">')]

        plot = clean_list(plot)
        plot = unescape(plot)

        if '<div class="title_spoiler">' in plot:
            spoiler = plot[plot.find('<div class="title_spoiler">'):plot.find('<!--spoiler_text_end-->')]
            spoiler = spoiler.replace('</div>', ' ').replace('"','')
            spoiler = spoiler.replace('#', '\n#')
            spoiler = tag_list(spoiler)

            plot = plot[:plot.find('<!--dle_spoiler')]
            plot = tag_list(plot)
            info['plot'] = '{}\n\n{}'.format(plot, spoiler)
        else:
            info['plot'] = tag_list(plot)
        
        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['year'], info['genre'], info['director'], info['author'], info['plot'])
        except: return 101
        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        self.addon.openSettings()

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'anistar.db'))
        except: pass        

        db_file = os.path.join(self.database_dir, 'anistar.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anistar.db'
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

    def exec_mirror_part(self):
        from network import WebTools
        self.net = WebTools(auth_usage=False, auth_status=False, proxy_data=self.proxy_data)
        del WebTools

        current_mirror = 'anistar_mirror_{}'.format(self.addon.getSetting('anistar_mirror_mode'))
        site_url = self.addon.getSetting('anistar_mirror_0')

        try:            
            #ht = self.net.get_html(target_name='https://anistar.org/')
            ht = self.net.get_html(target_name=site_url)
            actual_url = ht[ht.find('<center><h3><b><u>'):ht.find('</span></a></u></b></h3></center>')]
            actual_url = tag_list(actual_url).lower()
            actual_url = 'https://{}/'.format(actual_url)
            self.addon.setSetting('anistar_unblock', '0')
            self.dialog.ok('AniStar', '[COLOR=lime]Выполнено[/COLOR]: Применяем новый адрес:\n[COLOR=blue]{}[/COLOR], Отключаем разблокировку'.format(actual_url))            
        except:
            #actual_url = 'https://anistar.org/'
            actual_url = site_url
            self.addon.setSetting('anistar_unblock', '1')
            self.dialog.ok('AniStar', '[COLOR=red]Ошибка[/COLOR]: Применяем базовый адрес:\n[COLOR=blue]{}[/COLOR], Включаем разблокировку'.format(actual_url))

        self.addon.setSetting(current_mirror, actual_url)

    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&skin=new36'.format(self.site_url, self.params['id'], self.params['node'])
        label = self.database.get_title(self.params['id'])[0]

        if 'plus' in self.params['node']:
            try:
                self.network.get_html(target_name=url)
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно добавлено[/COLOR]'.format(label))
            except:
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - 103[/COLOR]'.format(label))

        if 'minus' in self.params['node']:
            try:
                self.network.get_html(target_name=url)
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно удалено[/COLOR]'.format(label))
            except:
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - 103[/COLOR]'.format(label))

    def exec_clean_part(self):
        try:
            self.addon.setSetting('anistar_search', '')
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]Успешно выполнено[/COLOR]')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        if self.auth_mode:
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=lime][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=lime][ Категории ][/COLOR][/B]', params={'mode': 'categories_part'})
        self.create_line(title='[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'new/'})
        self.create_line(title='[B][COLOR=lime][ RPG ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'rpg/'})
        self.create_line(title='[B][COLOR=lime][ Скоро ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'next/'})        
        if self.addon.getSetting('anistar_adult') == '1':
            if self.addon.getSetting('anistar_adult_pass') in self.anistar_ignor_list:
                self.create_line(title='[B][COLOR=lime][ Хентай ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'hentai/'})
        self.create_line(title='[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorams/'})
        self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'cartoons/'})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if not self.addon.getSetting('anistar_search'):
            self.addon.setSetting('anistar_search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title='[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})

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

        if self.params['param'] == 'genres':
            data = self.anistar_categories

        if self.params['param'] == 'years':
            data = ['2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011',
                    '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000',
                    '1999', '1998', '1997', '1996', '1995', '1994', '1993', '1992', '1991', '1990', '1989',
                    '1988', '1987', '1986', '1985', '1984', '1983', '1982', '1981', '1980', '1979', '1978',
                    '1976', '1975', '1972', '1969', '1968']

        if self.params['param'] == 'genres':
            for i in data:
                label = '{}'.format(i[1])
                self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&xf={}'.format(quote(i[1]))})

        if self.params['param'] == 'years':
            for i in data:
                label = '{}'.format(i)
                self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&type=year&r=anime&xf={}'.format(i)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_categories_part(self):
        data_array = self.anistar_categories

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

            day_title = '{}'.format(week_title[w])
            self.create_line(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(day_title), params={})
            
            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            for data in array:
                anime_id = data[data.find(self.site_url):data.find('.html">')].replace(self.site_url, '')
                anime_id = anime_id[:anime_id.find('-')]                
                series = ''

                if '<smal>' in data:
                    series = data[data.find('<smal>')+6:data.find('</smal>')]
                else:
                    series = data[data.find('<div class="timer_cal">'):]
                    series = tag_list(series)

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id, data=None, schedule=True)

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
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return   
        
        data_array = html[html.find('title_left">')+12:html.rfind('<div class="panel-bottom-shor">')]
        data_array = data_array.split('<div class="title_left">')

        if self.params['param'] == 'search_part':
            data_array.pop(0)

        if len(data_array) < 1:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return   

        i = 0
        for data in data_array:
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if '/m/">Манга</a>' in data: continue

            if '/hentai/">Хентай</a>' in data:
                if not self.addon.getSetting('anistar_adult_pass') in self.anistar_ignor_list:
                    continue

            anime_id = data[data.find(self.site_url):data.find('">')].replace(self.site_url, '')
            anime_id = anime_id.replace('index.php?newsid=', '').split('-',1)[0]

            series = ''
            if '<p class="reason">' in data:
                series = data[data.find('<p class="reason">')+18:data.rfind('</p>')]

            if anime_id in self.anistar_ignor_list:
                continue

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.is_anime_in_db(anime_id):
                inf = self.create_info(anime_id, data)

                if type(inf) == int:
                    if not inf == 999:
                        self.create_line(title='[B][ [COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                    continue

            label = self.create_title(self.database.get_title(anime_id), series)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        self.progress.close()

        if 'button_nav r"><a' in html:
            if self.params['param'] == 'search_part':
                self.create_line(title='[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
                                 'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
            else:
                self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_select_part(self):
        self.create_line(title='[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id']})
        self.create_line(title='[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_online_part(self):
        if not self.params['param']:
            video_url = '{}test/player2/videoas.php?id={}'.format(self.site_url, self.params['id'])
            html = self.network.get_html(target_name=video_url)

            data_array = html[html.find('playlst=[')+9:html.find('];')]
            data_array = data_array.split('{')
            data_array.pop(0)

            array = {'480p [multi voice]': [],'720p [multi voice]': [],'480p [single voice]': [],'720p [single voice]': []}

            for data in data_array:
                title = data[data.find('title:"')+7:data.find('",')]
                file_data =  data[data.find('php?360=')+4:data.rfind('",')]

                sd_url = file_data[file_data.find('360=')+4:file_data.find('.m3u8')+5]
                hd_url = sd_url.replace('360', '720')

                if 'Многоголосая озвучка' in title:
                    array['480p [multi voice]'].append('{}|{}'.format(title, sd_url))
                    array['720p [multi voice]'].append('{}|{}'.format(title, hd_url))
                else:
                    array['480p [single voice]'].append('{}|{}'.format(title, sd_url))
                    array['720p [single voice]'].append('{}|{}'.format(title, hd_url))

            for i in array.keys():
                if array[i]:
                    label = '[B]Качество: {}[/B]'.format(i)
                    self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(array[i])}, anime_id=self.params['id'])

        if self.params['param']:
            data_array = self.params['param'].split('|||')

            for data in data_array:
                data = data.split('|')
                self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        if not self.params['param']:
            html = self.network.get_html('{}index.php?newsid={}'.format(self.site_url, self.params['id']))

            if not '<div class="title">' in html:
                self.create_line(title='Контент не обнаружен', params={})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            data_array = html[html.find('<div class="title">')+19:html.rfind('<div class="bord_a1">')]
            data_array = data_array.split('<div class="title">')

            for data in data_array:
                torrent_url = data[data.find('gettorrent.php?id=')+18:data.find('">')]

                data = clean_list(data).replace('<b>','|').replace('&nbsp;','')            
                data = tag_list(data).split('|')

                torrent_title = data[0][:data[0].find('(')].strip()
                torrent_seed = data[1].replace('Раздают:', '').strip()
                torrent_peer = data[2].replace('Качают:', '').strip()
                torrent_size = data[4].replace('Размер:', '').strip()

                label = '{} , [COLOR=yellow]{}[/COLOR], Сидов: [COLOR=green]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
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