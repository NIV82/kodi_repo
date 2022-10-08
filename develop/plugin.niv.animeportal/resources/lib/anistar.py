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
    'Accept-Encoding': 'identity'
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    
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

        if '0' in self.addon.getSetting('anistar_adult'):
            self.addon.setSetting('anistar_adult_pass', '')

        self.proxy_data = self.exec_proxy_data()
        self.site_url = self.create_site_url()
        self.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))
        self.authorization = self.exec_authorization_part()
        self.adult = self.create_adult()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
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
                
        try:
            info['title_ru'] = v[0].strip().capitalize()
            info['title_en'] = v[1].strip().capitalize()
        except: pass
        
        return info
#========================#========================#========================#
    def create_title(self, title, series):
        if series:
            series = u' | [COLOR=gold]{}[/COLOR]'.format(series.strip())
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
            
        if '0' in self.addon.getSetting('anistar_covers'):
            return url
        else:
            local_img = 'anistar_{}{}'.format(anime_id, url[url.rfind('.'):])
            
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
    def create_adult(self):
        if '0' in self.addon.getSetting('anistar_adult'):
            return False
        
        from info import anistar_ignor_list

        if self.addon.getSetting('anistar_adult_pass') in anistar_ignor_list:
            return True
        else:
            return False
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anistar")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anistar")'.format(anime_id)))

        if self.authorization and not self.params['param'] == '':
            context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anistar")'.format(anime_id)))
            context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anistar")'.format(anime_id)))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anistar")'))
        context_menu.append(('[COLOR=darkorange]Обновить Зеркала[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anistar")'))
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=anistar")'))
        context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=renew&portal=anistar")'))
        context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=anistar")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, rating=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            if cover:
                pass
            else:
                cover = self.create_image(anime_id)
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

        params['portal'] = self.params['portal']
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, data, schedule=False, update=False):
        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'author', 'plot'], '')

        if schedule:
            url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.database.add_anime(
                    anime_id=anime_id,
                    title_ru='anime_id: {}'.format(anime_id),
                    title_en='anime_id: {}'.format(anime_id)
                    )
                return
            
            data = data_request.text

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
            self.dialog.notification(heading='Инфо-Парсер',message='Ошибка',icon=self.icon,time=3000,sound=False)
            #return 101

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
    def exec_authorization_part(self):
        if '0' in self.addon.getSetting('anistar_auth_mode'):
            return False

        if not self.addon.getSetting('anistar_username') or not self.addon.getSetting('anistar_password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='Введите Логин и Пароль',icon=self.icon,time=3000,sound=False)
            return

        if 'renew' in self.params['param']:
            self.addon.setSetting('anistar_auth', 'false')
            self.addon.setSetting('anistar_session','')
            
        try: temp_session = float(self.addon.getSetting('anistar_session'))
        except: temp_session = 0
        
        if time.time() - temp_session > 43200:
            self.addon.setSetting('anistar_session', str(time.time()))            
            try: os.remove(self.sid_file)
            except: pass            
            self.addon.setSetting('anistar_auth', 'false')

        auth_post_data = {
            "login_name": self.addon.getSetting('anistar_username'),
            "login_password": self.addon.getSetting('anistar_password'),
            "login": "submit"
            }

        import pickle

        if 'true' in self.addon.getSetting('anistar_auth'):
            try:
                with open(self.sid_file, 'rb') as read_file:
                    session.cookies.update(pickle.load(read_file))
                auth = True
            except:
                try:
                    r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)
                except Exception as e:
                    if '10054' in str(e):
                        self.exec_mirror_part()
                        r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)

                if 'dle_user_id' in str(r.cookies):
                    with open(self.sid_file, 'wb') as write_file:
                        pickle.dump(r.cookies, write_file)
                        
                    session.cookies.update(r.cookies)
                    auth = True
                else:
                    auth = False
        else:
            try:
                r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)
            except Exception as e:
                if '10054' in str(e):
                    self.exec_mirror_part()
                    r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)

            if 'dle_user_id' in str(r.cookies):
                with open(self.sid_file, 'wb') as write_file:
                    pickle.dump(r.cookies, write_file)
                    
                session.cookies.update(r.cookies)
                auth = True
            else:
                auth = False

        if not auth:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=3000,sound=False)
            return
        else:
            self.addon.setSetting('anistar_auth', str(auth).lower())

        return auth
#========================#========================#========================#
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True, schedule=True, data=None)
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
    def exec_mirror_part(self):
        self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'true')
        self.proxy_data = self.exec_proxy_data()
        self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'false')

        current_mirror = 'anistar_mirror_{}'.format(self.addon.getSetting('anistar_mirror_mode'))
        site_url = self.addon.getSetting('anistar_mirror_0')

        try:
            r = requests.get(url=site_url, proxies=self.proxy_data, headers=headers)
            data = r.text

            actual_url = data[data.find('<center><h3><b><u>'):data.find('</span></a></u></b></h3></center>')]
            actual_url = actual_url[actual_url.rfind('>')+1:].lower()
            actual_url = 'https://{}/'.format(actual_url)
            
            self.dialog.notification(heading='Зеркала',message='Применяем новый адрес:\n[COLOR=blue]{}[/COLOR]'.format(actual_url),icon=self.icon,time=3000,sound=False)
        except:
            actual_url = site_url
            self.dialog.notification(heading='Зеркала',message='Применяем базовый адрес:\n[COLOR=blue]{}[/COLOR]'.format(actual_url),icon=self.icon,time=3000,sound=False)

        self.addon.setSetting(current_mirror, actual_url)
