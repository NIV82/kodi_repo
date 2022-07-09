# -*- coding: utf-8 -*-

import os
import sys
import time
import base64

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import requests

if sys.version_info.major > 2:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape  

from utility import clean_tags
from utility import data_encode
from utility import data_decode

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity'
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Anidub:
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()
        
        self.session = requests.Session()

        self.params = params
        self.addon = addon
        self.icon = icon

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        if 'true' in self.addon.getSetting('anidub_unblock'):
            self.addon.setSetting('anidub_torrents','1')
        
        self.proxy_data = self.exec_proxy_data()
        self.site_url = self.create_site_url()
        self.sid_file = os.path.join(self.cookie_dir, 'anidub.sid')
        self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_anidub.db')):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_anidub.db'))
        del DataBase
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
        splitter = '/'

        title = clean_tags(title, '<', '>')        
        title = unescape(title)

        if '[' in title:
            info['series'] = title[title.rfind('[')+1:title.rfind(']')].strip()
            title = title[:title.rfind('[')]
        
        if u'Сасами-сан на Лень.com' in title:
            title = u'Сасами-сан на Лень.com / Sasami-san@Ganbaranai'
        if u'Идолм@стер' in title:
            title = u'Идолм@стер / Idolm@ster'
            
        rep_list = [
                ('|', '/'),('\\', '/'),('Reward / EEA','Reward - EEA'),('Inuyasha: Kagami','/ Inuyasha: Kagami'),
                (u'Сила Тысячи /',u'Сила Тысячи -'),(u'Судьба/',u'Судьба-'),('Fate/','Fate-'),
                (u'Начало/Загрузка/ ',u'Начало-Загрузка-'),('/Start/Load/End',': Start-Load-End')]
            
        for value in rep_list:
            title = title.replace(value[0], value[1])

        if '.hack' in title or 'Z/X' in title:
            splitter = ' / '

        data = title.split(splitter, 1)

        try:
            info['title_ru'] = data[0].capitalize().strip()
            info['title_en'] = data[1].capitalize().strip()
        except:
            pass

        return info
#========================#========================#========================#
    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        year = self.database.get_year(anime_id)
        
        year = '[COLOR=blue]{}[/COLOR] | '.format(year) if year else ''
        series = u' | [COLOR=gold]{}[/COLOR]'.format(series.strip()) if series else ''
        
        if '0' in self.addon.getSetting('anidub_titles'):
            label = u'{}{}{}'.format(year, title[0], series)
        if '1' in self.addon.getSetting('anidub_titles'):
            label = u'{}{}{}'.format(year, title[1], series)
        if '2' in self.addon.getSetting('anidub_titles'):
            label = u'{}{} / {}{}'.format(year, title[0], title[1], series)
            
        if 'anime_id:' in label:
            label = u'[COLOR=red]ERROR[/COLOR] | Ошибка 403-404 | [COLOR=gold]{}[/COLOR]'.format(
                title[0].replace('anime_id: ',''))
            
        return label
#========================#========================#========================#
    def create_image(self, url, anime_id):
        if not 'https://' in url:
            url = '{}{}'.format(self.site_url, url.replace('/','',1))

        if '0' in self.addon.getSetting('anidub_covers'):
            return url
        else:
            local_img = 'anidub_{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                try:                    
                    data_request = self.session.get(url=url, proxies=self.proxy_data)
                    with open(file_name, 'wb') as write_file:
                        write_file.write(data_request.content)
                    return file_name
                except:
                    return url
