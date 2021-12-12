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

from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
from urllib.request import urlopen
from html import unescape

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

#import utility, info
from utility import clean_list, tag_list, rep_list

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    return

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')
icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
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

        self.cache_dir = os.path.join(addon_data_dir, 'cache')
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.params = {
            'mode': 'main_part',
            'param': '',
            'page': '1',
            'sort':'',
            'node':''
            }

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = None
        # self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()

        self.auth_mode = bool(addon.getSetting('lostfilm_auth_mode') == '1')
#========================#========================#========================#
        try: session = float(addon.getSetting('lostfilm_session'))
        except: session = 0

        if time.time() - session > 28800:
            addon.setSetting('lostfilm_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'lostfilm.sid'))
            except: pass
            addon.setSetting('lostfilm_auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(addon.getSetting('lostfilm_auth') == 'true'),
            proxy_data=self.proxy_data
            )
        
        self.auth_post_data = 'act=users&type=login&mail={}&pass={}&need_captcha=1&rem=1'.format(
            addon.getSetting('lostfilm_username'), addon.getSetting('lostfilm_password')
            )
        
        self.network.auth_post_data = self.auth_post_data
        self.network.auth_url = '{}ajaxik.users.php'.format(self.site_url)

        self.network.sid_file = os.path.join(self.cookie_dir, 'lostfilm.sid')
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not addon.getSetting('lostfilm_username') or not addon.getSetting('lostfilm_password'):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ВВЕДИТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, icon))
                return

            if not self.network.auth_status:
                if not self.network.authorization():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, icon))
                    return
                else:
                    addon.setSetting('lostfilm_auth', str(self.network.auth_status).lower())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'lostfilm.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'lostfilm.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        site_url = addon.getSetting('lostfilm_mirror_0')
        current_mirror = 'lostfilm_mirror_{}'.format(addon.getSetting('lostfilm_mirror_mode'))

        if not addon.getSetting(current_mirror):
            site_url = addon.getSetting('lostfilm_mirror_0')
        else:
            site_url = addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_code(self, data):
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

        serial_season = int(rep_list(se_code[1], 'SE|,EP|,999|1'))
        serial_episode = int(rep_list(se_code[2], 'SE|,EP|,999|1'))

        image_id = self.database.get_image_id(se_code[0])
        
        if 'schedule_part' in self.params['mode']:
            if serial_episode == 1 and serial_season > 1:
                serial_season = serial_season - 1

        image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(
            image_id, serial_season
            )
        
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
            d = tag_list(d)
            d = d.replace('||', '')            
            d = d.split('|')
            
            while len(d) < 4:
                d.append('')

            if actors:
                cast.append('{}|{}'.format(d[0], d[2]))
            else:
                cast.append('{}'.format(d[0]))

        return cast
#========================#========================#========================#
    def create_description(self, data):
        data = unescape(data)
        data = clean_list(data)

        data = data.replace('Описание', 'Описание: ', 1)
        data = data.replace('Сюжет</strong>', '\n\nСюжет:')
        data = data.replace('Сюжет:</strong>', '\n\nСюжет:')
        
        data = tag_list(data)

        return data
#========================#========================#========================#
    def create_post(self):
        from info import genre, year, channel, types, sort, status
        
        post = None

        if 'catalog' in self.params['param']:
            lostfilm_genre = '&g={}'.format(genre[addon.getSetting('lostfilm_genre')]) if genre[addon.getSetting('lostfilm_genre')] else ''
            lostfilm_year = '&y={}'.format(year[addon.getSetting('lostfilm_year')]) if year[addon.getSetting('lostfilm_year')] else ''
            lostfilm_channel = '&c={}'.format(channel[addon.getSetting('lostfilm_channel')]) if channel[addon.getSetting('lostfilm_channel')] else ''
            lostfilm_types = '&r={}'.format(types[addon.getSetting('lostfilm_types')]) if types[addon.getSetting('lostfilm_types')] else ''
            lostfilm_sort = sort[addon.getSetting('lostfilm_sort')]
            lostfilm_status = status[addon.getSetting('lostfilm_status')]
            
            post = 'act=serial&type=search&o=0{}{}{}{}&s={}&t={}'.format(
                lostfilm_genre, lostfilm_year, lostfilm_channel, lostfilm_types, lostfilm_sort, lostfilm_status)

            #data_print(post)
