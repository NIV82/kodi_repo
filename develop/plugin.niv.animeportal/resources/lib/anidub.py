# -*- coding: utf-8 -*-

import os, sys, time
import xbmc, xbmcgui, xbmcplugin

try:
    from urllib import urlencode, urlopen, quote, unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen
    from html import unescape

from utility import tag_list, clean_list

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

        #self.proxy_data = self.create_proxy_data()
        self.proxy_data = None

        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('{}_auth_mode'.format(self.params['portal'])) == '1')
#========================#========================#========================#
        try: session = float(self.addon.getSetting('{}_session'.format(self.params['portal'])))
        except: session = 0

        if time.time() - session > 28800:
            self.addon.setSetting('{}_session'.format(self.params['portal']), str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal'])))
            except: pass
            self.addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('{}_auth'.format(self.params['portal'])) == 'true'),
            proxy_data=self.proxy_data, portal=self.params['portal'])
        self.auth_post_data = 'login_name={}&login_password={}&login=submit'.format(
            self.addon.getSetting('{}_username'.format(self.params['portal'])),
            self.addon.getSetting('{}_password'.format(self.params['portal']))
            )
        self.network.auth_post_data = self.auth_post_data
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not self.addon.getSetting('{}_username'.format(self.params['portal'])) or not self.addon.getSetting('{}_password'.format(self.params['portal'])):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ВВЕДИТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                    return
                else:
                    self.addon.setSetting('{}_auth'.format(self.params['portal']), str(self.network.auth_status).lower())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
#========================#========================#========================#
    # def create_proxy_data(self):
    #     if 'torrent_part' in self.params['mode']:
    #         self.addon.setSetting('{}_unblock'.format(self.params['portal']), '1')
    #     else:
    #         self.addon.setSetting('{}_unblock'.format(self.params['portal']), '0')

    #     if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
    #         return None

    #     try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
    #     except: proxy_time = 0

    #     if time.time() - proxy_time > 86400:
    #         self.addon.setSetting('animeportal_proxy_time', str(time.time()))
    #         proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

    #         try: proxy_pac = proxy_pac.decode('utf-8')
    #         except: pass
            
    #         proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
    #         self.addon.setSetting('animeportal_proxy', proxy)
    #         proxy_data = {'https': proxy}
    #     else:
    #         if self.addon.getSetting('animeportal_proxy'):
    #             proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
    #         else:
    #             proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

    #             try: proxy_pac = proxy_pac.decode('utf-8')
    #             except: pass

    #             proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
    #             self.addon.setSetting('animeportal_proxy', proxy)
    #             proxy_data = {'https': proxy}

    #     return proxy_data
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = '{}_mirror_{}'.format( self.params['portal'],
            self.addon.getSetting('{}_mirror_mode'.format(self.params['portal'])))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('{}_mirror_0'.format(self.params['portal']))
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_title_info(self, title):
        info = dict.fromkeys(['series', 'title_ru', 'title_en'], '')

        title = tag_list(title).replace('...','')
        title = title.replace('/ ', ' / ').replace('  ', ' ')
        title = title.replace('|', '/').replace(u' / ',' / ')
        title = title.replace('  [', ' [').replace ('\\', '/')

        v = title.split(' / ', 1)
        
        if len(v) == 1:           
            v = title.split('  ', 1)
            if len(v) == 1:
                title = title.replace('/ ', ' / ')
                v = title.split(' / ', 1)
            if len(v) == 1:
                title = title.replace(' /', ' / ')
                v = title.split(' / ', 1)
               
        try:
            part_pos = v[len(v) - 1][v[len(v) - 1].find(' ['):v[len(v) - 1].find(']')+1]
            v.insert(0, part_pos.replace('[', '').replace(']', '').strip())
            v[len(v) - 1] = v[len(v) - 1].replace(part_pos, '')
        except:
            v.insert(0, '')
        if len(v) == 2:
            v.append('')

        try:
            info['series'] = v[0]
            info['title_ru'] = v[1].capitalize()
            info['title_en'] = v[2].capitalize()
        except:
            pass
        return info
#========================#========================#========================#
    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        if series:
            series = series.strip()
            series = u' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
        
        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{} / {}{}'.format(title[0], title[1], series)

        if 'ERROR-404' in label:
            label = u'[COLOR=red][B]{}[/B][/COLOR]'.format(label)
        return label
