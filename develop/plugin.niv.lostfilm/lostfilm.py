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

if sys.version_info[0] == 2:
    from urllib import urlencode, urlopen, quote, unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
else:
    from urllib.parse import urlencode, quote, unquote, parse_qs
    from urllib.request import urlopen
    from html import unescape

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from utility import clean_list, clean_tags, fs_dec, fs_enc

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

if sys.version_info[0] == 2:
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))
else:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

class Lostfilm:    
    def __init__(self):
        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.images_dir = os.path.join(addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)
        
        self.cookie_dir = os.path.join(addon_data_dir, 'cookies')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.database_dir = os.path.join(addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.params = {'mode': 'main_part','param': '','page': '1','node': '0'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.site_url = self.create_site_url()
#========================#========================#========================#
        try: session = float(addon.getSetting('auth_session'))
        except: session = 0

        if time.time() - session > 28800:
            addon.setSetting('auth_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'lostfilm.sid'))
            except: pass
            addon.setSetting('auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(auth_usage=True,auth_status=bool(addon.getSetting('auth') == 'true'))        
        self.network.auth_post_data = 'act=users&type=login&mail={}&pass={}&need_captcha=1&rem=1'.format(
            addon.getSetting('username'), addon.getSetting('password'))
        self.network.auth_url = '{}ajaxik.users.php'.format(self.site_url)
        self.network.sid_file = os.path.join(self.cookie_dir, 'lostfilm.sid')
        del WebTools
#========================#========================#========================#
        if not addon.getSetting('username') or not addon.getSetting('password'):
            self.params['mode'] = 'addon_setting'
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ВВЕДИТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, icon))
            return

        if not self.network.auth_status:
            if not self.network.authorization():
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, icon))
                return
            else:
                addon.setSetting('auth', str(self.network.auth_status).lower())                    
                addon.setSetting('user_session', self.create_session())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'lostfilm.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'lostfilm.db'))
        del DataBase
#========================#========================#========================#
    def create_session(self):
        ht = self.network.get_html('{}my'.format(self.site_url))
        
        user_session = ht[ht.find('session = \'')+11:ht.find('UserData.newbie')]
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
    def create_code(self, data):
        if '/' in data[len(data)-1]:
            data = data[0:-1]

        data = data.strip()
        
        data = data.replace('season_', '')
        data = data.replace('episode_', '')
        
        data = data.split('/')
        
        while len(data) < 3:
            data.append('999')

        if 'additional' in data[1]:
            data[1] = '999'
            
        data[1] = 'SE{:>02}'.format(data[1])
        data[2] = 'EP{:>02}'.format(data[2])

        return data
#========================#========================#========================#
    def create_image(self, se_code):
        serial_season = int(se_code[1].replace('SE','').replace('999','1'))
        serial_episode = int(se_code[2].replace('EP','').replace('999','1'))
        
        image_id = self.database.get_image_id(se_code[0])

        if 'schedule_part' in self.params['mode']:
            if serial_season == 1 and serial_episode == 1:
                image = 'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(image_id)
                return image
                
            if serial_episode == 1 and serial_season > 1:
                serial_season = serial_season - 1

        image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(
            image_id, serial_season)
        
        return image
#========================#========================#========================#
    def create_cast(self, data, actors=False):
        cast = []
        
        data = data[:data.rfind('</a>')]      
        data = clean_list(data).split('</a>')
        
        for d in data:
            d = unescape(d)
            
            d = d[d.find('<div class="name-ru">'):]
            d = d.replace('<div class="clr">', '|')
            d = d.replace('<div class="role-pane">', '|')
            d = clean_tags(d, '<', '>')
            d = d.replace('||', '')            
            d = d.split('|')
            
            while len(d) < 4:
                d.append('')

            if actors:
                cast.append(u'{}|{}'.format(d[0], d[2]))
            else:
                cast.append(u'{}'.format(d[0]))

        return cast
#========================#========================#========================#
    def create_description(self, data):
        data = unescape(data)
        data = clean_list(data)

        data = data.replace(u'Описание', u'Описание: ', 1)
        data = data.replace(u'Сюжет</strong>', u'\n\nСюжет:')
        data = data.replace(u'Сюжет:</strong>', u'\n\nСюжет:')
        
        data = clean_tags(data, '<', '>')

        return data