#         if self.params['param'] == 'catalog':
#             post = 'query=catalog&page={}&filter=id%2Cseries%2Cannounce&xpage=catalog&search=%7B%22year%22%3A%22{}%22%2C%22genre%22%3A%22{}%22%2C%22season%22%3A%22{}%22%7D&sort={}&finish={}'.format(
#                 self.params['page'],
#                 addon.getSetting('{}_year'.format(self.params['portal'])),
#                 addon.getSetting('{}_genre'.format(self.params['portal'])),
#                 addon.getSetting('{}_season'.format(self.params['portal'])),
#                 anilibria_sort[addon.getSetting('{}_sort'.format(self.params['portal']))],
#                 anilibria_status[addon.getSetting('{}_status'.format(self.params['portal']))])
#         if self.params['mode'] == 'online_part':
#             post = 'query=release&id={}&filter=playlist'.format(self.params['id'])
#         if self.params['mode'] == 'torrent_part':
#             post = 'query=release&id={}&filter=torrents'.format(self.params['id'])
      
        return post
#========================#========================#========================#
    def create_title(self, se_code, series=None, mode=False):
        code = '[COLOR=blue]{}[/COLOR][COLOR=lime]{}[/COLOR] | '.format(
            se_code[1].replace('SE999',''), se_code[2].replace('EP999','')
            )
        
        # code = '{}{} | '.format(
        #     se_code[1].replace('SE999',''), se_code[2].replace('EP999',''))
        
        if mode:
            code = '{}{} | '.format(
                se_code[1].replace('SE999',''), se_code[2].replace('EP999',''))
            
        if 'EP' in code or 'SE' in code:
            code = code
        else:
            code = ''
        
        title = self.database.get_title(se_code[0])
        
        if series:
            series = series.split('|')
            
            series_title = ': {}'.format(
                series[int(addon.getSetting('lostfilm_titles'))]
                )
        else:
            series_title = ''

        label = '{}[B]{}[/B]{}'.format(
            code, title[int(addon.getSetting('lostfilm_titles'))], series_title)

        return label
# #========================#========================#========================#
#     def create_title(self, title, series, announce=None):        
#         if series:
#             res = u'Серии: {}'.format(series)
#             if announce:
#                 res = u'{} ] - [ {}'.format(res, announce)
#             series = u' - [COLOR=gold][ {} ][/COLOR]'.format(res)
#             if xbmc.getSkinDir() == 'skin.aeon.nox.silvo' and self.params['mode'] == 'common_part':
#                 series = u' - [ {} ]'.format(res)
#         else:
#             series = ''

#         if '0' in addon.getSetting('{}_titles'.format(self.params['portal'])):
#             label = u'{}{}'.format(title[0], series)
#         if '1' in addon.getSetting('{}_titles'.format(self.params['portal'])):
#             label = u'{}{}'.format(title[1], series)
#         if '2' in addon.getSetting('{}_titles'.format(self.params['portal'])):
#             label = u'{} / {}{}'.format(title[0], title[1], series)

#         return label
# #========================#========================#========================#
#     def create_image(self, anime_id):
#         site_url = self.site_url.replace('public/api/index.php','').replace('//www.','//static.')
#         url = '{}upload/release/350x500/{}.jpg'.format(site_url, anime_id)

