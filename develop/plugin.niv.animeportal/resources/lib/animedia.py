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

from utility import clean_list, clean_tags, data_encode, data_decode

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

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
    # def create_proxy_data(self):
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
        site_url = self.addon.getSetting('animedia_mirror_0')
        current_mirror = 'animedia_mirror_{}'.format(self.addon.getSetting('animedia_mirror_mode'))
        
        if not self.addon.getSetting(current_mirror):
            try:
                self.exec_mirror_part()
                site_url = self.addon.getSetting(current_mirror)
            except:
                site_url = site_url
            
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
                
        year = self.database.get_year(anime_id)
        year = '[COLOR=blue]{}[/COLOR] | '.format(year) if year else ''
        
        series = u' | [COLOR=gold]{}[/COLOR]'.format(series.strip()) if series else ''
            
        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}{}'.format(year, title[0], series)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}{}'.format(year, title[1], series)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{} / {}{}'.format(year, title[0], title[1], series)

        if 'anime_id:' in label:
            label = u'[COLOR=red]ERROR[/COLOR] | Ошибка 403-404 | [COLOR=gold]{}[/COLOR]'.format(
                title[0].replace('anime_id: ',''))
            
        return label
#========================#========================#========================#
    def create_image(self, url, anime_id):
        if '0' in self.addon.getSetting('animedia_covers'):
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
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=animedia")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]','Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=animedia")'.format(anime_id)))
            
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=animedia")'))
        
        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=animedia")'))
        #context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=animedia")'))
        #context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=animedia")'))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(cover, anime_id)

            li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
                       "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})
            
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
                'aired':anime_info[3]
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        #li.addContextMenuItems(self.create_context(anime_id, metadata))
        li.addContextMenuItems(self.create_context(anime_id))

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
    def create_info(self, anime_id, update=False):
        info = dict.fromkeys(['title_ru', 'title_en', 'genres', 'aired_on', 'studios', 'dubbing', 'description'], '')

        url = '{}anime/{}'.format(self.site_url, quote(anime_id))

        html = self.network.get_html(target_name=url)
        
        if not html:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru='anime_id: {}'.format(anime_id),
                title_en='anime_id: {}'.format(anime_id)
                )
            return

        html = unescape(html)

        if u'Релиз озвучивали:' in html:
            dubbing = html[html.find(u'Релиз озвучивали:')+17:html.find(u'Новые серии')]
            info['dubbing'] = clean_tags(dubbing)

        data_array = html[html.find('class="media__post">')+20:html.find('</article>')]
        data_array = data_array.splitlines()

        for data in data_array:
            if 'post__title">' in data:
                info['title_ru'] = clean_tags(data.replace(u'смотреть онлайн', ''))
            if 'original-title">' in data:
                info['title_en'] = clean_tags(data)
            if '<p>' in data:
                info['description'] = u'{}\n{}'.format(info['description'], clean_tags(data).strip())
            if u'Дата выпуска:' in data:
                data = clean_tags(data)
                for year in range(1975, 2030, 1):
                    if str(year) in data:
                        info['aired_on'] = year
            if u'Жанр:' in data:
                info['genres'] = clean_tags(data[data.find(':')+1:].replace('</a><a',', <a'))
            if u'Студия:' in data:
                info['studios'] = clean_tags(data[data.find(':')+1:])

        if not info['aired_on']:
            info['aired_on'] = 9999

        try:
            self.database.add_anime(
                anime_id = quote(anime_id),
                title_ru = info['title_ru'],
                title_en = info['title_en'],
                dubbing = info['dubbing'],
                genres = info['genres'],
                studios = info['studios'],
                aired_on = info['aired_on'],
                description = info['description'],
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
        # self.create_info(anime_id=self.params['id'], title_data=self.params['title_data'], update=True)
        self.create_info(anime_id=self.params['id'], update=True)
        xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_mirror_part(self):
        # auth = self.addon.getSetting('animedia_auth_mode')
        
        # self.addon.setSetting('animedia_auth_mode', '0')

        from network import WebTools
        self.net = WebTools()
        del WebTools

        mirror = self.net.get_animedia_actual(
            self.addon.getSetting('{}_mirror_0'.format(self.params['portal']))
        )

        self.addon.setSetting('{}_mirror_1'.format(self.params['portal']), 'https://{}/'.format(mirror))
        
        #self.addon.setSetting('animedia_auth_mode', auth)
        return
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
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=yellow]Анонсы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'announcements'})
        self.create_line(title='[B][COLOR=lime]ТОП-100[/COLOR][/B]', params={'mode': 'common_part', 'param': 'top-100-anime'})
        self.create_line(title='[B][COLOR=lime]Популярное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'populyarnye-anime-nedeli'})
        self.create_line(title='[B][COLOR=lime]Новинки[/COLOR][/B]', params={'mode': 'common_part', 'param': 'novinki-anime'})
        self.create_line(title='[B][COLOR=lime]Завершенные[/COLOR][/B]', params={'mode': 'common_part', 'param': 'completed'})
        self.create_line(title='[B][COLOR=blue]Каталог[/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('animedia_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('animedia_search').split('|')                    
                while len(data_array) >= 6:
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

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not '<div class="ads-list__item">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

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
            
            anime_cover = data[data.find('<img data-src="')+15:data.find('?h=')]

            torrent_url = data[data.find('tt.animedia.tv'):data.find(u'" title="Скачать')]
            if torrent_url:
                torrent_url = 'https://{}'.format(torrent_url)

            anime_code = data_encode('{}|{}'.format(anime_id, torrent_url))

            # if '></div></div>' in anime_id:
            #     continue

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id)
            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, params={'mode': 'select_part', 'id': anime_code})

        self.progress.close()

        if u'Загрузить ещё' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
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
        anime_code = data_decode(self.params['id'])
        self.create_line(title=u'[B]Онлайн просмотр[/B]', params={'mode': 'online_part', 'id': anime_code[0]})
        if anime_code[1]:
            self.create_line(title=u'[B]Торрент просмотр[/B]', params={'mode': 'torrent_part', 'id': self.params['id']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        html = self.network.get_html(
            target_name='{}anime/{}'.format(self.site_url,self.params['id']))
            
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
            
        if not 'data-entry_id=' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
            
        html = unescape(html)
            
        data_entry = html[html.find('data-entry_id="')+15:html.find('<li class="media__tabs__nav__item')]
        data_entry = data_entry[:data_entry.find('">')]

        data_array = html[html.find('<a href="#tab'):html.find('<div class="media__tabs__content')]
        data_array = data_array.strip()
        data_array = data_array.split('<li class="media__tabs__nav__item">')

        for data in data_array:
            tab_num = data[data.find('"#tab')+5:data.find('" role')]
            tab_name = data[data.find('"tab">')+6:data.find('</a></li>')]

            self.create_line(title='[B]{}[/B]'.format(tab_name), params={})
                
            url = '{}/embeds/playlist-j.txt/{}/{}'.format(self.site_url, data_entry, int(tab_num)+1)

            html = self.network.get_html(target_name=url)
            html = unescape(html)

            data_array = html.split('},')

            for data in data_array:
                series_title = data[data.find('title":"')+8:data.find('","file')]
                    
                series_file = data[data.find('file":"')+7:data.find('","poster')]
                if not 'https:' in series_file:
                    series_file = 'https:{}'.format(series_file)
                    
                series_poster = data[data.find('poster":"')+9:data.find('","id"')]
                series_poster = 'https:{}'.format(series_poster)

                series_id = data[data.find('id":"')+5:data.rfind('"')]
                series_id = series_id.replace('s', '').split('e')
                series_id = '[COLOR=blue]SE{:>02}[/COLOR][COLOR=lime]EP{:>02}[/COLOR]'.format(series_id[0],series_id[1])
                    
                label = '{} | [B]{}[/B]'.format(series_id, series_title)                    
                    
                self.create_line(title=label, cover=series_poster, anime_id=self.params['id'], params={}, online=series_file, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            anime_code = data_decode(self.params['id'])
            
            html = self.network.get_html(target_name=anime_code[1])
            html = unescape(html)

            cover = html[html.find('poster"><a href="')+17:html.find('" class="zoomLink')]
            #cover = html[html.rfind('<img src="')+10:html.rfind('" alt=')]
            
            info = dict.fromkeys(['series', 'quality', 'size'], '')

            if '<div class="media__tabs" id="down_load">' in html:
                tabs_nav = html[html.find('data-toggle="tab">')+18:html.find('<div class="media__tabs_')]
                tabs_nav = tabs_nav.split('data-toggle="tab">')

                tabs_content = html[html.find('<div class="tracker_info">')+26:html.rfind(u'Скачать торрент')]
                tabs_content = tabs_content.split('<div class="tracker_info">')

                for x, tabs in enumerate(tabs_nav):
                    title = tabs[:tabs.find('</a></li>')]

                    seed = tabs_content[x][tabs_content[x].find('green_text_top">')+16:tabs_content[x].find('</div></div></div>')]
                    peer = tabs_content[x][tabs_content[x].find('red_text_top">')+14:tabs_content[x].find('</div></div></div></div>')]
                    torrent_url = tabs_content[x][tabs_content[x].find('<a href="')+9:tabs_content[x].find('" class')]

                    content = tabs_content[x].splitlines()

                    for line in content:
                        if '<h3 class=' in line:
                            if title in line:
                                info['series'] = ''
                            else:
                                series = line[line.find('">')+2:line.find('</h3>')].replace(u'из XXX','')
                                info['series'] = series.replace(u'Серии','').replace(u'Серия','').strip()

                            info['quality'] = line[line.find('</h3>')+5:]
                            info['quality'] = info['quality'].replace(u'Качество','').strip()
                        if u'>Размер:' in line:
                            info['size'] = clean_tags(line[line.find('<span>'):])
                            
                    anime_code2 = data_encode('{}|{}'.format(anime_code[0], cover))
                        
                    label = u'{} | {} | [COLOR=yellow]{}[/COLOR] : [COLOR=blue]{}[/COLOR] | Сиды: [COLOR=lime]{}[/COLOR] , Пиры: [COLOR=red]{}[/COLOR]'.format(
                        title, info['series'], info['size'], info['quality'], seed, peer)
                    
                    self.create_line(title=label, anime_id=anime_code[0], cover=cover, params={'mode': 'torrent_part', 'id': anime_code2, 'param': torrent_url})
            else:
                tabs_content = html[html.find('<li class="tracker_info_pop_left">')+34:html.find('<!-- Media series tabs End-->')]
                tabs_content = tabs_content.split('<li class="tracker_info_pop_left">')

                for content in tabs_content:
                    title = content[content.find('left_top">')+10:content.find('</span>')]

                    quality = content[content.find('intup_left_ser'):content.find('intup_left_op')]
                    quality = [i for i in ('1080','720','480') if i in quality][0]
                    
                    torr_inf = content[content.find('left_op">')+9:content.rfind(';</span></span></p>')]
                    torr_inf = clean_tags(torr_inf)
                    torr_inf = torr_inf.replace(u'Размер: ','').replace(u'Сидов: ','').replace(u'Пиров: ','')
                    torr_inf = torr_inf.split(';')

                    # magnet_url = content[content.find('href="')+6:content.find('" class=')]
                    torrent_url = content[content.rfind('href="')+6:content.rfind('" class=')]
                    
                    anime_code2 = data_encode('{}|{}'.format(anime_code[0], cover))
                    
                    label = u'{} | [COLOR=blue]{}[/COLOR] : [COLOR=gold]{}[/COLOR] | Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                        title, quality, torr_inf[0], torr_inf[2], torr_inf[3])

                    self.create_line(title=label, anime_id=anime_code[0], cover=cover, params={'mode': 'torrent_part', 'id': anime_code2, 'param': torrent_url})

        if self.params['param']:
            anime_code = data_decode(self.params['id'])
            data_print(anime_code)
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