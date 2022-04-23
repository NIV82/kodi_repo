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

from utility import clean_tags, clean_list, data_encode, data_decode

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

        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('anidub_auth_mode') == '1')
#========================#========================#========================#
        try: session = float(self.addon.getSetting('anidub_o_session'))
        except: session = 0

        if time.time() - session > 14400:
            self.addon.setSetting('anidub_o_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anidub_o.sid'))
            except: pass
            self.addon.setSetting('anidub_o_auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('anidub_o_auth') == 'true'), portal='anidub')
        self.auth_post_data = 'login_name={}&login_password={}&login=submit'.format(
            self.addon.getSetting('anidub_o_username'),
            self.addon.getSetting('anidub_o_password')
            )
        self.network.auth_post_data = self.auth_post_data
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anidub_o.sid')
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not self.addon.getSetting('anidub_o_username') or not self.addon.getSetting('anidub_o_password'):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ВВЕДИТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('Notification({},{},{},{})'.format('Авторизация', '[COLOR=gold]ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ[/COLOR]', 5000, self.icon))
                    return
                else:
                    self.addon.setSetting('anidub_o_auth', str(self.network.auth_status).lower())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_anidub_o.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_anidub_o.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = 'anidub_o_mirror_{}'.format(self.addon.getSetting('anidub_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('anidub_o_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_title_info(self, title):
        info = dict.fromkeys(['series', 'title_ru', 'title_en'], '')
        splitter = '/'

        title = clean_tags(title, '<', '>')

        if '[' in title:
            info['series'] = title[title.rfind('[')+1:title.rfind(']')].strip()
            title = title[:title.rfind('[')]
        
        if u'Сасами-сан на Лень.com' in title:
            title = u'Сасами-сан на Лень.com / Sasami-san@Ganbaranai'
        if u'Идолм@стер' in title:
            title = u'Идолм@стер / Idolm@ster'
            
        rep_list = [
                ('|', '/'),('\\', '/'),('Reward / EEA','Reward - EEA'),('Inuyasha: Kagami','/ Inuyasha: Kagami'),
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
            
        if 'anime_id:' in label:
            label = u'[COLOR=red]ERROR[/COLOR] | Ошибка 403-404 | [COLOR=gold]{}[/COLOR]'.format(
                title[0].replace('anime_id: ',''))
            
        return label
#========================#========================#========================#
    def create_image(self, url, anime_id):
        if not 'https://' in url:
            url = '{}{}'.format(self.site_url, url.replace('/','',1))
        
        if '0' in self.addon.getSetting('anidub_covers'):
            return url
        else:
            local_img = 'anidub_o_{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []        
        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anidub")'))
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('Обновить аниме', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anidub")'.format(anime_id)))

        if self.auth_mode:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anidub")'.format(anime_id)))
                context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anidub")'.format(anime_id)))

        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=anidub")'))
        # context_menu.append(('[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal={}")'.format(self.params['portal'])))
        # context_menu.append(('[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal={}")'.format(self.params['portal'])))
        
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, rating=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(cover, anime_id)
            
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

            info = {
                'genre':anime_info[7], 
                'country':anime_info[18],
                'year':anime_info[3],
                'episode':anime_info[2],
                'director':anime_info[9],
                'mpaa':anime_info[5],
                'plot':description,
                'title':title,
                'duration':anime_info[6],
                'studio':anime_info[19],
                'writer':anime_info[8],
                'tvshowtitle':title,
                'premiered':anime_info[3],
                'status':anime_info[1],
                'aired':anime_info[3],
                'rating':rating
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
    def create_aired(self, data):
        data = data[data.find('</span>'):]

        if u'по' in data:
            data = data[0:data.find(u'по')]

        data = clean_tags(data, '<', '>')

        rep_list = [
            (u'янв', '.01.'),(u'фев', '.02.'),(u'мар', '.03.'),(u'апр', '.04.'),
            (u'май', '.05.'),(u'июн', '.06.'),(u'июл', '.07.'),(u'авг', '.08.'),
            (u'сен', '.09.'),(u'окт', '.10.'),(u'ноя', '.11.'),(u'дек', '.12.')        
        ]

        for value in rep_list:
            data = data.replace(value[0], value[1])

        s = []
        for i in data:
            if i.isdigit() or i in ('.'):
                s.append(i)
        data = ''.join(s)

        data = data.replace('..','.')

        if len(data) > 0:
            if '.' in data[0]:
                data = data[1:]
            if '.' in data[len(data)-1]:
                data = data[:len(data)-1]
            if len(data) > 10:
                data = data[0:10]

        return data
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        html = self.network.get_html(target_name=url)

        if not html:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru='anime_id: {}'.format(anime_id),
                title_en='anime_id: {}'.format(anime_id)
                )
            return

        html = unescape(html)

        info = dict.fromkeys(['title_ru', 'title_en', 'aired_on', 'released_on', 'genres', 'director', 'writer', 'description', 'dubbing',
                        'translation', 'timing', 'country', 'studios', 'image', 'year'], '')

        image = html[html.find('fposter img-box img-fit">')+25:html.find(u'" title="Постер аниме {')]
        info['image'] = image[image.find('data-src="')+10:]

        title_data = html[html.find('<h1>')+4:html.find('</h1>')]
        info.update(self.create_title_info(title_data))

        description = html[html.find(u'Описание</div>')+14:html.find(u'Рейтинг:</div>')]
        info['description'] = clean_tags(description, '<', '>')

        data_array = html[html.find('<div class="fmeta fx-row fx-start">'):html.find('<div class="fright-title">')]
        data_array = data_array.splitlines()

        for data in data_array:
            if 'xfsearch/year/' in data:
                info['year'] = clean_tags(data, '<', '>')
            if u'Начало показа:</span>' in data:
                info['aired_on'] = self.create_aired(data)
            if 'xfsearch/country/' in data:
                info['country'] = clean_tags(data, '<', '>')
            if u'Жанр:</span>' in data:
                info['genres'] = clean_tags(data[data.find('</span>'):], '<', '>')
            if u'Автор оригинала:</span>' in data:
                info['writer'] = clean_tags(data[data.find('</span>'):], '<', '>')
            if u'Режиссер:</span>' in data:
                info['director'] = clean_tags(data[data.find('</span>'):], '<', '>')
            if u'Перевод:</span>' in data:
                info['translation'] = clean_tags(data[data.find('</span>'):], '<', '>')
            if u'Студия:</span>' in data:
                info['studios'] = clean_tags(data[data.find('</span>'):], '<', '>')
            if u'Озвучивание:</span>' in data:
                info['dubbing'] = clean_tags(data[data.find('</span>'):], '<', '>')
            if u'Тайминг:</span>' in data:
                info['timing'] = clean_tags(data[data.find('</span>'):], '<', '>')

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
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True)
        xbmc.executebuiltin('Container.Refresh')
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'ap_anidub_o.db'))
        except: pass

        db_file = os.path.join(self.database_dir, 'ap_anidub_o.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_anidub_o.db'
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

            url = '{}mylists/page/{}/'.format(self.site_url, self.params['page'])
            html = self.network.get_html(target_name=url)

            if not html:
                self.create_line(title='ERROR PAGE', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
                
            if not '<div class="animelist">' in html:
                self.create_line(title='Контент не обнаружен', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            navigation = html[html.find('<div class="navigation">'):html.find('<div class="animelist">')]
            navigation = clean_tags(navigation, '<', '>').replace(' ','|')
            page = int(navigation[navigation.rfind('|')+1:]) if navigation else -1
            
            data_array = html[html.find('<div class="animelist">')+23:html.rfind('<label for="mlist">')]
            data_array = clean_list(data_array).split('<div class="animelist">')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                url = data[data.find(self.site_url)+len(self.site_url):data.find('.html"')]
                anime_id = url[url.rfind('/')+1:url.find('-')]

                cover = self.database.get_cover(anime_id)
                
                title = data[data.find('class="upd-title">')+18:]
                series = title[title.find('[')+1:title.find(']')]

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)
                    
                label = self.create_title(anime_id, series)
                anime_code = data_encode('{}|{}'.format(anime_id, cover))

                self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part', 'id': anime_code})
            self.progress.close()

            if page and int(self.params['page']) < page:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

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
            self.addon.setSetting('anidub_search', '')
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

        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        if self.auth_mode:
            self.create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title='[B][COLOR=lime]Аниме[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/'})
        self.create_line(title='[B][COLOR=lime]Онгоинги[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/anime_ongoing/'})
        self.create_line(title='[B][COLOR=lime]Вышедшие сериалы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime/full/'})
        self.create_line(title='[B][COLOR=blue]Аниме фильмы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title='[B][COLOR=blue]Аниме OVA[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title='[B][COLOR=gold]Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})
            self.create_line(title='[B]Поиск по жанрам[/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B]Поиск по году[/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title='[B]Поиск по алфавиту[/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = self.addon.getSetting('anidub_search').split('|')
            data_array.reverse()

            for data in data_array:
                if not data:
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': quote(data)})

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

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)
                self.params['param'] = 'search_string'
            else:
                return False

        if 'search_string' in self.params['param']:
            if self.params['search_string'] == '':
                return False
            #self.progress.create('ANIDUB', 'Инициализация')
            
            url = '{}index.php?do=search'.format(self.site_url)
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(quote(self.params['search_string']), self.params['page'])
            
            html = self.network.get_html(target_name=url, post=post)
            
            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            if not '<div class="th-item">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            navigation = html[html.rfind('<div class="navigation">'):html.rfind('<footer class="footer sect-bg">')]
            navigation = clean_tags(navigation, '<', '>').replace(' ','|')
            page = int(navigation[navigation.rfind('|')+1:]) if navigation else False
        
            data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
            data_array = clean_list(data_array).split('<div class="th-item">')

            #i = 0
            
            for data in data_array:
                data = unescape(data)
                anime_url = data[data.find('th-in" href="')+13:data.find('.html">')]

                if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                    continue
                    
                anime_cover = data[data.find('data-src="')+10:data.find('" title="')]
                anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
                anime_title = data[data.find('<div class="fx-1">')+18:data.find('</div><span>')]
                anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')] if '[' in anime_title else ''
                anime_rating = data[data.find('th-rating">')+11:data.find('</div><div class="th-info')]
                
                #i = i + 1
                #p = int((float(i) / len(data_array)) * 100)
                
                #if self.progress.iscanceled():
                #    break
                #self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id, anime_series)            
                anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))
            
                self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})

            if page and int(self.params['page']) < page:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': 'search_part', 'param': 'search_string', 'search_string': self.params['search_string'], 'page': int(self.params['page']) + 1})
                
            #self.progress.close()
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('{}'.format(self.params['portal'].upper()), 'Инициализация')

        url = '{}{}page/{}/'.format(self.site_url, quote(self.params['param']), self.params['page'])
        html = self.network.get_html(url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not '<div class="th-item">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        navigation = html[html.rfind('<div class="navigation">'):html.rfind('<footer class="footer sect-bg">')]
        navigation = clean_tags(navigation, '<', '>').replace(' ','|')
        page = int(navigation[navigation.rfind('|')+1:]) if navigation else False

        data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
        data_array = clean_list(data_array).split('<div class="th-item">')

        i = 0

        for data in data_array:
            data = unescape(data)
            anime_url = data[data.find('th-in" href="')+13:data.find('.html">')]

            if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                continue
                
            anime_cover = data[data.find('data-src="')+10:data.find('" title="')]
            anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
            anime_title = data[data.find('<div class="fx-1">')+18:data.find('</div><span>')]
            anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')] if '[' in anime_title else ''
            anime_rating = data[data.find('th-rating">')+11:data.find('</div><div class="th-info')]
            
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)
            
            if self.progress.iscanceled():
                break
            self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id, anime_series)            
            anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))

            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})

        if page and int(self.params['page']) < page:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        anime_code = data_decode(self.params['id'])
        anime_tid = None
        
        url = '{}index.php?newsid={}'.format(self.site_url, anime_code[0])
        html = self.network.get_html(url)
            
        if u'Ссылка на трекер:</span>' in html:
            anime_tid = html[html.find(u'Ссылка на трекер:</span>'):html.find(u'<div>Скачать с трекера')]
            anime_tid = anime_tid[anime_tid.find('href=\'')+6:anime_tid.find('.html')+5]

        if anime_tid:
            torrent_html = self.network.get_html(target_name=anime_tid)
            
            if torrent_html:
                result = self.dialog.yesno(
                    'Обнаружена торрент ссылка:',
                    'Смотреть через [COLOR=blue]Торрент[/COLOR] или [COLOR=lime]Онлайн[/COLOR] ?\n======\nАвтовыбор - [COLOR=lime]Онлайн[/COLOR], 5 секунд',
                    yeslabel='Торрент', nolabel ='Онлайн', autoclose=5000)
                
                self.exec_torrent_part(torrent_html) if result else self.exec_online_part(html)
            else:
                self.exec_online_part(html)
        else:
            self.exec_online_part(html)
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self, torrent_data=None):
        anime_code = data_decode(self.params['id'])
        
        if torrent_data:
            html = torrent_data
            
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

        else:
            url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['param'])

            file_name = 'anidub_{}'.format(self.params['param'])
            full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))

            if '0' in self.addon.getSetting('anidub_local_torrent'):
                if os.path.isfile(full_name):
                    result = self.dialog.yesno(
                        'Обнаружен загруженный торрент файл',
                        'загрузить [COLOR=blue]Новый[/COLOR] или использовать [COLOR=lime]Загруженный[/COLOR] ?',
                        yeslabel='Новый', nolabel ='Загруженный', autoclose=3000)

                    if result:
                        torrent_file = self.network.get_file(target_name=url, destination_name=full_name)
                    else:
                        torrent_file = full_name
                else:
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
                    #self.create_line(title=series[i], anime_id=anime_code[0], cover=anime_code[1], params={'portal_mode': 'play_part', 'index': i, 'id': file_name}, folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'play_part', 'index': 0, 'id': file_name}, folder=False, size=info['length'])
                #self.create_line(title=info['name'], anime_id=anime_code[0], cover=anime_code[1], params={'portal_mode': 'play_part', 'index': 0, 'id': file_name}, folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self, online_data=None):
        anime_code = data_decode(self.params['id'])

        if online_data:
            html = online_data

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
            anime_code = data_decode(self.params['id'])
            
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

            self.create_line(title=label, params={}, cover=anime_code[1], anime_id=anime_code[0], online=play_url, folder=False)

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