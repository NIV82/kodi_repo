# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

version = int(xbmc.getInfoLabel('System.BuildVersion')[:2])

if version >= 19:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.request import urlopen
    from urllib.parse import parse_qs
    from html import unescape
else:
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urllib import urlopen
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

if version >= 19:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
    plugin_dir = xbmcvfs.translatePath('special://home/addons/plugin.niv.lostfilm')
else:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))
    plugin_dir = fs_enc(xbmc.translatePath('special://home/addons/plugin.niv.lostfilm'))

progress_bg = xbmcgui.DialogProgressBG()
dialog = xbmcgui.Dialog()

if not os.path.exists(addon_data_dir):
    os.makedirs(addon_data_dir)

torrents_dir = os.path.join(addon_data_dir, 'torrents')
if not os.path.exists(torrents_dir):
    os.mkdir(torrents_dir)

class Lostfilm:
    def __init__(self):
        self.context_menu = []

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.sid_file = os.path.join(addon_data_dir, 'lostfilm.sid')

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'code': ''}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

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

        self.create_tclean()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(addon_data_dir, 'lostfilms.db')):
            self.create_database()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(addon_data_dir, 'lostfilms.db'))
        del DataBase
#========================#========================#========================#
    def create_tclean(self):
        try:
            clean_session = float(addon.getSetting('clean_session'))
        except:
            clean_session = 0

        if time.time() - clean_session > 604800:
            addon.setSetting('clean_session', str(time.time()))

            data_array = os.listdir(torrents_dir)

            try:
                for data in data_array:
                    file_path = os.path.join(torrents_dir, data)
                    try:
                        os.remove(file_path)
                    except:
                        pass
            except:
                pass
        return
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
            dialog.notification(heading='LostFilm', message='Введите Логин и Пароль', icon=icon, time=3000, sound=False)
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
            dialog.notification(heading='Авторизация', message='Проверьте Логин и Пароль', icon=icon, time=3000, sound=False)
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
        target_path = os.path.join(addon_data_dir, 'lostfilms.db')

        try:
            os.remove(target_path)
        except:
            pass

        progress_bg.create(u'Загрузка Базы Данных')

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
                        progress_bg.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                    except:
                        pass
            try:
                dialog.notification(heading='Загрузка файла',message='Успешно загружено',icon=icon,time=3000,sound=False)
            except:
                pass
        except:
            try:
                dialog.notification(heading='Загрузка файла',message='Ошибка при загрузке',icon=icon,time=3000,sound=False)
            except:
                pass

        progress_bg.close()
        
        return
#========================#========================#========================#
    def colorize(self, data):
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
    def create_info_data(self, serial_id='', se_code='', is_movie=False, is_watched=False, status='', sorttitle=''):
        info = {
            'serial_id':serial_id,
            'sorttitle': sorttitle,
            'cover': '',
            'genre': '',
            'studio': '',
            'director': '',
            'writer': '',
            'premiered': '',
            'country': '',
            'plot': '',
            'playcount': 0,
            'status': status,
            'se_code': se_code,
            'cast': [],
            'ismovie': is_movie,
        }

        if serial_id:
            info.update(self.database.obtain_content(serial_id))
            
            info_cast = self.database.obtain_cast(serial_id=serial_id)
            if info_cast:
                info['cast'] = self.create_cast(info_cast)

        if se_code:
            info['cover'] = self.create_image(se_code=se_code, ismovie=is_movie)
        
        if is_watched:
            info['playcount'] = 1

        return info
#========================#========================#========================#
    def create_image(self, se_code, ismovie=False):
        serial_episode = int(se_code[len(se_code)-3:len(se_code)])
        serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
        serial_image = int(se_code[:len(se_code)-6])

        if serial_season == 999:
            serial_season = 1

        image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_image, serial_season)

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

            if version >= 20:
                actors.append(xbmc.Actor(
                    name=node[0], role=node[1], order=1, thumbnail=node[2]))
            else:
                actors.append(
                    {'name': node[0], 'role': node[1], 'thumbnail':node[2]})

        return actors