#         if '0' in addon.getSetting('{}_covers'.format(self.params['portal'])):
#             return url
#         else:
#             local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
#             if local_img in os.listdir(self.images_dir):
#                 local_path = os.path.join(self.images_dir, local_img)
#                 return local_path
#             else:
#                 file_name = os.path.join(self.images_dir, local_img)
#                 return self.network.get_file(target_name=url, destination_name=file_name)
#========================#========================#========================#
    def create_context(self):
        context_menu = []
        
        #context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal={}")'.format(self.params['portal'])))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=clean_part")'))

        # if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
        #     context_menu.append(('[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal={}")'.format(anime_id, self.params['portal'])))

        # if self.auth_mode and 'common_part' in self.params['mode'] or self.auth_mode and 'schedule_part' in self.params['mode']:
        #     context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_add&portal={}")'.format(anime_id, self.params['portal'])))
        #     context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_del&portal={}")'.format(anime_id, self.params['portal'])))
        
        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=news")'))
        context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=play")'))
        context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=bugs")'))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, params=None, se_code=None, size=None, folder=True, online=None):  
        li = xbmcgui.ListItem(title)
        
        if se_code:
            cover = self.create_image(se_code)
            
            li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
                       "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})
            
            se_info = self.database.get_serial(se_code[0])

            info = {
                'genre':se_info[1], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                'country':se_info[3],#string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year':se_info[0],#	integer (2009)
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
                    
            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context())

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
        
        description_data = html[html.find('Описание</h2>'):html.find('<div class="social-pane">')]
        info['description'] = self.create_description(description_data)

        data_array = html[html.find('Премьера:'):html.find('Тип:')]
        data_array = clean_list(data_array).split('<br />')
        
        for data in data_array:            
            if 'Премьера:' in data:
                aired_on = data[data.find('content="')+9:data.find('" />')]
                info['aired_on'] = aired_on.replace('-', '.')
            if 'Канал, Страна:' in data:
                data = tag_list(data.replace('Канал, Страна:', ''))
                info['studios'] = data[:data.find('(')]
                info['country'] = data[data.rfind('(')+1:data.rfind(')')]
            if 'Жанр:' in data:
                info['genres'] = tag_list(data.replace('Жанр:', ''))

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
                update=False                
            )
        except:
            return 101

        cast = {'actors': [], 'directors': [], 'producers': [], 'writers': []}
        
        html2 = self.network.get_html('{}cast'.format(url))

        info_array = html2[html2.find('<div class="header-simple">'):html2.find('rightt-pane">')]        
        info_array = info_array.split('<div class="hor-breaker dashed"></div>')

        for cast_info in info_array:
            cast_info = clean_list(cast_info)

            if 'simple">Актеры' in cast_info:
                cast['actors'] = self.create_cast(cast_info, actors=True)

            if 'simple">Режиссеры' in cast_info:
                cast['directors'] = self.create_cast(cast_info)

            if 'simple">Продюсеры' in cast_info:
                cast['producers'] = self.create_cast(cast_info)

            if 'simple">Сценаристы' in cast_info:
                cast['writers'] = self.create_cast(cast_info)

        try:
            self.database.add_cast(
                serial_id=serial_id,
                actors='||'.join(cast['actors']),
                directors=','.join(cast['directors']),
                producers=','.join(cast['producers']),
                writers=','.join(cast['writers']),
                update=False
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
# #========================#========================#========================#
#     def exec_update_anime_part(self):
#         self.create_info(anime_id=self.params['id'], update=True)
#         xbmc.executebuiltin('Container.Refresh')
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
    # def exec_favorites_part(self):
    #     html = self.network.get_html(self.site_url, self.create_post())
       
    #     if 'status":false' in html:
    #         if 'fav_add' in self.params['param']:
    #             xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, icon))
    #         if 'fav_del' in self.params['param']:
    #             xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, icon))

    #     if 'status":true' in html:
    #         if 'fav_add' in self.params['param']:
    #             xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО ДОБАВЛЕНО[/COLOR]', 5000, icon))
    #         if 'fav_del' in self.params['param']:
    #             xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, icon))
        
    #     xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('lostfilm_search', '')
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
        # if self.auth_mode:
        #     self.create_line(title=u'[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites'})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=yellow][ Новинки Серий ][/COLOR][/B]', params={'mode': 'common_part', 'param':'new/'})
        self.create_line(title='[B][COLOR=yellow][ Новинки Сезонов ][/COLOR][/B]', params={'mode': 'common_part', 'param':'new_seasons/'})
        self.create_line(title='[B][COLOR=blue][ Сериалы - Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        #self.create_line(title='[B][COLOR=lime][ Новости ][/COLOR][/B]', params={'mode': 'news'})
        #self.create_line(title='[B][COLOR=lime][ Видео - Новости ][/COLOR][/B]', params={'mode': 'video'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = addon.getSetting('lostfilm_search').split('|')
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
                data_array = addon.getSetting('lostfilm_search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                addon.setSetting('lostfilm_search', data_array)

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

            self.create_line(title='[B][COLOR=white]{}[/COLOR][/B]'.format(title.capitalize()), params={})

            data = data.split('<td class="alpha"')
            data.pop(0)
            
            a = 0
            
            for d in data:
                d = clean_list(d)
                d = d[d.find('<td class="delta'):]
                
                d = d.replace('<!--', '').replace('-->', '')
                d = d.replace('<br />', '|')
                
                se_code = d[d.find('/series/')+8:d.find('/\',false)')]
                se_code = self.create_code(se_code)
                serial_id = se_code[0]
                
                d = tag_list(d)
                d = d.split('|')
                
                series_date = d[0]
                series_meta = d[1]
                
                a = a + 1
                
                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: [COLOR=gold]{}%[/COLOR]\n[COLOR=lime]День:[/COLOR] {} из {} | [COLOR=blue]Элементы:[/COLOR] {} из {} '.format(
                    p, i, len(data_array), a, len(data)))

                if not self.database.serial_in_db(se_code[0]):
                    inf = self.create_info(se_code[0])
                    
                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, serial_id), params={})
                        continue

                label = '{} | [COLOR=gold]{} - {}[/COLOR]'.format(self.create_title(se_code),series_date,series_meta)
                self.create_line(title=label, se_code=se_code, params={'mode': 'select_part', 'id': se_code[0]})
                
        self.progress.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def create_url(self):
        url = '{}{}page_{}'.format(self.site_url, self.params['param'], self.params['page'])
        
        if 'search_part' in self.params['param']:
            url = '{}search/?q={}'.format(self.site_url, quote(self.params['search_string']))
        
        if 'catalog' in self.params['param']:
            url = '{}ajaxik.php'.format(self.site_url)

        return url
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('LostFilm', 'Инициализация')
        
        html = self.network.get_html(target_name=self.create_url(), post=self.create_post())
        
        if 'catalog' in self.params['param']:
            data_array = html.split('},{')
        else:            
            if html.find('<div class="hor-breaker dashed">') == -1:
                self.create_line(title='[B][COLOR=white]Контент не найден[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            data_array = html[html.find('<div class="hor-breaker dashed">')+32:html.rfind('<div class="hor-breaker dashed">')]
            data_array = data_array.split('<div class="hor-breaker dashed">')

        i = 0

        for data in data_array:
            data = clean_list(data)

            series_url = data[data.find('series/')+7:data.find('/" style')]
            if 'search_part' in self.params['param']:
                series_url = data[data.find('series/')+7:data.find('" class')]
            if 'catalog' in self.params['param']:
                series_url = data[data.find('series\/')+8:data.find('","alias')]

            series = None
            if 'alpha">' in data:
                series_title_ru = data[data.find('alpha">')+7:data.find('</div><div class="beta">')]
                series_title_en = data[data.find('beta">')+6:data.find('</div><div class="hor-spacer3')]
                if series_title_ru:
                    series = '{}|{}'.format(series_title_ru, series_title_en)
            
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
            self.create_line(title=label, se_code=se_code, params={'mode': 'select_part', 'id': se_code[0]})

        self.progress.close()
        
        if '<div class="next-link active">' in html:
            self.create_line(title='[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        from info import genre, year, channel, types, status, sort
        
        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('lostfilm_genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('lostfilm_year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Канал: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('lostfilm_channel')), params={'mode': 'catalog_part', 'param': 'channel'})            
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('lostfilm_types')), params={'mode': 'catalog_part', 'param': 'types'})            
            self.create_line(title='Сортировка: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('lostfilm_sort')), params={'mode': 'catalog_part', 'param': 'sort'})            
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('lostfilm_status')), params={'mode': 'catalog_part', 'param': 'status'})            
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'genre' in self.params['param']:
            result = self.dialog.select('Жанр:', tuple(genre.keys()))
            addon.setSetting(id='lostfilm_genre', value=tuple(genre.keys())[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Год:', tuple(year.keys()))
            addon.setSetting(id='lostfilm_year', value=tuple(year.keys())[result])

        if 'channel' in self.params['param']:
            result = self.dialog.select('Канал:', tuple(channel.keys()))
            addon.setSetting(id='lostfilm_channel', value=tuple(channel.keys())[result])

        if 'types' in self.params['param']:
            result = self.dialog.select('Тип:', tuple(types.keys()))
            addon.setSetting(id='lostfilm_types', value=tuple(types.keys())[result])

        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(sort.keys()))
            addon.setSetting(id='lostfilm_sort', value=tuple(sort.keys())[result])

        if 'status' in self.params['param']:
            result = self.dialog.select('Статус релиза:', tuple(status.keys()))
            addon.setSetting(id='lostfilm_status', value=tuple(status.keys())[result])
#========================#========================#========================#
    def exec_select_part(self):
        if not self.params['param']:
            serial_data = self.params['id'].replace('SE', '')
            serial_data = serial_data.replace('EP','').split('|')
            
            url = '{}series/{}/seasons'.format(self.site_url, serial_data[0])            
            html = self.network.get_html(target_name=url)
            
            data_array = html[html.find('<h2>')+4:html.rfind('<td class="placeholder"></td>')]
            data_array = data_array.split('<h2>')
            
            for array in data_array:
                array = clean_list(array)

                title = array[:array.find('</h2>')]
                
                self.create_line(title='[B][COLOR=white]{}[/COLOR][/B]'.format(title.capitalize()), params={})

                array = array.split('<tr')
                array.pop(0)

                for data in array:
                    series_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
                    series_title = tag_list(series_title.replace('<br />','|').replace('<br>','|'))

                    series_url = data[data.rfind('/series/')+8:data.rfind('\',false)')]
                    if '/' in series_url[len(series_url)-1]:
                        series_url = series_url[:-1]

                    se_code = self.create_code(series_url)
                    
                    air_data = data[data.find('Ru:')+3:data.rfind('Eng:')]
                    air_data = tag_list(air_data)
                    
                    title = self.create_title(se_code)

                    label = '{} | [COLOR=gold]{}[/COLOR]'.format(
                        self.create_title(se_code, series_title), air_data)

                    if '"not-available"' in data:
                        label = '[COLOR=dimgray]{} | {}[/COLOR]'.format(
                            self.create_title(se_code, series_title, True), air_data)

                    self.create_line(title=label, se_code=se_code, params={'mode': 'select_part', 'param': '|'.join(se_code)})

        if self.params['param']:
            serial_data = self.params['param'].replace('SE', '')
            serial_data = serial_data.replace('EP','').split('|')

            image_id = self.database.get_image_id(serial_data[0])
            url = '{}v_search.php?c={}&s={}&e={}'.format(
                self.site_url,image_id,int(serial_data[1]),int(serial_data[2])
                )
            data_print(url)
                
            html = self.network.get_html(target_name=url)
            
            new_url = html[html.find('url=http')+4:html.find('&newbie=')]
            
            html = self.network.get_html(new_url)
            
            data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
            data_array = clean_list(data_array).split('<div class="inner-box--label">')
            
            for data in data_array:
                data = data.replace('</div>', '|').replace('||', '')
                data = tag_list(data).split('|')
                
                quality = data[0]
                title = data[1]
                node_url = data[2]
                info = data[3]

                label = '[COLOR=blue]{: >04}[/COLOR] | {}'.format(quality, info)

                self.create_line(title=label, params={'mode': 'torrent_part', 'torrent_url': unquote(node_url), 'id': self.params['param'], 'node':quality})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        url = self.params['torrent_url']
### Исправить костыль
        full_url = '{}?s={}'.format(
            url[:url.find('?s=')], quote(url[url.find('?s=')+3:])
            )
### =========================== ^^
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
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, se_code=se_code, folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_name}, se_code=se_code, folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
#========================#========================#========================#
    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])
        portal_engine = 'lostfilm_engine'

        if '0' in addon.getSetting(portal_engine):
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(addon.getSetting('lostfilm_tam'))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if '1' in addon.getSetting(portal_engine):
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


if __name__ == "__main__":
    lostfilm = Lostfilm()
    lostfilm.execute()
    del lostfilm

gc.collect()