#========================#========================#========================#
    def create_post(self):
        from info import genre, year, channel, types, sort, status
        
        post = None

        if 'catalog' in self.params['param']:
            lostfilm_genre = '&g={}'.format(genre[addon.getSetting('genre')]) if genre[addon.getSetting('genre')] else ''
            lostfilm_year = '&y={}'.format(year[addon.getSetting('year')]) if year[addon.getSetting('year')] else ''
            lostfilm_channel = '&c={}'.format(channel[addon.getSetting('channel')]) if channel[addon.getSetting('channel')] else ''
            lostfilm_types = '&r={}'.format(types[addon.getSetting('types')]) if types[addon.getSetting('types')] else ''
            lostfilm_sort = sort[addon.getSetting('sort')]
            lostfilm_status = status[addon.getSetting('status')]
            lostfilm_page = self.params['node']
            
            post = 'act=serial&type=search&o={}{}{}{}{}&s={}&t={}'.format(
                lostfilm_page,lostfilm_genre,lostfilm_year,lostfilm_channel,lostfilm_types,lostfilm_sort,lostfilm_status)

        if 'favorites_part' in self.params['mode']:
            post = 'session={}&act=serial&type=follow&id={}'.format(
                addon.getSetting('user_session'), self.database.get_image_id(self.params['id'])
                )
        
        if 'favorites' in self.params['param']:
            post = 'act=serial&type=search&o={}&s=2&t=99'.format(self.params['node'])
            
        if 'select_part' in self.params['mode']:
            post = 'act=serial&type=getmarks&id={}'.format(
                self.database.get_image_id(self.params['id'])
                )
        return post
#========================#========================#========================#
    def create_title(self, se_code, series=None, mode=False):
        code = '[COLOR=blue]{}[/COLOR][COLOR=lime]{}[/COLOR] | '.format(
            se_code[1].replace('SE999',''), se_code[2].replace('EP999','')
            )
        
        if mode:
            code = '{}{} | '.format(
                se_code[1].replace('SE999',''), se_code[2].replace('EP999',''))
            
        if 'EP' in code or 'SE' in code:
            code = code
        else:
            code = ''
        
        title = self.database.get_title(se_code[0])        
        year = self.database.get_year(se_code[0])
        
        if series:
            series = series.split('|')
            
            series_title = u': {}'.format(
                series[int(addon.getSetting('titles'))]
                )
        else:
            series_title = ''

        label = u'{}[B]{}[/B]{}'.format(
            code, title[int(addon.getSetting('titles'))], series_title)
        
        if 'search_part' in self.params['param'] or 'catalog_part' in self.params['mode'] or 'serials_part' in self.params['mode']:
            label = u'[COLOR=blue]{}[/COLOR] | [B]{}{}[/B]{}'.format(
                year, code, title[int(addon.getSetting('titles'))], series_title)

        return label
