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

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity'
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Anilibria:
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    #def __init__(self, addon_data_dir, params, addon, icon):
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
        
        if 'true' in self.addon.getSetting('anilibria_unblock'):
            self.addon.setSetting('anilibria_torrents','1')
        
        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'limit': '12', 'portal': 'anilibria'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = self.exec_proxy_data()
        self.site_url = self.create_site_url()
        self.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))

        self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        site_url = self.addon.getSetting('{}_mirror_0'.format(self.params['portal']))
        return site_url
#========================#========================#========================#
    def create_title(self, anime_id, series='', series_cur='', series_max='', announce=''):
        title = self.database.get_title(anime_id)
                        
        announce = u' | [COLOR=gold]{}[/COLOR]'.format(announce.strip()) if announce else ''
        
        if series_cur:
            if 'null' in series_cur:
                series_cur = 'XXX'
            series_cur = u' | [COLOR=gold]{}[/COLOR]'.format(series_cur)
            
        if series_max:
            if series_max == '0' or 'null' in series_max:
                series_max = u'XXX'            
            series_max = u'[COLOR=gold] из {}[/COLOR]'.format(series_max)
        
        series = u'{}{}'.format(series_cur, series_max)
        
        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}{}'.format(title[0], series, announce)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}{}'.format(title[1], series, announce)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{} / {}{}{}'.format(title[0], title[1], series, announce)
            
        if 'anime_id:' in label:
            label = u'[COLOR=red]ERROR[/COLOR] | Ошибка 403-404 | [COLOR=gold]{}[/COLOR]'.format(
                title[0].replace('anime_id: ',''))

        return label
