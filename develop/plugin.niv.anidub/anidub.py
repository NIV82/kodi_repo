# -*- coding: utf-8 -*-

import gc
import os
import sys
import urllib
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility
import info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.anidub')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        
    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon_data_dir = utility.fs_enc(xbmc.translatePath(Main.addon.getAddonInfo('profile')))
        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.params = {'mode': 'main_part', 'param': '', 'node': '', 'page': 1}

        args = utility.get_params()
        for a in args:
            self.params[a] = urllib.unquote_plus(args[a])

        if Main.addon.getSetting('unblock') == '1':
            try:
                proxy_time = float(Main.addon.getSetting('proxy_time'))
            except:
                proxy_time = 0
            
            if time.time() - proxy_time > 36000:
                Main.addon.setSetting('proxy_time', str(time.time()))
                proxy_pac = urllib.urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Main.addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}
            else:
                proxy_data = {'https': Main.addon.getSetting('proxy')}                
        else:
            proxy_data = None

        from network import WebTools
        self.network = WebTools(use_auth=True, auth_state=bool(Main.addon.getSetting('auth') == 'true'))
        del WebTools
        self.network.auth_post_data = {'login_name': Main.addon.getSetting('login'),
                                       'login_password': Main.addon.getSetting('password'),
                                       'login': 'submit'}        
        self.network.sid_file = utility.fs_enc(os.path.join(self.addon_data_dir, 'anidub.sid' ))
        self.network.download_dir = self.addon_data_dir

        if self.params['mode'] == 'main_part' and self.params['param'] == '':
            try: os.remove(self.network.sid_file)
            except: pass

        if not Main.addon.getSetting("login") or not Main.addon.getSetting("password"):
            self.params['mode'] = 'addon_setting'
            xbmc.executebuiltin('XBMC.Notification(Авторизация, Укажите логин и пароль)')            
            return

        if not self.network.auth_state:
            if not self.network.authorization():
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('XBMC.Notification(Ошибка, Проверьте логин и пароль)')
                return
            else:
                Main.addon.setSetting("auth", str(self.network.auth_state).lower())

        if not os.path.isfile(os.path.join(self.addon_data_dir, 'anidub.db')):
            try:
                data = urllib.urlopen('https://github.com/NIV82/kodi_repo/raw/master/release/plugin.niv.anidub/anidub.db')
                chunk_size = 8192
                bytes_read = 0
                file_size = int(data.info().getheaders("Content-Length")[0])
                self.progress.create('Загрузка Базы Данных')
                with open(os.path.join(self.addon_data_dir, 'anidub.db'), 'wb') as f:
                    while True:
                        chunk = data.read(chunk_size)
                        bytes_read = bytes_read + len(chunk)
                        f.write(chunk)
                        if len(chunk) < chunk_size:
                            break
                        p = bytes_read * 100 / file_size
                        if p > 100:
                            p = 100
                        self.progress.update(p, 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                    self.progress.close()
                xbmc.executebuiltin('XBMC.Notification(База Данных, [B]БД успешно загружена[/B])')
            except:
                xbmc.executebuiltin('XBMC.Notification(База Данных, Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
                pass

        from database import DBTools
        self.database = DBTools(utility.fs_dec(os.path.join(self.addon_data_dir, 'anidub.db')))
        del DBTools

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try:
            self.database.end()
        except:
            pass

    def exec_addon_setting(self):
        Main.addon.openSettings()

    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        if series:
            series = series.strip()
            series = ' - [ {} ]'.format(series)
        else:
            series = ''
       
        if Main.addon.getSetting('title_mode') == '0':
            label = '{}{}'.format(title[0], series)
        if Main.addon.getSetting('title_mode') == '1':
            label = '{}{}'.format(title[1], series)
        if Main.addon.getSetting('title_mode') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)

        return label

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
            info['title_ru'] = utility.rep_list(v[1]).capitalize()
            info['title_en'] = utility.rep_list(v[2]).capitalize()
        except:
            pass
        return info

    def create_image(self, anime_id):
        url = '{}'.format(self.database.get_cover(anime_id))

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                return utility.fs_dec(os.path.join(self.images_dir, local_img))
            else:
                self.network.download_dir = self.images_dir
                return self.network.get_file(target=url, dest_name=local_img)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)

            info = {'title': title, 'year': anime_info[9], 'genre': anime_info[0], 'director': anime_info[1], 'writer': anime_info[2],
                    'plot': anime_info[3], 'country': anime_info[7], 'studio': anime_info[8], 'year': anime_info[9]}

            info['plot'] = '{}\n\nОзвучивание: {}\nПеревод: {}\nРабота со звуком: {}'.format(info['plot'], anime_info[4], anime_info[5], anime_info[6])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)
                    
        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.anidub/?mode=clean_part")')])
        else:
            li.addContextMenuItems([('[B]Добавить FAV (anidub)[/B]', 'Container.Update("plugin://plugin.niv.anidub/?mode=favorites_part&node=plus&id={}")'.format(anime_id)), 
                                    ('[B]Удалить FAV (anidub)[/B]', 'Container.Update("plugin://plugin.niv.anidub/?mode=favorites_part&node=minus&id={}")'.format(anime_id))])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urllib.urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):

        html = self.network.get_html('https://tr.anidub.com/index.php?newsid={}'.format(anime_id))

        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'writer', 'plot', 'dubbing',
                      'translation', 'sound', 'country', 'studio', 'year', 'cover'], '')
        
        info['cover'] = html[html.find('"poster"><img src="')+19:html.find('" alt=""></span>')]

        title_data = html[html.find('<h1><span id="news-title">')+26:html.find('</span></h1>')]
        info.update(self.create_title_info(title_data))

        data_array = html[html.find('<div class="xfinfodata">')+24:html.find('<div class="story_b clr">')]
        data_array = utility.clean_list(data_array).split('<br>')

        for data in data_array:
            if 'Год: </b>' in data:
                for i in range(1950, 2030, 1):
                    if str(i) in data:
                        info['year'] = i
            if 'Жанр: </b>' in data:
                genre = utility.tag_list(data.replace('Жанр: </b>', ''))
                info['genre'] = utility.rep_list(genre).lower()
            if 'Страна: </b>' in data:
                info['country'] = utility.tag_list(data.replace('Страна: </b>', ''))
            if 'Дата выпуска: </b>' in data:
                if info['year'] == '':
                    for i in range(1975, 2030, 1):
                        if str(i) in data:
                            info['year'] = i
            if '<b itemprop="director"' in data:
                director = utility.tag_list(data.replace('Режиссер: </b>', ''))
                info['director'] = utility.rep_list(director)
            if '<b itemprop="author"' in data:
                writer = utility.tag_list(data.replace('Автор оригинала / Сценарист: </b>', ''))
                info['writer'] = utility.rep_list(writer)
            if 'Озвучивание: </b>' in data:
                dubbing = utility.tag_list(data.replace('Озвучивание: </b>', ''))
                info['dubbing'] = utility.rep_list(dubbing)
            if 'Перевод: </b>' in data:
                translation = utility.tag_list(data.replace('Перевод: </b>', ''))
                info['translation'] = utility.rep_list(translation)
            if 'Тайминг и работа со звуком: </b>' in data:
                sound = utility.tag_list(data.replace('Тайминг и работа со звуком: </b>', ''))
                info['sound'] = utility.rep_list(sound)
            if 'Студия:</b>' in data:
                studio = data[data.find('xfsearch/')+9:data.find('/">')]
                info['studio'] = utility.rep_list(studio)
            if 'Описание:</b>' in data:
                plot = utility.tag_list(data.replace('Описание:</b>', ''))
                info['plot'] = utility.rep_list(plot)
        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['genre'], info['director'], info['writer'], info['plot'],
                          info['dubbing'], info['translation'], info['sound'], info['country'], info['studio'], info['year'], info['cover'])
        except:
            xbmc.executebuiltin("XBMC.Notification(Ошибка парсера, ERROR: 101)")
            return 101
        return

    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, Успешно выполнено)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, [COLOR=yellow]ERROR: 102[/COLOR])")
            pass
        xbmc.executebuiltin('Container.Refresh')

    def exec_main_part(self):
        if not self.network.auth_state:
            self.create_line(title='[B][COLOR=red][ Ошибка Авторизации ][/COLOR][/B]', params={'mode': 'addon_setting'})
        else:
            self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
            self.create_line(title='[B][COLOR=blue][ Популярное за неделю ][/COLOR][/B]', params={'mode': 'common_part', 'node': 'popular'})
            self.create_line(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part'})      
            self.create_line(title='[B][COLOR=lime][ TV Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/anime_ongoing/'})
            self.create_line(title='[B][COLOR=lime][ TV 100+ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/shonen/'})
            self.create_line(title='[B][COLOR=lime][ TV Законченные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/full/'})
            self.create_line(title='[B][COLOR=lime][ Аниме OVA ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
            self.create_line(title='[B][COLOR=lime][ Аниме фильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
            self.create_line(title='[B][COLOR=lime][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
            self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if not Main.addon.getSetting('search'):
            Main.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title='[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title='[B][COLOR=red][ Поиск по алфавиту ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = Main.addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': urllib.quote(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = urllib.quote(skbd.getText())
                data_array = Main.addon.getSetting('search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), urllib.unquote(self.params['search_string']))
                Main.addon.setSetting('search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if self.params['param'] == 'genres':
            data = info.genres

        if self.params['param'] == 'years':
            data = reversed(info.years)
            data = tuple(data)

        if self.params['param'] == 'genres' or self.params['param'] == 'years':
            for i in data:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(urllib.quote_plus(i))})  

        if self.params['param'] == 'alphabet':
            data = info.alphabet
            for i in data:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(urllib.quote_plus(i))})  
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_favorites_part(self):
        url = 'https://tr.anidub.com/engine/ajax/favorites.php?fav_id={}&action={}&size=small&skin=Anidub'.format(self.params['id'], self.params['node'])
            
        try:
            self.network.get_html(target=url)
            xbmc.executebuiltin("XBMC.Notification(Избранное, Готово)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Избранное, ERROR: 103)")
            
        xbmc.executebuiltin('Container.Refresh')
    
    def exec_common_part(self):
        self.progress.create("AniDUB", "Инициализация")

        url = 'https://tr.anidub.com/{}page/{}/'.format(self.params['param'], self.params['page'])
        post = ''

        if self.params['param'] == 'search_part':
            url = 'https://tr.anidub.com/index.php?do=search'
            post = 'do=search&story={}&subaction=search&search_start={}&full_search=0'.format(urllib.quote_plus(self.params['search_string']), self.params['page'])
        

        html = self.network.get_html(url, post=post)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        if html.find('<h2>') > -1:            
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

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]tr.anidub.com[/COLOR]', data)
            return

    def exec_select_part(self):
        html = self.network.get_html('https://tr.anidub.com/index.php?newsid={}'.format(self.params['id']))
        html = html[html.find('<div class="torrent_c">')+23:html.rfind('Управление')]

        data_array = html.split('</ul-->')

        qa = []
        la = []

        for data in data_array:
            torrent_id = data[data.find('torrent_')+8:data.find('_info\'>')]

            if data.find('<div id="') > -1:
                quality = data[data.find('="')+2:data.find('"><')]
                qa.append(quality)

            if data.find('<div id=\'torrent_') > -1:
                quality = qa[len(qa) - 1]
                if data.find('Серии в торренте:') > -1:
                    series = data[data.find('Серии в торренте:')+31:data.find('Раздают')]
                    series = utility.tag_list(series)
                   
                    qid = '{} - [ {} ]'.format(quality, series)
                else:
                    qid = quality

                seed = data[data.find('li_distribute_m">')+17:data.find('</span> <')]
                peer = data[data.find('li_swing_m">')+12:data.find('</span> <span class="sep"></span> Размер:')]
                size = data[data.find('Размер: <span class="red">')+32:data.find('</span> <span class="sep"></span> Скачали')]

                label = '[COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(size, qid.upper(), seed, peer)
                la.append('{}|||{}'.format(label, torrent_id))

        for lb in reversed(la):
            lb = lb.split('|||')
            label = lb[0]
            torrent_id = lb[1]
            
            self.create_line(title=label, params={'mode': 'torrent_part', 'torrent_id': torrent_id, 'id': self.params['id']},  anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        self.network.download_dir = self.torrents_dir
        url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['torrent_id'])
        file_name = self.network.get_file(target=url, dest_name='{}.torrent'.format(self.params['torrent_id']))

        import bencode
        torrent_data = open(utility.fs_dec(file_name), 'rb').read()
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

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if Main.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Main.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(urllib.quote_plus(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(urllib.quote_plus(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '2':
            url = 'file:///{}'.format(url.replace('\\','/'))
            self.play_t2h(url, index, Main.addon.getSetting("DownloadDirectory"))

        xbmc.executebuiltin("Container.Refresh")

    def play_t2h(self, uri, file_id=0, DDir=""):
        try:            
            sys.path.append(os.path.join(xbmc.translatePath("special://home/"), "addons", "script.module.torrent2http", "lib"))
            from torrent2http import State, Engine, MediaType
            progressBar = xbmcgui.DialogProgress()
            from contextlib import closing
            if DDir == "": DDir = os.path.join(xbmc.translatePath("special://home/"), "userdata")
            progressBar.create('Torrent2Http', 'Запуск')
            ready = False
            pre_buffer_bytes = 15*1024*1024
            engine = Engine(uri, download_path=DDir)
            with closing(engine):
                engine.start(file_id)
                progressBar.update(0, 'Torrent2Http', 'Загрузка торрента', "")
                while not xbmc.abortRequested and not ready:
                    xbmc.sleep(500)
                    status = engine.status()
                    engine.check_torrent_error(status)
                    if file_id is None:
                        files = engine.list(media_types=[MediaType.VIDEO])
                        if files is None:
                            continue
                        if not files:
                            break
                            progressBar.close()
                        file_id = files[0].index
                        file_status = files[0]
                    else:
                        file_status = engine.file_status(file_id)
                        if not file_status:
                            continue
                    if status.state == State.DOWNLOADING:
                        if file_status.download >= pre_buffer_bytes:
                            ready = True
                            break
                        progressBar.update(100*file_status.download/pre_buffer_bytes, 'Torrent2Http', xbmc.translatePath('Предварительная буферизация: '+str(file_status.download/1024/1024)+" MB"), "")
                    elif status.state in [State.FINISHED, State.SEEDING]:
                        ready = True
                        break
                    if progressBar.iscanceled():
                        progressBar.update(0)
                        progressBar.close()
                        break
                progressBar.update(0)
                progressBar.close()
                if ready:
                    item = xbmcgui.ListItem(path=file_status.url)
                    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
                    if Main.addon.getSetting("MetodPlay") == 'true': xbmc.Player().play(file_status.url)
                    xbmc.sleep(3000)
                    while not xbmc.abortRequested and xbmc.Player().isPlaying(): xbmc.sleep(500)
        except:pass

if __name__ == "__main__":    
    anidub = Main()
    anidub.execute()
    del anidub

gc.collect()