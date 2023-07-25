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

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import parse_qs
from html import unescape

from utility import clean_tags
from utility import clean_list

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')
addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

class Lostfilm:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()
        
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

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.sid_file = os.path.join(self.cookie_dir, 'lostfilm.sid')

        from network import WebTools
        self.network = WebTools(
            auth_usage=True,
            auth_status=bool(addon.getSetting('auth') == 'true'),
            proxy_data = self.proxy_data)
        
        self.network.auth_post_data = urlencode({
            "act": "users", 
            "type": "login", 
            "mail": addon.getSetting('username'), 
            "pass": addon.getSetting('password'), 
            "need_captcha": "1", 
            "rem": "1"})

        self.network.auth_url = '{}ajaxik.users.php'.format(self.site_url)
        self.network.sid_file = self.sid_file
        del WebTools

        self.authorization = self.create_authorization()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'lostfilms.db')):
            self.create_database()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'lostfilms.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        site_url = addon.getSetting('mirror_0')
        current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))
        current_url = addon.getSetting(current_mirror)

        if not current_url:
            return site_url
        else:
            return current_url
#========================#========================#========================#
    def create_proxy_data(self):
        if '0' in addon.getSetting('unblock'):
            return None
        
        if '2' in addon.getSetting('unblock'):
            proxy_data = {'https': 'http://185.85.121.12:1088'}
            return proxy_data
        
        try:
            proxy_time = float(addon.getSetting('proxy_time'))
        except:
            proxy_time = 0

        from urllib.request import urlopen

        if time.time() - proxy_time > 604800:
            addon.setSetting('proxy_time', str(time.time()))
            proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()

            try:
                proxy_pac = str(proxy_pac, encoding='utf-8')
            except:
                pass

            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            addon.setSetting('proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if addon.getSetting('proxy'):
                proxy_data = {'https': addon.getSetting('proxy')}
            else:
                proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()
                
                try:
                    proxy_pac = str(proxy_pac, encoding='utf-8')
                except:
                    pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def create_authorization(self):
        if not addon.getSetting('username') or not addon.getSetting('password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='LostFilm', message='Введите Логин и Пароль', icon=icon, time=3000, sound=False)
            return

        try:
            temp_session = float(addon.getSetting('auth_session'))
        except:
            temp_session = 0
        
        if time.time() - temp_session > 86400:
            addon.setSetting('auth_session', str(time.time()))
            
            try:
                os.remove(self.sid_file)
            except:
                pass
            
            addon.setSetting('auth', 'false')
            addon.setSetting('user_session', '')

        authorization = self.network.authorization()

        if not authorization:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация', message='Проверьте Логин и Пароль', icon=icon, time=3000, sound=False)
            return
        else:
            addon.setSetting('auth', str(authorization).lower())

        if authorization:
            if not addon.getSetting('user_session'):
                url = '{}my'.format(self.site_url)
                html = self.network.get_html(url=url)
                
                user_session = html[html.find('session = \'')+11:html.find('UserData.newbie')]
                user_session = user_session[:user_session.rfind('\'')]
                user_session = user_session.strip()

                addon.setSetting('user_session', user_session)

        return authorization
#========================#========================#========================#
    def create_database(self):
        try:
            self.database.end()
        except:
            pass

        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/lostfilms.db'
        target_path = os.path.join(self.database_dir, 'lostfilms.db')

        try:
            os.remove(target_path)
        except:
            pass

        from urllib.request import urlopen

        self.progress_bg.create(u'Загрузка Базы Данных')

        try:                
            data = urlopen(target_url)
            chunk_size = 8192
            bytes_read = 0

            try:
                file_size = int(data.info().getheaders("Content-Length")[0])
            except:
                file_size = int(data.getheader('Content-Length'))

            with open(target_path, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    
                    try:
                        self.progress_bg.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                    except:
                        pass
            try:
                self.dialog.notification(heading='Загрузка файла',message='Успешно загружено',icon=icon,time=3000,sound=False)
            except:
                pass
        except:
            try:
                self.dialog.notification(heading='Загрузка файла',message='Ошибка при загрузке',icon=icon,time=3000,sound=False)
            except:
                pass

        self.progress_bg.close()
        
        return
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

        if serial_season == 999:
            serial_season = 1
            
        image = (
            'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_image, serial_season),
            'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image),
            'https://static.lostfilm.top/Images/{}/Posters/e_{}_{}.jpg'.format(serial_image, serial_season, serial_episode)
        )
        image = image[int(addon.getSetting('series_image_mode'))]

        if serial_episode == 999:
            image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_image, serial_season)
            
        if ismovie:
            image = 'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image)
        return image
#========================#========================#========================#
    def create_title(self, serial_title, data_code=None, watched=False, ismovie=False):

        serial_title = serial_title.replace('\/','/')

        if data_code:
            if ismovie:
                season = u'Фильм'
                episode = ''
            else:
                season = int(data_code[len(data_code)-6:len(data_code)-3])
                season = 'S{:>02}'.format(season)
                season = season.replace('999', '00')

                episode = int(data_code[len(data_code)-3:len(data_code)])
                episode = 'E{:>02}'.format(episode)

            if watched:
                data_code = u'{}{} | '.format(season, episode)
            else:
                data_code = u'[COLOR=blue]{}[/COLOR][COLOR=lime]{}[/COLOR] | '.format(season, episode)
        else:
            data_code = ''
            
        if watched:
            label = u'[COLOR=goldenrod]{}{}[/COLOR]'.format(data_code, serial_title)
        else:
            label = u'{}{}'.format(data_code, serial_title)

        return label
#========================#========================#========================#
    def create_cast(self, cast_info):
        actors = []

        actors_array = cast_info.split('*')
            
        for node in actors_array:
            node = node.split('|')

            if not node[0]:
                node[0] = 'uknown'
            if not node[1]:
                node[1] = 'uknown'
            if node[2]:
                node[2] = 'https://static.lostfilm.top/Names/{}/{}/{}/{}'.format(
                    node[2][1:2], node[2][2:3], node[2][3:4], node[2].replace('t','m', 1))
                

            actors.append(
                {'name': node[0], 'role': node[1], 'thumbnail':node[2]})
        
        return actors
#========================#========================#========================#
    def create_context(self, serial_id='', se_code='', ismovie=False):
        serial_episode = se_code[len(se_code)-3:len(se_code)]
        serial_image = se_code[:len(se_code)-6]

        context_menu = []

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=clean_part")'))

        if serial_id and self.params['mode'] in ('common_part','favorites_part','catalog_part','schedule_part','search_part','serials_part'):
            if not ismovie:
                context_menu.append(('[COLOR=cyan]Избранное - Добавить \ Удалить [/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)))

        if serial_id:
            context_menu.append(('[COLOR=white]Обновить описание[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, ismovie)))

        if se_code and not '999' in serial_episode:
            if not ismovie:
                context_menu.append(('[COLOR=blue]Перейти к Сериалу[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=select_part&id={}&code={}001999")'.format(serial_id,serial_image)))
            context_menu.append(('[COLOR=white]Открыть торрент файл[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)))
            context_menu.append(('[COLOR=yellow]Отметить как просмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(se_code)))
            context_menu.append(('[COLOR=yellow]Отметить как непросмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(se_code)))

        context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_authorization")'))
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_database")'))
        context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_proxy_data")'))
        return context_menu
#========================#========================#========================#
    # def exec_torrclean_part(self):
    #     data_array = os.listdir(self.torrents_dir)

    #     if 'clean' in self.params['param']:
    #         try:
    #             for data in data_array:
    #                 file_path = os.path.join(self.torrents_dir, data)
    #                 try: os.remove(file_path)
    #                 except: pass
                 #self.dialog.notification(heading='LostFilm',message='Выполнено',icon=icon,time=3000,sound=False)

                
    #             xbmc.executebuiltin("Container.Refresh()")
    #         except:
                 #self.dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)

        
    #     if not self.params['param']:
    #         try:
    #             for data in data_array:
    #                 file_path = os.path.join(self.torrents_dir, data)

    #                 if self.params['code'] in data:
    #                     try: os.remove(file_path)
    #                     except: pass
                  #self.dialog.notification(heading='LostFilm',message='Выполнено',icon=icon,time=3000,sound=False)
                
    #             xbmc.executebuiltin("Container.Refresh()")
    #         except:
                 #self.dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def create_line(self, title, serial_id='', se_code='', status='', watched=False, params=None, folder=True, ismovie=False):
        li = xbmcgui.ListItem(title)

        if serial_id and se_code:
            cover = self.create_image(se_code, ismovie=ismovie)
            li.setArt({
                "poster": cover,
                "icon": cover,
                "thumb": cover,
                #"banner": cover,
                "fanart": cover,
                #"clearart": cover,
                #"clearlogo": cover,
                #"landscape": cover,
                #"icon": cover
                })

            info = self.database.obtain_content(serial_id=serial_id)
            info.update({'status': status})

            info_cast = self.database.obtain_cast(serial_id=serial_id)
            cast = []
            if info_cast:
                cast = self.create_cast(info_cast)
                
            li.setCast(cast)

            if watched:
                info['playcount'] = 1

            li.setInfo(type='video', infoLabels=info)
            
        li.addContextMenuItems(
            self.create_context(serial_id = serial_id, se_code = se_code, ismovie=ismovie)
            )

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        # xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, serial_id, update=False, ismovie=False):
        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'genres', 'directors', 'producers',
                            'writers', 'studios', 'country', 'description', 'image_id', 'actors'], '')

        url = '{}series/{}/'.format(self.site_url, serial_id)
        
        if ismovie:
            info['title_en'] = '1'
            url = '{}movies/{}/'.format(self.site_url, serial_id)
        
        html = self.network.get_html(url=url)

        if not html:
            return False
            
        if not '<div class="title-block">' in html:
            return False
            
        image_id = html[html.find('/Images/')+8:]
        image_id = image_id[:image_id.find('/')]
        info['image_id'] = image_id
        del image_id

        title_ru = html[html.find('itemprop="name">')+16:]
        title_ru = title_ru[:title_ru.find('</h1>')]
        info['title_ru'] = title_ru.replace('/', '-')
        del title_ru

        description = html[html.find(u'Описание</h2>'):]
        description = description[:description.find('<div class="social-pane">')]
        
        if u'Сюжет' in description:
            description = description[description.find(u'Сюжет')+5:]
        else:
            description = description[description.find('description">')+13:]
        
        # if u'Сюжет<br />' in description:
        #     description = description[description.find(u'Сюжет<br />')+11:]
        # elif u'<strong class="bb">Сюжет' in description:
        #     description = description[description.find(u'<strong class="bb">Сюжет')+24:]
        # elif u'Сюжет' in description:
        #     description = description[description.find(u'Сюжет')+5:]
        # else:
        #     description = description[description.find('description">')+13:]

        description = description[:description.find('</div>')]
        description = unescape(description)

        if u'<strong class="bb">Сюжет' in description:
            description = u'Сюжет {}'.format(description)

        if description:
            if ':' in description[0]:
                description = description[1:]

            info['description'] = clean_tags(description)

        del description

        if 'dateCreated"' in html:
            data = html[html.find('dateCreated"'):html.find('</a></span><br />')+4]

            aired_on = data[data.find('content="')+9:]
            aired_on = aired_on[:aired_on.find('"')]
            info['aired_on'] = aired_on
            del aired_on

            if u'Страна:' in data:
                studios = data[data.find(u'Страна:')+7:]
                studios = studios[:studios.find('<br />')]

                if '(' and ')' in studios:
                    info['country'] = data[data.find('(')+1:data.find(')')]

                studios = studios.split(',')

                for studio in studios:
                    studio = studio[studio.find('">')+2:]
                    studio = studio[:studio.find('</a>')]
                    studio = studio.strip()

                    if info['studios']:
                        info['studios'] = u'{}*{}'.format(info['studios'], studio)
                    else:
                        info['studios'] = u'{}'.format(studio)

                del studios

            if 'itemprop="genre">' in data:
                genres = data[data.find('itemprop="genre">')+17:]
                genres = genres.split(',')

                for genre in genres:
                    genre = genre[genre.find('">')+2:]
                    genre = genre[:genre.find('</a>')]
                    genre = genre.strip()

                    if info['genres']:
                        info['genres'] = u'{}*{}'.format(info['genres'], genre)
                    else:
                        info['genres'] = u'{}'.format(genre)

                del genres

            del data

        if u'Дата выхода eng' in html:
            data = html[html.find(u'Дата выхода eng:')+16:]
            data = data[:data.find('<div class="hor-spacer">')]

            aired_on = data[:data.find('<br/>')]
            aired_on = aired_on[:aired_on.find(u'г.')].strip()
            aired_on = aired_on.replace(' ','-')

            month = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня',
                    u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']
                
            for i, x in enumerate(month):
                if x in aired_on:
                    info['aired_on'] = aired_on.replace(x, '{:>02}'.format(i+1))
                    break

            del aired_on
            del data

        url2 = '{}cast'.format(url)
        html2 = self.network.get_html(url=url2)
            
        try:
            info_array = html2[html2.find('<div class="header-simple">'):html2.find('rightt-pane">')]        
            info_array = info_array.split('<div class="hor-breaker dashed"></div>')
                    
            for cast_info in info_array:
                title = cast_info[cast_info.find('simple">')+8:cast_info.find('</div>')]
                title = title.replace(u'Актеры', 'actors').replace(u'Режиссеры', 'directors')
                title = title.replace(u'Продюсеры', 'producers').replace(u'Сценаристы', 'writers')

                cast_info = cast_info[:cast_info.rfind('</a>')]
                cast_info = cast_info.split('</a>')

                for c in cast_info:
                    cast_node = {'name': '', 'role': '', 'thumbnail': ''}

                    person = c[c.find('name-ru">')+9:]
                    person = person[:person.find('</div>')]
                    person = person.replace('*','').replace('\t','')
                    cast_node['name'] = u'{}'.format(person.strip())
                    del person

                    if 'autoload="' in c:
                        thumbnail = c[c.find('autoload="')+10:]
                        thumbnail = thumbnail[:thumbnail.find('"')]
                        thumbnail = thumbnail[thumbnail.rfind('/')+1:]
                        cast_node['thumbnail'] = u'{}'.format(thumbnail.strip())
                        del thumbnail

                    if 'actors' in title:
                        role = c[c.find('role-ru">')+9:]
                        role = role[:role.find('</div>')]
                        role = role.replace('*','').replace('\t','')
                        cast_node['role'] = u'{}'.format(role.strip())
                        node = u'|'.join(list(cast_node.values()))
                        del role
                    else:
                        node = u'{}'.format(cast_node['name'])

                    if info[title]:
                        info[title] = u'{}*{}'.format(info[title], node)
                    else:
                        info[title] = u'{}'.format(node)

                del cast_info

        except:
            pass
        
        if update:
            try:
                self.database.update_content(serial_id=serial_id, content=info)
            except:
                return False
        else:
            try:
                self.database.insert_content(serial_id=serial_id, content=info)
            except:
                return False

        return
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try:
            self.database.end()
        except:
            pass
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    def exec_update_database(self):
        self.create_database()
        return
#========================#========================#========================#
    def exec_update_serial(self):
        ismovie = bool(self.params['ismovie'] == 'True')

        self.create_info(
            serial_id=self.params['id'],
            ismovie=ismovie,            
            update=True
            )
        return
#========================#========================#========================#
    def exec_update_proxy_data(self):
        addon.setSetting('proxy','')
        addon.setSetting('proxy_time','')

        self.create_proxy_data()
        return
#========================#========================#========================#
    def exec_update_authorization(self):
        addon.setSetting('auth', 'false')
        addon.setSetting('auth_session','')

        from network import WebTools
        self.network = WebTools(
            auth_usage=True,
            auth_status=False,
            proxy_data = self.proxy_data)
            
        self.network.auth_post_data = urlencode({
            "act": "users",
            "type": "login",
            "mail": addon.getSetting('username'),
            "pass": addon.getSetting('password'),
            "need_captcha": "1",
            "rem": "1"})

        self.network.auth_url = '{}ajaxik.users.php'.format(self.site_url)
        self.network.sid_file = self.sid_file
        del WebTools

        self.create_authorization()
        return
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

        post_data = urlencode(post_data)

        html = self.network.get_html(url=url, post=post_data)

        if notice:
            if '"on' in str(html) or 'off' in str(html):
                self.dialog.notification(heading='LostFilm',message='Выполнено',icon=icon,time=3000,sound=False)
            if 'error' in str(html):
                self.dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.dialog.notification(heading='LostFilm',message='Выполнено',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=self.create_colorize('Поиск'), params={'mode': 'search_part'})
        self.create_line(title=self.create_colorize('Расписание'), params={'mode': 'schedule_part'})
        self.create_line(title=self.create_colorize('Избранное'), params={'mode': 'favorites_part'})
        self.create_line(title=self.create_colorize('Новинки'), params={'mode': 'common_part', 'param':'new/'})
        self.create_line(title=self.create_colorize('Фильмы'), params={'mode': 'movies_part'})
        self.create_line(title=self.create_colorize('Все сериалы'), params={'mode': 'serials_part'})
        self.create_line(title=self.create_colorize('Каталог'), params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=self.create_colorize('Поиск по названию'), params={'mode': 'search_part', 'param': 'search_word'})
            
            data_array = addon.getSetting('search').split('|')
            data_array.reverse()
            
            try:
                for data in data_array:
                    if data == '':
                        continue
                    self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param':'search_string', 'search_string': data})
            except:
                addon.setSetting('search', '')

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
            post_data = urlencode(post_data)

            html = self.network.get_html(url=url, post=post_data)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            if not ':[{' in html:
                self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            html = html[html.find('[')+1:html.find(']')]

            try:
                data_array = html.split('},{')
                
                for i, data in enumerate(data_array):
                    try:
                        if '\/movies\/' in data:
                            is_movie = True
                        else:
                            is_movie = False
                        
                        serial_title = data[data.find('title":"')+8:data.find('","title_orig')]

                        try:
                            serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                        except:
                            pass

                        serial_id = data[data.find('"link":"')+8:]
                        serial_id = serial_id[:serial_id.find('"')]
                        serial_id = serial_id[serial_id.rfind('/')+1:]
                        serial_id = serial_id.strip()
                        
                        image_id = data[data.find('"id":"')+6:]
                        image_id = image_id[:image_id.find('"')]

                        se_code = '{}001999'.format(image_id)

                        p = int((float(i+1) / len(data_array)) * 100)

                        self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                        if not self.database.content_in_db(serial_id):
                            self.create_info(serial_id)

                        label = self.create_title(serial_title=serial_title)
                        
                        if is_movie:
                            se_code = '{}001001'.format(se_code[:-6])
                            self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                                'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                        else:
                            self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})
                    except:
                        self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
            except:
                self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})

            self.progress_bg.close()
            
            if '<div class="next-link active">' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                    int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        url = '{}schedule/{}'.format(self.site_url, self.params['param'])
        
        html = self.network.get_html(url=url)
        
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
                
        if not '<tbody>' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
            
        table_data = html[html.find('<tbody>')+7:html.find('</tbody>')]

        table_data = clean_list(table_data)
        table_data = table_data.split('</tr><tr><th></th>')

        schedule_table = []
        today = False

        for data in table_data:
            schedule = []
            
            header = data[data.find('<th class'):data.find('</th><th></th></tr>')]
            header = header.split('</th>')

            for h in header:
                try:
                    if 'inactive' in h:
                        h = '***'
                    else:
                        if 'today' in h:
                            h = 'Сегодня'
                            today = True
                        else:
                            h = h[h.find('">')+2:]

                    h = h.replace('Вт', 'Вторник -').replace('Ср', 'Среда -')
                    h = h.replace('Чт', 'Четверг -').replace('Пт', 'Пятница -')
                    h = h.replace('Сб', 'Суббота -').replace('Вс', 'Воскресенье -')
                    h = h.replace('Пн', 'Понедельник -')
                except:
                    h = '[COLOR=red]Ошибка[/COLOR]'
                    
                schedule.append([h])

            data = data[data.find('</tr>')+5:data.rfind('</td>')]
            data = data.split('</tr>')
        
            for nodes in data:        
                nodes = nodes[nodes.find('<div class="table'):nodes.rfind('</div>')]
                node = nodes.split('</td>')

                for s,n in enumerate(node):
                    if 'title">' in n:
                        title = n[n.find('title">'):n.find('</span></a>')]
                        title = title[title.find('>')+1:].split('</br>')
                                              
                        try:
                            if '<span>' in title[1]:
                                code = title[1].replace('<span>','').replace('x','|').replace('х','|')
                                code = code.replace('ДОП','00').replace('-','|').split('|')
                                if len(code) > 2:
                                    code = '[COLOR=blue]S{:>02}[/COLOR][COLOR=lime]E{:>02}-{:>02}[/COLOR]'.format(
                                        int(code[0]), int(code[1]), int(code[2]))
                                else:
                                    code = '[COLOR=blue]S{:>02}[/COLOR][COLOR=lime]E{:>02}[/COLOR]'.format(int(code[0]),int(code[1]))
                                    
                            if '</a><div' in title[1]:
                                code = '[COLOR=blue]Фильм[/COLOR]'
                        except:
                            code = '[COLOR=red]Ошибка[/COLOR]'
                        
                        try:
                            title = '{} | {}'.format(code, title[0])
                        except:
                            title = '[COLOR=red]Ошибка[/COLOR]'
                        
                        schedule[s].append(title)
            schedule_table.extend(schedule)
            
        if '0' in addon.getSetting('schedule_mode_today'):
            if today:
                for i,x in enumerate(schedule_table):
                    if 'Сегодня' in x[0]:
                        schedule_table = schedule_table[i:]

        self.progress_bg.create('LostFilm', 'Инициализация')
        
        try:
            for u, sch in enumerate(schedule_table):
                if '***' in sch[0] or len(sch) < 2:
                    continue
                
                p = int((float(u+1) / len(schedule_table)) * 100)
                
                self.create_line(title='[B]{}[/B]'.format(sch[0]), params={})
                series = sch[1:]
                
                try:
                    for a, ep in enumerate(series):
                        
                        self.progress_bg.update(p, '[COLOR=lime]День:[/COLOR] {} из {} | [COLOR=blue]Элементы:[/COLOR] {} из {} '.format(u, len(schedule_table), a, len(data)))
                        self.create_line(title=ep, params={}, folder=False)
                except:
                    self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
        except:
            self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
            
        self.progress_bg.close()
        
        if 'next-link active' in html:
            next_link = html[html.find('next-link active'):]
            next_link = next_link[next_link.find('/schedule/')+10:next_link.find('<div')]
            
            title = next_link[next_link.rfind('>')+1:].capitalize()

            next_link = next_link[:next_link.find('\'')]

            label = 'Следующий - [COLOR=gold]{}[/COLOR]'.format(title)
            self.create_line(title=label, params={'mode': 'schedule_part', 'param': next_link})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_favorites_part(self):
        if 'serial_id' in self.params:
            post_data = {
                'session' : addon.getSetting('user_session'),
                'act': 'serial',
                'type': 'follow',
                'id': self.database.obtain_image_id(self.params['serial_id'])
            }
            post_data = urlencode(post_data)

            url = '{}ajaxik.php'.format(self.site_url)
            html = self.network.get_html(url=url, post=post_data)

            if '"on' in str(html):
                self.dialog.notification(heading='LostFilm',message='Добавлено',icon=icon,time=3000,sound=False)
            if 'off' in str(html):
                self.dialog.notification(heading='LostFilm',message='Удалено',icon=icon,time=3000,sound=False)
            if 'error' in str(html):
                self.dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)

            return
        
        if self.params['page'] == '1':
            self.params['page'] = '0'
            
        post_data = {
            'act': 'serial',
            'type':'search',
            'o': self.params['page'],
            's': '2',
            't':'99'
            }
        
        post_data = urlencode(post_data)

        url = '{}ajaxik.php'.format(self.site_url)
        html = self.network.get_html(url=url, post=post_data)
            
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not ':[{' in html:
            self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('LostFilm', 'Инициализация')
            
        try:
            html = html[html.find('[')+1:html.find(']')]

            data_array = html.split('},{')

            for i, data in enumerate(data_array):
                try:
                    if '\/movies\/' in data:
                        is_movie = True
                    else:
                        is_movie = False
                    
                    serial_title = data[data.find('title":"')+8:data.find('","title_orig')]

                    try:
                        serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                    except:
                        pass
                        
                    serial_id = data[data.find('"link":"')+8:]
                    serial_id = serial_id[:serial_id.find('"')]
                    serial_id = serial_id[serial_id.rfind('/')+1:]
                    serial_id = serial_id.strip()

                    image_id = data[data.find('"id":"')+6:]
                    image_id = image_id[:image_id.find('"')]

                    se_code = '{}001001'.format(image_id)

                    p = int((float(i+1) / len(data_array)) * 100)
                    
                    self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                        
                    if not self.database.content_in_db(serial_id):
                        self.create_info(serial_id=serial_id, ismovie=is_movie)

                    label = self.create_title(serial_title=serial_title)
                        
                    if is_movie:
                        self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                            'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                    else:
                        self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                            'mode': 'select_part', 'id': serial_id, 'code': se_code})
                except:
                    self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
        except:
            self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
                
        self.progress_bg.close()

        try:
            if len(data_array) >= 10:
                page_count = (int(self.params['page']) / 10) + 1
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 10)})
        except:
            pass
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page_{}'.format(self.site_url, self.params['param'], self.params['page'])

        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not '<div class="hor-breaker dashed">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('LostFilm', 'Инициализация')

        try:
            data_array = html[html.find('breaker dashed">')+16:html.rfind('<div class="hor-breaker dashed">')]
            data_array = data_array.split('<div class="hor-breaker dashed">')

            for i, data in enumerate(data_array):
                try:
                    is_movie = False
                    if 'data-ismovie="1' in data:
                        is_movie = True

                    is_watched = False
                    if 'haveseen-btn checked' in data:
                        is_watched = True

                    serial_title = data[data.find('name-ru">')+9:]
                    serial_title = serial_title[:serial_title.find('</div>')]
                    serial_title = u'[B]{}[/B]'.format(serial_title)
                    
                    if '/series/' in data:
                        serial_id = data[data.find('series/')+7:]
                        serial_id = serial_id[:serial_id.find('/')]

                    if '/movies/' in data:
                        serial_id = data[data.find('movies/')+7:]
                        serial_id = serial_id[:serial_id.find('"')]

                    serial_id = serial_id.strip()
            
                    se_code = data[data.find('episode="')+9:]
                    se_code = se_code[:se_code.find('"')]

                    if 'alpha">' in data:
                        episode_title = data[data.find('alpha">')+7:]
                        episode_title = episode_title[:episode_title.find('</div>')]
                        episode_title = unescape(episode_title).strip()
                        if episode_title:
                            serial_title = u'{}: {}'.format(serial_title, episode_title)

                    p = int((float(i+1) / len(data_array)) * 100)
                    
                    self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                    if not self.database.content_in_db(serial_id):
                        try:
                            self.create_info(serial_id=serial_id, ismovie=is_movie)
                        except:
                            pass

                    label = self.create_title(serial_title, se_code, watched=is_watched, ismovie=is_movie)

                    self.create_line(title=label, serial_id=serial_id, se_code=se_code, watched=is_watched, folder=False, ismovie=is_movie, params={
                                'mode': 'play_part', 'id': serial_id, 'param': se_code})
                except:
                    self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
        except:
            self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
            
        self.progress_bg.close()
        
        if '<div class="next-link active">' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={
                'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_movies_part(self):
        if self.params['code']:
            url = '{}movies/{}'.format(self.site_url, self.params['id'])
            html = self.network.get_html(url=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            movie_title = html[html.find('title-ru" itemprop="name">')+26:]
            movie_title = movie_title[:movie_title.find('</h1>')]
            movie_title = u'[B]{}[/B]'.format(movie_title)

            if '<div class="expected">' in html:
                label = u'[COLOR=dimgray]Ожидается | {}[/COLOR]'.format(movie_title)

                self.create_line(title=label, folder=False, params={})
            else:
                is_watched = False
                if 'isawthat-btn checked' in html:
                    is_watched = True

                label = self.create_title(movie_title, self.params['code'], watched=is_watched, ismovie=True)

                self.create_line(title=label, serial_id=self.params['id'], se_code=self.params['code'], watched=is_watched, folder=False, ismovie=True, params={
                                'mode': 'play_part', 'id': self.params['id'], 'param': self.params['code']})
        else:
            if self.params['page'] == '1':
                self.params['page'] = '0'

            post_data = {
                "act": "movies",
                "type": "search",
                "o": self.params['page'],
                "s": "3",
                "t": "0"
                }

            url = '{}ajaxik.php'.format(self.site_url)
            html = self.network.get_html(url=url, post=urlencode(post_data))

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            if not ':[{' in html:
                self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
                
            try:
                html = html[html.find('[')+1:html.find(']')]

                data_array = html.split('},{')

                for i, data in enumerate(data_array):
                    try:
                        if '\/movies\/' in data:
                            is_movie = True
                        else:
                            is_movie = False
                        
                        serial_title = data[data.find('title":"')+8:data.find('","title_orig')]

                        try:
                            serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                        except:
                            pass
                            
                        serial_id = data[data.find('"link":"')+8:]
                        serial_id = serial_id[:serial_id.find('"')]
                        serial_id = serial_id[serial_id.rfind('/')+1:]
                        serial_id = serial_id.strip()

                        image_id = data[data.find('"id":"')+6:]
                        image_id = image_id[:image_id.find('"')]

                        se_code = '{}001001'.format(image_id)

                        p = int((float(i+1) / len(data_array)) * 100)

                        self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                            
                        if not self.database.content_in_db(serial_id):
                            self.create_info(serial_id=serial_id, ismovie=is_movie)

                        label = self.create_title(serial_title=serial_title)

                        self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                            'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                    except:
                        self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
            except:
                self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
                    
            self.progress_bg.close()

            try:
                if len(data_array) >= 10:
                    page_count = (int(self.params['page']) / 10) + 1
                    label = u'[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                    self.create_line(title=label, params={'mode': self.params['mode'], 'page': (int(self.params['page']) + 10)})
            except:
                pass
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_serials_part(self):
        self.progress_bg.create('LostFilm', 'Инициализация')

        try:
            data_array = self.database.obtain_serials_id()
            data_array.sort()
        except:
            data_array = None

        try:
            for i, data in enumerate(data_array):
                try:
                    serial_id = data[1]

                    p = int((float(i+1) / len(data_array)) * 100)

                    self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                    if '0' in addon.getSetting('serials_mode'):
                        if '1' in data[3]:
                            label = self.create_title(serial_title=data[0], data_code=se_code, ismovie=True)
                            se_code = '{}001001'.format(data[2])
                            self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=True,
                                             params={'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                        else:
                            label = self.create_title(serial_title=data[0])
                            se_code = '{}001999'.format(data[2])
                            self.create_line(title=label, serial_id=serial_id, se_code=se_code, params={
                                'mode': 'select_part', 'id': serial_id, 'code': se_code})
                    else:
                        if '1' in data[3]:
                            label = self.create_title(serial_title=data[0], data_code=se_code, ismovie=True)
                            se_code = '{}001001'.format(data[2])
                            self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                        else:
                            label = self.create_title(serial_title=data[0])
                            se_code = '{}001999'.format(data[2])
                            self.create_line(title=label, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})
                except:
                    self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
        except:
            self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
            
        self.progress_bg.close()
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self, data_string=''):
        atl_names = bool(addon.getSetting('use_atl_names') == 'true')
        
        if not self.params['param']:
            url = '{}series/{}/seasons'.format(self.site_url, self.params['id'])
            html = self.network.get_html(url=url)
            
            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return    
            
            if '<div class="status">' in html: #and not atl_names:
                serial_status = html[html.find('<div class="status">')+20:]
                serial_status = serial_status[:serial_status.find('</span>')]
                serial_status = clean_list(serial_status)
                serial_status = serial_status.replace(u'Статус:','').strip()
                serial_status = u'{}'.format(serial_status)
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
            
            try:
                season_array = []

                for i, data in enumerate(data_array):
                    try:
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

                        p = int((float(i+1) / len(data_array)) * 100)

                        self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                        if 'PlayEpisode(' in data:
                            label = u'[B]{} {}[/B]'.format(title, season_status)

                            season_array.append(
                                u'{}|||{}'.format(label,se_code)
                            )
                        else:
                            if not atl_names:
                                label = u'[COLOR=dimgray][B]{}[/B][/COLOR]'.format(title)

                                season_array.append(
                                    u'{}|||{}'.format(label, se_code)
                            )
                    except:
                        self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})

                season_array.reverse()

                for se in season_array:
                    se = se.split('|||')
                    
                    self.create_line(title=se[0], serial_id=self.params['id'], se_code=se[1], status=serial_status, params={
                        'mode': 'select_part', 'param': se[1], 'id': self.params['id']})
            except:
                self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
                
            self.progress_bg.close()

        if self.params['param']:
            code = self.params['param']
            image_id = code[:len(code)-6]
            season_id = code[len(code)-6:len(code)-3]
            
            if data_string:
                html = data_string
            else:
                url = '{}series/{}/season_{}'.format(self.site_url, self.params['id'], int(season_id))
                html = self.network.get_html(url=url)

                if not html:
                    self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                    return
                
            try:
                url = '{}ajaxik.php'.format(self.site_url)
                post = {
                    "act": "serial",
                    "type": "getmarks",
                    "id": image_id
                    }                
                post = urlencode(post)

                watched_data = self.network.get_html(url=url, post=post)
            except:
                watched_data = []

            if '<div class="status">' in html:
                serial_status = html[html.find('<div class="status">')+20:]
                serial_status = serial_status[:serial_status.find('</span>')]
                serial_status = clean_list(serial_status)
                serial_status = serial_status.replace(u'Статус:','').strip()
                serial_status = u'{}'.format(serial_status)
            else:
                serial_status = ''

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            serial_title = html[html.find('ativeHeadline">')+15:html.find('</h2>')]
            
            data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
            data_array = data_array.split('<td class="alpha">')
            
            try:
                episode_array = []

                for i, data in enumerate(data_array):
                    try:
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
                        
                        p = int((float(i+1) / len(data_array)) * 100)

                        self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                        if 'data-code=' in data:
                            if atl_names:
                                label = u'{}.S{:>02}E{:>02}'.format(
                                    serial_title,
                                    int(se_code[len(se_code)-6:len(se_code)-3]),
                                    int(se_code[len(se_code)-3:len(se_code)])
                                    )
                            else:
                                label = self.create_title(serial_title=episode_title, watched=is_watched, data_code=se_code)
                                                            
                            episode_array.append(
                                u'{}|||{}|||{}'.format(label, se_code, is_watched)
                                )
                        else:
                            if not atl_names:
                                label = '[COLOR=dimgray]S{:>02}E{:02} | {}[/COLOR]'.format(
                                    int(season_id), len(data_array), episode_title)
                                
                                episode_array.append(
                                    u'{}'.format(label)
                                    )
                    except:
                        self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})

                episode_array.reverse()

                for ep in episode_array:
                    ep = ep.split('|||')

                    if len(ep) < 3:
                        self.create_line(title=ep[0], folder=False, params={})
                    else:
                        self.create_line(title=ep[0], serial_id=self.params['id'], se_code=ep[1], status=serial_status, watched=bool(ep[2]=='True'), folder=False, params={
                            'mode': 'play_part', 'id': self.params['id'], 'param': ep[1]})

            except:
                self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})

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
            

            html = self.network.get_html(url=url)         

            new_url = html[html.find('url=http')+4:html.find('&newbie=')]

            from network import WebTools
            self.net = WebTools()
            del WebTools

            html = self.net.get_html(url=new_url)

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

            file_name = '{}.torrent'.format(se_code)
            torrent_file = os.path.join(self.torrents_dir, file_name)

            content = self.net.get_bytes(url=url)
            
            with open(torrent_file, 'wb') as write_file:
                write_file.write(content)

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

        if 'catalog' in self.params['param']:
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
                
            url = '{}ajaxik.php'.format(self.site_url)

            html = self.network.get_html(url=url, post=urlencode(post_data))
                
            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
                
            if not ':[{' in html:
                self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
                
            try:
                html = html[html.find('[')+1:html.find(']')]
                
                data_array = html.split('},{')

                for i, data in enumerate(data_array):
                    try:
                        if '\/movies\/' in data:
                            is_movie = True
                        else:
                            is_movie = False
                        
                        serial_title = data[data.find('title":"')+8:data.find('","title_orig')]

                        try:
                            serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                        except:
                            pass
                            
                        serial_id = data[data.find('"link":"')+8:]
                        serial_id = serial_id[:serial_id.find('"')]
                        serial_id = serial_id[serial_id.rfind('/')+1:]
                        serial_id = serial_id.strip()

                        image_id = data[data.find('"id":"')+6:]
                        image_id = image_id[:image_id.find('"')]

                        se_code = '{}001001'.format(image_id)

                        p = int((float(i+1) / len(data_array)) * 100)

                        self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                            
                        if not self.database.content_in_db(serial_id):
                            self.create_info(serial_id=serial_id, ismovie=is_movie)

                        label = self.create_title(serial_title=serial_title)
                            
                        if is_movie:
                            self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                                'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                        else:
                            self.create_line(title=label, serial_id=serial_id, se_code=se_code, ismovie=is_movie, params={
                                'mode': 'select_part', 'id': serial_id, 'code': se_code})
                    except:
                        self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
            except:
                self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
                    
            self.progress_bg.close()

            try:
                if len(data_array) >= 10:
                    page_count = (int(self.params['page']) / 10) + 1
                    label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                    self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 10)})
            except:
                pass
            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_play_part(self):
        se_code = self.params['param']
        serial_episode = int(se_code[len(se_code)-3:len(se_code)])
        serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
        image_id = int(se_code[:len(se_code)-6])

        url = '{}v_search.php?c={}&s={}&e={}'.format(
            self.site_url, image_id, serial_season, serial_episode)

        html = self.network.get_html(url=url)
        
        new_url = html[html.find('url=http')+4:html.find('&newbie=')]

        from network import WebTools
        self.net = WebTools()
        del WebTools

        html = self.net.get_html(url=new_url)

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

        html = self.net.get_bytes(url=url)

        file_name = '{}.torrent'.format(se_code)
        
        torrent_file = os.path.join(self.torrents_dir, file_name)
        
        with open(torrent_file, 'wb') as write_file:
            write_file.write(html)

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
            
            try:
                data = urlencode(data)
            except:
                pass

            html = self.network.get_html(url=url, post=data)
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

def start():
    lostfilm = Lostfilm()
    lostfilm.execute()
    del lostfilm

gc.collect()