# -*- coding: utf-8 -*-

import gc
import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

if sys.version_info.major > 2:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import parse_qs
    from html import unescape
else:
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

from utility import clean_tags, fs_enc

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

if sys.version_info.major > 2:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

try:
    xbmcaddon.Addon('script.module.requests')
except:
    xbmcgui.Dialog().notification(
        heading='Установка Библиотеки',
        message='script.module.requests',
        icon=icon,time=3000,sound=False
        )
    xbmc.executebuiltin('RunPlugin("plugin://script.module.requests")')

import requests

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            #'Accept': '*/*',
            #'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            #'Accept-Charset': 'utf-8',
            #'Accept-Encoding': 'identity',
            #'Content-Type': 'application/json'
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin':'https://www.lostfilm.tv/',
            'Referer': 'https://www.lostfilm.tv/'
            }

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

class Lostfilm:    
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        self.session = requests.Session()
        
        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)
        
        self.cookie_dir = os.path.join(addon_data_dir, 'cookies')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.database_dir = os.path.join(addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'code': ''}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.sid_file = os.path.join(self.cookie_dir, 'lostfilm.sid')
        self.proxy_data = None #self.exec_proxy_data()
        self.site_url = self.create_site_url()
        #self.authorization = self.exec_authorization_part()
        self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'lostfilm.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'lostfilm.db'))
        del DataBase
#========================#========================#========================#
    def create_session(self):
        url = '{}my'.format(self.site_url)
        r = self.session.get(url=url, headers=headers)

        html = r.text

        user_session = html[html.find('session = \'')+11:html.find('UserData.newbie')]
        user_session = user_session[:user_session.rfind('\'')].strip()
        
        addon.setSetting('user_session', user_session)
        return user_session
#========================#========================#========================#
    def create_site_url(self):
        site_url = addon.getSetting('mirror_0')
        current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))

        if not addon.getSetting(current_mirror):
            site_url = addon.getSetting('mirror_0')
        else:
            site_url = addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_colorize(self, data):
        setting_id = {
            'Поиск':'search_color',
            'Расписание':'schedule_color',
            'Избранное':'favorites_color',
            'Новинки':'new_color',
            'Все сериалы':'serials_color',
            'Фильмы':'movies_color',
            'Каталог':'catalog_color',
            'Поиск по названию':'search_name_color',
            'Архив Торрентов': 'archive_color'
            }
        
        color_id = {'0':'none','1':'red','2':'lime','3':'blue','4':'gold','5':'orange'}

        data_color = color_id[
            addon.getSetting(setting_id[data])
            ]

        label = '[B][COLOR={}]{}[/COLOR][/B]'.format(data_color, data)
        
        return label
#========================#========================#========================#
    def create_image(self, se_code, ismovie=False):
        serial_episode = int(se_code[len(se_code)-3:len(se_code)])
        serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
        serial_image = int(se_code[:len(se_code)-6])

        image = (
            'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_image, serial_season),
            'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image),
            'https://static.lostfilm.top/Images/{}/Posters/e_{}_{}.jpg'.format(serial_image, serial_season, serial_episode)
        )
        image = image[int(addon.getSetting('series_image_mode'))]

        if 'schedule_part' in self.params['mode']:

            if serial_episode == 1 and serial_season == 1:
                image = 'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image)
            else:
                image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_image, 1)

        if serial_episode == 999:
            image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_image, serial_season)
            
        if ismovie:
            image = 'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image)
        return image
#========================#========================#========================#
    def create_title(self, serial_title='', episode_title='', data_code='', serial_id='', watched=False, ismovie=False):
        if serial_title:
            serial_title = u'[B]{}[/B]'.format(serial_title)
        
        if episode_title:
            if serial_title:
                serial_title = u'{}: '.format(serial_title)
            
            episode_title = u'{}'.format(episode_title)

        if data_code:
            if ismovie:
                serial_season = u'Фильм'
                serial_episode = '' 
            else:
                serial_season = int(data_code[len(data_code)-6:len(data_code)-3])
                serial_season = 'S{:>02}'.format(serial_season)
                serial_season = serial_season.replace('S999', 'A00')

                serial_episode = int(data_code[len(data_code)-3:len(data_code)])
                serial_episode = 'E{:>02}'.format(serial_episode)
            if watched:
                data_code = u'[COLOR=goldenrod]{}{} | [/COLOR]'.format(serial_season, serial_episode)
            else:
                data_code = u'[COLOR=blue]{}[/COLOR][COLOR=lime]{}[/COLOR] | '.format(serial_season, serial_episode)
        
        if watched:
            label = u'{}[COLOR=goldenrod]{}{}[/COLOR]'.format(data_code, serial_title, episode_title)
        else:
            label = u'{}{}{}'.format(data_code, serial_title, episode_title)
            
        return label
