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

class Anidub:
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.params = params
        self.addon = addon
        self.icon = icon

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('anidub_auth_mode') == '1')
#================================================
        try: anidub_session = float(self.addon.getSetting('anidub_session'))
        except: anidub_session = 0

        if time.time() - anidub_session > 28800:
            self.addon.setSetting('anidub_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anidub.sid'))
            except: pass
            self.addon.setSetting('anidub_auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('anidub_auth') == 'true'),
            proxy_data=self.proxy_data, portal='anidub')
        self.auth_post_data = {
            'login_name': self.addon.getSetting('anidub_username'),
            'login_password': self.addon.getSetting('anidub_password'),
            'login': 'submit'}
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anidub.sid' )
        del WebTools
#================================================
        if self.auth_mode:
            if not self.addon.getSetting("anidub_username") or not self.addon.getSetting("anidub_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting("anidub_auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'anidub.db')):
            self.exec_update_part()
#================================================
        from database import Anidub_DB
        self.database = Anidub_DB(os.path.join(self.database_dir, 'anidub.db'))
        del Anidub_DB
#================================================
    def create_proxy_data(self):
        if self.addon.getSetting('anidub_unblock') == '0':
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
                
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#================================================
    def create_site_url(self):
        current_mirror = 'anidub_mirror_{}'.format(self.addon.getSetting('anidub_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('anidub_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#================================================
    def create_title_info(self, title):
        info = dict.fromkeys(['series', 'title_ru', 'title_en'], '')

        title = tag_list(title).replace('...','')
        title = title.replace('/ ', ' / ').replace('  ', ' ')
        title = title.replace('|', '/')
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

    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        if series:
            series = series.strip()
            series = u' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
       
        if '0' in self.addon.getSetting('anidub_titles'):
            label = u'{}{}'.format(title[0], series)
        if '1' in self.addon.getSetting('anidub_titles'):
            label = u'{}{}'.format(title[1], series)
        if '2' in self.addon.getSetting('anidub_titles'):
            label = u'{} / {}{}'.format(title[0], title[1], series)

        return label

    def create_image(self, anime_id):
        url = '{}'.format(self.database.get_cover(anime_id))

        if self.addon.getSetting('anidub_covers') == '0':
            return url
        else:
            #local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)

    def create_context(self, anime_id):
        context_menu = []
        context_menu.append((u'[B][COLOR=darkorange]Обновить Базу Данных[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anidub")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append((u'[B][COLOR=red]Очистить историю[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")'))

        if self.auth_mode:
            if 'common_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
                context_menu.append((u'[B][COLOR=white]Добавить FAV (сайт)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anidub")'.format(anime_id)))
                context_menu.append((u'[B][COLOR=white]Удалить FAV (сайт)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anidub")'.format(anime_id)))
        
        context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append((u'[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anidub")'))
        context_menu.append((u'[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=anidub")'))
        context_menu.append((u'[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=anidub")'))
        context_menu.append((u'[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        return context_menu

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True):        
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)

            info = {'title': title, 'year': anime_info[9], 'genre': anime_info[0], 'director': anime_info[1], 'writer': anime_info[2],
                    'plot': anime_info[3], 'country': anime_info[7], 'studio': anime_info[8], 'year': anime_info[9]}

            info['plot'] = u'{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(info['plot'], anime_info[4])
            info['plot'] = u'{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(info['plot'], anime_info[5])
            info['plot'] = u'{}\n[COLOR=steelblue]Работа со звуком[/COLOR]: {}'.format(info['plot'], anime_info[6])

            if size: info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = 'anidub'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):
        html = self.network.get_html2('https://tr.anidub.com/index.php?newsid={}'.format(anime_id))
        html = unescape(html)

        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'writer', 'plot', 'dubbing',
                      'translation', 'sound', 'country', 'studio', 'year', 'cover'], '')
        
        info['cover'] = html[html.find('"poster"><img src="')+19:html.find('" alt=""></span>')]

        title_data = html[html.find('<h1><span id="news-title">')+26:html.find('</span></h1>')]
        info.update(self.create_title_info(title_data))

        data_array = html[html.find('<div class="xfinfodata">')+24:html.find('<div class="story_b clr">')]
        data_array = clean_list(data_array).split('<br>')

        for data in data_array:
            if u'Год: </b>' in data:
                for year in range(1950, 2030, 1):
                    if str(year) in data:
                        info['year'] = year
            if u'Жанр: </b>' in data:
                info['genre'] = tag_list(data.replace(u'Жанр: </b>', '')).lower()
            if u'Страна: </b>' in data:
                info['country'] = tag_list(data.replace(u'Страна: </b>', ''))
            if u'Дата выпуска: </b>' in data:
                if info['year'] == '':
                    for year in range(1975, 2030, 1):
                        if str(year) in data:
                            info['year'] = year
            if u'<b itemprop="director"' in data:
                info['director'] = tag_list(data.replace(u'Режиссер: </b>', ''))
            if u'<b itemprop="author"' in data:
                info['writer'] = tag_list(data.replace(u'Автор оригинала / Сценарист: </b>', ''))
            if u'Озвучивание: </b>' in data:
                info['dubbing'] = tag_list(data.replace(u'Озвучивание: </b>', ''))
            if u'Перевод: </b>' in data:
                info['translation'] = tag_list(data.replace(u'Перевод: </b>', ''))
            if u'Тайминг и работа со звуком: </b>' in data:
                info['sound'] = tag_list(data.replace(u'Тайминг и работа со звуком: </b>', ''))
            if u'Студия:</b>' in data:
                info['studio'] = data[data.find('xfsearch/')+9:data.find('/">')]
            if u'Описание:</b>' in data:
                info['plot'] = tag_list(data.replace(u'Описание:</b>', ''))
        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['genre'], info['director'], info['writer'], info['plot'],
                          info['dubbing'], info['translation'], info['sound'], info['country'], info['studio'], info['year'], info['cover'])
        except: return 101
        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        self.addon.openSettings()

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, '{}.db'.format(self.params['portal'])))
        except: pass

        db_file = os.path.join(self.database_dir, '{}.db'.format(self.params['portal']))
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/{}.db'.format(self.params['portal'])
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
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
            pass

    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&size=small&skin=Anidub'.format(self.site_url, self.params['id'], self.params['node'])        
        label = self.database.get_title(self.params['id'])[0]

        if 'plus' in self.params['node']:
            try:
                self.network.get_html2(target_name=url)
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]Успешно добавлено[/COLOR]', 5000, self.icon))
            except:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=yellow]Ошибка - 103[/COLOR]', 5000, self.icon))

        if 'minus' in self.params['node']:
            try:
                self.network.get_html2(target_name=url)
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]Успешно удалено[/COLOR]', 5000, self.icon))
            except:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=yellow]Ошибка - 103[/COLOR]', 5000, self.icon))
        
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=lime]успешно выполнено[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=yellow]ERROR: 102[/COLOR]', 5000, self.icon))
            pass

    def exec_information_part(self):
        from info import animeportal_data
        txt = animeportal_data
            
        start = '[{}]'.format(self.params['param'])
        end = '[/{}]'.format(self.params['param'])
        data = txt[txt.find(start)+6:txt.find(end)].strip()

        self.dialog.textviewer('Информация', data)
        return

    def exec_main_part(self):
        self.create_line(title=u'[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        if self.auth_mode:
            self.create_line(title=u'[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})        
        self.create_line(title=u'[B][COLOR=lime][ Популярное за неделю ][/COLOR][/B]', params={'mode': 'common_part', 'node': 'popular'})
        self.create_line(title=u'[B][COLOR=lime][ Новое ][/COLOR][/B]', params={'mode': 'common_part'})      
        self.create_line(title=u'[B][COLOR=lime][ TV Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/anime_ongoing/'})
        self.create_line(title=u'[B][COLOR=lime][ TV 100+ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/shonen/'})
        self.create_line(title=u'[B][COLOR=lime][ TV Законченные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/full/'})
        self.create_line(title=u'[B][COLOR=lime][ Аниме OVA ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title=u'[B][COLOR=lime][ Аниме фильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title=u'[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по алфавиту ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = self.addon.getSetting('anidub_search').split('|')
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
                data_array = self.addon.getSetting('anidub_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('anidub_search', data_array)
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
   
    def exec_common_part(self):
        self.progress.create("AniDUB", "Инициализация")

        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        post = ''

        if self.params['param'] == 'search_part':
            url = '{}index.php?do=search'.format(self.site_url)
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(quote(self.params['search_string']), self.params['page'])
        
        html = self.network.get_html2(url, post=post)

        # if type(html) == int:
        #     self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
        #     return

        if '<h2>' in html:         
            if self.params['node'] == 'popular':
                data_array = html[html.find('hover</a>')+9:html.rfind('<!-- END OF OV')]
                data_array = data_array.split('hover</a>')
            else:
                data_array = html[html.find('<h2>')+4:html.rfind('</h2>')+5]
                data_array = data_array.split('<h2>')

            i = 0

            for data in data_array:
                data = unescape(data)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                ai = data[data.find('<a href="')+9:data.find('</a>')]

                if '/manga/' in ai or '/ost/' in ai or '/podcast/' in ai or '/anons_ongoing/' in ai or '/games/' in ai or '11310' in ai:
                    continue

                url = ai[:ai.find('.html')]
                title = ai[ai.find('>')+1:]
                anime_id = url[url.rfind('/')+1:url.find('-')]

                # if '11310' in anime_id:
                #     continue

                info = self.create_title_info(title)

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(anime_id, info['series'])

                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
        
        if '<span class="n_next rcol"><a ' in html and not self.params['node'] == 'popular':
            if self.params['param'] == 'search_part':
                self.create_line(title='[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
                                 'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
            else:
                self.create_line(title='[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
                               'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        
        self.progress.close()        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_select_part(self):
        html = self.network.get_html2('{}index.php?newsid={}'.format(self.site_url, self.params['id']))
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
            
            self.create_line(title=label, params={'mode': 'torrent_part', 'torrent_id': torrent_id, 'id': self.params['id']},  anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        url = '{}engine/download.php?id={}'.format(self.site_url, self.params['torrent_id'])
        
        file_name = '{}_{}'.format(self.params['portal'], self.params['torrent_id'])
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
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])

        if self.addon.getSetting(portal_engine) == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if self.addon.getSetting(portal_engine) == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
