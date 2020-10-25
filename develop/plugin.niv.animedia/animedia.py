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
    addon = xbmcaddon.Addon(id='plugin.niv.animedia')
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

        self.params = {'mode': 'main_part', 'param': '', 'page': 0}
       
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
        self.network = WebTools(proxy_data)
        del WebTools

        self.network.download_dir = self.addon_data_dir

        if not os.path.isfile(os.path.join(self.addon_data_dir, 'animedia.db')):
            try:
                data = urllib.urlopen('https://github.com/NIV82/kodi_repo/raw/master/release/plugin.niv.animedia/animedia.db')
                chunk_size = 8192
                bytes_read = 0
                file_size = int(data.info().getheaders("Content-Length")[0])
                self.progress.create('Загрузка Базы Данных')
                with open(os.path.join(self.addon_data_dir, 'animedia.db'), 'wb') as f:
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

        from database import AnimeDB
        self.DB = AnimeDB(utility.fs_dec(os.path.join(self.addon_data_dir, 'animedia.db')))
        del AnimeDB

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try:
            self.DB.end()
        except:
            pass

    def create_title(self, anime_id, series):
        title = self.DB.get_title(anime_id)

        if series:
            #series = series.replace('Серия','').replace('Серии','')
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

    def create_image(self, anime_id):        
        cover = self.DB.get_cover(anime_id)
        url = 'https://static.animedia.tv/uploads/{}'.format(cover[0])

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                return utility.fs_dec(os.path.join(self.images_dir, local_img))
            else:
                self.network.download_dir = self.images_dir
                return self.network.get_file(target=url, dest_name=local_img)

    def create_info(self, anime_id):
        url = 'https://tt.animedia.tv/anime/{}'.format(anime_id)

        html = self.network.get_html(url)

        if type(html) == int: return html

        info = dict.fromkeys(['title_ru', 'title_en', 'genre', 'year', 'studio', 'director', 'author', 'plot', 'cover'], '')

        info['cover'] = html[html.rfind('<a href="https://static.animedia.tv/uploads/')+44:html.rfind('" class="zoomLink">')]

        data_array = html[html.find('post__header">')+14:html.find('<!--Media post End-->')]

        info['plot'] = data_array[data_array.find('<p>'):data_array.rfind('</p>')]
        info['plot'] = utility.tag_list(info['plot'])
        info['plot'] = utility.clean_list(info['plot'])
        info['plot'] = utility.rep_list(info['plot'])
        
        data_array = data_array.splitlines()

        for data in data_array:
            if '<h1 class="media' in data:
                info['title_ru'] = data[data.find('title">')+7:data.find('</h1>')].strip()
            if 'Жанр:' in data:
                data = data.replace('Жанр: ','').replace('</a>', ', ')
                info['genre'] = utility.tag_list(data)[:-1]
            if 'Английское название:' in data:
                info['title_en'] = data[data.find('<span>')+6:data.find('</span>')].strip()
            if 'Дата выпуска:' in data:
                data = utility.tag_list(data)
                for i in range(1975, 2030, 1):
                    if str(i) in data:
                        info['year'] = i
            if 'Студия:' in data:
                info['studio'] = data[data.find('<span>')+6:data.find('</span>')]
                info['studio'] = utility.rep_list(info['studio'])
            if 'Режисер:' in data:
                info['director'] = data[data.find('<span>')+6:data.find('</span>')]
            if 'Автор оригинала:' in data:
                info['author'] = data[data.find('<span>')+6:data.find('</span>')]

        try:
            self.DB.add_anime(anime_id, info['title_ru'], info['title_en'], info['genre'], info['year'],
                          info['studio'], info['director'], info['author'], info['plot'], info['cover'])
        except:
            xbmc.executebuiltin("XBMC.Notification(Ошибка парсера, ERROR: 101, time=3000)")
            return 101
        return

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, ex_info=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.DB.get_anime(anime_id)
            info = {'title': title, 'genre': anime_info[0], 'year': anime_info[1], 'studio': anime_info[2], 'director': anime_info[3], 'writer': anime_info[4], 'plot': anime_info[5]}

            if ex_info:
                info['plot'] += '\n\nСерии: {}\nКачество: {}\nРазмер: {}\nКонтейнер: {}\nВидео: {}\nАудио: {}\nПеревод: {}\nТайминг: {}'.format(
                    ex_info['series'], ex_info['quality'], ex_info['size'], ex_info['container'], ex_info['video'], ex_info['audio'], ex_info['translate'], ex_info['timing'])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)
            
        if self.params['mode'] == 'search_part':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.animedia/?mode=clean_part")')])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urllib.urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, Успешно выполнено)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, [COLOR=yellow]ERROR: 102[/COLOR])")
            pass
        xbmc.executebuiltin('Container.Refresh')

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular'})
        self.create_line(title='[B][COLOR=yellow][ Новинки ][/COLOR][/B]', params={'mode': 'common_part'})      
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    
    def exec_search_part(self):
        if not Main.addon.getSetting('search'):
            Main.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

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

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_common_part(self, url=None):
        self.progress.create("Animedia", "Инициализация")

        url = 'https://tt.animedia.tv/P{}'.format(self.params['page'])

        if self.params['param'] == 'search_part':
            url = 'https://tt.animedia.tv/ajax/search_result/P0?limit=100&keywords={}&orderby_sort=entry_date|desc'.format(self.params['search_string'])

        if self.params['param'] == 'popular':
            url = 'https://tt.animedia.tv/ajax/search_result/P0?limit=100&orderby_sort=view_count_one|desc'

        if self.params['param'] == 'catalog':
            genre = '&category={}'.format(info.genre[Main.addon.getSetting('genre')]) if info.genre[Main.addon.getSetting('genre')] else ''
            voice = '&search:voiced={}'.format(Main.addon.getSetting('voice')) if Main.addon.getSetting('voice') else ''
            studio = '&search:studies={}'.format(Main.addon.getSetting('studio')) if Main.addon.getSetting('studio') else ''
            sort = '&orderby_sort={}'.format(info.sort[Main.addon.getSetting('sort')]) if info.sort[Main.addon.getSetting('sort')] else ''
            year = '&search:datetime={}'.format(info.year[Main.addon.getSetting('year')]) if info.year[Main.addon.getSetting('year')] else ''
            form = '&search:type={}'.format(info.form[Main.addon.getSetting('form')]) if info.form[Main.addon.getSetting('form')] else ''
            ongoing = '&search:ongoing={}'.format(info.status[Main.addon.getSetting('status')]) if info.status[Main.addon.getSetting('status')] else ''

            url = 'https://tt.animedia.tv/ajax/search_result/P0?limit=100{}{}{}{}{}{}{}'.format(genre, voice, studio, year, form, ongoing, sort)

        html = self.network.get_html(target=url)
        
        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        if html.find('<div class="ads-list__item">') > -1:
            data_array = html[html.find('<div class="ads-list__item">')+28:html.find('<!-- Pagination End-->')]            
            data_array = data_array.split('<div class="ads-list__item">')

            i = 0

            for data in data_array:
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                series = data[data.find('font">')+6:data.find('</div></div></div>')]
                anime_id = data[data.find('primary"><a href="')+47:data.find('" title=')]

                if '></div></div>' in anime_id: continue

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.DB.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=lime]ID: {} ][/COLOR][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(anime_id, series)
                self.create_line(title=label,anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
        
        self.progress.close()

        if html.find('">Вперёд</a></li>') > -1:
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 16)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        if Main.addon.getSetting('sort') == '':
            Main.addon.setSetting(id='sort', value='Дате добавления')

        if self.params['param'] == '':
            self.create_line(title='Форма выпуска: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('form')), params={'mode': 'catalog_part', 'param': 'form'})
            self.create_line(title='Жанр аниме: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Озвучивал: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('voice')), params={'mode': 'catalog_part', 'param': 'voice'})
            self.create_line(title='Студия: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('studio')), params={'mode': 'catalog_part', 'param': 'studio'})
            self.create_line(title='Год выпуска: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Статус раздачи: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='Сортировка по: [COLOR=yellow]{}[/COLOR]'.format(Main.addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='[COLOR=yellow][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        
        if self.params['param'] == 'form':
            result = self.dialog.select('Выберите Тип:', info.form.keys())
            Main.addon.setSetting(id='form', value=info.form.keys()[result])
        
        if self.params['param'] == 'genre':
            result = self.dialog.select('Выберите Жанр:', info.genre.keys())
            Main.addon.setSetting(id='genre', value=info.genre.keys()[result])

        if self.params['param'] == 'voice':
            result = self.dialog.select('Выберите Войсера:', info.voice)
            Main.addon.setSetting(id='voice', value=info.voice[result])

        if self.params['param'] == 'studio':
            result = self.dialog.select('Выберите Студию:', info.studio)
            Main.addon.setSetting(id='studio', value=info.studio[result])

        if self.params['param'] == 'year':
            result = self.dialog.select('Выберите Год:', info.year.keys())
            Main.addon.setSetting(id='year', value=info.year.keys()[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Выберите статус:', info.status.keys())
            Main.addon.setSetting(id='status', value=info.status.keys()[result])
        
        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', info.sort.keys())
            Main.addon.setSetting(id='sort', value=info.sort.keys()[result])

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

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]Animedia.tv[/COLOR]', data)
        return

    def exec_select_part(self):
        html = self.network.get_html('https://tt.animedia.tv/anime/{}'.format(self.params['id']))

        ex_info = dict.fromkeys(['series', 'quality', 'size', 'container', 'video', 'audio', 'translate', 'timing'], '')

        tab = []

        if html.find('<div class="media__tabs" id="down_load">') > -1:
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
                            ex_info['series'] = ''
                        else:
                            series = line[line.find('">')+2:line.find('</h3>')].replace('из XXX','')
                            series = series.replace('Серии','').replace('Серия','').strip()
                            ex_info['series'] = ' - [ {} ]'.format(series)

                        ex_info['quality'] = line[line.find('</h3>')+5:]
                        ex_info['quality'] = ex_info['quality'].replace('Качество','').strip()
                    if '>Размер:' in line:
                        ex_info['size'] = utility.tag_list(line[line.find('<span>'):])
                    if 'Контейнер:' in line:
                        ex_info['container'] = line[line.find('<span>')+6:line.find('</span>')]
                    if 'Видео:' in line:
                        ex_info['video'] = line[line.find('<span>')+6:line.find('</span>')]
                    if 'Аудио:' in line:                        
                        ex_info['audio'] = line[line.find('<span>')+6:line.find('</span>')].strip()
                    if 'Перевод:' in line:                        
                        ex_info['translate'] = line[line.find('<span>')+6:line.find('</span>')]
                    if 'Тайминг и сведение звука:' in line:
                        ex_info['timing'] = line[line.find('<span>')+6:line.find('</span>')]
                    
                label = '{}{} , [COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сиды: [COLOR=lime]{}[/COLOR] , Пиры: [COLOR=red]{}[/COLOR]'.format(
                    title, ex_info['series'], ex_info['size'], ex_info['quality'], seed, peer)                    
                
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'], ex_info=ex_info)
        else:
            tabs_content = html[html.find('<li class="tracker_info_pop_left">')+34:html.find('<!-- Media series tabs End-->')]
            tabs_content = tabs_content.split('<li class="tracker_info_pop_left">')

            for content in tabs_content:
                content = utility.clean_list(content)
                title = content[content.find('left_top">')+10:content.find('</span>')]
                title = title.replace('Серии ','').replace('Серия ','').strip()
                
                quality = content[content.find(')')+1:content.find('</span><p>')]
                quality = quality.replace('р', 'p').strip()

                torr_inf = content[content.find('left_op">')+9:content.rfind(';</span></span></p>')]
                torr_inf = utility.tag_list(torr_inf)
                torr_inf = torr_inf.replace('Размер: ','').replace('Сидов: ','').replace('Пиров: ','')
                torr_inf = torr_inf.split(';')

                # magnet_url = content[content.find('href="')+6:content.find('" class=')]
                torrent_url = content[content.rfind('href="')+6:content.rfind('" class=')]

                label = 'Серии: {} , [COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                    title, torr_inf[0], quality, torr_inf[2], torr_inf[3])

                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        self.network.download_dir = self.torrents_dir
        file_name = self.network.get_file(target=self.params['torrent_url'], dest_name='{}.torrent'.format(self.params['id']))

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
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': self.params['id']}, anime_id=self.params['id'], folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': self.params['id']}, anime_id=self.params['id'], folder=False, size=info['length'])
        
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

        xbmc.executebuiltin("Container.Refresh")

if __name__ == "__main__":    
    animedia = Main()
    animedia.execute()
    del animedia

gc.collect()