#========================#========================#========================#
    def create_image(self, anime_id):
        url = '{}'.format(self.database.get_cover(anime_id))

        if not 'https://' in url:
            url = '{}{}'.format(self.site_url, url.replace('/','',1))
        
        if '0' in self.addon.getSetting('{}_covers'.format(self.params['portal'])):
            return url
        else:
            local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal={}")'.format(self.params['portal'])))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal={}")'.format(self.params['portal'])))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal={}")'.format(anime_id, self.params['portal'])))

        if self.auth_mode:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal={}")'.format(anime_id, self.params['portal'])))
                context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal={}")'.format(anime_id, self.params['portal'])))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal={}")'.format(self.params['portal'])))
        context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal={}")'.format(self.params['portal'])))
        context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal={}")'.format(self.params['portal'])))
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            if cover:
                pass
            else:
                cover = self.create_image(anime_id)
            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})
            # 0     1       2           3           4           5       6       7       8       9           10          11      12          13      14      15          16      17      18      19
            #kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios
            anime_info = self.database.get_anime(anime_id)
            
            description = u'{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(anime_info[10], anime_info[11])
            description = u'{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(description, anime_info[12])
            description = u'{}\n[COLOR=steelblue]Тайминг[/COLOR]: {}'.format(description, anime_info[13])
            description = u'{}\n[COLOR=steelblue]Работа над звуком[/COLOR]: {}'.format(description, anime_info[14])
            description = u'{}\n[COLOR=steelblue]Mastering[/COLOR]: {}'.format(description, anime_info[15])
            description = u'{}\n[COLOR=steelblue]Редактирование[/COLOR]: {}'.format(description, anime_info[16])
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
    def create_year(self, data):
        data = tag_list(data)

        rep_list = [
            (u'январ', '.01.'),(u'янв', '.01.'),(u'феврал', '.02.'),(u'фев', '.02.'),
            (u'март', '.03.'),(u'апрел', '.04.'),(u'апр','.04.'),(u'май', '.05.'),
            (u'июн', '.06.'),(u'июл', '.07.'),(u'август', '.08.'),(u'авг', '.08.'),
            (u'сентябр', '.09.'),(u'сен', '.09.'),(u'октябр', '.10.'),(u'окт', '.10.'),
            (u'ноябр', '.11.'),(u'декабр', '.12.'),(u'дек', '.12.'),
            (u'Начало показа:',''),(u'по','|'),(',','|'),('-','|'),('..','.')
            ]

        for value in rep_list:
            data = data.replace(value[0], value[1])
        
        s = []
        for i in data:
            if i.isdigit() or i in ('.','|'):
                s.append(i)
        data = ''.join(s)
       
        if not data:
            return
        
        data_array = data.split('|')        

        if len(data_array) == 1:
            aired_on = data_array[0]
            
            if '.' in aired_on[len(aired_on)-1]:
                aired_on = aired_on[:len(aired_on)-1]
                
            return {'aired_on':aired_on,'released_on':''}
        
        if len(data_array) == 2:
            aired_on = data_array[0]
            released_on = data_array[1]

            if '.' in aired_on[len(aired_on)-1]:
                aired_on = aired_on[:len(aired_on)-1]
            
            if '.' in released_on[len(released_on)-1]:
                released_on = released_on[:len(released_on)-1]

            return {'aired_on':aired_on, 'released_on':released_on}

        if len(data_array) > 2:
            return {'aired_on': 'EXCEPTIONS','released_on':'EXCEPTIONS'}
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        html = self.network.get_html(target_name=url)

        if type(html) == int:
            self.database.add_anime(anime_id=anime_id, title_ru='ERROR-404', title_en='ERROR-404')
            return

        html = unescape(html)

        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'released_on', 'genres', 'director', 'writer', 'description', 'dubbing',
                      'translation', 'timing', 'country', 'studios', 'image', 'anime_tid'], '')

        image = html[html.find('fposter img-box img-fit">')+25:html.find(u'" title="Постер аниме {')]
        info['image'] = image[image.find('data-src="')+10:]

        title_data = html[html.find('<h1>')+4:html.find('</h1>')]
        info.update(self.create_title_info(title_data))

        description = html[html.find(u'Описание</div>')+14:html.find(u'Рейтинг:</div>')]
        info['description'] = clean_list(tag_list(description))

        data_array = html[html.find('<div class="fmeta fx-row fx-start">'):html.find('<div class="fright-title">')]
        data_array = data_array.splitlines()

        for data in data_array:
            if 'xfsearch/year/' in data:
                info['aired_on'] = tag_list(data)
            if u'Начало показа:</span>' in data:
                inf = self.create_year(data)
                if inf:
                    info.update(inf)
            if 'xfsearch/country/' in data:
                info['country'] = tag_list(data)
            if u'Жанр:</span>' in data:
                info['genres'] = tag_list(data.replace(u'Жанр:</span>', '')).lower()
            if u'Автор оригинала:</span>' in data:
                info['writer'] = tag_list(data.replace(u'Автор оригинала:</span>', ''))
            if u'Режиссер:</span>' in data:
                info['director'] = tag_list(data.replace(u'Режиссер:</span>', ''))
            if u'Перевод:</span>' in data:
                info['translation'] = tag_list(data.replace(u'Перевод:</span>', ''))
            if u'Студия:</span>' in data:
                info['studios'] = tag_list(data.replace(u'Студия:</span>', ''))
            if u'Озвучивание:</span>' in data:
                info['dubbing'] = tag_list(data.replace(u'Озвучивание:</span>', ''))
            if u'Тайминг:</span>' in data:
                info['timing'] = tag_list(data.replace(u'Тайминг:</span>', ''))
            if u'Ссылка на трекер:</span>' in data:
                anime_tid = data[data.find('https://tr.anidub.com/')+22:data.find('.html')]
                info['anime_tid'] = anime_tid.replace('-','')
        
        try:
            self.database.add_anime(
                anime_id = anime_id,
                anime_tid = info['anime_tid'],
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
                released_on = info['released_on'],
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
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True)
        xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        except: pass

        db_file = os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_{}.db'.format(self.params['portal'])
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
    def exec_favorites_part(self):
        if not self.params['node']:
            self.progress.create('{}'.format(self.params['portal'].upper()), u'Инициализация')

            url = '{}mylists/page/{}/'.format(self.site_url,self.params['page'])
            html = self.network.get_html(target_name=url)
            
            pages = html[html.find('<div class="navigation">'):html.find('<div class="animelist">')]
            pages = tag_list(pages).replace(' ','|')

            if pages: last_page = int(pages[pages.rfind('|')+1:])
            else: last_page = -1
                
            data_array = html[html.find('<div class="animelist">')+23:html.rfind('<label for="mlist">')]
            data_array = clean_list(data_array).split('<div class="animelist">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                url = data[data.find(self.site_url)+len(self.site_url):data.find('.html"')]
                anime_id = url[url.rfind('/')+1:url.find('-')]

                title = data[data.find('class="upd-title">')+18:]
                series = title[title.find('[')+1:title.find(']')]

                if self.progress.iscanceled():
                    break
                self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue
                    
                label = self.create_title(anime_id, series)

                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
            self.progress.close()

            if int(self.params['page']) < last_page:
                self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'plus' in self.params['node']:
            try:
                url = '{}mylists/'.format(self.site_url)
                post = 'news_id={}&status_id=3'.format(self.params['id'])
                self.network.get_html(target_name=url, post=post)
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО ДОБАВЛЕНО[/COLOR]', 5000, self.icon))
            except:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, self.icon))

        if 'minus' in self.params['node']:
            try:
                url = '{}mylists/'.format(self.site_url)
                post = 'news_id={}&status_id=0'.format(self.params['id'])
                self.network.get_html(target_name=url, post=post)
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, self.icon))
            except:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, self.icon))
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', '[COLOR=gold]ERROR: 102[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
    def exec_information_part(self):
        from info import animeportal_data as info
            
        start = '[{}]'.format(self.params['param'])
        end = '[/{}]'.format(self.params['param'])
        data = info[info.find(start)+6:info.find(end)].strip()

        self.dialog.textviewer(u'Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=u'[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        if self.auth_mode:
            self.create_line(title=u'[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title=u'[B][COLOR=lime][ Аниме ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/'})
        self.create_line(title=u'[B][COLOR=lime][ Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/anime_ongoing/'})
        self.create_line(title=u'[B][COLOR=lime][ Вышедшие сериалы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/full/'})
        self.create_line(title=u'[B][COLOR=lime][ Аниме фильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title=u'[B][COLOR=lime][ Аниме OVA ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title=u'[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по алфавиту ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')
            data_array.reverse()

            for data in data_array:
                if not data: continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if 'search' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if 'genres' in self.params['param']:
            from info import anidub_genres
            for i in anidub_genres:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

        if 'years' in self.params['param']:
            from info import anidub_years
            for i in anidub_years:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

        if 'alphabet' in self.params['param']:
            from info import anidub_alphabet            
            for i in anidub_alphabet:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(quote(i))})  
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('{}'.format(self.params['portal'].upper()), 'Инициализация')

        #url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        url = '{}{}page/{}/'.format(self.site_url, quote(self.params['param']), self.params['page'])
        post = ''

        if 'search_part' in self.params['param']:
            url = '{}index.php?do=search'.format(self.site_url)
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(quote(self.params['search_string']), self.params['page'])

        html = self.network.get_html(url, post=post)
        
        if html.find('<div class="th-item">') > -1:
            #pages = html[html.rfind('<div class="navigation">'):html.rfind('<!--/noindex-->')]
            pages = html[html.rfind('<div class="navigation">'):html.rfind('<footer class="footer sect-bg">')]
            pages = tag_list(pages).replace(' ','|')

            if pages: last_page = int(pages[pages.rfind('|')+1:])
            else: last_page = -1

            data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
            data_array = clean_list(data_array).split('<div class="th-item">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                    
                url = data[data.find('th-in" href="')+13:data.find('.html">')]

                if '/manga/' in url or '/ost/' in url or '/podcast/' in url or '/anons_ongoing/' in url or '/games/' in url or '/videoblog/' in url:
                    continue

                anime_id = url[url.rfind('/')+1:url.find('-')]
                
                title = data[data.find('<div class="fx-1">')+18:data.find('</div><span>')]
                info = self.create_title_info(title)

                if self.progress.iscanceled():
                    break
                self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(anime_id, info['series'])

                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
            
            if int(self.params['page']) < last_page:
                if 'search_part' in self.params['param']:
                    self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                        'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
                else:
                    self.create_line(title=u'[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={
                        'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        else:
            self.create_line(title='[COLOR=red][B][ Контент не найден ][/B][/COLOR]', params={'mode': 'main_part'})

        self.progress.close()        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        self.create_line(title=u'[B]Онлайн просмотр[/B]', params={'mode': 'online_part', 'id': self.params['id']})
        if self.database.get_tid(self.params['id']):
            self.create_line(title=u'[B]Торрент просмотр[/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        from utility import digit_list
        if not self.params['param']:
            url = '{}index.php?newsid={}'.format(self.site_url, self.params['id'])
            
            html = self.network.get_html(url)

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
            url = 'https://video.sibnet.ru/shell.php?videoid={}'.format(self.params['param'])

            html = self.network.get_html(target_name=url)            

            if 'player.src' in html:
                video_src = html[html.find('player.src([{src: "')+19:html.find(';player.persistvolume')]
                video_src = video_src[:video_src.find('"')]

                play_url = 'https://video.sibnet.ru{}|referer={}'.format(video_src, url)

                label = 'Смотреть'

            if 'class=videostatus><p>' in html:
                status = html[html.find('class=videostatus><p>')+21:html.find('</p></div><script')]
                label = '[COLOR=red][B][ {} ][/B][/COLOR]'.format(status.replace('.',''))
                play_url = ''

            self.create_line(title=label, params={}, anime_id=self.params['id'], online=play_url, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            anime_tid = self.database.get_tid(self.params['id'])
            html = self.network.get_html('https://tr.anidub.com/index.php?newsid={}'.format(anime_tid))
        
            html = html[html.find('<div class="torrent_c">')+23:html.rfind(u'Управление')]

            data_array = html.split('</ul-->')

            qa = []
            la = []

            for data in data_array:
                torrent_id = data[data.find('torrent_')+8:data.find('_info\'>')]

                if '<div id="' in data:
                    quality = data[data.find('="')+2:data.find('"><')]
                    qa.append(quality)

                if '<div id=\'torrent_' in data:
                    quality = qa[len(qa) - 1]
                    if u'Серии в торренте:' in data:
                        series = data[data.find(u'Серии в торренте:')+17:data.find(u'Раздают')]
                        series = tag_list(series)
                    
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

                self.create_line(title=label, anime_id=self.params['id'], params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id']})

        if self.params['param']:
            url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['param'])            
            
            file_name = '{}_{}'.format(self.params['portal'], self.params['param'])
            full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))
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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False,  size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], folder=False, size=info['length'])

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