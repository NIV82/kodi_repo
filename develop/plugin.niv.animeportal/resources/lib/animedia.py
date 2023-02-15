# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

if sys.version_info.major > 2:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

import requests
session = requests.Session()

from utility import clean_tags
from utility import data_encode
from utility import data_decode
from utility import sha1

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity'
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Animedia:
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon = xbmcaddon.Addon(id='plugin.niv.animeportal')

        if sys.version_info.major > 2:
            self.addon_data_dir = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
            self.icon = xbmcvfs.translatePath(self.addon.getAddonInfo('icon'))
            self.fanart = xbmcvfs.translatePath(self.addon.getAddonInfo('fanart'))
        else:
            from utility import fs_enc
            self.addon_data_dir = fs_enc(xbmc.translatePath(self.addon.getAddonInfo('profile')))
            self.icon = fs_enc(xbmc.translatePath(self.addon.getAddonInfo('icon')))
            self.fanart = fs_enc(xbmc.translatePath(self.addon.getAddonInfo('fanart')))

        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.database_dir = os.path.join(self.addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.cookie_dir = os.path.join(self.addon_data_dir, 'cookie')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'portal': 'animedia'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        if 'true' in self.addon.getSetting('animedia_unblock'):
            self.addon.setSetting('animedia_torrents','1')
            
        self.proxy_data = self.exec_proxy_data()
        self.site_url = self.create_site_url()
        self.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))
        self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_animedia.db')):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        site_url = self.addon.getSetting('animedia_mirror_0')
        current_mirror = 'animedia_mirror_{}'.format(self.addon.getSetting('animedia_mirror_mode'))
        
        if not self.addon.getSetting(current_mirror):
            try:
                #self.exec_mirror_part()
                site_url = self.addon.getSetting(current_mirror)
            except:
                site_url = site_url
            
        else:
            site_url = self.addon.getSetting(current_mirror)
            
        return site_url
#========================#========================#========================#
    def create_title(self, anime_id, series=None):
        title = self.database.get_title(anime_id)
                
        series = u' | [COLOR=gold]{}[/COLOR]'.format(series.strip()) if series else ''
        
        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{} / {}{}'.format(title[0], title[1], series)
        
        if 'anime_id:' in label:
            label = u'[COLOR=red]ERROR[/COLOR] | Ошибка 403-404 | [COLOR=gold]{}[/COLOR]'.format(
                title[0].replace('anime_id: ',''))
            
        return label