#========================#========================#========================#
    def create_context(self, se_code=None):
        context_menu = []
        
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_database_part")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=clean_part")'))

        if se_code and self.params['mode'] in ('common_part','favorites_part','catalog_part','schedule_part','search_part'):
            context_menu.append(('[COLOR=cyan]Избранное - Добавить \ Удалить [/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&id={}")'.format(se_code[0])))
        
        if se_code:
            context_menu.append(('[COLOR=white]Обновить описание[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial_part&id={}")'.format(se_code[0])))
        
        if se_code and not '999' in se_code[2]:
            context_menu.append(('[COLOR=yellow]Отметить как просмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(','.join(se_code))))
            context_menu.append(('[COLOR=yellow]Отметить как непросмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(','.join(se_code))))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=news")'))
        context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=play")'))
        context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=bugs")'))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, params=None, se_code=None, watched=False, size=None, folder=True, online=None):
        if watched:
            title = clean_tags(title, '[', ']')
            title = u'[COLOR=goldenrod]{}[/COLOR]'.format(title)
            
        li = xbmcgui.ListItem(title)

        if se_code:
            cover = self.create_image(se_code)
            
            li.setArt({
                #"thumb": cover, 
                "poster": cover, 
                #"tvshowposter": cover, 
                #"fanart": cover,
                #"clearart": cover,
                #"clearlogo": cover, 
                #"landscape": cover, 
                "icon": cover
                })
            
            se_info = self.database.get_serial(se_code[0])

            info = {
                'genre':se_info[1], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                'country':se_info[3],#string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year': int(se_info[0][0:4]),#	integer (2009)
                #'episode':anime_info[2],#	integer (4)
                #'director':directors,#	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                #'mpaa':anime_info[5],#	string (PG-13)
                'plot':se_info[4],#	string (Long Description)
                'title':title,#	string (Big Fan)
                #'duration':duration,#	integer (245) - duration in seconds
                'studio':se_info[2],#	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                #'writer':writers,#	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                'tvshowtitle':title,#	string (Heroes)
                'premiered':se_info[0],#	string (2005-03-04)
                #'status':anime_info[1],#	string (Continuing) - status of a TVshow
                'aired':se_info[0],#	string (2008-12-07)
            }
            
            if self.database.cast_in_db(se_code[0]):
                cast = self.database.get_cast(se_code[0])
                if cast['actors']:
                    li.setCast(cast['actors'])
                if cast['directors']:
                    info['director'] = cast['directors']
                if cast['writers']:
                    info['writer'] = cast['writers']
            
            if watched:
                info['playcount'] = 1

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(se_code))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        #if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, serial_id, update=False):
        url = '{}series/{}/'.format(self.site_url, serial_id)

        html = self.network.get_html(url)
        html = unescape(html)

        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'genres', 'studios', 'country', 'description', 'image_id'], '')
              
        info['image_id'] = html[html.find('/Images/')+8:html.find('/Posters/')]
                
        info['title_ru'] = html[html.find('itemprop="name">')+16:html.find('</h1>')]
        info['title_en'] = html[html.find('alternativeHeadline">')+21:html.find('</h2>')]
        
        description_data = html[html.find(u'Описание</h2>'):html.find('<div class="social-pane">')]
        info['description'] = self.create_description(description_data)

        data_array = html[html.find(u'Премьера:'):html.find(u'Тип:')]
        data_array = clean_list(data_array).split('<br />')
        
        for data in data_array:            
            if u'Премьера:' in data:
                aired_on = data[data.find('content="')+9:data.find('" />')]
                info['aired_on'] = aired_on.replace('-', '.')
            if u'Канал, Страна:' in data:
                data = clean_tags(data.replace(u'Канал, Страна:', ''), '<','>')
                info['studios'] = data[:data.find('(')]
                info['country'] = data[data.rfind('(')+1:data.rfind(')')]
            if u'Жанр:' in data:
                info['genres'] = clean_tags(data.replace(u'Жанр:', ''), '<','>')

        try:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru=info['title_ru'],
                title_en=info['title_en'],
                aired_on=info['aired_on'],
                genres=info['genres'],
                studios=info['studios'],
                country=info['country'],
                description=info['description'],
                image_id=info['image_id'],
                update=update                
            )
        except:
            return 101

        cast = {'actors': [], 'directors': [], 'producers': [], 'writers': []}
        
        html2 = self.network.get_html('{}cast'.format(url))

        info_array = html2[html2.find('<div class="header-simple">'):html2.find('rightt-pane">')]        
        info_array = info_array.split('<div class="hor-breaker dashed"></div>')

        for cast_info in info_array:
            cast_info = clean_list(cast_info)

            if u'simple">Актеры' in cast_info:
                cast['actors'] = self.create_cast(cast_info, actors=True)

            if u'simple">Режиссеры' in cast_info:
                cast['directors'] = self.create_cast(cast_info)

            if u'simple">Продюсеры' in cast_info:
                cast['producers'] = self.create_cast(cast_info)

            if u'simple">Сценаристы' in cast_info:
                cast['writers'] = self.create_cast(cast_info)

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
            return 101
        
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
    def exec_update_serial_part(self):
        self.create_info(serial_id=self.params['id'], update=True)
        xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'lostfilm.db'))
        except: pass

        db_file = os.path.join(self.database_dir, 'lostfilm.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/lostfilm.db'
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
            xbmc.executebuiltin('Notification({},{},{},{})'.format('База Данных', '[COLOR=lime]УСПЕШНО ЗАГРУЖЕНА[/COLOR]', 5000, icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('База Данных', '[COLOR=gold]ERROR: 100[/COLOR]', 5000, icon))
            pass
#========================#========================#========================#
    def exec_mark_part(self, notice=True, se_code=False, mode=False):
        se_code = se_code.split(',') if se_code else self.params['id'].split(',')
        mode = mode if mode else self.params['param']
        
        data_code = '{}{:>03}{:>03}'.format(
            self.database.get_image_id(se_code[0]),se_code[1].replace('SE', ''), se_code[2].replace('EP', ''))
        
        html = self.network.get_html(
            target_name='{}ajaxik.php'.format(self.site_url),
            post = 'session={}&act=serial&type=markepisode&val={}&auto=0&mode={}'.format(
                addon.getSetting('user_session'), data_code, mode))
        
        if notice:
            if '"on' in str(html):
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]ОТМЕЧЕНО КАК ПРОСМОТРЕННОЕ[/COLOR]', 5000, icon))
            if 'off' in str(html):
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]ОТМЕЧЕНО КАК НЕПРОСМОТРЕННОЕ[/COLOR]', 5000, icon))
            if 'error' in str(html):
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 104[/COLOR]', 5000, icon))
            
        xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_favorites_part(self):
        html = self.network.get_html('{}ajaxik.php'.format(self.site_url), self.create_post())

        if '"on' in str(html):
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО ДОБАВЛЕНО[/COLOR]', 5000, icon))
        if 'off' in str(html):
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, icon))
        if 'error' in str(html):
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, icon))

        xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Удаление истории', '[COLOR=lime]УСПЕШНО ВЫПОЛНЕНО[/COLOR]', 5000, icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Удаление истории', '[COLOR=gold]ERROR: 102[/COLOR]', 5000, icon))
            pass