#========================#========================#========================#
    def create_line(self, title, params={}, folder=True, image=None, **info):
        li = xbmcgui.ListItem(title)

        serial_data = {}

        if info:
            serial_data['serial_id'] = info.pop('serial_id')
            serial_data['se_code'] = info.pop('se_code')
            serial_data['ismovie'] = info.pop('ismovie')

            status = info.pop('status')
            cover = info.pop('cover')
            cast = info.pop('cast')

            if cover:
                li.setArt({
                    "poster": cover,
                    #"icon": cover,
                    #"icon": image,
                    "thumb": cover
                    })

            try:
                info['title'] = info['sorttitle']
            except:
                pass

            if version >= 20:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setTitle(title)
                videoinfo.setPremiered(info['premiered'])
                videoinfo.setGenres(info['genre'])
                videoinfo.setDirectors(info['director'])
                videoinfo.setWriters(info['writer'])
                videoinfo.setStudios(info['studio'])
                videoinfo.setTvShowStatus(status)
                videoinfo.setCountries(info['country'])
                videoinfo.setPlot(info['plot'])
                videoinfo.setCast(cast)
                videoinfo.setPlaycount(info['playcount'])
            else:
                li.setCast(cast)
                info.update({'status': status})
                li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.context_menu)

        if image:
            li.setArt({"icon": image})

        if folder==False:
            li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))
        # if 'tam' in params:
        #     label = u'{} | {}'.format(info['title'], title)

        #     if version <= 18:
        #         try:
        #             label = label.encode('utf-8')
        #         except:
        #             pass

        #     info_data = repr({'title':label})
        #     url='plugin://plugin.video.tam/?mode=open&info={}&url={}'.format(quote_plus(info_data), quote(params['tam']))
        # else:
        #     url = '{}?{}'.format(sys.argv[0], urlencode(params))

        #xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
        return
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

        title_ru = html[html.find('itemprop="name">')+16:]
        title_ru = title_ru[:title_ru.find('</h1>')]
        info['title_ru'] = title_ru.replace('/', '-')

        description = html[html.find(u'Описание</h2>'):]
        description = description[:description.find('<div class="social-pane">')]
        
        if u'Сюжет' in description:
            description = description[description.find(u'Сюжет')+5:]
        else:
            description = description[description.find('description">')+13:]
        
        description = description[:description.find('</div>')]
        description = unescape(description)

        if u'<strong class="bb">Сюжет' in description:
            description = u'Сюжет {}'.format(description)

        if description:
            if ':' in description[0]:
                description = description[1:]

            from utility import clean_tags
            info['description'] = clean_tags(description)

        if 'dateCreated"' in html:
            data = html[html.find('dateCreated"'):html.find('</a></span><br />')+4]

            aired_on = data[data.find('content="')+9:]
            aired_on = aired_on[:aired_on.find('"')]
            info['aired_on'] = aired_on

            if u'Страна:' in data:
                studios = data[data.find(u'Страна:')+7:]
                studios = studios[:studios.find('<br />')]

                if '(' and ')' in studios:
                    info['country'] = data[data.find('(')+1:data.find(')')]

                studio = studios[studios.find('">')+2:]
                studio = studio[:studio.find('</a>')]
                studio = studio.strip()
                info['studios'] = u'{}'.format(studio)

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

                    if 'autoload="' in c:
                        thumbnail = c[c.find('autoload="')+10:]
                        thumbnail = thumbnail[:thumbnail.find('"')]
                        thumbnail = thumbnail[thumbnail.rfind('/')+1:]
                        cast_node['thumbnail'] = u'{}'.format(thumbnail.strip())

                    if 'actors' in title:
                        role = c[c.find('role-ru">')+9:]
                        role = role[:role.find('</div>')]
                        role = role.replace('*','').replace('\t','')
                        cast_node['role'] = u'{}'.format(role.strip())
                        node = u'|'.join(list(cast_node.values()))
                    else:
                        node = u'{}'.format(cast_node['name'])

                    if info[title]:
                        info[title] = u'{}*{}'.format(info[title], node)
                    else:
                        info[title] = u'{}'.format(node)
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
        return
#========================#========================#========================#
    def exec_information_part(self):
        from info import update_info
        dialog.textviewer('Информация', update_info)
        return
#========================#========================#========================#
    def exec_library_part(self):

        if 'create_source' in self.params['param']:
            import library.manage as manage
            manage.create_source()

        if 'create_media' in self.params['param']:
            import library.manage as manage
            manage.create_tvshows(serial_id=self.params['id'])
        
        if 'update_media' in self.params['param']:
            import library.manage as manage
            manage.update_tvshows()
        
        if 'manage' in self.params['param']:
            media_items = os.listdir(os.path.join(addon_data_dir, 'library'))

            if len(media_items) < 1:
                dialog.notification(heading='Медиатека',message='Медиатека пуста',icon=icon,time=1000,sound=False)
                return

            for serial_id in media_items:
                image_id = self.database.obtain_image_id(serial_id)
                is_movie = self.database.obtain_is_movie(serial_id)
                title_ru = self.database.obtain_title_ru(serial_id)

                se_code = '{}001999'.format(image_id)

                info = self.create_info_data(serial_id=serial_id, se_code=se_code, is_movie=is_movie)

                self.context_menu = [
                    ('Удалить из Медиатеки', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=remove_media&id={}")'.format(serial_id)),
                    ('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")')
                ]

                self.create_line(title=title_ru, params={'mode': 'select_part', 'id': serial_id, 'code': se_code}, **info)

            xbmcplugin.endOfDirectory(handle, succeeded=True)
        
        if 'remove_media' in self.params['param']:
            from library.manage import library_path

            serial_dir = os.path.join(library_path, self.params['id'])

            if not os.path.isdir(serial_dir):
                return

            for item in os.listdir(serial_dir):
                full_path = os.path.join(serial_dir, item)
                os.remove(full_path)

            os.rmdir(serial_dir)

            dialog.notification(heading='Медиатека',message='Сериал Удален',icon=icon,time=1000,sound=False)

        return
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
                dialog.notification(heading='LostFilm',message='Выполнено',icon=icon,time=3000,sound=False)
            if 'error' in str(html):
                dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)
        return
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            dialog.notification(heading='LostFilm',message='Выполнено',icon=icon,time=3000,sound=False)
        except:
            dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=3000,sound=False)
            pass

        return