#========================#========================#========================#
    def create_image(self, url, anime_id):
        if '0' in self.addon.getSetting('animedia_covers'):
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
    def create_context(self, anime_id):
        context_menu = []
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=animedia")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]','Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=animedia")'.format(anime_id)))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=animedia")'))
        
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=animedia")'))
        #context_menu.append(('[COLOR=darkorange]Загрузить Обложки[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&param=cover_set&portal=animedia")'))
        context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=update&portal=animedia")'))
        context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=animedia")'))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(cover, anime_id)

            li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
                       "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})
            
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

            duration = anime_info[6] * 60 if anime_info[6] else 0

            info = {
                'genre':anime_info[7],
                'country':anime_info[18],
                'year':anime_info[3],
                'episode':anime_info[2],
                'director':anime_info[9],
                'mpaa':anime_info[5],
                'plot':description,
                'title':title,
                'duration':duration,
                'studio':anime_info[19],
                'writer':anime_info[8],
                'tvshowtitle':title,
                'premiered':anime_info[3],
                'status':anime_info[1],
                'aired':anime_info[3]
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = 'animedia'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_title_info(self, data):
        try: data = data.decode('utf-8')
        except: pass

        data = data.split('/')
        title_ru = data[0].strip()
        title_en = data[1].strip()
        data = {'title_ru': title_ru, 'title_en': title_en}
        return data
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        url = '{}anime/{}'.format(self.site_url, quote(anime_id))

        data_request = session.get(url=url, proxies=self.proxy_data)
        
        if not data_request.status_code == requests.codes.ok:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru='anime_id: {}'.format(anime_id),
                title_en='anime_id: {}'.format(anime_id)
                )
            return

        html = data_request.text
        
        info = dict.fromkeys(['title_ru', 'title_en', 'genres', 'aired_on', 'studios', 'dubbing', 'description'], '')
        
        if u'Релиз озвучивали:' in html:
            dubbing = html[html.find(u'Релиз озвучивали:')+17:html.find(u'Новые серии')]
            info['dubbing'] = clean_tags(dubbing)

        data_array = html[html.find('class="media__post">')+20:html.find('</article>')]
        data_array = data_array.splitlines()

        for data in data_array:
            if 'post__title">' in data:
                info['title_ru'] = clean_tags(data.replace(u'смотреть онлайн', ''))
            if 'original-title">' in data:
                info['title_en'] = clean_tags(data)
            if '<p>' in data:
                info['description'] = u'{}\n{}'.format(info['description'], clean_tags(data).strip())
            if u'Дата выпуска:' in data:
                data = clean_tags(data)
                for year in range(1975, 2030, 1):
                    if str(year) in data:
                        info['aired_on'] = year
            if u'Жанр:' in data:
                info['genres'] = clean_tags(data[data.find(':')+1:].replace('</a><a',', <a'))
            if u'Студия:' in data:
                info['studios'] = clean_tags(data[data.find(':')+1:])

        try:
            self.database.add_anime(
                anime_id = quote(anime_id),
                title_ru = info['title_ru'],
                title_en = info['title_en'],
                dubbing = info['dubbing'],
                genres = info['genres'],
                studios = info['studios'],
                aired_on = info['aired_on'],
                description = info['description'],
                update=update
                )
        except:
            self.dialog.notification(heading='Инфо-Парсер',message='Ошибка',icon=self.icon,time=3000,sound=False)
            #return 101
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
        if '0' in self.addon.getSetting('{}_auth_mode'.format(self.params['portal'])):
            return False

        if not self.addon.getSetting('{}_username'.format(self.params['portal'])) or not self.addon.getSetting('{}_password'.format(self.params['portal'])):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
            return

        if 'update' in self.params['param']:
            self.addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
            self.addon.setSetting('{}_session'.format(self.params['portal']),'')
            
        try: temp_session = float(self.addon.getSetting('{}_session'.format(self.params['portal'])))
        except: temp_session = 0
        
        if time.time() - temp_session > 43200:
            self.addon.setSetting('{}_session'.format(self.params['portal']), str(time.time()))            
            try: os.remove(self.sid_file)
            except: pass            
            self.addon.setSetting('{}_auth'.format(self.params['portal']), 'false')

        auth_post_data = {
            'ACT': '14',
            'RET': '/',
            'site_id': '1',
            'username': self.addon.getSetting('animedia_username'),
            'password': self.addon.getSetting('animedia_password')
            }
        
        import pickle

        if 'true' in self.addon.getSetting('{}_auth'.format(self.params['portal'])):
            try:
                with open(self.sid_file, 'rb') as read_file:
                    session.cookies.update(pickle.load(read_file))
                auth = True if 'anime_sessionid' in str(session.cookies) else False
            except:
                session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data)
                auth = True if 'anime_sessionid' in str(session.cookies) else False
                with open(self.sid_file, 'wb') as write_file:
                    pickle.dump(session.cookies, write_file)
        else:
            try:
                session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data)
                auth = True if 'anime_sessionid' in str(session.cookies) else False
                with open(self.sid_file, 'wb') as write_file:
                    pickle.dump(session.cookies, write_file)
            except:
                auth = False

        if not auth:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
            return
        else:
            self.addon.setSetting('{}_auth'.format(self.params['portal']), str(auth).lower())

        return auth
#========================#========================#========================#
    def exec_update_anime_part(self):
        self.create_info(anime_id=self.params['id'], update=True)
#========================#========================#========================#
    # def exec_mirror_part(self):
    #     from network import WebTools
    #     self.net = WebTools()
    #     del WebTools

    #     mirror = self.net.get_animedia_actual(
    #         self.addon.getSetting('{}_mirror_0'.format(self.params['portal']))
    #         )

    #     self.addon.setSetting('{}_mirror_1'.format(self.params['portal']), 'https://{}/'.format(mirror))
    #     return