#========================#========================#========================#
    def exec_information_part(self):
        from info import lostfilm_data as info
            
        start = '[{}]'.format(self.params['param'])
        end = '[/{}]'.format(self.params['param'])
        data = info[info.find(start)+6:info.find(end)].strip()

        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'catalog_part', 'param': 'favorites'})
        self.create_line(title='[B][COLOR=yellow][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param':'new/'})
        self.create_line(title='[B][COLOR=yellow][ Все сериалы ][/COLOR][/B]', params={'mode': 'serials_part'})
        #self.create_line(title='[B][COLOR=yellow][ Новинки Сезонов ][/COLOR][/B]', params={'mode': 'common_part', 'param':'new_seasons/'})
        self.create_line(title='[B][COLOR=blue][ Каталог Сериалов][/COLOR][/B]', params={'mode': 'catalog_part'})
        #self.create_line(title='[B][COLOR=lime][ Новости ][/COLOR][/B]', params={'mode': 'news'})
        #self.create_line(title='[B][COLOR=lime][ Видео - Новости ][/COLOR][/B]', params={'mode': 'video'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': data})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = addon.getSetting('search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                addon.setSetting('search', data_array)

                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        self.progress.create('LostFilm', 'Инициализация')

        url = '{}schedule/'.format(self.site_url)
        html = self.network.get_html(target_name=url)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        data_array = html[html.find('<th colspan="6">')+16:html.rfind('<td class="placeholder">')]        
        data_array = data_array.split('<th colspan="6">')

        i = 0

        for data in data_array:
            data = unescape(data)
            title = data[:data.find('</th>')]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.create_line(title=u'[B][COLOR=white]{}[/COLOR][/B]'.format(title.capitalize()), params={})

            data = data.split('<td class="alpha"')
            data.pop(0)
            
            a = 0
            
            for d in data:
                d = clean_list(d)
                
                series_title = d[d.find('<td class="gamma'):]
                series_title = series_title[series_title.find(';">')+3:series_title.find('<br />')]

                d = d[d.find('<td class="delta'):]
                
                d = d.replace('<!--', '').replace('-->', '')
                d = d.replace('<br />', '|')
                
                se_code = d[d.find('/series/')+8:d.find('/\',false)')]
                se_code = self.create_code(se_code)

                d = clean_tags(d, '<', '>')
                d = d.split('|')
                
                series_date = d[0]
                series_meta = d[1]
                
                a = a + 1
                
                if self.progress.iscanceled():
                    break
                self.progress.update(p, u'Обработано: [COLOR=gold]{}%[/COLOR]\n[COLOR=lime]День:[/COLOR] {} из {} | [COLOR=blue]Элементы:[/COLOR] {} из {} '.format(
                    p, i, len(data_array), a, len(data)))

                if not self.database.serial_in_db(se_code[0]):
                    inf = self.create_info(se_code[0])
                    
                    if type(inf) == int:
                        self.create_line(title=u'[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, se_code[0]), params={})
                        continue

                label = u'{}: {} | [COLOR=gold]{} - {}[/COLOR]'.format(
                    self.create_title(se_code), series_title, series_date, series_meta
                    )
                self.create_line(title=label, se_code=se_code, params={'mode': 'select_part', 'id': se_code[0]})

        self.progress.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('LostFilm', 'Инициализация')

        url = '{}{}page_{}'.format(self.site_url, self.params['param'], self.params['page'])
        if 'search_part' in self.params['param']:
            url = '{}search/?q={}'.format(self.site_url, quote(self.params['search_string']))

        html = self.network.get_html(target_name=url)

        if not '<div class="hor-breaker dashed">' in html:
            self.create_line(title='[B][COLOR=white]Контент не найден[/COLOR][/B]', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        data_array = html[html.find('<div class="hor-breaker dashed">')+32:html.rfind('<div class="hor-breaker dashed">')]
        data_array = data_array.split('<div class="hor-breaker dashed">')
        
        i = 0

        for data in data_array:
            is_watched = True if 'haveseen-btn checked' in data else False

            data = clean_list(data)

            series_url = data[data.find('series/')+7:data.find('" ')]
            
            series = None
            if 'alpha">' in data:
                series_title_ru = data[data.find('alpha">')+7:data.find('</div><div class="beta">')]
                series_title_en = data[data.find('beta">')+6:data.find('</div><div class="hor-spacer3')]
                if series_title_ru:
                    series = u'{}|{}'.format(series_title_ru, series_title_en)
            
            se_code = self.create_code(series_url)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.serial_in_db(se_code[0]):
                inf = self.create_info(se_code[0])
                
                if type(inf) == int:
                    self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, serial_id), params={})
                    continue

            label = self.create_title(se_code, series)
            
            if 'new/' in self.params['param']:
                self.create_line(title=label, se_code=se_code, watched=is_watched, params={'mode': 'select_part', 'id': se_code[0], 'param': u'|'.join(se_code)})
            else:
                self.create_line(title=label, se_code=se_code, watched=is_watched, params={'mode': 'select_part', 'id': se_code[0]})

        self.progress.close()
        
        if '<div class="next-link active">' in html:
            self.create_line(title='[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        from info import genre, year, channel, types, status, sort
        
        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Канал: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('channel')), params={'mode': 'catalog_part', 'param': 'channel'})            
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('types')), params={'mode': 'catalog_part', 'param': 'types'})            
            self.create_line(title='Сортировка: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})            
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})            
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

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
        
        if 'catalog' in self.params['param'] or 'favorites' in self.params['param']:
            self.progress.create('LostFilm', 'Инициализация')
            
            html = self.network.get_html(
                '{}ajaxik.php'.format(self.site_url), self.create_post()
                )

            html = html[html.find('":[')+3:html.find('],"')]

            if not html:
                self.create_line(title='[B][COLOR=white]Контент не найден[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            data_array = html.split('},{')

            i = 0
            
            for data in data_array:
                data = clean_list(data)
                series_url = data[data.find('series\/')+8:data.find('","alias')]
                
                se_code = self.create_code(series_url)
                
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
                
                if not self.database.serial_in_db(se_code[0]):
                    inf = self.create_info(se_code[0])
                    
                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, serial_id), params={})
                        continue
                
                label = self.create_title(se_code)
                self.create_line(title=label, se_code=se_code, params={'mode': 'select_part', 'id': se_code[0]})

            self.progress.close()

            if len(data_array) >= 10:
                self.create_line(title='[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={'mode': self.params['mode'], 'param': self.params['param'], 'node': (int(self.params['node']) + 10)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_serials_part(self):
        self.progress.create('LostFilm', 'Инициализация')

        data_array = self.database.get_serials_id()
        data_array.sort(key=lambda tup: tup[int(addon.getSetting('titles'))+1])
            
        i = 0
        
        for data in data_array:
            se_code = self.create_code(data[0])

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)
            
            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
            label = self.create_title(se_code)
            self.create_line(title=label, se_code=se_code, params={'mode': 'select_part', 'id': se_code[0]})
        
        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)        
        return