#========================#========================#========================#
    def exec_main_part(self):
        xbmcplugin.setContent(handle, '')

        self.context_menu = [
            ('Обновить Авторизацию', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_authorization")'),
            ('Обновить Базу Данных', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_database")'),
            ('Обновить Прокси', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_proxy_data")'),
            ('Новости обновлений', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part")')
        ]
        self.create_line(title=self.colorize('Поиск'), params={'mode': 'search_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'search.png'))
        self.create_line(title=self.colorize('Расписание'), params={'mode': 'schedule_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'schedule.png'))
        self.create_line(title=self.colorize('Избранное'), params={'mode': 'favorites_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'fav.png'))
        self.create_line(title=self.colorize('Новинки'), params={'mode': 'common_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'new.png'))
        self.create_line(title=self.colorize('Фильмы'), params={'mode': 'films_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'movies.png'))
        self.create_line(title=self.colorize('Все сериалы'), params={'mode': 'serials_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'series.png'))
        self.create_line(title=self.colorize('Каталог'), params={'mode': 'catalog_part'},
                        image=os.path.join(plugin_dir, 'resources', 'media', 'catalog.png'))
        
        if 'true' in addon.getSetting('show_librarynode'):
            self.create_line(title='[B]Медиатека[/B]', params={'mode': 'library_part', 'param': 'manage'},
                            image=os.path.join(plugin_dir, 'resources', 'media', 'medialib.png'))
            
        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            xbmcplugin.setContent(handle, '')
            self.create_line(title='Поиск по названию', params={'mode': 'search_part', 'param': 'search_word'},
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'search.png'))

            data_array = addon.getSetting('search').split('|')
            data_array.reverse()

            self.context_menu = [
                ('Очистить историю', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=clean_part")')
                ]
            
            for data in data_array:
                if data == '':
                    continue
                try:
                    self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param':'search_string', 'search_string': data},
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'tags.png'))
                except:
                    continue

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                if not self.params['search_string'] == '':
                    data_array = addon.getSetting('search').split('|')
                    while len(data_array) >= 6:
                        data_array.pop(0)
                    data_array.append(self.params['search_string'])
                    addon.setSetting('search', '|'.join(data_array))
                    self.params['param'] = 'search_string'
                else:
                    return False
            else:
                return False

        if 'search_string' in self.params['param']:
            if self.params['search_string'] == '':
                return False

            url = '{}search/?q={}'.format(self.site_url, quote(self.params['search_string']))
            html = self.network.get_html(url=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'},
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            if not '<div class="hor-breaker dashed">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']},
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return

            progress_bg.create('LostFilm', 'Инициализация')

            try:
                data_array = html[html.find('breaker dashed">')+16:html.rfind('<div class="hor-breaker dashed">')]
                data_array = data_array.split('<div class="hor-breaker dashed">')
                
                for i, data in enumerate(data_array):
                    try:
                        is_movie = False

                        serial_title = data[data.find('name-ru">')+9:]
                        serial_title = serial_title[:serial_title.find('</div>')]

                        if '/series/' in data:
                            serial_id = data[data.find('series/')+7:]
                            serial_id = serial_id[:serial_id.find('"')]

                        if '/movies/' in data:
                            serial_id = data[data.find('movies/')+7:]
                            serial_id = serial_id[:serial_id.find('"')]
                            is_movie = True

                        serial_id = serial_id.strip()

                        image_id = data[data.find('Images/')+7:]
                        image_id = image_id[:image_id.find('/')].strip()

                        se_code = '{}001999'.format(image_id)

                        p = int((float(i+1) / len(data_array)) * 100)

                        progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                        if not self.database.content_in_db(serial_id):
                            self.create_info(serial_id)

                        info = self.create_info_data(serial_id=serial_id,se_code=se_code,is_movie=is_movie, sorttitle=serial_title)

                        label = self.create_title(serial_title=serial_title)

                        self.context_menu = [
                            ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                            ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie)),
                            ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)),
                            ('Добавить в Медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=create_media&id={}&ismovie={}")'.format(serial_id, is_movie)),
                            ('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")')
                        ]

                        if is_movie:
                            self.context_menu.append(
                                ('Перейти к Фильму', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=movies_part&id={}&code={}001001")'.format(serial_id,image_id))
                                )
                            self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code},
                                             image=os.path.join(plugin_dir, 'resources', 'media', 'movies.png'), **info)
                        else:
                            self.context_menu.append(
                                ('Перейти к Сериалу', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=select_part&id={}&code={}001999")'.format(serial_id,image_id))
                            )
                            self.create_line(title=label, params={'mode': 'select_part', 'id': serial_id, 'code': se_code},
                                             image=os.path.join(plugin_dir, 'resources', 'media', 'series.png'), **info)
                    except:
                        self.create_line(title='Ошибка обработки строки',
                                         image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            except:
                self.create_line(title='Ошибка - сообщите автору',
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))

            progress_bg.close()

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_schedule_part(self):
        xbmcplugin.setContent(handle, '')
        url = '{}schedule/{}'.format(self.site_url, self.params['param'])

        html = self.network.get_html(url=url)
        
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
                
        if not '<tbody>' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        table = html[html.find('<th class'):html.find('</tbody>')]
        
        if version < 19:
            try:
                table = table.encode('utf-8')
            except:
                pass

        schedule_table = []
        count = 0
        start = table.find('<th class="')

        while start > -1 and count < 5:
            schedule = []

            header = table[:table.find('<th></th>')]
            header = header[:header.rfind('</th>')]
            header = header.split('</th>')

            for h in header:
                try:
                    if 'inactive' in h:
                        h = '***'
                    else:
                        if 'today' in h:
                            h = 'Сегодня'
                        else:
                            h = h[h.find('">')+2:]

                    h = h.replace('Вт', 'Вторник -').replace('Ср', 'Среда -')
                    h = h.replace('Чт', 'Четверг -').replace('Пт', 'Пятница -')
                    h = h.replace('Сб', 'Суббота -').replace('Вс', 'Воскресенье -')
                    h = h.replace('Пн', 'Понедельник -')
                except:
                    h = 'Ошибка'

                schedule.append([h])
            
            table = table[table.find('</tr>')+5:]
            
            lines = table[:table.find('<th></th>')]
            lines = lines[lines.find('<div class="table'):lines.rfind('<td class="')]
            lines = lines.split('<tr>')

            for line in lines:
                line = line[line.find('<div class="table'):line.rfind('</div>')]
                line = line.split('</td>')
                
                for i,node in enumerate(line):
                    if 'title">' in node:
                        title = node[node.find('title">'):node.find('</span>')]

                        try:
                            if '<span>' in title:
                                code = title[title.find('<span>')+6:]
                                code = code.strip()
                                code = code.replace('x','|').replace('х','|')
                                code = code.replace('ДОП','00').replace('-','|').split('|')

                                if len(code) > 2:
                                    code = '[COLOR=blue]S{:>02}[/COLOR][COLOR=lime]E{:>02}-{:>02}[/COLOR]'.format(
                                        int(code[0]), int(code[1]), int(code[2]))
                                else:
                                    code = '[COLOR=blue]S{:>02}[/COLOR][COLOR=lime]E{:>02}[/COLOR]'.format(int(code[0]),int(code[1]))

                            if '</a>' in title:
                                code = '[COLOR=blue]Фильм[/COLOR]'
                        except:
                            code = '[COLOR=red]Ошибка[/COLOR]'

                        title = title[title.find('>')+1:title.find('<')]

                        try:
                            title = '{} | {}'.format(code, title)
                        except:
                            title = '[COLOR=red]Ошибка[/COLOR]'
                        
                        schedule[i].append(title)

            schedule_table.extend(schedule)

            table = table[table.find('<th></th>')+9:]

            start = table.find('<th class="')
            count = count + 1

        for i,x in enumerate(schedule_table):
            if 'Сегодня' in x[0]:
                schedule_table = schedule_table[i:]

        try:
            for sch in schedule_table:
                if '***' in sch[0] or len(sch) < 2:
                    continue

                self.create_line(title='[B]{}[/B]'.format(sch[0]), folder=False,
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'schedule.png'))
                series = sch[1:]
                
                try:
                    for ep in series:
                        self.create_line(title=ep, folder=False,
                                         image=os.path.join(plugin_dir, 'resources', 'media', 'empty.png'))
                except:
                    self.create_line(title='Ошибка обработки строки',
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
        except:
            self.create_line(title='Ошибка - сообщите автору',
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
        
        if 'next-link active' in html:
            next_link = html[html.find('next-link active'):]
            next_link = next_link[next_link.find('/schedule/')+10:next_link.find('<div')]
            
            title = next_link[next_link.rfind('>')+1:].capitalize()
            
            if sys.version_info.major < 3:
                try:
                    title = title.encode('utf-8')
                except:
                    pass

            next_link = next_link[:next_link.find('\'')]

            label = 'Следующий - [COLOR=gold]{}[/COLOR]'.format(title)
            self.create_line(title=label, params={'mode': 'schedule_part', 'param': next_link},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'next.png'))

        xbmcplugin.endOfDirectory(handle, succeeded=True)
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
                dialog.notification(heading='LostFilm',message='Добавлено',icon=icon,time=1000,sound=False)
            if 'off' in str(html):
                dialog.notification(heading='LostFilm',message='Удалено',icon=icon,time=1000,sound=False)
            if 'error' in str(html):
                dialog.notification(heading='LostFilm',message='Ошибка',icon=icon,time=1000,sound=False)

            return
        
        url = '{}my/type_1'.format(self.site_url)
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        if not '<div class="serial-box">' in html:
            self.create_line(title='Контент отсутствует', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        data_array = html[html.find('<div class="serial-box">')+24:]
        data_array = data_array[:data_array.find('<div class="bottom-push"></div>')]
        data_array = data_array.split('<div class="serial-box">')

        progress_bg.create('LostFilm', 'Инициализация')

        try:
            for i, data in enumerate(data_array):
                try:
                    image_id = data[data.find('/Images/')+8:]
                    image_id = image_id[:image_id.find('/')]
                    se_code = '{}001001'.format(image_id)

                    serial_id = data[data.find('href="/')+7:]
                    serial_id = serial_id[:serial_id.find('"')]

                    is_movie = False
                    if 'movies/' in serial_id:
                        is_movie = True
                    
                    serial_id = serial_id[serial_id.find('/')+1:]
                    serial_id = serial_id.strip()

                    serial_title = data[data.find('title-ru">')+10:]
                    serial_title = serial_title[:serial_title.find('<')]
                    serial_title = serial_title.strip()

                    p = int((float(i+1) / len(data_array)) * 100)
                    progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                    if not self.database.content_in_db(serial_id):
                        self.create_info(serial_id=serial_id, ismovie=is_movie)
                    
                    info = self.create_info_data(serial_id=serial_id,se_code=se_code,is_movie=is_movie,sorttitle=serial_title)

                    self.context_menu = [
                        ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                        ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie)),
                        ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)),
                        ('Добавить в Медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=create_media&id={}&ismovie={}")'.format(serial_id, is_movie)),
                        ('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")')
                        ]

                    if is_movie:
                        label = self.create_title(serial_title=serial_title, data_code=se_code, ismovie=True)
                        self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code}, **info)
                    else:
                        label = self.create_title(serial_title=serial_title)
                        self.create_line(title=label, params={'mode': 'select_part', 'id': serial_id, 'code': se_code}, **info)
                except:
                    self.create_line(title='Ошибка обработки строки', folder=False,
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
        except:
            self.create_line(title='Ошибка - сообщите автору', folder=False,
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))

        progress_bg.close()

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}new/page_{}'.format(self.site_url, self.params['page'])

        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<div class="hor-breaker dashed">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        progress_bg.create('LostFilm', 'Инициализация')
        
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
                    
                    progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                    if not self.database.content_in_db(serial_id):
                        try:
                            self.create_info(serial_id=serial_id, ismovie=is_movie)
                        except:
                            pass

                    info = self.create_info_data(serial_id=serial_id,se_code=se_code,is_movie=is_movie, is_watched=is_watched, sorttitle=serial_title)

                    label = self.create_title(serial_title, se_code, watched=is_watched, ismovie=is_movie)

                    self.context_menu = [
                        ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                        ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie)),
                        ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)),
                        ('Отметить как просмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(se_code)),
                        ('Отметить как непросмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(se_code))
                        ]

                    if not is_movie:
                        self.context_menu.append(('Перейти к Сериалу', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=select_part&id={}&code={}001999")'.format(serial_id,se_code[0:3])))
                        self.context_menu.append(('Добавить в Медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=create_media&id={}&ismovie={}")'.format(serial_id, is_movie)))
                        self.context_menu.append(('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")'))
                    else:
                        self.context_menu.append(('Перейти к Фильму', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=movies_part&id={}&code={}001001")'.format(serial_id,se_code[0:3])))

                    self.create_line(title=label, folder=False, params={'mode': 'play_part', 'id': serial_id, 'param': se_code}, **info)
                except:
                    self.create_line(title='Ошибка обработки строки',
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
        except:
            self.create_line(title='Ошибка - сообщите автору',
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            
        progress_bg.close()

        if '<div class="next-link active">' in html:
            self.context_menu = []
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'next.png'))

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_films_part(self):
        xbmcplugin.setContent(handle, 'videos')

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
            self.create_line(title='Ошибка получения данных', params={'mode': self.params['mode']},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not ':[{' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        progress_bg.create('LostFilm', 'Инициализация')
                
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

                    progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                            
                    if not self.database.content_in_db(serial_id):
                        self.create_info(serial_id=serial_id, ismovie=is_movie)

                    info = self.create_info_data(serial_id=serial_id,se_code=se_code,is_movie=is_movie, sorttitle=serial_title)

                    label = self.create_title(serial_title=serial_title)

                    self.context_menu = [
                        ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                        ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie)),
                        ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)),
                        ('Отметить как просмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(se_code)),
                        ('Отметить как непросмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(se_code))
                        ]

                    self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code}, **info)
                except:
                    self.create_line(title='Ошибка обработки строки',
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
        except:
            self.create_line(title='Ошибка - сообщите автору',
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                    
        progress_bg.close()

        try:
            if len(data_array) >= 10:
                page_count = (int(self.params['page']) / 10) + 1
                label = u'[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'page': (int(self.params['page']) + 10)},
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'next.png'))
        except:
            pass

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_movies_part(self):
        url = '{}movies/{}'.format(self.site_url, self.params['id'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': self.params['mode']},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        movie_title = html[html.find('title-ru" itemprop="name">')+26:]
        movie_title = movie_title[:movie_title.find('</h1>')]
        movie_title = u'[B]{}[/B]'.format(movie_title)

        info = self.create_info_data(
            serial_id=self.params['id'], 
            se_code='{}001001'.format(self.params['code'][:-6]),
            is_movie=True, 
            sorttitle=movie_title
            )

        if '<div class="expected">' in html:
            label = u'[COLOR=dimgray]Ожидается | {}[/COLOR]'.format(info['sorttitle'])
            self.create_line(title=label, folder=False, params={})
        else:
            is_watched = False
            if 'isawthat-btn checked' in html:
                is_watched = True
                info['playcount'] = 1

            self.context_menu = [
                ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(self.params['id'], True)),
                ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(self.params['id'], info['se_code'])),
                ('Отметить как просмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(info['se_code'])),
                ('Отметить как непросмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(info['se_code'])),
            ]

            label = self.create_title(info['sorttitle'], info['se_code'], watched=is_watched, ismovie=True)
            self.create_line(title=label, folder=False, params={'mode': 'play_part', 'id': info['serial_id'], 'param': info['se_code']}, **info)

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_serials_part(self):
        progress_bg.create('LostFilm', 'Инициализация')

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

                    progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))


                    if '1' in data[3]:
                        se_code='{}001001'.format(data[2])
                        is_movie = True

                        self.context_menu = [
                            ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                            ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie)),
                            ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code))
                        ]
                    else:
                        se_code='{}001999'.format(data[2])
                        is_movie = False

                        self.context_menu = [
                            ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                            ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie)),
                            ('Добавить в Медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=create_media&id={}&ismovie={}")'.format(serial_id, is_movie)),
                            ('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")')
                        ]

                    if '0' in addon.getSetting('serials_mode'):
                        if '1' in data[3]:
                            info = self.create_info_data(serial_id=serial_id, se_code=se_code, is_movie=is_movie, sorttitle=data[0])
                            label = self.create_title(serial_title=data[0], data_code=se_code, ismovie=is_movie)
                            self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code}, **info)
                        else:
                            info = self.create_info_data(serial_id=serial_id, se_code=se_code, sorttitle=data[0])
                            label = self.create_title(serial_title=data[0])
                            self.create_line(title=label, params={'mode': 'select_part', 'id': serial_id, 'code': se_code}, **info)
                    else:
                        if '1' in data[3]:
                            label = self.create_title(serial_title=data[0], data_code=se_code, ismovie=is_movie)
                            self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code})
                        else:
                            label = self.create_title(serial_title=data[0])
                            self.create_line(title=label, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})
                except:
                    self.create_line(title='Ошибка обработки строки',
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
        except:
            self.create_line(title='Ошибка - сообщите автору',
                             image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            
        progress_bg.close()

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self, data_string=''):

        atl_names = bool(addon.getSetting('use_atl_names') == 'true')

        if not self.params['param']:
            url = '{}series/{}/seasons'.format(self.site_url, self.params['id'])
            html = self.network.get_html(url=url)
            
            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'},
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return    

            serial_status = ''
            if '<div class="status">' in html: #and not atl_names:
                serial_status = html[html.find('<div class="status">')+20:]
                serial_status = serial_status[:serial_status.find('</span>')]
                serial_status = serial_status.replace(u'Статус:','')
                serial_status = serial_status.strip()

            image_id = self.params['code'][:len(self.params['code'])-6]

            data_array = html[html.find('<h2>')+4:html.rfind('holder"></td>')+13]
            data_array = data_array.split('<h2>')
            data_array.reverse()

            # if len(data_array) < 2:
            #     params={'mode': 'select_part', 'param': '{}001999'.format(image_id), 'id': self.params['id']}
            #     self.exec_select_part(data_string=html)
            #     return

            info = self.create_info_data(serial_id=self.params['id'], status=serial_status)

            progress_bg.create('LostFilm', 'Инициализация')
            
            try:
                for i, data in enumerate(data_array):
                    try:
                        season_status = ''
                        if '<div class="details">' in data:
                            season_status = data[data.find('<div class="details">')+21:]
                            season_status = season_status[:season_status.find('<div class')]
                            season_status = season_status.replace(u'Статус:','').strip()
                            
                            if u'Идет' in season_status:
                                season_status = u'| [COLOR=gold]{}[/COLOR]'.format(season_status)
                            else:
                                season_status = u'| [COLOR=blue]{}[/COLOR]'.format(season_status)

                        title = data[:data.find('</h2>')]

                        season = title.replace(u'сезон','').strip()
                        season = season.replace(u'Дополнительные материалы', '999')

                        se_code = '{}{:>03}999'.format(image_id, int(season))
                        info['se_code'] = se_code
                        info['cover'] = self.create_image(se_code=se_code)

                        p = int((float(i+1) / len(data_array)) * 100)

                        progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                        
                        if 'PlayEpisode(' in data:
                            label = u'[B]{} {}[/B]'.format(title, season_status)

                            self.context_menu = [
                                ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(self.params['id'], se_code))
                            ]

                            self.create_line(title=label, params={'mode': 'select_part', 'param': se_code, 'id': self.params['id']}, **info)
                        else:
                            if not atl_names:
                                label = u'[COLOR=dimgray][B]{}[/B][/COLOR]'.format(title)
                                self.create_line(title=label, folder=False)
                    except:
                        self.create_line(title='Ошибка обработки строки',
                                         image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            except:
                self.create_line(title='Ошибка - сообщите автору',
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                
            progress_bg.close()

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
                    self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'},
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                    xbmcplugin.endOfDirectory(handle, succeeded=True)
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

            serial_status = ''
            if '<div class="status">' in html: #and not atl_names:
                serial_status = html[html.find('<div class="status">')+20:]
                serial_status = serial_status[:serial_status.find('</span>')]
                serial_status = serial_status.replace(u'Статус:','')
                serial_status = serial_status.strip()
            
            info = self.create_info_data(
                serial_id=self.params['id'],
                se_code=self.params['param'],
                status = serial_status
                )

            progress_bg.create('LostFilm', 'Инициализация')
            
            serial_title = html[html.find('ativeHeadline">')+15:html.find('</h2>')]
            
            data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
            data_array = data_array.split('<td class="alpha">')
            data_array.reverse()
            
            try:
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

                        progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                        if 'data-code=' in data:
                            if atl_names:
                                label = u'{}.S{:>02}E{:>02}'.format(
                                    serial_title,
                                    int(se_code[len(se_code)-6:len(se_code)-3]),
                                    int(se_code[len(se_code)-3:len(se_code)])
                                    )
                            else:
                                label = self.create_title(serial_title=episode_title, watched=is_watched, data_code=se_code)
                            
                            info['se_code'] = se_code

                            self.context_menu = [
                                ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(self.params['id'], False)),
                                ('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(self.params['id'], se_code)),
                                ('Отметить как просмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(se_code)),
                                ('Отметить как непросмотренное', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(se_code)),
                                ('Добавить в Медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=create_media&id={}&ismovie={}")'.format(self.params['id'], False)),
                                ('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")')
                            ]

                            self.create_line(title=label, folder=False, params={'mode': 'play_part', 'id': self.params['id'], 'param': se_code}, **info)
                        else:
                            if not atl_names:

                                label = '[COLOR=dimgray]S{:>02}E{:02} | {}[/COLOR]'.format(
                                    int(season_id), len(data_array), episode_title)

                                self.create_line(title=label, folder=False)
                    except:
                        self.create_line(title='Ошибка обработки строки',
                                         image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            except:
                self.create_line(title='Ошибка - сообщите автору',
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))

            progress_bg.close()

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
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


            new_url = html[html.find('url=http')+4:]
            new_url = new_url[:new_url.find('"')]

            from network import get_web
            html = get_web(url=new_url)

            if u'Контент недоступен на территории' in html:
                label = u'Контент недоступен на территории Российской Федерации\nПриносим извинения за неудобства'
                dialog.ok(u'LostFilm', label)
                return
            
            data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
            data_array = data_array.split('<div class="inner-box--label">')
            
            is_movie = False
            if u'Фильм' in html:
                is_movie = True

            info = self.create_info_data(serial_id=self.params['id'], se_code=se_code, is_movie=is_movie)

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
                        
                result = dialog.select('Доступное качество: ', choice)
                result_quality = choice[int(result)]
                url = quality[result_quality]

            file_name = '{}.torrent'.format(se_code)
            torrent_file = os.path.join(torrents_dir, file_name)

            content = get_web(url=url, bytes=True)
            
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
                    self.create_line(title=series[i], folder=False, params={'mode': 'torrent_part', 'id': file_name, 'param': i}, **info)
            else:
                self.create_line(title=torrent['info']['name'], folder=False, params={'mode': 'torrent_part', 'id': file_name, 'param': 0}, **info)

        if self.params['param']:
            torrent_file = os.path.join(torrents_dir, self.params['id'])

            self.exec_selector_part(torrent_index=self.params['param'], torrent_url=torrent_file)

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
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
            xbmcplugin.endOfDirectory(handle, succeeded=True)

        if 'form' in self.params['param']:
            result = dialog.select('Сортировать по:', tuple(form.keys()))
            addon.setSetting(id='form', value=tuple(form.keys())[result])
            
        if 'alphabet' in self.params['param']:
            result = dialog.select('Название с буквы:', tuple(alphabet.keys()))
            addon.setSetting(id='alphabet', value=tuple(alphabet.keys())[result])
            
        if 'genre' in self.params['param']:
            result = dialog.select('Жанр:', tuple(genre.keys()))
            addon.setSetting(id='genre', value=tuple(genre.keys())[result])

        if 'year' in self.params['param']:
            result = dialog.select('Год:', tuple(year.keys()))
            addon.setSetting(id='year', value=tuple(year.keys())[result])
            
        if 'channel' in self.params['param']:
            result = dialog.select('Канал:', tuple(channel.keys()))
            addon.setSetting(id='channel', value=tuple(channel.keys())[result])
    
        if 'types' in self.params['param']:
            result = dialog.select('Тип:', tuple(types.keys()))
            addon.setSetting(id='types', value=tuple(types.keys())[result])

        if 'sort' in self.params['param']:
            result = dialog.select('Сортировать по:', tuple(sort.keys()))
            addon.setSetting(id='sort', value=tuple(sort.keys())[result])
            
        if 'status' in self.params['param']:
            result = dialog.select('Статус релиза:', tuple(status.keys()))
            addon.setSetting(id='status', value=tuple(status.keys())[result])
            
        if 'country' in self.params['param']:
            result = dialog.select('Страна:', tuple(country.keys()))
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
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
                
            if not ':[{' in html:
                self.create_line(title='[B][COLOR=white]Контент отсутствует[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return

            progress_bg.create('LostFilm', 'Инициализация')
                
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

                        progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                            
                        if not self.database.content_in_db(serial_id):
                            self.create_info(serial_id=serial_id, ismovie=is_movie)

                        info = self.create_info_data(serial_id=serial_id,se_code=se_code,is_movie=is_movie)

                        label = self.create_title(serial_title=serial_title)

                        self.context_menu = [
                            ('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                            ('Обновить описание', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial&id={}&ismovie={}")'.format(serial_id, is_movie))
                        ]

                        if is_movie:                            
                            self.create_line(title=label, params={'mode': 'movies_part', 'id': serial_id, 'code': se_code}, **info)
                        else:
                            self.context_menu.extend([
                                ('Добавить в Медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=create_media&id={}&ismovie={}")'.format(serial_id, False)),
                                ('Обновить медиатеку', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=library_part&param=update_media")')
                            ])
                            
                            self.create_line(title=label, params={'mode': 'select_part', 'id': serial_id, 'code': se_code}, **info)
                    except:
                        self.create_line(title='Ошибка обработки строки',
                                         image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
            except:
                self.create_line(title='Ошибка - сообщите автору',
                                 image=os.path.join(plugin_dir, 'resources', 'media', 'error.png'))
                    
            progress_bg.close()

            try:
                if len(data_array) >= 10:
                    page_count = (int(self.params['page']) / 10) + 1
                    label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                    self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 10)})
            except:
                pass
            
            xbmcplugin.endOfDirectory(handle, succeeded=True)
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

        new_url = html[html.find('url=http')+4:]
        new_url = new_url[:new_url.find('"')]

        from network import get_web
        
        html = get_web(url=new_url)

        if u'Контент недоступен на территории' in html:
            label = u'Контент недоступен на территории Российской Федерации\nПриносим извинения за неудобства'
            dialog.ok(u'LostFilm', label)
            return

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
            result = dialog.select('Доступное качество: ', choice)
            result_quality = choice[int(result)]
            url = quality[result_quality]

        html = get_web(url=url, bytes=True)

        file_name = '{}.torrent'.format(se_code)
        
        torrent_file = os.path.join(torrents_dir, file_name)
        
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
        
        return
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
                xbmcplugin.setResolvedUrl(handle, True, item)
                return True
            except:
                return False

        if '1' in addon.getSetting('engine'):
            try:
                purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(handle, True, item)
                return True
            except:
                return False
        return

def lostfilm_start():
    lostfilm = Lostfilm()
    lostfilm.execute()