#========================#========================#========================#
    def create_context(self, serial_id='', se_code='', ismovie=False):
        serial_episode = se_code[len(se_code)-3:len(se_code)]
        serial_image = se_code[:len(se_code)-6]

        context_menu = []
        if not 'archive_part' in self.params['mode']:
            if 'search_part' in self.params['mode'] and self.params['param'] == '':
                context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=clean_part")'))

            if serial_id and self.params['mode'] in ('common_part','favorites_part','catalog_part','schedule_part','search_part','serials_part'):
                if not ismovie:
                    context_menu.append(('[COLOR=cyan]Избранное - Добавить \ Удалить [/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&id={}")'.format(serial_id)))

            if serial_id:
                context_menu.append(('[COLOR=white]Обновить описание[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial_part&id={}")'.format(serial_id)))

            if se_code and not '999' in serial_episode:
                if not ismovie:
                    context_menu.append(('[COLOR=blue]Перейти к Сериалу[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=select_part&id={}&code={}001999")'.format(serial_id,serial_image)))
                context_menu.append(('[COLOR=white]Открыть торрент файл[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)))
                context_menu.append(('[COLOR=yellow]Отметить как просмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(se_code)))
                context_menu.append(('[COLOR=yellow]Отметить как непросмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(se_code)))

        if 'archive_part' in self.params['mode']:
            context_menu.append(('[COLOR=blue]Удалить данный файл[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrclean_part&id={}&code={}")'.format(serial_id,se_code)))
            context_menu.append(('[COLOR=red]Удалить все файлы[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrclean_part&param=clean")'.format(serial_id,se_code)))            

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=news")'))
        context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=authorization_part&param=update")'))
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_database_part")'))
        return context_menu
#========================#========================#========================#
    def exec_torrclean_part(self):
        data_array = os.listdir(self.torrents_dir)

        if 'clean' in self.params['param']:
            try:
                for data in data_array:
                    file_path = os.path.join(self.torrents_dir, data)
                    try: os.remove(file_path)
                    except: pass
                self.dialog.notification(heading='Архив',message='УСПЕШНО',icon=icon,time=5000,sound=False)
                
                xbmc.executebuiltin("Container.Refresh()")
            except:
                self.dialog.notification(heading='Архив',message='ОШИБКА',icon=icon,time=5000,sound=False)
        
        if not self.params['param']:
            try:
                for data in data_array:
                    file_path = os.path.join(self.torrents_dir, data)

                    if self.params['code'] in data:
                        try: os.remove(file_path)
                        except: pass
                self.dialog.notification(heading='Архив',message='УСПЕШНО',icon=icon,time=5000,sound=False)
                
                xbmc.executebuiltin("Container.Refresh()")
            except:
                self.dialog.notification(heading='Архив',message='ОШИБКА',icon=icon,time=5000,sound=False)

#========================#========================#========================#
    def create_line(self, title, serial_id='', se_code='', watched=False, params=None, folder=True, ismovie=False):
        li = xbmcgui.ListItem(title)

        if serial_id and se_code:
            cover = self.create_image(se_code, ismovie=ismovie)

            li.setArt({"poster": cover,"icon": cover, "thumb": cover})

            se_info = self.database.get_serial(serial_id)

            info = {
                'genre':se_info[1],
                'country':se_info[3],
                'year': se_info[0][0:4],
                'plot':se_info[4],
                'title':title,
                'studio':se_info[2],
                'tvshowtitle':title,
                'premiered':se_info[0],
                'aired':se_info[0]
            }

            if self.database.cast_in_db(serial_id):
                cast = self.database.get_cast(serial_id)
                if cast['actors']:
                    li.setCast(cast['actors'])
                if cast['directors']:
                    info['director'] = cast['directors']
                if cast['writers']:
                    info['writer'] = cast['writers']
            
            if watched:
                info['playcount'] = 1

            li.setInfo(type='video', infoLabels=info)
            
        li.addContextMenuItems(
            self.create_context(serial_id = serial_id, se_code = se_code, ismovie=ismovie)
            )

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, serial_id, update=False):
        url = '{}series/{}/'.format(self.site_url, serial_id)

        data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)

        if not data_request.status_code == requests.codes.ok:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru='serial_id: {}'.format(serial_id)
                )
            return
        
        html = data_request.text
        
        if '<div class="title-block">' in html:
            pass
        else:
            url = '{}movies/{}/'.format(self.site_url, serial_id)
            
            data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
            html = data_request.text
            
            if '<div class="title-block">' in html:
                pass
            else:
                self.database.add_serial(serial_id=serial_id,title_ru='serial_id: {}'.format(serial_id))
                return

        ismovie = True if 'data-ismovie="1' in html else False

        info = dict.fromkeys(['title_ru', 'aired_on', 'genres', 'studios', 'country', 'description', 'image_id'], '')
                    
        info['image_id'] = html[html.find('/Images/')+8:html.find('/Posters/')]
        
        info['title_ru'] = html[html.find('itemprop="name">')+16:html.find('</h1>')]
        info['title_ru'] = info['title_ru'].replace('/', '-')

        description = html[html.find(u'Описание</h2>'):html.find('<div class="social-pane">')]

        if u'<strong class="bb">Сюжет' in description:
            description = description[description.find(u'<strong class="bb">Сюжет')+24:]    
        else:
            description = description[description.find('description">')+13:]
    
        description = description[:description.find('</div>')]
        description = unescape(description)

        if description and ':' in description[0]:
            description = description[1:]
            
        info['description'] = clean_tags(description)

        data_array = html[html.find('dateCreated"'):html.find('</a></span><br />')]
        data_array = data_array.split('<br />')

        for data in data_array:
            if 'dateCreated' in data:
                aired_on = data[data.find('content="')+9:data.find('" />')]
                info['aired_on'] = aired_on.replace('-', '.')
            if 'search&c=' in data:
                data = data[data.find('">')+2:]
                info['studios'] = data[:data.find('</a>')]
                info['country'] = data[data.find('(')+1:data.find(')')]
            if 'prop="genre' in data:
                genre = []
                data = data[data.find('<a href="'):].split('</a>')
                for d in data:
                    d = d[d.find('">')+2:].strip()
                    genre.append(d)
                info['genres'] = ', '.join(genre)
                
        try:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru=info['title_ru'],
                aired_on=info['aired_on'],
                genres=info['genres'],
                studios=info['studios'],
                country=info['country'],
                description=info['description'],
                image_id=info['image_id'],
                update=update                
            )
        except:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru='serial_id: {}'.format(serial_id)
                )
            self.dialog.notification(heading='Описание',message='Ошибка',icon=icon,time=3000,sound=False)
            return

        if not ismovie:
            cast = {'actors': [], 'directors': [], 'producers': [], 'writers': []}
            
            url = '{}cast'.format(url)
            data_request2 = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
            html2 = data_request2.text

            info_array = html2[html2.find('<div class="header-simple">'):html2.find('rightt-pane">')]        
            info_array = info_array.split('<div class="hor-breaker dashed"></div>')

            for cast_info in info_array:
                title = cast_info[cast_info.find('simple">')+8:cast_info.find('</div>')]
                title = title.replace(u'Актеры', 'actors').replace(u'Режиссеры', 'directors')
                title = title.replace(u'Продюсеры', 'producers').replace(u'Сценаристы', 'writers')
                
                cast_info = cast_info[:cast_info.rfind('</a>')]
                cast_info = cast_info.split('</a>')

                for c in cast_info:
                    person = c[c.find('name-ru">')+9:]
                    person = person[:person.find('</div>')]

                    node = u'{}'.format(person.strip())

                    if 'actors' in title:
                        role = c[c.find('role-ru">')+9:]
                        role = role[:role.find('</div>')]

                        node = u'{}|{}'.format(person.strip(), role.strip())

                    cast[title].append(node)

            try:
                self.database.add_cast(
                    serial_id=serial_id,
                    actors='||'.join(cast['actors']),
                    directors=','.join(cast['directors']),
                    producers=','.join(cast['producers']),
                    writers=','.join(cast['writers']),
                    update=update
                )
            except:
                self.dialog.notification(heading='Кастинг',message='Ошибка',icon=icon,time=3000,sound=False)
                return
            
        return
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    def exec_authorization_part(self):
        if not addon.getSetting('username') or not addon.getSetting('password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='Введите Логин и Пароль',icon=icon,time=3000,sound=False)
            return

        if 'update' in self.params['param']:
            addon.setSetting('auth', 'false')
            addon.setSetting('auth_session','')
        
        auth_url = '{}ajaxik.users.php'.format(self.site_url)
        
        try:
            session = float(addon.getSetting('auth_session'))
        except:
            session = 0
        
        if time.time() - session > 86400:
            addon.setSetting('auth_session', str(time.time()))
            
            try:
                os.remove(self.sid_file)
            except:
                pass
            
            addon.setSetting('auth', 'false')
            addon.setSetting('user_session', '')
            
        auth_post_data = {
            "act": "users",
            "type": "login",
            "mail": addon.getSetting('username'),
            "pass": addon.getSetting('password'),
            "need_captcha": "1",
            "rem": "1"
        }

        import pickle

        if 'true' in addon.getSetting('auth'):
            try:
                with open(self.sid_file, 'rb') as read_file:
                    self.session.cookies.update(pickle.load(read_file))
                auth = True
            except:
                r = requests.post(url=auth_url, proxies=self.proxy_data, data=auth_post_data)
                
                if 'success' in r.text:
                    with open(self.sid_file, 'wb') as write_file:
                        pickle.dump(r.cookies, write_file)
                        
                    self.session.cookies.update(r.cookies)                
                    auth = True
                else:
                    auth = False
        else:
            r = requests.post(url=auth_url, proxies=self.proxy_data, data=auth_post_data)

            if 'success' in r.text:
                with open(self.sid_file, 'wb') as write_file:
                    pickle.dump(r.cookies, write_file)

                self.session.cookies.update(r.cookies)                
                auth = True
            else:
                auth = False                    


        if not auth:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='Проверьте Логин и Пароль',icon=icon,time=3000,sound=False)
            return
        else:
            addon.setSetting('auth', str(auth).lower())
            
        if auth:
            if not addon.getSetting('user_session'):
                addon.setSetting('user_session', self.create_session())
            
        return auth
#========================#========================#========================#
    def exec_update_serial_part(self):
        self.create_info(serial_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_database_part(self):
        try:
            self.database.end()
        except:
            pass

        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/lostfilm.db'
        target_path = os.path.join(self.database_dir, 'lostfilm.db')

        try:
            os.remove(target_path)
        except:
            pass

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
            self.dialog.notification(heading='Загрузка файла',message='Успешно загружено',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Загрузка файла',message='Ошибка при загрузке',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_mark_part(self, notice=True, se_code=None, mode=False):
        se_code = se_code if se_code else self.params['id']
        mode = mode if mode else self.params['param']

        url='{}ajaxik.php'.format(self.site_url)
        post_data = {
            "session": addon.getSetting('user_session'),
            "act": "serial",
            "type": "markepisode",
            "val": se_code,
            "mode": mode
            }

        data_request = self.session.post(url=url, data=post_data, headers=headers)

        html = data_request.text

        if notice:
            if '"on' in str(html) or 'off' in str(html):
                self.dialog.notification(heading='LostFilm',message='ВЫПОЛНЕНО',icon=icon,time=3000,sound=False)
            if 'error' in str(html):
                self.dialog.notification(heading='LostFilm',message='ОШИБКА',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_favorites_part(self):
        post = 'session={}&act=serial&type=follow&id={}'.format(
            addon.getSetting('user_session'), self.database.get_image_id(self.params['id']))
        
        url = '{}ajaxik.php'.format(self.site_url)
        data_request = self.session.post(url=url, data=post, proxies=self.proxy_data, headers=headers)
        
        html = data_request.text

        if '"on' in str(html):
            self.dialog.notification(heading='LostFilm',message='ДОБАВЛЕНО',icon=icon,time=3000,sound=False)
        if 'off' in str(html):
            self.dialog.notification(heading='LostFilm',message='УДАЛЕНО',icon=icon,time=3000,sound=False)
        if 'error' in str(html):
            self.dialog.notification(heading='LostFilm',message='ОШИБКА',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.dialog.notification(heading='LostFilm',message='ВЫПОЛНЕНО',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='LostFilm',message='ОШИБКА',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_information_part(self):
        lostfilm_data = u'[B][COLOR=darkorange]Version 0.9.7[/COLOR][/B]\n\
    - Исправлена ошибка в разделе Расписание\n\
    - В Расписание добавлены заглушки для ошибок\n\
    * заглушки высвечивают ошибки отдельно и раздел продолжает работать'
        self.dialog.textviewer('Информация', lostfilm_data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=self.create_colorize('Поиск'), params={'mode': 'search_part'})
        self.create_line(title=self.create_colorize('Расписание'), params={'mode': 'schedule_part'})
        self.create_line(title=self.create_colorize('Избранное'), params={'mode': 'catalog_part', 'param': 'favorites'})
        self.create_line(title=self.create_colorize('Новинки'), params={'mode': 'common_part', 'param':'new/'})
        self.create_line(title=self.create_colorize('Фильмы'), params={'mode': 'catalog_part', 'param': 'movies'})
        self.create_line(title=self.create_colorize('Все сериалы'), params={'mode': 'serials_part'})
        self.create_line(title=self.create_colorize('Каталог'), params={'mode': 'catalog_part'})
        self.create_line(title=self.create_colorize('Архив Торрентов'), params={'mode': 'archive_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=self.create_colorize('Поиск по названию'), params={'mode': 'search_part', 'param': 'search_word'})
            data_array = addon.getSetting('search').split('|')
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
                data_array = addon.getSetting('search').split('|')
                while len(data_array) >= 7:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                addon.setSetting('search', data_array)

                self.params['param'] = 'search_string'
            else:
                return False

        if 'search_string' in self.params['param']:            
            if self.params['search_string'] == '':
                return False

            url = '{}ajaxik.php'.format(self.site_url)
            
            post_data = {
                "session": addon.getSetting('user_session'),
                "act": "common",
                "type": "search",
                "val": self.params['search_string']
                }

            data_request = self.session.post(url=url, data=post_data, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            html = data_request.text
            
            if not ':[{' in html:
                self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            html = html[html.find('[')+1:html.find(']')]

            data_array = html.split('},{')
            
            i = 0

            for data in data_array:
                is_movie = True if '\/movies\/' in data else False
                
                serial_title = data[data.find('title":"')+8:data.find('","title_orig')]

                try:
                    serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                except:
                    pass

                serial_id = data[data.find('"link":"')+8:]
                serial_id = serial_id[:serial_id.find('"')]
                serial_id = serial_id[serial_id.rfind('/')+1:]
                
                image_id = data[data.find('"id":"')+6:]
                image_id = image_id[:image_id.find('"')]

                se_code = '{}001999'.format(image_id)
                
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                
                if not self.database.serial_in_db(serial_id):
                    self.create_info(serial_id)

                label = self.create_title(serial_title=serial_title)
                
                if is_movie:
                    se_code = '{}001001'.format(se_code[:-6])
                    
                    self.create_line(title=label, serial_id=serial_id, se_code=se_code, folder=False, ismovie=is_movie, params={
                        'mode': 'play_part', 'id': serial_id, 'param': se_code})
                else:
                    self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})

            self.progress_bg.close()
            
            if '<div class="next-link active">' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                    int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        url = '{}schedule/my_0/type_0'.format(self.site_url)
        data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)

        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        html = data_request.text
        
        if not '<th colspan="6">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('LostFilm', 'Инициализация')

        data_array = html[html.find('<th colspan="6">')+16:html.rfind('<td class="placeholder">')]        
        data_array = data_array.split('<th colspan="6">')

        i = 0
        
        try:
            for data in data_array:
                title = data[:data.find('</th>')]

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.create_line(title=u'[B]{}[/B]'.format(title.capitalize()), params={})

                data = data.split('<td class="alpha"')
                data.pop(0)
                
                a = 0
                
                try:
                    for d in data:
                        is_movie = True if '/movies/' in d else False
                        
                        if is_movie:
                            serial_id = d[d.find('/movies/')+8:d.find('\',false')]
                            serial_id = serial_id.strip()
                        else:
                            serial_id = d[d.find('/series/')+8:d.find('\',false')]
                            serial_id = serial_id.strip()
                        
                        image_id = d[d.find('/Images/')+8:d.find('/Posters/')]
                        
                        serial_title = d[d.find('class="ru">')+11:]
                        serial_title = serial_title[:serial_title.find('</div>')]

                        episode_title = d[d.find('<td class="gamma'):]
                        episode_title = episode_title[episode_title.find(';">')+3:episode_title.find('<br />')]

                        if is_movie:
                            code = ['1','1']
                        else:
                            # code = d[d.rfind('{}/'.format(serial_id))+len(serial_id)+1:d.rfind('/\'')]
                            # code = code.replace('season_','').replace('episode_','')
                            # code = code.replace('additional','999').split('/')
                            code = d[d.rfind('{}'.format(serial_id))+len(serial_id):d.rfind('/\'')]
                            code = code.replace('season_','').replace('episode_','').strip()
                            code = code.replace('additional','999').replace('/', '', 1).split('/')
                            
                        se_code = '{}{:>03}{:>03}'.format(image_id,int(code[0]),int(code[1]))

                        day_release = d[d.rfind('false);">')+9:d.rfind('<br />')].strip()
                        
                        if '<p>' in d:
                            when_release = d[d.find('<p>')+3:d.find('</p>')]
                        else:
                            when_release = d[d.rfind('<span>')+6:d.rfind('</span>')]
                            when_release = u'Дней осталось: {}'.format(when_release)
                        
                        a = a + 1
                        
                        self.progress_bg.update(p, u'[COLOR=lime]День:[/COLOR] {} из {} | [COLOR=blue]Элементы:[/COLOR] {} из {} '.format(
                            i, len(data_array), a, len(data)))

                        if not self.database.serial_in_db(serial_id):
                            self.create_info(serial_id)

                        if is_movie:
                            label = self.create_title(serial_title=serial_title, data_code=se_code,ismovie=is_movie)
                        else:
                            label = self.create_title(serial_title, episode_title, se_code, ismovie=is_movie)
                        label = u'{} | [COLOR=gold]{} - {}[/COLOR]'.format(label, day_release, when_release)

                        self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})
                except:
                    self.create_line(title=u'[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
        except:
            self.create_line(title=u'[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
             
        self.progress_bg.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page_{}'.format(self.site_url, self.params['param'], self.params['page'])

        data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        html = data_request.text
        
        if not '<div class="hor-breaker dashed">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('LostFilm', 'Инициализация')
        
        data_array = html[html.find('breaker dashed">')+16:html.rfind('<div class="hor-breaker dashed">')]
        data_array = data_array.split('<div class="hor-breaker dashed">')
        
        i = 0

        for data in data_array:
            is_movie = True if 'data-ismovie="1' in data else False
            is_watched = True if 'haveseen-btn checked' in data else False

            serial_title = data[data.find('name-ru">')+9:]
            serial_title = serial_title[:serial_title.find('</div>')]
            
            if '/series/' in data:
                serial_id = data[data.find('series/')+7:]
                serial_id = serial_id[:serial_id.find('/')]

            if '/movies/' in data:
                serial_id = data[data.find('movies/')+7:]
                serial_id = serial_id[:serial_id.find('"')]

            serial_id = serial_id.strip()
    
            se_code = data[data.find('episode="')+9:data.find('" data-code')]

            episode_title = None
            if 'alpha">' in data:
                episode_title = data[data.find('alpha">')+7:]
                episode_title = episode_title[:episode_title.find('</div>')]
                episode_title = unescape(episode_title).strip()
                
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

            if not self.database.serial_in_db(serial_id):
                self.create_info(serial_id=serial_id)

            label = self.create_title(serial_title, episode_title, se_code, watched=is_watched, ismovie=is_movie)

            self.create_line(title=label, serial_id=serial_id, se_code=se_code, watched=is_watched, folder=False, ismovie=is_movie, params={
                        'mode': 'play_part', 'id': serial_id, 'param': se_code})

        self.progress_bg.close()
        
        if '<div class="next-link active">' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={
                'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_serials_part(self):
        self.progress_bg.create('LostFilm', 'Инициализация')

        data_array = self.database.get_serials_id()
        data_array.sort()

        i = 0
        
        for data in data_array:
            
            try:
                serial_id = data[1]
                se_code = '{}001999'.format(data[2])
            except:
                label = '[COLOR=red][B]{}[/B][/COLOR]'.format(serial_id)
                self.create_line(title=label, params={})
                continue

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

            label = self.create_title(serial_title=data[0])
            self.create_line(title=label, serial_id=serial_id, se_code=se_code, params={
                'mode': 'select_part', 'id': serial_id, 'code': se_code})

        self.progress_bg.close()
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self, data_string=''):
        atl_names = bool(addon.getSetting('use_atl_names') == 'true')
        
        if not self.params['param']:
            url = '{}series/{}/seasons'.format(self.site_url, self.params['id'])

            data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return    

            html = data_request.text
            
            if '<div class="status">' in html and not atl_names:
                serial_status = html[html.find('<div class="status">')+20:]
                serial_status = serial_status[:serial_status.find('</span>')]
                serial_status = serial_status.replace(u'Статус:','').strip()
                serial_status = u'[COLOR=dimgray]{}[/COLOR]'.format(serial_status)
                self.create_line(title=serial_status, folder=False, watched=True, params={})
            else:
                serial_status = ''

            image_id = self.params['code'][:len(self.params['code'])-6]

            data_array = html[html.find('<h2>')+4:html.rfind('holder"></td>')+13]
            data_array = data_array.split('<h2>')

            if len(data_array) < 2:
                self.params={'mode': 'select_part', 'param': '{}001999'.format(image_id), 'id': self.params['id']}
                self.exec_select_part(data_string=html)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')

            i = 0
            
            for data in data_array:                
                if '<div class="details">' in data:
                    season_status = data[data.find('<div class="details">')+21:]
                    season_status = season_status[:season_status.find('<div class')]
                    season_status = season_status.replace(u'Статус:','').strip()
                    
                    if u'Идет' in season_status:
                        season_status = u'| [COLOR=gold]{}[/COLOR]'.format(season_status)
                    else:
                        season_status = u'| [COLOR=blue]{}[/COLOR]'.format(season_status)

                else:
                    season_status = ''
                    
                title = data[:data.find('</h2>')]

                season = title.replace(u'сезон','').strip()
                season = season.replace(u'Дополнительные материалы', '999')

                se_code = '{}{:>03}999'.format(image_id, int(season))

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                if 'PlayEpisode(' in data:
                    #label = u'[B]{}[/B]'.format(title)
                    label = u'[B]{} {}[/B]'.format(title, season_status)
                    self.create_line(title=label, serial_id=self.params['id'], se_code=se_code ,params={
                        'mode': 'select_part', 'param': '{}'.format(se_code), 'id': self.params['id']})
                else:
                    if not atl_names:
                        label = u'[COLOR=dimgray][B]{}[/B][/COLOR]'.format(title)
                        self.create_line(title=label, params={
                            'mode': 'select_part', 'param': '{}'.format(se_code), 'id': self.params['id']})

            self.progress_bg.close()

        if self.params['param']:                
            code = self.params['param']
            image_id = code[:len(code)-6]
            season_id = code[len(code)-6:len(code)-3]
            
            if data_string:
                html = data_string
            else:
                url = '{}series/{}/season_{}'.format(self.site_url, self.params['id'], int(season_id))
                data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)

                if not data_request.status_code == requests.codes.ok:
                    self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                    return

                html = data_request.text
                
            try:
                url = '{}ajaxik.php'.format(self.site_url)
                post = {
                    "act": "serial",
                    "type": "getmarks",
                    "id": image_id
                    }
                data_request2 = self.session.post(url=url, data=post, proxies=self.proxy_data, headers=headers)
                watched_data = data_request2.text
            except:
                watched_data = []

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            serial_title = html[html.find('ativeHeadline">')+15:html.find('</h2>')]
            
            data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
            data_array = data_array.split('<td class="alpha">')

            i = 0
            
            for data in data_array:
                se_code = data[data.find('episode="')+9:]
                se_code = se_code[:se_code.find('"')]

                episode_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
                if '<br>' in episode_title:
                    episode_title = episode_title[episode_title.find('">')+2:episode_title.find('<br>')].strip()        
                if '<br />' in episode_title:
                    episode_title = episode_title[episode_title.find('<div>')+5:episode_title.find('<br />')].strip()
                if not episode_title:
                    continue
                
                is_watched = True if se_code in watched_data else False

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                
                if 'data-code=' in data:
                    if atl_names:
                        #label = label[:label.find('|')].strip()
                        #label = u'{}.{}'.format(serial_title, label)

                        label = u'{}.S{:>02}E{:>02}'.format(
                            serial_title,
                            int(se_code[len(se_code)-6:len(se_code)-3]),
                            int(se_code[len(se_code)-3:len(se_code)])
                            )
                    else:
                        label = self.create_title(episode_title=episode_title, watched=is_watched, data_code=se_code)
                        
                        
                    self.create_line(title=label, serial_id=self.params['id'], se_code=se_code, watched=is_watched, folder=False, params={
                                     'mode': 'play_part', 'id': self.params['id'], 'param': se_code})
                else:
                    if not atl_names:
                        label = '[COLOR=dimgray]S{:>02}E{:02} | {}[/COLOR]'.format(
                            int(season_id), len(data_array), episode_title)
                        self.create_line(title=label, folder=False, params={})

            self.progress_bg.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            se_code = self.params['code']
            serial_episode = int(se_code[len(se_code)-3:len(se_code)])
            serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
            image_id = int(se_code[:len(se_code)-6])

            url = '{}v_search.php?c={}&s={}&e={}'.format(
                self.site_url, image_id, serial_season, serial_episode)
            
            data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
            html = data_request.text
            
            new_url = html[html.find('url=http')+4:html.find('&newbie=')]
            
            data_request = self.session.get(url=new_url, proxies=self.proxy_data, headers=headers)
            html = data_request.text

            data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
            data_array = data_array.split('<div class="inner-box--label">')

            quality = {}
                        
            for data in data_array:
                quality_data = data[:data.find('</div>')].strip()
                    
                torrent_url = data[data.find('<a href="')+9:]
                torrent_url = torrent_url[:torrent_url.find('">')]
                
                quality[quality_data] = torrent_url

            current_quality = addon.getSetting('quality')

            try:
                url = quality[current_quality]
            except:
                url = ''

            if not url:
                choice = list(quality.keys())
                        
                result = self.dialog.select('Доступное качество: ', choice)
                result_quality = choice[int(result)]
                url = quality[result_quality]

            data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)

            file_name = data_request.headers['content-disposition']
            file_name = file_name[file_name.find('filename=')+9:]
            file_name = file_name.replace('"','').replace(',','')
            file_name = '{}000_{}'.format(se_code[:len(se_code)-3], file_name)

            torrent_file = os.path.join(self.torrents_dir, file_name)
            
            with open(torrent_file, 'wb') as write_file:
                write_file.write(data_request.content)

            import bencode
                
            with open(torrent_file, 'rb') as read_file:
                torrent_data = read_file.read()

            torrent = bencode.bdecode(torrent_data)

            valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
            
            if 'files' in torrent['info']:                
                series = {}
                    
                for i, x in enumerate(torrent['info']['files']):
                    extension = x['path'][-1][x['path'][-1].rfind('.'):]
                        
                    if extension in valid_media:
                        series[i] = x['path'][-1]

                for i in sorted(series, key=series.get):
                    self.create_line(title=series[i], serial_id=self.params['id'], se_code=se_code, folder=False, params={
                        'mode': 'torrent_part', 'id': file_name, 'param': i})
            else:
                self.create_line(title=torrent['info']['name'], serial_id=self.params['id'], se_code=se_code, folder=False, params={
                    'mode': 'torrent_part', 'id': file_name, 'param': 0})
                
        if self.params['param']:
            torrent_file = os.path.join(self.torrents_dir, self.params['id'])

            self.exec_selector_part(torrent_index=self.params['param'], torrent_url=torrent_file)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        if self.params['page'] == '1':
            self.params['page'] = '0'

        from info import genre, year, types, sort, country, alphabet, form, channel, status

        if self.params['param'] == '':
            self.create_line(title='Формат: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('form')), params={'mode': 'catalog_part', 'param': 'form'})
            self.create_line(title='По алфавиту: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('alphabet')), params={'mode': 'catalog_part', 'param': 'alphabet'})
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            
            if 'Сериалы' in addon.getSetting('form'):
                self.create_line(title='Канал: [COLOR=gold]{}[/COLOR]'.format(
                    addon.getSetting('channel')), params={'mode': 'catalog_part', 'param': 'channel'})
                
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('types')), params={'mode': 'catalog_part', 'param': 'types'})
            self.create_line(title='Страна: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('country')), params={'mode': 'catalog_part', 'param': 'country'})
            self.create_line(title='Сортировка: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})

            if 'Сериалы' in addon.getSetting('form'):
                self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                    addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})
                
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'form' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(form.keys()))
            addon.setSetting(id='form', value=tuple(form.keys())[result])
            
        if 'alphabet' in self.params['param']:
            result = self.dialog.select('Название с буквы:', tuple(alphabet.keys()))
            addon.setSetting(id='alphabet', value=tuple(alphabet.keys())[result])
            
        if 'genre' in self.params['param']:
            result = self.dialog.select('Жанр:', tuple(genre.keys()))
            addon.setSetting(id='genre', value=tuple(genre.keys())[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Год:', tuple(year.keys()))
            addon.setSetting(id='year', value=tuple(year.keys())[result])
            
        if 'channel' in self.params['param']:
            result = self.dialog.select('Канал:', tuple(channel.keys()))
            addon.setSetting(id='channel', value=tuple(channel.keys())[result])
    
        if 'types' in self.params['param']:
            result = self.dialog.select('Тип:', tuple(types.keys()))
            addon.setSetting(id='types', value=tuple(types.keys())[result])

        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(sort.keys()))
            addon.setSetting(id='sort', value=tuple(sort.keys())[result])
            
        if 'status' in self.params['param']:
            result = self.dialog.select('Статус релиза:', tuple(status.keys()))
            addon.setSetting(id='status', value=tuple(status.keys())[result])
            
        if 'country' in self.params['param']:
            result = self.dialog.select('Страна:', tuple(country.keys()))
            addon.setSetting(id='country', value=tuple(country.keys())[result])
        
        if 'catalog' in self.params['param'] or 'favorites' in self.params['param'] or 'movies' in self.params['param']:
            
            post_data = {
                'type':'search',
                'o': self.params['page'],
                't':'0'
                }
            
            post_data.update({'act': form[addon.getSetting('form')]})
            
            if alphabet[addon.getSetting('alphabet')]:
                post_data.update({'l': alphabet[addon.getSetting('alphabet')]})
                
            if genre[addon.getSetting('genre')]:
                post_data.update({'g': genre[addon.getSetting('genre')]})
            
            if year[addon.getSetting('year')]:
                post_data.update({'y': year[addon.getSetting('year')]})

            if channel[addon.getSetting('channel')]:
                post_data.update({'c': channel[addon.getSetting('channel')]})
                
            if types[addon.getSetting('types')]:
                post_data.update({'r': types[addon.getSetting('types')]})
            
            if country[addon.getSetting('country')]:
                post_data.update({'cntr': country[addon.getSetting('country')]})
                
            post_data.update({'s': sort[addon.getSetting('sort')]})
            
            if 'favorites' in self.params['param']:
                post_data = {
                    'act': 'serial',
                    'type':'search',
                    'o': self.params['page'],
                    's': '2',
                    't':'99'
                    }
                
            if 'movies' in self.params['param']:
                post_data = {
                    "act": "movies",
                    "type": "search",
                    "o": "0",
                    "s": "3",
                    "t": "0"
                    }
                
            url = '{}ajaxik.php'.format(self.site_url)
            data_request = self.session.post(url=url, data=post_data, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='[B][COLOR=white]Контент не найден[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            html = data_request.text
            
            if not ':[{' in html:
                self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            html = html[html.find('[')+1:html.find(']')]

            data_array = html.split('},{')
            
            i = 0

            for data in data_array:
                is_movie = True if '\/movies\/' in data else False
                
                serial_title = data[data.find('title":"')+8:data.find('","title_orig')]

                try:
                    serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                except:
                    pass
                
                serial_id = data[data.find('"link":"')+8:]
                serial_id = serial_id[:serial_id.find('"')]
                serial_id = serial_id[serial_id.rfind('/')+1:]

                image_id = data[data.find('"id":"')+6:]
                image_id = image_id[:image_id.find('"')]

                se_code = '{}001001'.format(image_id)
                
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                
                if not self.database.serial_in_db(serial_id):
                    self.create_info(serial_id)

                label = self.create_title(serial_title=serial_title)
                
                if is_movie:
                    self.create_line(title=label, serial_id=serial_id, se_code=se_code, folder=False, ismovie=is_movie, params={
                        'mode': 'play_part', 'id': serial_id, 'param': se_code})
                else:
                    self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                    'mode': 'select_part', 'id': serial_id, 'code': se_code})
                
            self.progress_bg.close()

            if len(data_array) >= 10:
                page_count = (int(self.params['page']) / 10) + 1
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 10)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        return
#========================#========================#========================#
    def exec_archive_part(self):
        if not self.params['param']:
            data_array = os.listdir(self.torrents_dir)

            for data in data_array:
                try:
                    se_code = data[:data.find('_')]
                    file_name = data[data.find('_')+1:].replace('.torrent', '')
                    serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
                    image_id = int(se_code[:len(se_code)-6])
                except:
                    continue

                serial_id = self.database.get_serial_id(image_id)
                
                self.create_line(title=file_name, serial_id=serial_id, se_code=se_code, params={'mode': 'archive_part', 'param': data, 'code': se_code, 'id': serial_id})

        if self.params['param']:
            torrent_file = os.path.join(self.torrents_dir, self.params['param'])

            import bencode
                
            with open(torrent_file, 'rb') as read_file:
                torrent_data = read_file.read()

            torrent = bencode.bdecode(torrent_data)

            valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
            
            if 'files' in torrent['info']:
                
                series = {}
                    
                for i, x in enumerate(torrent['info']['files']):
                    extension = x['path'][-1][x['path'][-1].rfind('.'):]
                        
                    if extension in valid_media:
                        series[i] = x['path'][-1]

                for i in sorted(series, key=series.get):
                    self.create_line(title=series[i], serial_id=self.params['id'], se_code=self.params['code'], folder=False, params={
                        'mode': 'torrent_part', 'id': self.params['param'], 'param': i})
            else:
                self.create_line(title=torrent['info']['name'], serial_id=self.params['id'], se_code=self.params['code'], folder=False, params={
                    'mode': 'torrent_part', 'id': self.params['param'], 'param': 0})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_play_part(self):
        se_code = self.params['param']
        serial_episode = int(se_code[len(se_code)-3:len(se_code)])
        serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
        image_id = int(se_code[:len(se_code)-6])

        url = '{}v_search.php?c={}&s={}&e={}'.format(
            self.site_url, image_id, serial_season, serial_episode)

        data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
        html = data_request.text
        
        new_url = html[html.find('url=http')+4:html.find('&newbie=')]

        data_request = self.session.get(url=new_url, proxies=self.proxy_data, headers=headers)
        html = data_request.text

        data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
        data_array = data_array.split('<div class="inner-box--label">')

        quality = {}
                        
        for data in data_array:
            quality_data = data[:data.find('</div>')].strip()
                    
            torrent_url = data[data.find('<a href="')+9:]
            torrent_url = torrent_url[:torrent_url.find('">')]
                
            quality[quality_data] = torrent_url

        try:
            url = quality[addon.getSetting('quality')]
        except:
            choice = list(quality.keys())
            result = self.dialog.select('Доступное качество: ', choice)
            result_quality = choice[int(result)]
            url = quality[result_quality]

        data_request = self.session.get(url=url, proxies=self.proxy_data, headers=headers)
        
        file_name = data_request.headers['content-disposition']
        file_name = file_name[file_name.find('filename=')+9:]
        file_name = file_name.replace('"','').replace(',','')
        file_name = '{}000_{}'.format(se_code[:len(se_code)-3], file_name)

        torrent_file = os.path.join(self.torrents_dir, file_name)
        
        with open(torrent_file, 'wb') as write_file:
            write_file.write(data_request.content)

        confirm = self.exec_selector_part(series_index=serial_episode, torrent_url=torrent_file)

        if confirm:
            url = '{}ajaxik.php'.format(self.site_url)
            data = {
                "session": addon.getSetting('user_session'),
                "act": "serial",
                "type": "markepisode",
                "val": self.params['param'],
                "auto": "0",
                "mode": "on"
                }

            data_request = self.session.post(url = url, data=data, proxies=self.proxy_data, headers=headers)
#========================#========================#========================#
    def exec_selector_part(self, torrent_url, series_index='', torrent_index=''):
        if series_index:
            try:
                index = int(series_index)
            except:
                index = series_index

            if index > 0:
                index = index - 1

            from utility import get_index
            index = get_index(torrent_url, index)

        if torrent_index:
            try:
                index = int(torrent_index)
            except:
                index = torrent_index

        if '0' in addon.getSetting('engine'):
            try:
                tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver', 'torrserver_tam', 'lt2http')
                engine = tam_engine[int(addon.getSetting('tam'))]
                purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(torrent_url, index, engine)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
                return True
            except:
                return False

        if '1' in addon.getSetting('engine'):
            try:
                purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
                return True
            except:
                return False

        if '2' in addon.getSetting('engine'):
            try:
                from utility import torrent2magnet
                url = torrent2magnet(torrent_url)
                import torrserver_player
                torrserver_player.Player(
                    torrent=url,
                    sort_index=index,
                    host=addon.getSetting('ts_host'),
                    port=addon.getSetting('ts_port'))
                return True
            except:
                return False
            return

if __name__ == "__main__":
    lostfilm = Lostfilm()
    lostfilm.execute()
    del lostfilm

gc.collect()