# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
#import xbmcvfs

from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
from urllib.request import urlopen
from html import unescape

import info
import utility

class Anidub:
    addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
        
    def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.images_dir = images_dir
        self.torrents_dir = torrents_dir
        self.database_dir = database_dir
        self.cookie_dir = cookie_dir
        self.params = params

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.auth_mode = bool(Anidub.addon.getSetting('anidub_auth_mode') == '1')
#================================================
        try: anidub_session = float(Anidub.addon.getSetting('anidub_session'))
        except: anidub_session = 0

        if time.time() - anidub_session > 28800:
            Anidub.addon.setSetting('anidub_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anidub.sid'))
            except: pass
            Anidub.addon.setSetting('anidub_auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(Anidub.addon.getSetting('anidub_auth') == 'true'),
            proxy_data=self.proxy_data, portal='anidub')
        self.auth_post_data = {
            'login_name': Anidub.addon.getSetting('anidub_username'),
            'login_password': Anidub.addon.getSetting('anidub_password'),
            'login': 'submit'}
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anidub.sid' )
        del WebTools
#================================================
        if self.auth_mode:
            if not Anidub.addon.getSetting("anidub_username") or not Anidub.addon.getSetting("anidub_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    Anidub.addon.setSetting("anidub_auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'anidub.db')):
            self.exec_update_part()
#================================================
        from database import Anidub_DB
        self.database = Anidub_DB(os.path.join(self.database_dir, 'anidub.db'))
        del Anidub_DB
