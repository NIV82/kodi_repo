# -*- coding: utf-8 -*-

import os, sys, time, base64
import xbmc, xbmcgui, xbmcplugin

try:
    from urllib import urlencode, urlopen, quote, unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen
    from html import unescape

from utility import clean_list, clean_tags, data_encode, data_decode

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Anidub:
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()
        
        self.params = params
        self.addon = addon
        self.icon = icon.replace('icon', self.params['portal'])

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        self.proxy_data = None

        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('anidub_auth_mode') == '1')
#========================#========================#========================#
        try: session = float(self.addon.getSetting('anidub_t_session'))
        except: session = 0

        if time.time() - session > 28800:
            self.addon.setSetting('anidub_t_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anidub_t.sid'))
            except: pass
            self.addon.setSetting('anidub_t_auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('anidub_t_auth') == 'true'),
            proxy_data=self.proxy_data, portal='anidub_t')
        # self.auth_post_data = 'login_name={}&login_password={}&login=submit'.format(
        #     self.addon.getSetting('anidub_t_username'),self.addon.getSetting('anidub_t_password'))
        
        #self.network.auth_post_data = self.auth_post_data
        self.network.auth_post_data = 'login_name={}&login_password={}&login=submit'.format(
            self.addon.getSetting('anidub_t_username'),self.addon.getSetting('anidub_t_password'))
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anidub_t.sid')
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not self.addon.getSetting('anidub_t_username') or not self.addon.getSetting('anidub_t_password'):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ВВЕДИТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                    return
                else:
                    self.addon.setSetting('anidub_t_auth', str(self.network.auth_status).lower())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_anidub_t.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_anidub_t.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = 'anidub_t_mirror_{}'.format(self.addon.getSetting('anidub_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('anidub_t_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
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

        if 'ERROR-404' in label:
            label = u'[COLOR=red][B]{}[/B][/COLOR]'.format(label)
        return label
# #========================#========================#========================#
#     def create_image(self, url):
#         if not 'https://' in url:
#             url = '{}{}'.format(self.site_url, url.replace('/','',1))
        
#         if '0' in self.addon.getSetting('{}_covers'.format(self.params['portal'])):
#             return url
#         else:
#             local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
#             if local_img in os.listdir(self.images_dir):
#                 local_path = os.path.join(self.images_dir, local_img)
#                 return local_path
#             else:
#                 file_name = os.path.join(self.images_dir, local_img)
#                 return self.network.get_file(target_name=url, destination_name=file_name)
# #========================#========================#========================#
#     def create_context(self, anime_id):
#         context_menu = []
#         context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal={}")'.format(self.params['portal'])))

#         if 'search_part' in self.params['mode'] and self.params['param'] == '':
#             context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal={}")'.format(self.params['portal'])))

#         if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
#             context_menu.append(('[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal={}")'.format(anime_id, self.params['portal'])))

#         if self.auth_mode:
#             if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
#                 context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal={}")'.format(anime_id, self.params['portal'])))
#                 context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal={}")'.format(anime_id, self.params['portal'])))

#         context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal={}")'.format(self.params['portal'])))
#         context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal={}")'.format(self.params['portal'])))
#         context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal={}")'.format(self.params['portal'])))
#         return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, rating=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            #cover = cover
            #cover = self.create_image(cover)
            
            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})
            # 0     1       2           3           4           5       6       7       8       9           10          11      12          13      14      15          16      17      18      19
            #kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios
            anime_info = self.database.get_anime(anime_id)
            
            description = anime_info[10] if anime_info[10] else ''

            if anime_info[11]:
                description = u'{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(anime_info[10], anime_info[11])
            if anime_info[12]:
                description = u'{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(description, anime_info[12])
            if anime_info[13]:
                description = u'{}\n[COLOR=steelblue]Тайминг[/COLOR]: {}'.format(description, anime_info[13])
            if anime_info[14]:
                description = u'{}\n[COLOR=steelblue]Работа над звуком[/COLOR]: {}'.format(description, anime_info[14])
            if anime_info[15]:
                description = u'{}\n[COLOR=steelblue]Mastering[/COLOR]: {}'.format(description, anime_info[15])
            if anime_info[16]:
                description = u'{}\n[COLOR=steelblue]Редактирование[/COLOR]: {}'.format(description, anime_info[16])
            if anime_info[17]:
                description = u'{}\n[COLOR=steelblue]Другое[/COLOR]: {}'.format(description, anime_info[17])

            info = {
                'genre':anime_info[7], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                'country':anime_info[18],#string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year':anime_info[3],#	integer (2009)
                'episode':anime_info[2],#	integer (4)
                'director':anime_info[9],#	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                'mpaa':anime_info[5],#	string (PG-13)
                'plot':description,#	string (Long Description)
                'title':title,#	string (Big Fan)
                'duration':anime_info[6],#	integer (245) - duration in seconds
                'studio':anime_info[19],#	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                'writer':anime_info[8],#	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                'tvshowtitle':title,#	string (Heroes)
                'premiered':anime_info[3],#	string (2005-03-04)
                'status':anime_info[1],#	string (Continuing) - status of a TVshow
                'aired':anime_info[3],#	string (2008-12-07)
                'rating':rating
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        #li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_aired(self, data):
        if '</b>' in data:
            data = data[data.find('</b>')+4:]
        if u'по' in data:
            data = data[:data.find(u'по')]

        data = clean_tags(data, '<', '>')

        rep_list = [
            (u'г',''),(u'с ', ''),(u'c ', ''),
            (u'апр','07'),(u'октября','10'),(' ','.'),('..','.'),
            (u'окт.','10.'),(u'??.08','16.08'),(u'С.',''),(u'OVA1-',''),
            (u'.OVA2-',''),(u'TV-1:',''),(u'января','01'),(u'марта','03'),
            ('.-.',',')
            ]
        
        for value in rep_list:
            data = data.replace(value[0], value[1])

        data = data.strip()
        
        if '.' in data[0]:
            data = data[1:]
        if '.' in data[len(data)-1]:
            data = data[:len(data)-1]
        if ',' in data:
            data = data[:data.find(',')]

        result = []
        for d in data:
            if d.isdigit() or '.' in d:
                result.append(d)

        data = ''.join(result)

        if len(data) < 4:
            data = ''
        
        rev_test = data.split('.')
        if len(rev_test) > 2:
            if len(rev_test[0]) > 2:
                if len(rev_test[2]) < 4:
                    rev_test.reverse()
                    data = '.'.join(rev_test)

        return data
#========================#========================#========================#
    def create_title_info(self, title):
        info = dict.fromkeys(['series', 'title_ru', 'title_en'], '')
        splitter = '/'

        title = clean_tags(title, '<', '>')

        if '[' in title:
            info['series'] = title[title.rfind('[')+1:title.rfind(']')].strip()
            title = title[:title.rfind('[')]

        rep_list = [
            ('|', '/'),('\\', '/'),('Reward / EEA','Reward - EEA'),('[email&#160;protected] /','Idolm@ster /'),
            ('/ [email&#160;protected]','/ Sasami-san@Ganbaranai'), ('Inuyasha: Kagami','/ Inuyasha: Kagami'),
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
    def create_info(self, anime_id, update=False):
        html = self.network.get_html('https://tr.anidub.com/index.php?newsid={}'.format(anime_id))
        
        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'released_on', 'genres', 'director', 'writer', 'description', 'dubbing',
                            'translation', 'timing', 'country', 'studios', 'image', 'year'], '')
            
        info['image'] = html[html.find('"poster"><img src="')+19:html.find('" alt=""></span>')]

        title_data = html[html.find('<h1><span id="news-title">')+26:html.find('</span></h1>')]
        
        if u'Сасами-сан на Лень.com' in title_data or u'Идолм@стер' in title_data:
            title_data = html[html.find('title" content="')+16:html.find('<meta property="og:url"')]

        info.update(self.create_title_info(title_data))

        data_array = html[html.find('<div class="xfinfodata">')+24:html.find('<div class="story_b clr">')]
        data_array = clean_list(data_array).split('<br>')

        for data in data_array:
            data = unescape(data)
            if u'Год: </b>' in data:
                for year in range(1950, 2030, 1):
                    if str(year) in data:
                        info['year'] = year
                        break
            if u'Жанр: </b>' in data:
                info['genres'] = clean_tags(data[data.find('</b>'):], '<', '>')
            if u'Страна: </b>' in data:
                info['country'] = clean_tags(data[data.find('</b>'):], '<', '>')            
            if u'Дата выпуска: </b>' in data:
                info['aired_on'] = self.create_aired(data)                   
            if u'<b itemprop="director"' in data:
                info['director'] = clean_tags(data[data.find('</b>'):], '<', '>')
            if u'<b itemprop="author"' in data:
                info['writer'] = clean_tags(data[data.find('</b>'):], '<', '>')
            if u'Озвучивание: </b>' in data:
                info['dubbing'] = clean_tags(data[data.find('</b>'):], '<', '>')
            if u'Перевод: </b>' in data:
                info['translation'] = clean_tags(data[data.find('</b>'):], '<', '>')
            if u'Тайминг и работа со звуком: </b>' in data:
                info['timing'] = clean_tags(data[data.find('</b>'):], '<', '>')
            if u'Студия:</b>' in data:
                info['studios'] = data[data.find('xfsearch/')+9:data.find('/">')]
            if u'Описание:</b>' in data:
                info['description'] = clean_tags(data[data.find('</b>'):], '<', '>')

        if not info['aired_on']:
            if info['year']:
                info['aired_on'] = info['year']

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
            return 101

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
#     def exec_update_anime_part(self):        
#         self.create_info(anime_id=self.params['id'], update=True)
#         xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'ap_anidub_t.db'))
        except: pass

        db_file = os.path.join(self.database_dir, 'ap_anidub_t.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_anidub_t.db'
        try:                
            data = urlopen(db_url)
            chunk_size = 8192
            bytes_read = 0

            try: file_size = int(data.info().getheaders("Content-Length")[0])
            except: file_size = int(data.getheader('Content-Length'))

            self.progress.create(u'Загрузка Базы Данных')
            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                self.progress.close()
            xbmc.executebuiltin('Notification({},{},{},{})'.format('База Данных', '[COLOR=lime]УСПЕШНО ЗАГРУЖЕНА[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('База Данных', '[COLOR=gold]ERROR: 100[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
#     def exec_favorites_part(self):
#         if not self.params['node']:
#             self.progress.create('{}'.format(self.params['portal'].upper()), u'Инициализация')

#             url = '{}mylists/page/{}/'.format(self.site_url,self.params['page'])
#             html = self.network.get_html(target_name=url)
           
#             pages = html[html.find('<div class="navigation">'):html.find('<div class="animelist">')]
#             pages = tag_list(pages).replace(' ','|')

#             last_page = int(pages[pages.rfind('|')+1:]) if pages else -1
                
#             data_array = html[html.find('<div class="animelist">')+23:html.rfind('<label for="mlist">')]
#             data_array = clean_list(data_array).split('<div class="animelist">')

#             i = 0

#             for data in data_array:
#                 data = unescape(data)

#                 i = i + 1
#                 p = int((float(i) / len(data_array)) * 100)

#                 url = data[data.find(self.site_url)+len(self.site_url):data.find('.html"')]
#                 anime_id = url[url.rfind('/')+1:url.find('-')]
#                 cover = data[data.find('data-src="')+10:data.find('" title="')]
                
#                 title = data[data.find('class="upd-title">')+18:]
#                 series = title[title.find('[')+1:title.find(']')]
                

#                 if self.progress.iscanceled():
#                     break
#                 self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

#                 if not self.database.anime_in_db(anime_id):
#                     inf = self.create_info(anime_id)

#                     if type(inf) == int:
#                         self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
#                         continue
                    
#                 label = self.create_title(anime_id, series)
#                 anime_code = data_encode('{}|{}'.format(anime_id, cover))

#                 self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part', 'id': anime_code})
#             self.progress.close()

#             if int(self.params['page']) < last_page:
#                 self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
#                     'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

#             xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

#         if 'plus' in self.params['node']:
#             try:
#                 url = '{}mylists/'.format(self.site_url)
#                 post = 'news_id={}&status_id=3'.format(self.params['id'])
#                 self.network.get_html(target_name=url, post=post)
#                 xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО ДОБАВЛЕНО[/COLOR]', 5000, self.icon))
#             except:
#                 xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, self.icon))

#         if 'minus' in self.params['node']:
#             try:
#                 url = '{}mylists/'.format(self.site_url)
#                 post = 'news_id={}&status_id=0'.format(self.params['id'])
#                 self.network.get_html(target_name=url, post=post)
#                 xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, self.icon))
#             except:
#                 xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, self.icon))
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', '[COLOR=gold]ERROR: 102[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
#     def exec_information_part(self):
#         from info import animeportal_data as info
            
#         start = '[{}]'.format(self.params['param'])
#         end = '[/{}]'.format(self.params['param'])
#         data = info[info.find(start)+6:info.find(end)].strip()

#         self.dialog.textviewer(u'Информация', data)
#         return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        if self.auth_mode:
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title='[B][COLOR=lime][ Популярное за неделю ][/COLOR][/B]', params={'mode': 'popular_part'})
        self.create_line(title='[B][COLOR=lime][ Новое ][/COLOR][/B]', params={'mode': 'common_part'})
        self.create_line(title='[B][COLOR=lime][ TV Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/anime_ongoing/'})
        self.create_line(title='[B][COLOR=lime][ TV 100+ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/shonen/'})
        self.create_line(title='[B][COLOR=lime][ TV Законченные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/full/'})
        self.create_line(title='[B][COLOR=lime][ Аниме OVA ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title='[B][COLOR=lime][ Аниме фильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title='[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
#     def exec_search_part(self):
#         if not self.params['param']:
#             self.create_line(title=u'[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
#             self.create_line(title=u'[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
#             self.create_line(title=u'[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})
#             self.create_line(title=u'[B][COLOR=red][ Поиск по алфавиту ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'alphabet'})

#             data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')
#             data_array.reverse()

#             for data in data_array:
#                 if not data: continue
#                 self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

#         if 'search' in self.params['param']:
#             skbd = xbmc.Keyboard()
#             skbd.setHeading(u'Поиск:')
#             skbd.doModal()
#             if skbd.isConfirmed():
#                 self.params['search_string'] = quote(skbd.getText())
#                 data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')                    
#                 while len(data_array) >= 10:
#                     data_array.pop(0)
#                 data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
#                 self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)
#                 self.params['param'] = 'search_part'
#                 self.exec_common_part()
#             else:
#                 return False

#         if 'genres' in self.params['param']:
#             from info import anidub_genres
#             for i in anidub_genres:
#                 self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

#         if 'years' in self.params['param']:
#             from info import anidub_years
#             for i in anidub_years:
#                 self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

#         if 'alphabet' in self.params['param']:
#             from info import anidub_alphabet            
#             for i in anidub_alphabet:
#                 self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(quote(i))})  
        
#         xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def create_post(self):
        post = ''
        
        if 'search_part' in self.params['param']:
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(quote(self.params['search_string']), self.params['page'])
            
        return post
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('ANIDUB', 'Инициализация')

        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        
        if 'search_part' in self.params['param']:
            url = '{}index.php?do=search'.format(self.site_url)

        html = self.network.get_html(url, post=self.create_post())
        
        data_array = html[html.find('<h2>')+4:html.rfind('</article>')]
        data_array = data_array.split('<h2>')
        
        i = 0
        
        for data in data_array:
            ai = data[data.find('<a href="')+9:data.find('</a>')]
            anime_series = ai[ai.rfind('[')+1:ai.rfind(']')] if '[' in ai else ''
            anime_url = ai[:ai.find('.html')]
            
            # if '/manga/' in anime_url or '/ost/' in anime_url or '/podcast/' in anime_url or '/anons_ongoing/' in anime_url or '/games/' in anime_url or '/videoblog/' in anime_url:
            #     continue
            if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                    continue 
            
            anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
            anime_title = ai[ai.find('>')+1:]
            anime_cover = data[data.find('<img src="')+10:data.find('" alt=""></a>')]
            anime_rating = data[data.find('<sup>рейтинг <b>')+16:data.find('из 5')]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                inf = self.create_info(anime_id)

                if type(inf) == int:
                    self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                    continue

            label = self.create_title(anime_id, anime_series)            
            anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))

            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})
        
        if '<span class="n_next rcol"><a ' in html:
            self.create_line(title='[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                               'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
            
        # if '<span class="n_next rcol"><a ' in html and not self.params['node'] == 'popular':
        #     if self.params['param'] == 'search_part':
        #         self.create_line(title='[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
        #                          'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
        #     else:
        #         self.create_line(title='[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
        #                        'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        # if int(self.params['page']) < last_page:
        #     if 'search_part' in self.params['param']:
        #         self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
        #             'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
        #     else:
        #         self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
        #             'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        
        # else:
        #     self.create_line(title='[COLOR=red][B][ Контент не найден ][/B][/COLOR]', params={'mode': 'main_part'})

        self.progress.close()        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        anime_code = data_decode(self.params['id'])
        
        html = self.network.get_html('https://tr.anidub.com/index.php?newsid={}'.format(anime_code[0]))

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
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        
    def exec_torrent_part(self):
        anime_code = data_decode(self.params['id'])
        
        url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['param'])

        file_name = '{}_{}'.format(self.params['portal'], self.params['param'])
        full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))

        if os.path.isfile(full_name):
            #ret = self.dialog.select('Файл уже существует - выбрать действие:', ['Запустить Уже загруженный торррент', 'Скачать новый торрент с сайта'])
            result = self.dialog.contextmenu(['Использовать старый файл', 'Загрузить новый файл'])

            if result == 0:
                torrent_file = full_name                
            if result == 1:
                torrent_file = self.network.get_file(target_name=url, destination_name=full_name)
        else:
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
                self.create_line(title=series[i], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'play_part', 'index': i, 'id': file_name}, folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'play_part', 'index': 0, 'id': file_name}, folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])

        if '0' in self.addon.getSetting(portal_engine):
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if '1' in self.addon.getSetting(portal_engine):
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)