#========================#========================#========================#
    def exec_update_file_part(self):
        if 'cover_set' in self.params['param']:
            target_url = 'http://getfile.dokpub.com/yandex/get/https://disk.yandex.ru/d/sbeL3-5VPwVs2g'
            target_path = os.path.join(self.images_dir, 'animedia_set.zip')
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
            self.dialog.notification(heading='Загрузка файла',message='Успешно загружено',icon=self.icon,time=3000,sound=False)
            
            if 'cover_set' in self.params['param']:
                self.create_image_set(target_path)

        except:
            self.dialog.notification(heading='Загрузка файла',message='Ошибка при загрузке',icon=self.icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            self.dialog.notification(heading='Поиск',message='УСПЕШНО УДАЛЕНО',icon=self.icon,time=5000,sound=False)
        except:
            self.dialog.notification(heading='База Данных',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
            pass
#========================#========================#========================#
    def exec_information_part(self):
        data = u'[B][COLOR=darkorange]V-1.0.1[/COLOR][/B]\n\
    - Исправлены метки просмотренного в торрента файлах'
        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=yellow]Анонсы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'announcements'})
        self.create_line(title='[B][COLOR=lime]ТОП-100[/COLOR][/B]', params={'mode': 'common_part', 'param': 'top-100-anime'})
        self.create_line(title='[B][COLOR=lime]Популярное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'populyarnye-anime-nedeli'})
        self.create_line(title='[B][COLOR=lime]Новинки[/COLOR][/B]', params={'mode': 'common_part', 'param': 'novinki-anime'})
        self.create_line(title='[B][COLOR=lime]Завершенные[/COLOR][/B]', params={'mode': 'common_part', 'param': 'completed'})
        self.create_line(title='[B][COLOR=blue]Каталог[/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = self.addon.getSetting('animedia_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param':'search_string', 'search_string': data})

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)
                self.params['param'] = 'search_string'
            else:
                return False
        
        if 'search_string' in self.params['param']:
            if self.params['search_string'] == '':
                return False
            
            url = '{}ajax/search_result_search_page_2/P0?limit=12&keywords={}&orderby_sort=entry_date|desc'.format(
                self.site_url, quote(self.params['search_string'])
            )
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            html = data_request.text
            
            if not '<div class="ads-list__item">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            self.progress_bg.create('Animedia', u'Инициализация')
            
            data_array = html[html.find('<div class="ads-list__item">')+28:html.find('<div class="about-page">')]
            data_array = data_array.split('<div class="ads-list__item">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                anime_id = data[data.find('<a href="')+9:]
                anime_id = anime_id[:anime_id.find('"')]
                anime_id = anime_id[anime_id.rfind('/')+1:]

                try:        
                    anime_id = quote(anime_id.encode('utf-8'))
                except:
                    pass
                
                anime_cover = data[data.find('<img data-src="')+15:data.find('?h=')]

                torrent_url = data[data.find('tt.animedia.tv'):data.find(u'" title="Скачать')]
                if torrent_url:
                    torrent_url = 'https://{}'.format(torrent_url)

                anime_code = data_encode('{}|{}'.format(anime_id, torrent_url))

                self.progress_bg.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id)
                self.create_line(title=label, anime_id=anime_id, cover=anime_cover, params={'mode': 'select_part', 'id': anime_code})

            self.progress_bg.close()

            if u'Загрузить ещё' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        
#========================#========================#========================#
    def exec_common_part(self, url=None):
        url = '{}{}'.format(self.site_url, self.params['param'])

        if 'completed' in self.params['param']:
            page = (int(self.params['page']) - 1) * 25
            
            url = '{}ajax/search_result_search_page_2/P{}?limit=25&search:ongoing=1&orderby_sort=entry_date|desc'.format(
                self.site_url, page
            )

        data_request = session.get(url=url, proxies=self.proxy_data)

        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        html = data_request.text
        
        if not '<div class="ads-list__item">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('Animedia', u'Инициализация')
        
        data_array = html[html.find('<div class="ads-list__item">')+28:html.find('<div class="about-page">')]
        data_array = data_array.split('<div class="ads-list__item">')

        i = 0

        for data in data_array:
            #data = unescape(data)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)
            
            anime_id = data[data.find('<a href="')+9:]
            anime_id = anime_id[:anime_id.find('"')]
            anime_id = anime_id[anime_id.rfind('/')+1:]

            try:        
                anime_id = quote(anime_id.encode('utf-8'))
            except:
                pass
            
            anime_cover = data[data.find('<img data-src="')+15:data.find('?h=')]

            torrent_url = data[data.find('tt.animedia.tv'):data.find(u'" title="Скачать')]
            if torrent_url:
                torrent_url = 'https://{}'.format(torrent_url)

            anime_code = data_encode('{}|{}'.format(anime_id, torrent_url))

            self.progress_bg.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id)
            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, params={'mode': 'select_part', 'id': anime_code})

        self.progress_bg.close()

        if u'Загрузить ещё' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        from info import animedia_form, animedia_genre, animedia_voice, animedia_studio, animedia_year, animedia_status, animedia_sort

        if self.params['param'] == '':
            self.create_line(title='Форма выпуска: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_form')), params={'mode': 'catalog_part', 'param': 'form'})
            self.create_line(title='Жанр аниме: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Озвучивал: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_voice')), params={'mode': 'catalog_part', 'param': 'voice'})
            self.create_line(title='Студия: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_studio')), params={'mode': 'catalog_part', 'param': 'studio'})
            self.create_line(title='Год выпуска: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Статус раздачи: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='Сортировка по: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            
            self.create_line(title='[COLOR=yellow][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        
        if 'form' in self.params['param']:
            result = self.dialog.select('Выберите Тип:', tuple(animedia_form.keys()))
            self.addon.setSetting(id='animedia_form', value=tuple(animedia_form.keys())[result])

        if 'genre' in self.params['param']:
            result = self.dialog.select('Выберите Жанр:', tuple(animedia_genre.keys()))
            self.addon.setSetting(id='animedia_genre', value=tuple(animedia_genre.keys())[result])

        if 'voice' in self.params['param']:
            result = self.dialog.select('Выберите Войсера:', animedia_voice)
            self.addon.setSetting(id='animedia_voice', value=animedia_voice[result])

        if 'studio' in self.params['param']:
            result = self.dialog.select('Выберите Студию:', animedia_studio)
            self.addon.setSetting(id='animedia_studio', value=animedia_studio[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Выберите Год:', tuple(animedia_year.keys()))
            self.addon.setSetting(id='animedia_year', value=tuple(animedia_year.keys())[result])
        
        if 'status' in self.params['param']:
            result = self.dialog.select('Выберите статус:', tuple(animedia_status.keys()))
            self.addon.setSetting(id='animedia_status', value=tuple(animedia_status.keys())[result])
        
        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(animedia_sort.keys()))
            self.addon.setSetting(id='animedia_sort', value=tuple(animedia_sort.keys())[result])
        
        if 'catalog' in self.params['param']:
            page = (int(self.params['page']) - 1) * 25
            
            genre = '&category={}'.format(animedia_genre[self.addon.getSetting('animedia_genre')]) if animedia_genre[self.addon.getSetting('animedia_genre')] else ''
            voice = '&search:voiced={}'.format(quote(self.addon.getSetting('animedia_voice'))) if self.addon.getSetting('animedia_voice') else ''
            studio = '&search:studies={}'.format(quote(self.addon.getSetting('animedia_studio'))) if self.addon.getSetting('animedia_studio') else ''
            year = '&search:datetime={}'.format(animedia_year[self.addon.getSetting('animedia_year')]) if animedia_year[self.addon.getSetting('animedia_year')] else ''
            form = '&search:type={}'.format(quote(animedia_form[self.addon.getSetting('animedia_form')])) if animedia_form[self.addon.getSetting('animedia_form')] else ''
            status = animedia_status[self.addon.getSetting('animedia_status')] if animedia_status[self.addon.getSetting('animedia_status')] else ''
            sort = animedia_sort[self.addon.getSetting('animedia_sort')]

            url = '{}ajax/search_result_search_page_2/P{}?limit=25{}{}{}{}{}{}{}'.format(
                self.site_url, page, genre, voice, studio, year, form, status, sort)
            
            data_request = session.get(url=url, proxies=self.proxy_data)

            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not '<div class="ads-list__item">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('Animedia', u'Инициализация')
            
            data_array = html[html.find('<div class="ads-list__item">')+28:html.find('<div class="about-page">')]
            data_array = data_array.split('<div class="ads-list__item">')

            i = 0

            for data in data_array:
                #data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                anime_id = data[data.find('<a href="')+9:]
                anime_id = anime_id[:anime_id.find('"')]
                anime_id = anime_id[anime_id.rfind('/')+1:]

                try:        
                    anime_id = quote(anime_id.encode('utf-8'))
                except:
                    pass
                
                anime_cover = data[data.find('<img data-src="')+15:data.find('?h=')]

                torrent_url = data[data.find('tt.animedia.tv'):data.find(u'" title="Скачать')]
                if torrent_url:
                    torrent_url = 'https://{}'.format(torrent_url)

                anime_code = data_encode('{}|{}'.format(anime_id, torrent_url))

                self.progress_bg.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id)
                self.create_line(title=label, anime_id=anime_id, cover=anime_cover, params={'mode': 'select_part', 'id': anime_code})

            self.progress_bg.close()

            if u'Загрузить ещё' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        anime_code = data_decode(self.params['id'])
        self.create_line(title=u'[B]Онлайн просмотр[/B]', params={'mode': 'online_part', 'id': anime_code[0]})
        if anime_code[1]:
            self.create_line(title=u'[B]Торрент просмотр[/B]', params={'mode': 'torrent_part', 'id': self.params['id']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        url = '{}anime/{}'.format(self.site_url, self.params['id'])

        data_request = session.get(url=url, proxies=self.proxy_data)
            
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        html = data_request.text
        
        if not 'data-entry_id=' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        data_entry = html[html.find('data-entry_id="')+15:html.find('<li class="media__tabs__nav__item')]
        data_entry = data_entry[:data_entry.find('">')]

        data_array = html[html.find('<a href="#tab'):html.find('<div class="media__tabs__content')]
        data_array = data_array.strip()
        data_array = data_array.split('<li class="media__tabs__nav__item">')

        for data in data_array:
            tab_num = data[data.find('"#tab')+5:data.find('" role')]
            tab_name = data[data.find('"tab">')+6:data.find('</a></li>')]

            self.create_line(title=u'[B]{}[/B]'.format(tab_name), params={})
                
            url = '{}/embeds/playlist-j.txt/{}/{}'.format(self.site_url, data_entry, int(tab_num)+1)

            data_request = session.get(url=url, proxies=self.proxy_data)
            html = data_request.text
            
            data_array = html.split('},')

            for data in data_array:
                series_title = data[data.find('title":"')+8:data.find('","file')]
                    
                series_file = data[data.find('file":"')+7:data.find('","poster')]
                if not 'https:' in series_file:
                    series_file = 'https:{}'.format(series_file)
                    
                series_poster = data[data.find('poster":"')+9:data.find('","id"')]
                series_poster = 'https:{}'.format(series_poster)

                series_id = data[data.find('id":"')+5:data.rfind('"')]
                series_id = series_id.replace('s', '').split('e')
                series_id = '[COLOR=blue]SE{:>02}[/COLOR][COLOR=lime]EP{:>02}[/COLOR]'.format(series_id[0],series_id[1])
                    
                label = u'{} | [B]{}[/B]'.format(series_id, series_title)                    
                    
                self.create_line(title=label, cover=series_poster, anime_id=self.params['id'], params={}, online=series_file, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_torrent_part(self):
        
        if '0' in self.addon.getSetting('animedia_torrents'):
            self.addon.setSetting('animedia_unblock', 'true')
            self.proxy_data = self.exec_proxy_data()
            self.addon.setSetting('animedia_unblock', 'false')
                
        if not self.params['param']:
            anime_code = data_decode(self.params['id'])
            
            data_request = session.get(url=anime_code[1], proxies=self.proxy_data)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text

            cover = html[html.find('poster"><a href="')+17:html.find('" class="zoomLink')]

            if '<div class="media__tabs" id="down_load">' in html:
                tabs_nav = html[html.find('data-toggle="tab">')+18:html.find('<div class="media__tabs_')]
                tabs_nav = tabs_nav.split('data-toggle="tab">')

                tabs_content = html[html.find('<div class="tracker_info">')+26:html.rfind(u'Скачать торрент')]
                tabs_content = tabs_content.split('<div class="tracker_info">')

                for x, tabs in enumerate(tabs_nav):
                    title = tabs[:tabs.find('</a></li>')]

                    torrent_url = tabs_content[x][tabs_content[x].find('<a href="')+9:tabs_content[x].find('" class')]

                    content = tabs_content[x].splitlines()

                    for line in content:
                        if '<h3 class=' in line:
                            if title in line:
                                series = ''
                            else:
                                series = line[line.find('">')+2:line.find('</h3>')].replace(u'из XXX','')
                                series = series.replace(u'Серии','').replace(u'Серия','').strip()

                            quality = line[line.find('</h3>')+5:]
                            
                        if u'>Размер:' in line:
                            size = clean_tags(line[line.find('<span>'):])

                    size = u' | [COLOR=blue]{}[/COLOR]'.format(size)
                    series = u' | [COLOR=gold]{}[/COLOR]'.format(series) if series else ''
                    quality = u' | [COLOR=blue]{}[/COLOR]'.format(quality) if quality else ''

                    anime_code2 = data_encode('{}|{}'.format(anime_code[0], cover))
                    
                    label = u'{}{}{}{}'.format(title, quality, size, series)
                    
                    self.create_line(title=label, anime_id=anime_code[0], cover=cover, params={'mode': 'torrent_part', 'id': anime_code2, 'param': torrent_url})
            else:
                tabs_content = html[html.find('intup_left_top">')+16:html.rfind(u'Скачать</a>')]
                tabs_content = tabs_content.split('intup_left_top">')
                
                for content in tabs_content:
                    data = content[0:content.find('<p>')]
                    title = content[0:content.find('</span>')]

                    if ')' in data:
                        quality = data[data.find(')')+1:data.rfind('</span>')]
                        quality = u' | [COLOR=blue]{}[/COLOR]'.format(quality.strip())
                    else:
                        quality = ''
                        
                    size = content[content.find('left_op_in">')+12:content.find('</abbr>')]
                    size = u' | [COLOR=blue]{}[/COLOR]'.format(clean_tags(size))
                    
                    torrent_url = content[content.rfind('href="')+6:content.rfind('" class=')]
                    
                    anime_code2 = data_encode('{}|{}'.format(anime_code[0], cover))
                    
                    label = u'{}{}{}'.format(title, quality, size)

                    self.create_line(title=label, anime_id=anime_code[0], cover=cover, params={'mode': 'torrent_part', 'id': anime_code2, 'param': torrent_url})

        if self.params['param']:
            from utility import valid_media
            anime_code = data_decode(self.params['id'])
            url = self.params['param']

            data_request = session.get(url=url, proxies=self.proxy_data)

            file_name = sha1(
                '{}_{}'.format(self.params['portal'],anime_code[0])
                )
            
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
                                        
                    if not valid_media(x['path'][-1]):
                        continue
                    
                    size[i] = x['length']
                    series[i] = x['path'][-1]
                    
                for i in sorted(series, key=series.get):
                    self.create_line(title=series[i], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'selector_part', 'index': i, 'id': file_name}, folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, folder=False, size=info['length'])

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
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=5000,sound=False)

        if '1' in self.addon.getSetting(portal_engine):
            try:
                purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=5000,sound=False)

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
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=5000,sound=False)