#================================================
    def create_proxy_data(self):
        if Anidub.addon.getSetting('anidub_unblock') == '0':
            return None

        try: proxy_time = float(Anidub.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            Anidub.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
                
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            Anidub.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if Anidub.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': Anidub.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Anidub.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#================================================
    def create_site_url(self):
        site_url = Anidub.addon.getSetting('anidub_mirror_0')
        #current_mirror = 'anidub_mirror_{}'.format(Anidub.addon.getSetting('anidub_mirror_mode'))

        # if not Anidub.addon.getSetting(current_mirror):
        #     pass
        # else:
        #     site_url = Anidub.addon.getSetting(current_mirror)
            
        return site_url
#================================================
    def create_title_info(self, title):
        info = dict.fromkeys(['series', 'title_ru', 'title_en'], '')

        title = utility.tag_list(title).replace('...','')
        title = title.replace('/ ', ' / ').replace('  ', ' ')
        title = title.replace(' ', ' ').replace('|', '/')
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
            info['title_ru'] = unescape(v[1]).capitalize()
            info['title_en'] = unescape(v[2]).capitalize()
        except:
            pass
        return info

    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        if series:
            series = series.strip()
            series = ' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
       
        if Anidub.addon.getSetting('anidub_titles') == '0':
            label = '{}{}'.format(title[0], series)
        if Anidub.addon.getSetting('anidub_titles') == '1':
            label = '{}{}'.format(title[1], series)
        if Anidub.addon.getSetting('anidub_titles') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)

        return label

    def create_image(self, anime_id):
        url = '{}'.format(self.database.get_cover(anime_id))

        if Anidub.addon.getSetting('anidub_covers') == '0':
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

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True):        
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)

            info = {'title': title, 'year': anime_info[9], 'genre': anime_info[0], 'director': anime_info[1], 'writer': anime_info[2],
                    'plot': anime_info[3], 'country': anime_info[7], 'studio': anime_info[8], 'year': anime_info[9]}

            info['plot'] = '{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(info['plot'], anime_info[4])
            info['plot'] = '{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(info['plot'], anime_info[5])
            info['plot'] = '{}\n[COLOR=steelblue]Работа со звуком[/COLOR]: {}'.format(info['plot'], anime_info[6])

            if size: info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")')])

        if self.params['mode'] == 'common_part' or self.params['param'] == 'search_part':
            li.addContextMenuItems([('[B]Добавить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anidub")'.format(anime_id)), 
                                    ('[B]Удалить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anidub")'.format(anime_id))])
        
        if self.params['mode'] == 'information_part':
            li.addContextMenuItems([('[B]Обновить Базу Данных[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anidub")')])

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = 'anidub'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):
        html = self.network.get_html('{}index.php?newsid={}'.format(self.site_url,anime_id))

        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'writer', 'plot', 'dubbing',
                      'translation', 'sound', 'country', 'studio', 'year', 'cover'], '')
        
        info['cover'] = html[html.find('"poster"><img src="')+19:html.find('" alt=""></span>')]

        title_data = html[html.find('<h1><span id="news-title">')+26:html.find('</span></h1>')]
        info.update(self.create_title_info(title_data))

        data_array = html[html.find('<div class="xfinfodata">')+24:html.find('<div class="story_b clr">')]
        data_array = utility.clean_list(data_array).split('<br>')

        for data in data_array:
            if 'Год: </b>' in data:
                for year in range(1950, 2030, 1):
                    if str(year) in data:
                        info['year'] = year
            if 'Жанр: </b>' in data:
                genre = utility.tag_list(data.replace('Жанр: </b>', ''))
                info['genre'] = unescape(genre).lower()
            if 'Страна: </b>' in data:
                info['country'] = utility.tag_list(data.replace('Страна: </b>', ''))
            if 'Дата выпуска: </b>' in data:
                if info['year'] == '':
                    for year in range(1975, 2030, 1):
                        if str(year) in data:
                            info['year'] = year
            if '<b itemprop="director"' in data:
                director = utility.tag_list(data.replace('Режиссер: </b>', ''))
                info['director'] = unescape(director)
            if '<b itemprop="author"' in data:
                writer = utility.tag_list(data.replace('Автор оригинала / Сценарист: </b>', ''))
                info['writer'] = unescape(writer)
            if 'Озвучивание: </b>' in data:
                dubbing = utility.tag_list(data.replace('Озвучивание: </b>', ''))
                info['dubbing'] = unescape(dubbing)
            if 'Перевод: </b>' in data:
                translation = utility.tag_list(data.replace('Перевод: </b>', ''))
                info['translation'] = unescape(translation)
            if 'Тайминг и работа со звуком: </b>' in data:
                sound = utility.tag_list(data.replace('Тайминг и работа со звуком: </b>', ''))
                info['sound'] = unescape(sound)
            if 'Студия:</b>' in data:
                studio = data[data.find('xfsearch/')+9:data.find('/">')]
                info['studio'] = unescape(studio)
            if 'Описание:</b>' in data:
                plot = utility.tag_list(data.replace('Описание:</b>', ''))
                info['plot'] = unescape(plot)
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
        Anidub.addon.openSettings()

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'anidub.db'))
        except: pass        

        db_file = os.path.join(self.database_dir, 'anidub.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anidub.db'
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
            self.dialog.ok('AniDUB - База Данных','БД успешно загружена')
        except:
            self.dialog.ok('AniDUB - База Данных','Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
            pass

    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&size=small&skin=Anidub'.format(self.site_url, self.params['id'], self.params['node'])        
        label = self.database.get_title(self.params['id'])[0]
        #self.create_title(self.params['id'], None)

        if 'plus' in self.params['node']:
            try:
                self.network.get_html(target_name=url)
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно добавлено[/COLOR]'.format(label))
            except:
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - 103[/COLOR]'.format(label))

        if 'minus' in self.params['node']:
            try:
                self.network.get_html(target_name=url)
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно удалено[/COLOR]'.format(label))
            except:
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - 103[/COLOR]'.format(label))
        
    def exec_clean_part(self):
        try:
            Anidub.addon.setSetting('anidub_search', '')
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]Успешно выполнено[/COLOR]')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})        
        self.create_line(title='[B][COLOR=lime][ Популярное за неделю ][/COLOR][/B]', params={'mode': 'common_part', 'node': 'popular'})
        self.create_line(title='[B][COLOR=lime][ Новое ][/COLOR][/B]', params={'mode': 'common_part'})      
        self.create_line(title='[B][COLOR=lime][ TV Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/anime_ongoing/'})
        self.create_line(title='[B][COLOR=lime][ TV 100+ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/shonen/'})
        self.create_line(title='[B][COLOR=lime][ TV Законченные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/full/'})
        self.create_line(title='[B][COLOR=lime][ Аниме OVA ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title='[B][COLOR=lime][ Аниме фильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title='[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})            
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.anidub_data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]tr.anidub.com[/COLOR]', data)
            return
    
    def exec_search_part(self):
        if not Anidub.addon.getSetting('anidub_search'):
            Anidub.addon.setSetting('anidub_search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title='[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title='[B][COLOR=red][ Поиск по алфавиту ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = Anidub.addon.getSetting('anidub_search').split('|')
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
                data_array = Anidub.addon.getSetting('anidub_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                Anidub.addon.setSetting('anidub_search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if self.params['param'] == 'genres':
            data = info.anidub_genres

        if self.params['param'] == 'years':
            data = reversed(info.anidub_years)
            data = tuple(data)

        if self.params['param'] == 'genres' or self.params['param'] == 'years':
            for i in data:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})  

        if self.params['param'] == 'alphabet':
            data = info.anidub_alphabet
            for i in data:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(quote(i))})  
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
   
    def exec_common_part(self):
        self.progress.create("AniDUB", "Инициализация")

        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        post = ''

        if self.params['param'] == 'search_part':
            url = '{}index.php?do=search'.format(self.site_url)
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(quote(self.params['search_string']), self.params['page'])
        
        html = self.network.get_html(url, post=post)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        if '<h2>' in html:         
            if self.params['node'] == 'popular':
                data_array = html[html.find('hover</a>')+9:html.rfind('<!-- END OF OV')]
                data_array = data_array.split('hover</a>')
            else:
                data_array = html[html.find('<h2>')+4:html.rfind('</h2>')+5]
                data_array = data_array.split('<h2>')

            i = 0

            for data in data_array:
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                ai = data[data.find('<a href="')+9:data.find('</a>')]

                if '/manga/' in ai or '/ost/' in ai or '/podcast/' in ai or '/anons_ongoing/' in ai or '/games/' in ai:
                    continue

                url = ai[:ai.find('.html')]
                title = ai[ai.find('>')+1:]
                anime_id = url[url.rfind('/')+1:url.find('-')]

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
        html = self.network.get_html('{}index.php?newsid={}'.format(self.site_url, self.params['id']))
        html = html[html.find('<div class="torrent_c">')+23:html.rfind('Управление')]

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
                if 'Серии в торренте:' in data:
                    series = data[data.find('Серии в торренте:')+17:data.find('Раздают')]
                    series = utility.tag_list(series)
                   
                    qid = '{} - [ {} ]'.format(quality, series)
                else:
                    qid = quality

                seed = data[data.find('li_distribute_m">')+17:data.find('</span> <')]
                peer = data[data.find('li_swing_m">')+12:data.find('</span> <span class="sep"></span> Размер:')]
                size = data[data.find('Размер: <span class="red">'):data.find('</span> <span class="sep"></span> Скачали')]
                size = size.replace('Размер: <span class="red">', '')

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
        file_name = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['torrent_id']))
        torrent_file = self.network.get_file(target_name=url, destination_name=file_name)

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
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': self.params['torrent_id']}, anime_id=self.params['id'], folder=False,  size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': self.params['torrent_id']}, anime_id=self.params['id'], folder=False, size=info['length'])
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))