#========================#========================#========================#
    def exec_select_part(self):
        if not self.params['param']:
            url = '{}series/{}/seasons'.format(self.site_url, self.params['id'])
            html = self.network.get_html(target_name=url)

            watched_data = self.network.get_html('{}ajaxik.php'.format(self.site_url), self.create_post())

            data_array = html[html.find('<h2>')+4:html.rfind('<td class="placeholder"></td>')]
            data_array = data_array.split('<h2>')
            
            for array in data_array:
                array = clean_list(array)
                
                title = array[:array.find('</h2>')]
                
                code = array[array.find('PlayEpisode(')+12:array.find(')">')]
                
                if code:
                    code = code.replace('\'', '').replace(',', '/')
                    code = code.replace(code[:code.find('/')], self.params['id'])
                    
                    self.create_line(title=u'[B][COLOR=white]{}[/COLOR][/B]'.format(
                        title.capitalize()), params={'mode': 'select_part', 'param': u'|'.join(self.create_code(code))})
                else:
                    self.create_line(title=u'[B][COLOR=dimgray]{}[/COLOR][/B]'.format(title.capitalize()), params={})

                array = array.split('<tr')
                array.pop(0)

                for data in array:
                    series_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
                    series_title = clean_tags(series_title.replace('<br />','|').replace('<br>','|'), '<', '>')

                    series_url = data[data.rfind('/series/')+8:data.rfind('\',false)')]
                    if '/' in series_url[len(series_url)-1]:
                        series_url = series_url[:-1]

                    se_code = self.create_code(series_url)
                    
                    data_code = '{:>03}{:>03}'.format(
                        se_code[1].replace('SE', ''), se_code[2].replace('EP', ''))
                    is_watched = True if data_code in watched_data else False

                    air_data = data[data.find('Ru:')+3:data.rfind('Eng:')]
                    air_data = clean_tags(air_data, '<', '>')
                    
                    title = self.create_title(se_code)

                    label = u'{} | [COLOR=gold]{}[/COLOR]'.format(
                        self.create_title(se_code, series_title), air_data)

                    if '"not-available"' in data:
                        label = u'[COLOR=dimgray]{} | {}[/COLOR]'.format(
                            self.create_title(se_code, series_title, True), air_data)
                        self.create_line(title=label, se_code=se_code, params={})
                    else:
                        self.create_line(title=label, se_code=se_code, watched=is_watched, params={'mode': 'select_part', 'param': u'|'.join(se_code)})

        if self.params['param']:
            data_print(self.params['param'])
            serial_data = self.params['param'].replace('SE', '')
            serial_data = serial_data.replace('EP','').split('|')

            image_id = self.database.get_image_id(serial_data[0])
            url = '{}v_search.php?c={}&s={}&e={}'.format(
                self.site_url,image_id,int(serial_data[1]),int(serial_data[2])
                )

            html = self.network.get_html(target_name=url)
            
            new_url = html[html.find('url=http')+4:html.find('&newbie=')]
            
            html = self.network.get_html(new_url)
            
            data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
            data_array = clean_list(data_array).split('<div class="inner-box--label">')
            
            for data in data_array:
                data = data.replace('</div>', '|').replace('||', '')
                data = clean_tags(data, '<', '>').split('|')

                quality = data[0]
                title = data[1]
                node_url = data[2]
                info = data[3]

                label = u'[COLOR=blue]{: >04}[/COLOR] | {}'.format(quality, info)

                self.create_line(title=label, params={'mode': 'torrent_part', 'torrent_url': unquote(node_url), 'id': self.params['param'], 'node':quality})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        url = self.params['torrent_url']
        full_url = '{}?s={}'.format(url[:url.find('?s=')], quote(url[url.find('?s=')+3:]))
        se_code = self.params['id'].split('|')
        file_name = '{}_{}{}_{}'.format(se_code[0],se_code[1],se_code[2],self.params['node'])
        full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))
        torrent_file = self.network.get_file(target_name=full_url, destination_name=full_name)

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
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name, 'node': self.params['id']}, se_code=se_code, folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_name, 'node': self.params['id']}, se_code=se_code, folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
#========================#========================#========================#
    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if '0' in addon.getSetting('engine'):
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(addon.getSetting('tam'))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if '1' in addon.getSetting('engine'):
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        self.exec_mark_part(notice=False, se_code=self.params['node'].replace('|', ','), mode='on')

if __name__ == "__main__":
    lostfilm = Lostfilm()
    lostfilm.execute()
    del lostfilm

gc.collect()