#========================#========================#========================#
    def create_image(self, cover):
        anime_cover = 'https://static.anilibria.tv{}'.format(cover)
        return anime_cover
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal={}")'.format(self.params['portal'])))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal={}")'.format(anime_id, self.params['portal'])))

        if self.authorization:
            if self.params['mode'] in ('common_part','schedule_part','favorites_part'):
                context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=PUT&portal={}")'.format(anime_id, self.params['portal'])))
                context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=DELETE&portal={}")'.format(anime_id, self.params['portal'])))
            if 'catalog_part' in self.params['mode'] and 'catalog' in self.params['param'] or 'search_part' in self.params['mode'] and 'search_string' in self.params['param']:
                context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=PUT&portal={}")'.format(anime_id, self.params['portal'])))
                context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=DELETE&portal={}")'.format(anime_id, self.params['portal'])))
        
        context_menu.append((u'[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal={}")'.format(self.params['portal'])))
        context_menu.append((u'[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=renew_auth&portal=anilibria")'))
        context_menu.append((u'[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal={}")'.format(self.params['portal'])))
        
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(cover)

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
                'aired':anime_info[3],
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

            if '1' in self.addon.getSetting('anilibria_inputstream'):
                li.setProperty('inputstream', 'inputstream.adaptive')
                li.setProperty('inputstream.adaptive.manifest_type', 'hls')

        params['portal'] = self.params['portal']
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        from utility import fix_list
        
        url = 'https://api.anilibria.tv/v2/getTitle?id={}{}'.format(
            anime_id, '&filter=id,names,type.code,type.length,genres,team,season.year,description')

        data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)

        if not data_request.status_code == requests.codes.ok:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru='anime_id: {}'.format(anime_id),
                title_en='anime_id: {}'.format(anime_id)
                )
            return

        html = data_request.text
        html = unescape(html)

        anime_id = html[html.find(':')+1:html.find(',')]
        title_ru = html[html.find('ru":"')+5:html.find('","en')]
        title_en = html[html.find('en":"')+5:html.find('","alt')]
        kind = html[html.find('code":')+6:html.find(',"length')]
        length = html[html.find('length":')+8:html.find('},"genres')]
        genres = html[html.find('genres":[')+9:html.find('],"team')]
        voice = html[html.find('voice":[')+8:html.find('],"translator')]
        translator = html[html.find('translator":[')+13:html.find('],"editing')]
        editing = html[html.find('editing":[')+10:html.find('],"decor')]
        decor = html[html.find('decor":[')+8:html.find('],"timing')]
        timing = html[html.find('timing":[')+9:html.find(']},"season')]
        year = html[html.find('year":')+6:html.find('},"descrip')]

        description = html[html.find('description":')+13:]
        description = description[:description.find('}')]

        if '"' in description[0]:
            description = description[1:]
        if '"' in description[len(description)-1]:
            description = description[0:-1]
        if 'null' in description:
            description = ''
        description = fix_list(description)
        
        try: length = int(length)
        except: length = ''
        
        try:
            self.database.add_anime(
                anime_id = anime_id,
                title_ru = title_ru,
                title_en = title_en,
                kind = kind,
                duration = length,
                genres = genres.replace('"','').replace(',', ', '),
                dubbing = voice.replace('"','').replace(',', ', '),
                translation = translator.replace('"','').replace(',', ', '),
                editing = editing.replace('"','').replace(',', ', '),
                mastering = decor.replace('"','').replace(',', ', '),
                timing = timing.replace('"','').replace(',', ', '),
                aired_on = year,
                description = description,
                update=update
                )                    
        except:
            self.dialog.notification(heading='Инфо-Парсер',message='Ошибка',icon=self.icon,time=3000,sound=False)

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
            proxy_request = requests.get(url='https://antizapret.prostovpn.org:8443/proxy.pac', headers=headers)

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
                proxy_request = requests.get(url='https://antizapret.prostovpn.org:8443/proxy.pac', headers=headers)

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
            self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=3000,sound=False)
            return

        if 'renew_auth' in self.params['param']:
            data_print('update')
            self.addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
            self.addon.setSetting('{}_session'.format(self.params['portal']),'')
            self.addon.setSetting('{}_session_id'.format(self.params['portal']),'')
            
        try: temp_session = float(self.addon.getSetting('{}_session'.format(self.params['portal'])))
        except: temp_session = 0
        
        if time.time() - temp_session > 604800:
            self.addon.setSetting('{}_session'.format(self.params['portal']), str(time.time()))            
            try: os.remove(self.sid_file)
            except: pass            
            self.addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
        
        if 'true' in self.addon.getSetting('anilibria_auth'):
            data_print('111')
            return True
        else:
            data_print('222')
            auth_url = 'https://www.anilibria.tv/public/login.php'
        
            auth_post_data = {
                'mail': self.addon.getSetting('{}_username'.format(self.params['portal'])),
                'passwd': self.addon.getSetting('{}_password'.format(self.params['portal']))
            }
            
            try:
                r = requests.post(url=auth_url, proxies=self.proxy_data, data=auth_post_data)
            except:
                self.addon.setSetting('anilibria_unblock','true')
                self.proxy_data = self.exec_proxy_data()
                r = requests.post(url=auth_url, proxies=self.proxy_data, data=auth_post_data)
                self.addon.setSetting('anilibria_unblock','false')
            
            response = r.text
            
            if 'success' in response:
                auth = True
                sessionid = response[response.find('sessionId":"')+12:]
                sessionid = sessionid[:sessionid.find('"')]
                
                self.addon.setSetting('anilibria_session_id', sessionid)
            else:
                auth = False
    
            if not auth:
                self.params['mode'] = 'addon_setting'
                self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=3000,sound=False)
                return
            else:
                self.addon.setSetting('{}_auth'.format(self.params['portal']), str(auth).lower())

        return auth