#========================#========================#========================#
    def create_image_set(self, target_path):
        try:
            self.progress_bg.create(u'Распаковка...')
                
            import zipfile
                
            i = 0
                
            with zipfile.ZipFile(target_path, mode="r") as archive:
                archive_len = len(archive.namelist())

                for filename in archive.namelist():
                    archive.extract(filename, self.images_dir)

                    i = i + 1
                    percent = int((float(i) / archive_len) * 100)
                    
                    self.progress_bg.update(percent, u'Распаковано: {} из {}'.format(i, archive_len))

            self.progress_bg.close()
            self.dialog.notification(heading=u'Распаковка',message=u'Успешно завершена',icon=self.icon,time=3000,sound=False)
                
            try: os.remove(target_path)
            except: pass
        
        except:
            self.dialog.notification(heading=u'Распаковка',message=u'Ошибка при распаковке',icon=self.icon,time=3000,sound=False)
            pass
        return
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []        
        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anidub")'))
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('Обновить аниме', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anidub")'.format(anime_id)))

        if self.authorization:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anidub")'.format(anime_id)))
                context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anidub")'.format(anime_id)))

        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=anidub")'))
        context_menu.append(('[COLOR=darkorange]Загрузить Обложки[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&param=cover_set&portal=anidub")'))
        context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=update&portal=anidub")'))
        context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=anidub")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, rating=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(cover, anime_id)
            
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
    def create_info(self, anime_id, update=False):
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        data_request = self.session.get(url=url, proxies=self.proxy_data)

        if not data_request.status_code == requests.codes.ok:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru='anime_id: {}'.format(anime_id),
                title_en='anime_id: {}'.format(anime_id)
                )
            return

        html = data_request.text

        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'released_on', 'genres', 'director', 'writer', 'description', 'dubbing',
                        'translation', 'timing', 'country', 'studios', 'image', 'year'], '')

        info['image'] = html[html.find('data-src="')+10:]
        info['image'] = info['image'][:info['image'].find('"')]

        title_data = html[html.find('<h1>')+4:html.find('</h1>')]
        info.update(self.create_title_info(title_data))

        info['description'] = html[html.find(u'Описание</div>')+14:html.find(u'Рейтинг:</div>')]
        info['description'] = clean_tags(info['description'])
        info['description'] = unescape(info['description'])
        info['description'] = info['description'].replace('\t','')

        if 'xfsearch/year/' in html:
            anidata = html[html.find('xfsearch/year/')+14:html.rfind('<span><a href="')]
            info['aired_on'] = anidata[:anidata.find('/')].strip()
            info['aired_on'] = info['aired_on'][0:4]
            if '<span>' in anidata:
                info['country'] = anidata[anidata.find('<span>')+6:anidata.rfind('</span>')].strip()
            del anidata

        if not info['country']:
            country = (u'<span>Великобритания</span>', u'<span>Китай</span>', u'<span>Нидерланды</span>', u'<span>США</span>',
                       u'<span>Таиланд</span>', u'<span>Франция</span>', u'<span>Южная Корея</span>', u'<span>Япония</span>')
            for x in country:
                if x in html:
                    info['country'] = x[x.find('<span>')+6:x.find('</span>')].strip()

        data_array = html[html.find('<ul class="flist">'):html.find('<div class="fright-title">')]
        data_array = data_array.splitlines()

        for data in data_array:
            data = unescape(data)
            if u'Начало показа:</span>' in data:
                if not info['aired_on']:
                    for i in range(1960, 2030, 1):
                        if str(i) in data:
                            info['aired_on'] = str(i)
            if u'Жанр:</span>' in data:
                info['genres'] = clean_tags(data[data.find('</span>'):])        
            if u'Автор оригинала:</span>' in data:
                info['writer'] = clean_tags(data[data.find('</span>'):])
            if u'Режиссер:</span>' in data:
                info['director'] = clean_tags(data[data.find('</span>'):])
            if u'Перевод:</span>' in data:
                info['translation'] = clean_tags(data[data.find('</span>'):])
            if u'Студия:</span>' in data:
                info['studios'] = clean_tags(data[data.find('</span>'):])
            if u'Озвучивание:</span>' in data:
                info['dubbing'] = clean_tags(data[data.find('</span>'):])
            if u'Тайминг:</span>' in data:
                info['timing'] = clean_tags(data[data.find('</span>'):])
        
        try:
            self.database.add_anime(
                anime_id = anime_id,
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
                image = info['image'],
                update = update)
        except:
            self.dialog.notification(heading='Инфо-Парсер',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
    
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
            self.addon.setSetting('anidub_proxy','')
            self.addon.setSetting('anidub_proxy_time','')

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
        if '0' in self.addon.getSetting('anidub_auth_mode'):
            return False

        if not self.addon.getSetting('anidub_username') or not self.addon.getSetting('anidub_password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
            return

        if 'update' in self.params['param']:
            self.addon.setSetting('anidub_auth', 'false')
            self.addon.setSetting('anidub_session','')
            
        try: session = float(self.addon.getSetting('anidub_session'))
        except: session = 0
        
        if time.time() - session > 43200:
            self.addon.setSetting('anidub_session', str(time.time()))            
            try: os.remove(self.sid_file)
            except: pass            
            self.addon.setSetting('anidub_auth', 'false')

        auth_post_data = {
            "login_name": self.addon.getSetting('anidub_username'),
            "login_password": self.addon.getSetting('anidub_password'),
            "login": "submit"
            }

        import pickle

        if 'true' in self.addon.getSetting('anidub_auth'):
            try:
                with open(self.sid_file, 'rb') as read_file:
                    self.session.cookies.update(pickle.load(read_file))                    
                auth = True if 'dle_user_id' in str(self.session.cookies) else False
            except:
                self.session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data)
                auth = True if 'dle_user_id' in str(self.session.cookies) else False
                with open(self.sid_file, 'wb') as write_file:
                    pickle.dump(self.session.cookies, write_file)
        else:
            self.session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data)
            auth = True if 'dle_user_id' in str(self.session.cookies) else False
            with open(self.sid_file, 'wb') as write_file:
                pickle.dump(self.session.cookies, write_file)

        if not auth:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
            return
        else:
            self.addon.setSetting('anidub_auth', str(auth).lower())

        return auth