#========================#========================#========================#
    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&skin=new36'.format(self.site_url, self.params['id'], self.params['node'])

        if 'plus' in self.params['node']:
            try:
                data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
                self.dialog.notification(heading='Избранное',message='Выполнено',icon=self.icon,time=3000,sound=False)
            except:
                self.dialog.notification(heading='Избранное',message='Ошибка',icon=self.icon,time=3000,sound=False)

        if 'minus' in self.params['node']:
            try:
                data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
                self.dialog.notification(heading='Избранное',message='Выполнено',icon=self.icon,time=3000,sound=False)
            except:
                self.dialog.notification(heading='Избранное',message='Ошибка',icon=self.icon,time=3000,sound=False)
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
        data = u'[B][COLOR=darkorange]AniStar[/COLOR][/B]\n\
    - Суб плагин переведен на библиотеку requests\n\
    - Общая оптимизация, правки\n\
    - Отлючен игнор лист - т.е. вся реклама теперь видна'
        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        if self.authorization:
            self.create_line(title=u'[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title=u'[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title=u'[B][COLOR=lime]Расписание[/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title=u'[B][COLOR=lime]Новинки[/COLOR][/B]', params={'mode': 'common_part', 'param': 'new/'})
        self.create_line(title=u'[B][COLOR=lime]RPG[/COLOR][/B]', params={'mode': 'common_part', 'param': 'rpg/'})
        self.create_line(title=u'[B][COLOR=lime]Скоро[/COLOR][/B]', params={'mode': 'common_part', 'param': 'next/'})        

        if self.adult:
            self.create_line(title=u'[B][COLOR=lime]Хентай[/COLOR][/B]', params={'mode': 'common_part', 'param': 'hentai/'})
            
        self.create_line(title=u'[B][COLOR=gold]Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorams/'})
        self.create_line(title=u'[B][COLOR=blue]Мультфильмы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'cartoons/'})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})
            self.create_line(title=u'[B]Поиск по жанрам[/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title=u'[B]Поиск по году[/B]', params={'mode': 'search_part', 'param': 'years'})

            data_array = self.addon.getSetting('anistar_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue               
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': data})

        if 'genres' in self.params['param']:
            from info import anistar_genres

            for i in anistar_genres:
                self.create_line(title=i[1], params={'mode': 'common_part', 'param': 'genres', 'node': i[0]})
                
        if 'years' in self.params['param']:
            from info import anistar_years

            for i in anistar_years:
                self.create_line(title=i, params={'mode': 'common_part','param':'years', 'node': i})
                
        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()                                    
                data_array = self.addon.getSetting('anistar_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)
                self.params['param'] = 'search_string'
            else:
                return False
        
        if 'search_string' in self.params['param']:
            from info import anistar_ignor_list
            
            if self.params['search_string'] == '':
                return False
            
            try:
                search_string = self.params['search_string'].encode('cp1251')
            except:
                search_string = self.params['search_string']
            
            url = self.site_url
            
            post_data = {
                "do": "search",
                "subaction": "search",
                "story": search_string,
                "search_start": self.params['page'],
                "full_search": "1",
                #"result_from": result,
                "catlist[]": ["175","39","113","76"]
                }
            
            data_request = session.post(url=url, proxies=self.proxy_data, data=post_data, headers=headers)

            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            html = data_request.text
            html = unescape(html)

            try:
                html = html.decode(encoding='utf-8', errors='replace')
            except:
                pass
            
            data_array = html[html.find('title_left">')+12:html.rfind('<div class="panel-bottom-shor">')]
            data_array = data_array.split('<div class="title_left">')
            data_array.pop(0)
            
            if len(data_array) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
            
            i = 0

            for data in data_array:

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                if u'/m/">Манга</a>' in data:
                    continue
                
                if u'>Хентай</a>' in data:
                    if self.adult:
                        pass
                    else:
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
                    if inf == 999:
                        continue

                label = self.create_title(self.database.get_title(anime_id), series)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

            self.progress_bg.close()
            
            if 'button_nav r"><a' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'search_string': self.params['search_string'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        url = '{}{}'.format(self.site_url, 'raspisanie-vyhoda-seriy-ongoingov.html')
        
        data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        html = data_request.text
        html = unescape(html)

        try:
            html = html.decode(encoding='utf-8', errors='replace')
        except:
            pass

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

        if 'genre' in self.params['param']:
            url = '{}anime/{}/page/{}/'.format(self.site_url, self.params['node'],self.params['page'])
            
        if 'years' in self.params['param']:
            url = '{}index.php?cstart={}&do=xfsearch&type=year&r=anime&xf={}'.format(
                self.site_url, self.params['page'], self.params['node']
                )
            
        data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        html = data_request.text
        html = unescape(html)

        try:
            html = html.decode(encoding='utf-8', errors='replace')
        except:
            pass
        
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
            #data = unescape(data)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if u'/m/">Манга</a>' in data:
                continue

            if u'>Хентай</a>' in data:
                if self.adult:
                    pass
                else:
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
                if inf == 999:
                    continue
                
            label = self.create_title(self.database.get_title(anime_id), series)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        self.progress_bg.close()

        if 'button_nav r"><a' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'node':self.params['node'], 'page': (int(self.params['page']) + 1)})

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
            
            data_request = session.get(url=video_url, proxies=self.proxy_data, headers=headers)

            html = data_request.text
            html = unescape(html)

            try:
                html = html.decode(encoding='utf-8', errors='replace')
            except:
                pass

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
            url = '{}index.php?newsid={}'.format(self.site_url, self.params['id'])
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            html = data_request.text
            html = unescape(html)
            
            try:
                html = html.decode(encoding='utf-8', errors='replace')
            except:
                pass
            
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
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)

            file_name = 'torrent.torrent'
            
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
                    self.create_line(title=series[i], params={'mode': 'selector_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], folder=False, size=info['length'])

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