#========================#========================#========================#
    def exec_update_anime_part(self):
        self.create_info(anime_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_file_part(self):
        if 'cover_set' in self.params['param']:
            target_url = 'http://getfile.dokpub.com/yandex/get/https://disk.yandex.ru/d/sbeL3-5VPwVs2g'
            target_path = os.path.join(self.images_dir, 'anilibria_set.zip')
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
        if not self.params['param']:
            session_id = self.addon.getSetting('anilibria_session_id')
            filters = '&filter=id,posters.medium,type,player.series.string'
            url = '{}/v2/getFavorites?session={}{}'.format(self.site_url, session_id, filters)

            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)

            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not '},{' in html:
                if not '}]' in html:
                    self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                    return
                
            self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
            
            data_array = html.split('},{')

            i = 0
            
            for data in data_array:
                anime_id = data[data.find(':')+1:data.find(',')]
                type_code = data[data.find('code":')+6:data.find(',"string')]
                series_max = data[data.find('series":')+8:data.find(',"length')]
                series_cur = data[data.rfind('string":"')+9:data.rfind('"}')]    
                poster = data[data.find('url":"')+6:data.find('","raw_base64')]

                if type_code == '0':
                    series_cur = u'Фильм'
                    series_max = ''
                    
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id=anime_id,series_cur=series_cur,series_max=series_max)
                self.create_line(title=label, anime_id=anime_id, cover=poster ,params={'mode': 'select_part', 'id': anime_id})

            self.progress_bg.close()

            if len(data_array) >= int(self.params['limit']):
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)        
        else:
            if 'PUT' in self.params['param']:
                url = '{}addFavorite?session={}&title_id={}'.format(
                    self.site_url, self.addon.getSetting('anilibria_session_id'), self.params['id'])
                data_request = session.put(url=url, proxies=self.proxy_data, headers=headers)

            if 'DELETE' in self.params['param']:
                url = '{}delFavorite?session={}&title_id={}'.format(
                    self.site_url, self.addon.getSetting('anilibria_session_id'), self.params['id'])
                data_request = session.delete(url=url, proxies=self.proxy_data, headers=headers)

            html = data_request.text
                
            if 'success":true' in html:
                self.dialog.notification(heading='Избранное',message='Выполнено',icon=self.icon,time=3000,sound=False)
            else:
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
        data = u'[B][COLOR=darkorange]V-1.0.1[/COLOR][/B]\n\
    - Исправлены метки просмотренного в торрента файлах'
        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        if self.authorization:
            self.create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white]Расписание[/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=yellow]Новое[/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated'})
        self.create_line(title='[B][COLOR=blue]Популярное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'in_favorites'})
        self.create_line(title='[B][COLOR=lime]Каталог[/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': data})
        
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
            if not self.params['search_string']:
                return False
            
            url = '{}searchTitles?search={}&limit=100&filter=id,posters.medium,type,player.series.string'.format(
                self.site_url, quote(self.params['search_string']))

            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not '},{' in html:
                if not '}]' in html:
                    self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                    return
                
            self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
            
            data_array = html.split('},{')

            i = 0
            
            for data in data_array:
                anime_id = data[data.find(':')+1:data.find(',')]
                type_code = data[data.find('code":')+6:data.find(',"string')]
                series_max = data[data.find('series":')+8:data.find(',"length')]
                series_cur = data[data.rfind('string":"')+9:data.rfind('"}')]    
                poster = data[data.find('url":"')+6:data.find('","raw_base64')]

                if type_code == '0':
                    series_cur = u'Фильм'
                    series_max = ''
                    
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id=anime_id,series_cur=series_cur,series_max=series_max)
                self.create_line(title=label, anime_id=anime_id, cover=poster ,params={'mode': 'select_part', 'id': anime_id})

            self.progress_bg.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')

        url = '{}getSchedule?filter=id,posters.medium,announce,type'.format(self.site_url,)

        data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
        html = data_request.text

        week = ('Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье')

        nodes = html.split(']},{')

        i = 0

        for node in nodes:
            day = week[i]
            data_array = node[node.find(':[{')+3:].split('},{')
            self.create_line(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(day), params={})
            
            i = i + 1
            p = int((float(i) / len(nodes)) * 100)

            self.progress_bg.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(nodes)))
                
            for data in data_array:
                data = unescape(data)
                
                anime_id = data[data.find(':')+1:data.find(',')]
                poster = data[data.find('medium":{"url":"')+16:data.find('","raw_base64')]

                announce = data[data.find('announce":')+10:data.find(',"type"')]
                announce = announce.replace('"','').replace('null','')

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id=anime_id, announce=announce)
                self.create_line(title=label, anime_id=anime_id, cover=poster ,params={'mode': 'select_part', 'id': anime_id})
                
        self.progress_bg.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        api_page = (int(self.params['page']) - 1) * int(self.params['limit'])
        api_filter = '&filter=id,posters.medium,type,player.series.string'
        
        url = '{}getUpdates?limit=12{}&after={}'.format(self.site_url, api_filter, api_page)
        
        if 'in_favorites' in self.params['param']:
            url = '{}advancedSearch?query={{id}}&order_by={}&limit=12{}&sort_direction=1&after={}'.format(
                self.site_url, self.params['param'], api_filter, api_page)

        data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        html = data_request.text
        
        if not '},{' in html:
            if not '}]' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
        
        self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
        
        data_array = html.split('},{')

        i = 0
        
        for data in data_array:
            anime_id = data[data.find(':')+1:data.find(',')]
            type_code = data[data.find('code":')+6:data.find(',"string')]
            series_max = data[data.find('series":')+8:data.find(',"length')]
            series_cur = data[data.rfind('string":"')+9:data.rfind('"}')]    
            poster = data[data.find('url":"')+6:data.find('","raw_base64')]

            if type_code == '0':
                series_cur = u'Фильм'
                series_max = ''
                
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
        
            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id=anime_id,series_cur=series_cur,series_max=series_max)
            self.create_line(title=label, anime_id=anime_id, cover=poster ,params={'mode': 'select_part', 'id': anime_id})

        self.progress_bg.close()

        if len(data_array) >= int(self.params['limit']):
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):        
        from info import anilibria_year, anilibria_season, anilibria_genre, anilibria_status, anilibria_sort

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_genre'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_year'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_season'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_sort'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_status'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'genre' in self.params['param']:
            result = self.dialog.select('Жанр:', anilibria_genre)
            self.addon.setSetting(id='{}_genre'.format(self.params['portal']), value=anilibria_genre[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Год:', anilibria_year)
            self.addon.setSetting(id='{}_year'.format(self.params['portal']), value=anilibria_year[result])

        if 'season' in self.params['param']:
            result = self.dialog.select('Сезон:', tuple(anilibria_season.keys()))
            self.addon.setSetting(id='{}_season'.format(self.params['portal']), value=tuple(anilibria_season.keys())[result])

        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(anilibria_sort.keys()))
            self.addon.setSetting(id='{}_sort'.format(self.params['portal']), value=tuple(anilibria_sort.keys())[result])

        if 'status' in self.params['param']:
            result = self.dialog.select('Статус релиза:', tuple(anilibria_status.keys()))
            self.addon.setSetting(id='{}_status'.format(self.params['portal']), value=tuple(anilibria_status.keys())[result])
        
        if 'catalog' in self.params['param']:
            self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
            
            year = '%20and%20{{season.year}}=={}'.format(self.addon.getSetting('anilibria_year')) if self.addon.getSetting('anilibria_year') else ''
            genre = '%20and%20"{}"%20in%20{{genres}}'.format(quote(self.addon.getSetting('anilibria_genre'))) if self.addon.getSetting('anilibria_genre') else ''
            season = '%20and%20{{season.code}}=={}'.format(anilibria_season[self.addon.getSetting('anilibria_season')]) if self.addon.getSetting('anilibria_season') else ''

            status = '%20and%20{{status.code}}=={}'.format(anilibria_status[self.addon.getSetting(
                'anilibria_status')]) if anilibria_status[self.addon.getSetting('anilibria_status')] else ''

            sort = '&order_by={}&sort_direction=1'.format(anilibria_sort[self.addon.getSetting('anilibria_sort')])
    
            api_filter = '&filter=id,posters.medium,type,player.series.string'
            api_page = '&after={}'.format((int(self.params['page'])-1) * int(self.params['limit']))
            api_limit = '&limit={}'.format(self.params['limit'])
                
            url = '{}advancedSearch?query={{id}}{}{}{}{}{}{}{}{}'.format(
                self.site_url, status, year, genre, season, sort, api_limit, api_filter, api_page)

            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)

            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not '},{' in html:
                if not '}]' in html:
                    self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                    return

            data_array = html.split('},{')

            i = 0
                
            for data in data_array:
                anime_id = data[data.find(':')+1:data.find(',')]
                type_code = data[data.find('code":')+6:data.find(',"string')]
                series_max = data[data.find('series":')+8:data.find(',"length')]
                series_cur = data[data.rfind('string":"')+9:data.rfind('"}')]    
                poster = data[data.find('url":"')+6:data.find('","raw_base64')]

                if type_code == '0':
                    series_cur = 'Фильм'
                    series_max = ''
                        
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
                
                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id=anime_id,series_cur=series_cur,series_max=series_max)
                self.create_line(title=label, anime_id=anime_id, cover=poster ,params={'mode': 'select_part', 'id': anime_id})

            if len(data_array) >= int(self.params['limit']):
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

            self.progress_bg.close()
            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        if '0' in self.addon.getSetting('anilibria_mode'):
            self.exec_torrent_part()
        if '1' in self.addon.getSetting('anilibria_mode'):
            self.exec_online_part()
        if '2' in self.addon.getSetting('anilibria_mode'):
            self.create_line(title='[B]ONLINE[/B]', params={'mode': 'online_part', 'id': self.params['id']})
            self.create_line(title='[B]TORRENT[/B]', params={'mode': 'torrent_part', 'id': self.params['id']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            array = {'1080p': [], '720p': [], '480p': []}
            
            url = '{}getTitle?id={}&playlist_type=array&filter=posters.medium,player'.format(
                self.site_url, self.params['id'])
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            html = data_request.text
        
            cover = html[html.find('url":')+5:html.find(',"raw_base64')]
            cover = cover.replace('"', '')
            host = html[html.find('host":"')+7:html.find('","series')]
        
            data_array = html[html.find('playlist":[{')+12:]
            data_array = data_array.split('},{')

            for data in data_array:
                name = data[data.find(':')+1:data.find(',')]
                            
                data = data[data.find('hls":{')+6:data.rfind('}')].replace('"', '')
                if '}' in data:
                    data = data[:data.find('}')]

                fhd = data[data.find('fhd:')+4:data.find(',hd:')].replace('null', '')
                hd = data[data.find(',hd:')+4:data.find(',sd:')].replace('null', '')
                sd = data[data.find(',sd:')+4:].replace('null', '')

                if fhd:
                    array['1080p'].append('{}||{}{}'.format(name, host, fhd))
                if hd:
                    array['720p'].append('{}||{}{}'.format(name, host, hd))
                if sd:
                    array['480p'].append('{}||{}{}'.format(name, host, sd))

            for i in array.keys():
                if array[i]:
                    label = '[COLOR=lime]ONLINE[/COLOR] | [B]{}[/B]'.format(i)
                    self.create_line(title=label, params={'mode': 'online_part', 'param': ','.join(array[i]), 'id': self.params['id'],'node':cover})
                    
        if self.params['param']:
            data_array = self.params['param'].split(',')
            for data in data_array:
                data = data.split('||')
                label = u'Серия: {}'.format(data[0])
                online_url = 'https://{}'.format(data[1])
                self.create_line(title=label, cover=self.params['node'] ,params={}, anime_id=self.params['id'], online=online_url, folder=False)
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            url = '{}getTitle?id={}&playlist_type=array&filter=posters.medium,torrents'.format(
                self.site_url, self.params['id'])
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            html = data_request.text
        
            cover = html[html.find('url":')+5:html.find(',"raw_base64')]
            cover = cover.replace('"', '')
            
            data_array = html[html.find('list":[{')+8:]
            data_array = data_array.split(',{')

            for data in data_array:
                torrent_id = data[data.find(':')+1:data.find(',')]
                series = data[data.find('string":"')+9:data.find('"},"quality')]
                quality = data[data.find('lity":{"string":"')+17:data.find('","type')]
                leechers = data[data.find('leechers":')+10:data.find(',"seeders')]            
                seeders = data[data.find('seeders":')+9:data.find(',"downloads')]

                torrent_size = data[data.find('total_size":')+12:data.find(',"url')]
                torrent_size = float('{:.2f}'.format(int(torrent_size)/1024.0/1024/1024))

                label = '[COLOR=orange]TORRENT[/COLOR] | Серии: {} | [COLOR=blue]{}[/COLOR] | [COLOR=F0FFD700]{} GB[/COLOR] | [COLOR=F000F000]{}[/COLOR] / [COLOR=F0F00000]{}[/COLOR]'.format(
                                series, quality, torrent_size, seeders, leechers)
                
                self.create_line(title=label, params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id'], 'node': cover})
                
        if self.params['param']:
            if '0' in self.addon.getSetting('anilibria_torrents'):
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'true')
                self.proxy_data = self.exec_proxy_data()
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'false')
                
            url = 'https://www.anilibria.tv/public/torrent/download.php?id={}'.format(self.params['param'])
            
            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
            
            from utility import sha1
            
            file_name = sha1(
                '{}_{}'.format(self.params['portal'], self.params['id'])
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
                    size[i] = x['length']
                    series[i] = x['path'][-1]
                for i in sorted(series, key=series.get):
                    self.create_line(title=series[i], cover=self.params['node'], params={'mode': 'selector_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], cover=self.params['node'], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
#========================#========================#========================#
    def exec_selector_part(self):
        torrent_url = os.path.join(self.torrents_dir, self.params['id'])
        data_print(torrent_url)
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