#========================#========================#========================#
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_file_part(self):
        if 'cover_set' in self.params['param']:
            target_url = 'http://getfile.dokpub.com/yandex/get/https://disk.yandex.ru/d/sbeL3-5VPwVs2g'
            target_path = os.path.join(self.images_dir, 'anidub_set.zip')
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
    def exec_favorites_part(self):        
        if not self.params['node']:
            url = '{}mylists/page/{}/'.format(self.site_url, self.params['page'])
            data_request = self.session.get(url=url, proxies=self.proxy_data)
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='ERROR PAGE', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not '<div class="animelist">' in html:
                self.create_line(title='Контент не обнаружен', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('{}'.format(self.params['portal'].upper()), u'Инициализация')
            
            navigation = html[html.find('<div class="navigation">'):html.find('<div class="animelist">')]
            navigation = clean_tags(navigation, '<', '>').replace(' ','|')
            page = int(navigation[navigation.rfind('|')+1:]) if navigation else -1
            
            data_array = html[html.find('<div class="animelist">')+23:html.rfind('<label for="mlist">')]
            data_array = data_array.split('<div class="animelist">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                url = data[data.find('href="')+6:]
                url = url[:url.find('.html')]
                anime_id = url[url.rfind('/')+1:url.find('-')]

                cover = self.database.get_cover(anime_id)
                
                series = data[data.rfind('class="upd-title">')+18:]
                series = series[:series.find('</a>')]
                series = series[series.find('[')+1:series.find(']')]

                self.progress_bg.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)
                    
                label = self.create_title(anime_id, series)
                anime_code = data_encode('{}|{}'.format(anime_id, cover))

                self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part', 'id': anime_code})
            self.progress_bg.close()

            if page and int(self.params['page']) < page:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'plus' in self.params['node']:
            try:
                url = '{}mylists/'.format(self.site_url)
                post = {'news_id': self.params['id'], 'status_id': 3}
                self.session.post(url=url, data=post)
                xbmc.executebuiltin("Container.Refresh()")
                self.dialog.notification(heading='Избранное',message='УСПЕШНО ДОБАВЛЕНО',icon=self.icon,time=5000,sound=False)
            except:
                self.dialog.notification(heading='Избранное',message='ОШИБКА',icon=self.icon,time=5000,sound=False)

        if 'minus' in self.params['node']:
            try:
                url = '{}mylists/'.format(self.site_url)
                post = {'news_id': self.params['id'], 'status_id': 0}
                self.session.post(url=url, data=post)
                xbmc.executebuiltin("Container.Refresh()")
                self.dialog.notification(heading='Избранное',message='УСПЕШНО УДАЛЕНО',icon=self.icon,time=5000,sound=False)
            except:
                self.dialog.notification(heading='Избранное',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('anidub_search', '')
            self.dialog.notification(heading='Поиск',message='УСПЕШНО УДАЛЕНО',icon=self.icon,time=5000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
            pass
#========================#========================#========================#
    def exec_information_part(self):
        data = u'[B][COLOR=darkorange]Version 0.9.83[/COLOR][/B]\n\
    - Мелкие исправления, оптимизация в разделе Избранное\n\
    - Добавлена возможность скачать сразу все обложки\n\
    \n[B][COLOR=darkorange]Version 0.9.82[/COLOR][/B]\n\
    - Перевод плагина на библиотеку requests\n\
    - Добавлена разблокировка (пока только онлайн режим)\n\
    - Мелкие исправления в системе поиска по годам и жанрам\n\
    - Торрент файлы сохраняются с оригинальным названием\n\
    - Движки ТАМ приведены в актуальное состояние (в настройках)\n\
    - Клиентская часть Торрсерва основана на module.torrserver (3.3)\n\
    - Правки, исправления, оптимизация\n\
    \n[B][COLOR=blue]Ожидается:[/COLOR][/B]\n\
    - Мелкие исправления, оптимизация\n'
        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        if self.authorization:
            self.create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title='[B][COLOR=lime]Аниме[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/'})
        self.create_line(title='[B][COLOR=lime]Онгоинги[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/anime_ongoing/'})
        self.create_line(title='[B][COLOR=lime]Вышедшие сериалы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/full/'})
        self.create_line(title='[B][COLOR=blue]Аниме фильмы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title='[B][COLOR=blue]Аниме OVA[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title='[B][COLOR=gold]Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})
            self.create_line(title='[B]Поиск по жанрам[/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B]Поиск по году[/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title='[B]Поиск по алфавиту[/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = self.addon.getSetting('anidub_search').split('|')
            data_array.reverse()

            for data in data_array:
                if not data:
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': data})

        if 'genres' in self.params['param']:
            from info import anidub_genres
            for i in anidub_genres:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/genre/{}/'.format(i)})

        if 'years' in self.params['param']:
            from info import anidub_years
            for i in anidub_years:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/year/{}/'.format(i)})

        if 'alphabet' in self.params['param']:
            from info import anidub_alphabet            
            for i in anidub_alphabet:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(i)})

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
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
            
            url = '{}index.php?do=search'.format(self.site_url)            
            post = {"do": "search","subaction": "search","search_start": self.params['page'],"full_search": "0","story": self.params['search_string']}

            data_request = self.session.get(url=url, data=post, proxies=self.proxy_data)

            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not '<div class="th-item">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('ANIDUB', 'Инициализация')
            
            navigation = html[html.rfind('<div class="navigation">'):html.rfind('<footer class="footer sect-bg">')]
            navigation = clean_tags(navigation, '<', '>').replace(' ','|')
            page = int(navigation[navigation.rfind('|')+1:]) if navigation else False
        
            data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
            data_array = data_array.split('<div class="th-item">')
            
            i = 0
            
            for data in data_array:
                anime_url = data[data.find('th-in" href="')+13:data.find('.html">')]

                if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                    continue

                anime_cover = data[data.find('data-src="')+10:data.find('" title="')]
                anime_cover = unescape(anime_cover)
                anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
                anime_title = data[data.find('<div class="fx-1">')+18:]
                anime_title = anime_title[:anime_title.find('</div>')]
                anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')] if '[' in anime_title else ''
                anime_rating = data[data.find('th-rating">')+11:]
                anime_rating = anime_rating[:anime_rating.find('</div>')]
    
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id, anime_series)            
                anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))
            
                self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})
            self.progress_bg.close()
            
            if page and int(self.params['page']) < page:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': 'search_part', 'param': 'search_string', 'search_string': self.params['search_string'], 'page': int(self.params['page']) + 1})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        # p =  {
        #     'http': 'http://proxy-nossl.antizapret.prostovpn.org:29976',
        #     #'https': 'https://proxy-ssl.antizapret.prostovpn.org:3143'
        #     }

        url = '{}{}page/{}/'.format(self.site_url, quote(self.params['param']), self.params['page'])
        #url = url.replace('https','http')
        data_request = self.session.get(url=url, proxies=self.proxy_data)
        #data_request = self.session.get(url=url, proxies=p)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        html = data_request.text
        
        if not '<div class="th-item">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
        
        navigation = html[html.rfind('<div class="navigation">'):html.rfind('<footer class="footer sect-bg">')]
        navigation = clean_tags(navigation, '<', '>').replace(' ','|')
        page = int(navigation[navigation.rfind('|')+1:]) if navigation else False

        data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
        data_array = data_array.split('<div class="th-item">')

        i = 0

        for data in data_array:
            anime_url = data[data.find('th-in" href="')+13:data.find('.html">')]

            if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                continue

            anime_cover = data[data.find('data-src="')+10:data.find('" title="')]
            anime_cover = unescape(anime_cover)
            anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
            anime_title = data[data.find('<div class="fx-1">')+18:]
            anime_title = anime_title[:anime_title.find('</div>')]
            anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')] if '[' in anime_title else ''
            anime_rating = data[data.find('th-rating">')+11:]
            anime_rating = anime_rating[:anime_rating.find('</div>')]
            
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id, anime_series)            
            anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))

            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})
        self.progress_bg.close()
        
        if page and int(self.params['page']) < page:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        anime_code = data_decode(self.params['id'])
        anime_tid = None
        
        url = '{}index.php?newsid={}'.format(self.site_url, anime_code[0])
        data_request = self.session.get(url=url, proxies=self.proxy_data)
        html = data_request.text

        if u'Ссылка на трекер:</span>' in html:
            anime_tid = html[html.find(u'Ссылка на трекер:</span>'):html.find(u'<div>Скачать с трекера')]
            anime_tid = anime_tid[anime_tid.find('href=\'')+6:anime_tid.find('.html')+5]

        if anime_tid:
            if '0' in self.addon.getSetting('anidub_torrents'):
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'true')
                self.proxy_data = self.exec_proxy_data()
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'false')

            try:
                torrent_request = requests.get(url=anime_tid, proxies=self.proxy_data)
                torrent_html = torrent_request.text                
                result = self.dialog.yesno(
                    'Обнаружена торрент ссылка:',
                    'Смотреть через [COLOR=blue]Торрент[/COLOR] или [COLOR=lime]Онлайн[/COLOR] ?\n======\nАвтовыбор - [COLOR=lime]Онлайн[/COLOR], 5 секунд',
                    yeslabel='Торрент', nolabel ='Онлайн', autoclose=5000)
                
                self.exec_torrent_part(torrent_html) if result else self.exec_online_part(html)
            except:
                self.dialog.notification(heading='Торрент-файлы',message='Требуется разблокировка',icon=self.icon,time=5000,sound=False)
                self.exec_online_part(html)
        else:
            self.exec_online_part(html)
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self, torrent_data=None):
        anime_code = data_decode(self.params['id'])
        
        if torrent_data:
            html = torrent_data
            
            data_array = html[html.find('<div class="torrent_c">')+23:html.rfind(u'Управление')]
            data_array = data_array.split(u'Управление')

            qa = []
            la = []
                                    
            for data in data_array:
                data = data[data.find('<div id="'):]
                                        
                torrent_id = data[data.find('torrent_')+8:data.find('_info')]

                if '<div id="' in data:
                    quality = data[data.find('="')+2:data.find('"><')]
                    qa.append(quality)

                if '<div id=\'torrent_' in data:
                    quality = qa[len(qa) - 1]
                    if u'Серии в торренте:' in data:
                        series = data[data.find(u'Серии в торренте:')+17:data.find(u'Раздают')]
                        series = clean_tags(series, '<', '>')

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

                self.create_line(title=label, params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id']} )

        else:
            if '0' in self.addon.getSetting('anidub_torrents'):
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'true')
                self.proxy_data = self.exec_proxy_data()
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'false')
                
            url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['param'])
            data_request = self.session.get(url=url, proxies=self.proxy_data)

            file_name = data_request.headers['content-disposition']
            file_name = file_name[file_name.find('filename=')+9:]
            file_name = file_name.replace('"','').replace(',','')
            
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
                    self.create_line(title=series[i], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'selector_part', 'index': i, 'id': file_name}, folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self, online_data=None):
        anime_code = data_decode(self.params['id'])

        if online_data:
            html = online_data

            data_array = html[html.rfind('<div class="fthree tabs-box">')+29:html.rfind('</span></div></div>')]
            data_array = data_array.split('</span>')

            for data in data_array:
                data = data[data.find('?videoid=')+9:]
                video_url = data[:data.find('"')]
                
                if '&quot;' in video_url:
                    video_url = video_url[:video_url.find('&quot;')]

                video_title = data[data.find('>')+1:]

                self.create_line(title=video_title, params={'mode': 'online_part', 'param': video_url, 'id': self.params['id']})

        if self.params['param']:
            anime_code = data_decode(self.params['id'])
            
            url = 'https://video.sibnet.ru/shell.php?videoid={}'.format(self.params['param'])

            #data_request = self.session.get(url=url, proxies=self.proxy_data)
            data_request = requests.get(url=url)
            html = data_request.text

            if 'player.src' in html:
                video_src = html[html.find('player.src([{src: "')+19:html.find(';player.persistvolume')]
                video_src = video_src[:video_src.find('"')]

                play_url = 'https://video.sibnet.ru{}|referer={}'.format(video_src, url)

                label = 'Смотреть'

            if 'class=videostatus><p>' in html:
                status = html[html.find('class=videostatus><p>')+21:html.find('</p></div><script')]
                label = '[COLOR=red][B][ {} ][/B][/COLOR]'.format(status.replace('.',''))
                play_url = ''

            self.create_line(title=label, params={}, cover=anime_code[1], anime_id=anime_code[0], online=play_url, folder=False)

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