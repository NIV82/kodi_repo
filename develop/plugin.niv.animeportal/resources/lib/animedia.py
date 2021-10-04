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

class Animedia:
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

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        #self.auth_mode = bool(self.addon.getSetting('animedia_auth_mode') == '1')
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
        self.network = WebTools(auth_usage=self.auth_mode,
                                auth_status=bool(self.addon.getSetting('animedia_auth') == 'true'),
                                proxy_data=self.proxy_data,
                                portal='animedia')
        self.network.sid_file = os.path.join(self.cookie_dir, 'animedia.sid' )
        self.network.auth_post_data = 'ACT=14&RET=%2F&site_id=1&username={}&password={}'.format(
            self.addon.getSetting('animedia_username'), self.addon.getSetting('animedia_password'))
        self.network.auth_url = self.site_url
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
    def create_proxy_data(self):
        if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

            try: proxy_pac = proxy_pac.decode('utf-8')
            except: pass
            
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = proxy_pac.decode('utf-8')
                except: pass
                
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def create_site_url(self):
        site_url = self.addon.getSetting('animedia_mirror_0')
        current_mirror = 'animedia_mirror_{}'.format(self.addon.getSetting('animedia_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('animedia_mirror_0')
            pass
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_url(self):
        url = '{}{}'.format(self.site_url, self.params['param'])

        page = (int(self.params['page']) - 1) * 25

        if 'completed' in self.params['param']:
            url = '{}ajax/search_result_search_page_2/P{}?limit=25&search:ongoing=1&orderby_sort=entry_date|desc'.format(
                self.site_url, page
            )

        if 'search_part' in self.params['param']:
            url = '{}ajax/search_result_search_page_2/P0?limit=25&keywords={}&orderby_sort=entry_date|desc'.format(
                self.site_url, self.params['search_string']
            )

        if 'catalog' in self.params['param']:
            from info import animedia_form, animedia_genre, animedia_voice, animedia_studio, animedia_year, animedia_status, animedia_sort

            genre = '&category={}'.format(animedia_genre[self.addon.getSetting('animedia_genre')]) if animedia_genre[self.addon.getSetting('animedia_genre')] else ''
            voice = '&search:voiced={}'.format(quote(self.addon.getSetting('animedia_voice'))) if self.addon.getSetting('animedia_voice') else ''
            studio = '&search:studies={}'.format(quote(self.addon.getSetting('animedia_studio'))) if self.addon.getSetting('animedia_studio') else ''
            year = '&search:datetime={}'.format(animedia_year[self.addon.getSetting('animedia_year')]) if animedia_year[self.addon.getSetting('animedia_year')] else ''
            form = '&search:type={}'.format(quote(animedia_form[self.addon.getSetting('animedia_form')])) if animedia_form[self.addon.getSetting('animedia_form')] else ''
            status = animedia_status[self.addon.getSetting('animedia_status')] if animedia_status[self.addon.getSetting('animedia_status')] else ''
            sort = animedia_sort[self.addon.getSetting('animedia_sort')]

            url = '{}ajax/search_result_search_page_2/P{}?limit=25{}{}{}{}{}{}{}'.format(self.site_url, page, genre, voice, studio, year, form, status, sort)

        return url
#========================#========================#========================#
    def create_title(self, anime_id, series=None):
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

        return label
#========================#========================#========================#
    def create_image(self, anime_id):        
        url = self.database.get_cover(anime_id)

        if self.addon.getSetting('animedia_covers') == '0':
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
    def create_context(self, anime_id, title_data):
        context_menu = []

        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=animedia")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=animedia")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]',
                                 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&title_data={}&portal=animedia")'.format(anime_id, title_data)))

        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=animedia")'))
        context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=animedia")'))
        context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=animedia")'))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)

            li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
                       "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})
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

            duration = anime_info[6] * 60 if anime_info[6] else 0

            info = {
                'genre':anime_info[7], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                'country':anime_info[18],#string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year':anime_info[3],#	integer (2009)
                'episode':anime_info[2],#	integer (4)
                'director':anime_info[9],#	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                'mpaa':anime_info[5],#	string (PG-13)
                'plot':description,#	string (Long Description)
                'title':title,#	string (Big Fan)
                'duration':duration,#	integer (245) - duration in seconds
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

        li.addContextMenuItems(self.create_context(anime_id, metadata))

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
    def create_info(self, anime_id, title_data=None, update=False):
        info = dict.fromkeys(['anime_tid','title_ru', 'title_en', 'genres', 'year', 'studios', 'dubbing', 'description', 'image'], '')

        if title_data:
            info.update(self.create_title_info(title_data))
        else:
            info.update(self.create_title_info(self.params['title_data']))

        try:
            info['title_ru'] = info['title_ru'].decode(encoding='utf-8', errors='replace')
            info['title_en'] = info['title_en'].decode(encoding='utf-8', errors='replace')
        except:
            pass

        url = '{}anime/{}'.format(self.site_url, anime_id)
        html = self.network.get_html(target_name=url)
        
        if type(html) == int:
            label_ru = u'[B][COLOR=red]ERROR-404 - {}[/COLOR][/B]'.format(info['title_ru'])
            label_en = u'[B][COLOR=red]ERROR-404 - {}[/COLOR][/B]'.format(info['title_ru'])
            self.database.add_anime(anime_id=anime_id, title_ru=label_ru, title_en=label_en)
            return

        html = unescape(html)

        if html.find(u'Скачать торрент') > -1:
            anime_tid = html[html.find('torrents-list/')+14:html.find('" class="btn btn__big btn__g')]
            info['anime_tid'] = quote(anime_tid.encode('utf-8'))

        if html.find(u'Релиз озвучивали:') > -1:
            dubbing = html[html.find(u'Релиз озвучивали:')+17:html.find(u'Новые серии')]
            info['dubbing'] = tag_list(dubbing)

        info['image'] = html[html.find('image" content="')+16:html.find('<meta property="og:type')-5]

        data_array = html[html.find('post__body">')+12:html.find('</article>')]
        data_array = data_array.splitlines()

        for data in data_array:
            if '<p>' in data:
                description = tag_list(data)
                info['description'] = u'{}\n{}'.format(info['description'],description).strip()
            if u'Дата выпуска:' in data:
                data = tag_list(data)
                for year in range(1975, 2030, 1):
                    if str(year) in data:
                        info['year'] = year
            if u'Жанр:' in data:
                data = tag_list(data.replace('</a><a',', <a'))
                info['genres'] = data.replace(u'Жанр:','').strip()
            if u'Студия:' in data:
                data = tag_list(data).replace(u'Студия:','')
                info['studios'] = data.strip()

        try:
            self.database.add_anime(
                anime_id = anime_id,
                anime_tid = info['anime_tid'],
                title_ru = info['title_ru'],
                title_en = info['title_en'],
                dubbing = info['dubbing'],
                genres = info['genres'],
                studios = info['studios'],
                aired_on = info['year'],
                description = info['description'],
                image = info['image'],
                update=update
                )
        except:
            return 101
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
        self.create_info(anime_id=self.params['id'], title_data=self.params['title_data'], update=True)
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
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Удаление истории', '[COLOR=lime]УСПЕШНО ВЫПОЛНЕНО[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Удаление истории', '[COLOR=gold]ERROR: 102[/COLOR]', 5000, self.icon))
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
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=yellow][ Анонсы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'announcements'})
        self.create_line(title='[B][COLOR=lime][ ТОП-100 ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'top-100-anime'})
        self.create_line(title='[B][COLOR=lime][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'populyarnye-anime-nedeli'})
        self.create_line(title='[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'novinki-anime'})
        self.create_line(title='[B][COLOR=lime][ Завершенные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'completed'})
        self.create_line(title='[B][COLOR=blue][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('animedia_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('animedia_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('animedia_search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self, url=None):
        self.progress.create('Animedia', u'Инициализация')

        html = self.network.get_html(target_name=self.create_url())

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if '<div class="ads-list__item">' in html:
            data_array = html[html.find('<div class="ads-list__item">')+28:html.find('<div class="about-page">')]
            data_array = data_array.split('<div class="ads-list__item">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                anime_id = data[data.rfind('col-l"><a href="')+16:data.find(u'" title="Подробнее')]
                anime_id = anime_id[anime_id.rfind('/')+1:]
                anime_id = quote(anime_id.encode('utf-8'))

                title_data = data[data.find(u'смотреть аниме онлайн')+21:data.find('" class="btn btn__black')]

                # if '></div></div>' in anime_id:
                #     continue

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id, title_data)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=lime]ID: {} ][/COLOR][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(anime_id)
                self.create_line(title=label, anime_id=anime_id, metadata=title_data.encode('utf-8'), params={'mode': 'select_part', 'id': anime_id})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
        
        self.progress.close()

        if 'Загрузить ещё' in html:
            self.create_line(title='[B][COLOR=orange][ Следующая страница ][/COLOR][/B]', params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

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
            self.create_line(title='[COLOR=yellow][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        
        if self.params['param'] == 'form':
            result = self.dialog.select('Выберите Тип:', tuple(animedia_form.keys()))
            self.addon.setSetting(id='animedia_form', value=tuple(animedia_form.keys())[result])
        
        if self.params['param'] == 'genre':
            result = self.dialog.select('Выберите Жанр:', tuple(animedia_genre.keys()))
            self.addon.setSetting(id='animedia_genre', value=tuple(animedia_genre.keys())[result])

        if self.params['param'] == 'voice':
            result = self.dialog.select('Выберите Войсера:', animedia_voice)
            self.addon.setSetting(id='animedia_voice', value=animedia_voice[result])

        if self.params['param'] == 'studio':
            result = self.dialog.select('Выберите Студию:', animedia_studio)
            self.addon.setSetting(id='animedia_studio', value=animedia_studio[result])

        if self.params['param'] == 'year':
            result = self.dialog.select('Выберите Год:', tuple(animedia_year.keys()))
            self.addon.setSetting(id='animedia_year', value=tuple(animedia_year.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Выберите статус:', tuple(animedia_status.keys()))
            self.addon.setSetting(id='animedia_status', value=tuple(animedia_status.keys())[result])
        
        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', tuple(animedia_sort.keys()))
            self.addon.setSetting(id='animedia_sort', value=tuple(animedia_sort.keys())[result])
#========================#========================#========================#
    def exec_select_part(self):
        self.create_line(title=u'[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id']})
        if self.database.get_tid(self.params['id']):
            self.create_line(title=u'[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            html = self.network.get_html(
                target_name='{}anime/{}'.format(self.site_url,self.params['id']))
            
            html = unescape(html)

            if 'data-entry_id=' in html:
                data_entry = html[html.find('data-entry_id="')+15:html.find('<li class="media__tabs__nav__item')]
                data_entry = data_entry[:data_entry.find('">')]

                data_array = html[html.find('<a href="#tab'):html.find('<div class="media__tabs__content')]
                data_array = data_array.strip()
                data_array = data_array.split('<li class="media__tabs__nav__item">')

                for data in data_array:
                    tab_num = data[data.find('"#tab')+5:data.find('" role')]
                    tab_name = data[data.find('"tab">')+6:data.find('</a></li>')]

                    tab_entry = '|||{}/{}'.format(data_entry, int(tab_num)+1)
                    
                    self.create_line(title=tab_name, params={'mode': 'online_part', 'param': tab_entry, 'id': self.params['id']})
            else:
                self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})

        if '|||' in self.params['param']:
            url = '{}ajax/episodes/{}/undefined'.format(self.site_url, self.params['param'].replace('|||',''))

            html = self.network.get_html(target_name=url)
            
            html = unescape(html)

            data_array = html[html.find('list__item">')+12:html.find('<div class="clearfix">')]
            data_array = data_array.split('<div class="media__tabs__series__list__item">')

            for data in data_array:
                data = data.strip()

                series_url = data[data.find('<a href="/')+10:data.find('" title')]
                series_title = data[data.find('title="')+7:data.find('"><img data-src')]

                self.create_line(title=series_title, anime_id=self.params['id'], params={'mode': 'online_part', 'param': series_url, 'id': self.params['id']})

        if 'anime/' in self.params['param']:
            html = self.network.get_html(
                target_name='{}{}'.format(self.site_url, self.params['param']))
            
            html = unescape(html)

            title = html[html.find('post__title">')+13:html.find('</h1>')]
            title = title.replace(u'Смотреть онлайн','').strip()

            video_url = html[html.find('iframe" content="')+17:html.find('<meta property="ya:ovs:allow_embed')]
            video_url = video_url[:video_url.find('" />')]

            if video_url:
                html = self.network.get_html(target_name=video_url)

                online_url = html[html.find('file: "')+7:html.find('",poster')]
                if not 'https:' in online_url:
                    online_url = online_url.replace('//','https://')
              
                self.create_line(title=title, params={}, anime_id=self.params['id'], online=online_url, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            html = self.network.get_html(
                target_name='https://tt.animedia.tv/anime/{}'.format(self.database.get_tid(self.params['id']))
                )

            html = unescape(html)

            metadata = dict.fromkeys(['series', 'quality', 'size', 'container', 'video', 'audio', 'translate', 'timing'], '')

            tab = []

            if '<div class="media__tabs" id="down_load">' in html:
                tabs_nav = html[html.find('data-toggle="tab">')+18:html.find('<!-- tabs navigation end-->')]
                tabs_nav = tabs_nav.split('data-toggle="tab">')

                for tabs in tabs_nav:
                    nav = tabs[:tabs.find('</a></li>')]
                    tab.append(nav)

                tabs_content = html[html.find('<div class="tracker_info">')+26:html.find('<!-- tabs content end-->')]
                tabs_content = tabs_content.split('<div class="tracker_info">')
                
                for x, content in enumerate(tabs_content):
                    title = tab[x].strip()

                    seed = content[content.find('green_text_top">')+16:content.find('</div></div></div>')]
                    peer = content[content.find('red_text_top">')+14:content.find('</div></div></div></div>')]

                    torrent_url = content[content.find('<a href="')+9:content.find('" class')]
                    #magnet_url = content[content.rfind('<a href="')+9:content.rfind('" class')]

                    content = content.splitlines()

                    for line in content:
                        if '<h3 class=' in line:
                            if title in line:
                                metadata['series'] = ''
                            else:
                                series = line[line.find('">')+2:line.find('</h3>')].replace(u'из XXX','')
                                series = series.replace(u'Серии','').replace(u'Серия','').strip()
                                metadata['series'] = u' - [ {} ]'.format(series)

                            metadata['quality'] = line[line.find('</h3>')+5:]
                            metadata['quality'] = metadata['quality'].replace(u'Качество','').strip()
                        if u'>Размер:' in line:
                            metadata['size'] = tag_list(line[line.find('<span>'):])
                        # if u'Контейнер:' in line:
                        #     metadata['container'] = line[line.find('<span>')+6:line.find('</span>')]
                        # if u'Видео:' in line:
                        #     metadata['video'] = line[line.find('<span>')+6:line.find('</span>')]
                        # if u'Аудио:' in line:                        
                        #     metadata['audio'] = line[line.find('<span>')+6:line.find('</span>')].strip()
                        # if u'Перевод:' in line:                        
                        #     metadata['translate'] = line[line.find('<span>')+6:line.find('</span>')]
                        # if u'Тайминг и сведение звука:' in line:
                        #     metadata['timing'] = line[line.find('<span>')+6:line.find('</span>')]
                        
                    label = u'{}{} , [COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сиды: [COLOR=lime]{}[/COLOR] , Пиры: [COLOR=red]{}[/COLOR]'.format(
                        title, metadata['series'], metadata['size'], metadata['quality'], seed, peer)                    
                    
                    #self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'], metadata=metadata)
                    #self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'param': torrent_url},  anime_id=self.params['id'], metadata=metadata)
                    self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'param': torrent_url},  anime_id=self.params['id'])
            else:
                tabs_content = html[html.find('<li class="tracker_info_pop_left">')+34:html.find('<!-- Media series tabs End-->')]
                tabs_content = tabs_content.split('<li class="tracker_info_pop_left">')

                for content in tabs_content:
                    content = clean_list(content)
                    title = content[content.find('left_top">')+10:content.find('</span>')]
                    title = title.replace(u'Серии ','').replace(u'Серия ','').strip()
                    
                    quality = content[content.find(')')+1:content.find('</span><p>')]

                    quality = quality.replace(u'р', u'p').strip()

                    torr_inf = content[content.find('left_op">')+9:content.rfind(';</span></span></p>')]
                    torr_inf = tag_list(torr_inf)
                    torr_inf = torr_inf.replace(u'Размер: ','').replace(u'Сидов: ','').replace(u'Пиров: ','')
                    torr_inf = torr_inf.split(';')

                    # magnet_url = content[content.find('href="')+6:content.find('" class=')]
                    torrent_url = content[content.rfind('href="')+6:content.rfind('" class=')]

                    label = u'Серии: {} , [COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                        title, torr_inf[0], quality, torr_inf[2], torr_inf[3])

                    self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'param': torrent_url},  anime_id=self.params['id'])

        if self.params['param']:
            url = self.params['param']

            file_name = '{}_{}'.format(self.params['portal'], self.params['id'])
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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False, size=size[i])
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