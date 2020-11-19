# -*- coding: utf-8 -*-

import gc
import os
import sys
import urllib
import time

import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmcaddon

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility
import info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.anilibria')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon_data_dir = utility.fs_enc(xbmc.translatePath(Main.addon.getAddonInfo('profile')))
        if not xbmcvfs.exists(self.addon_data_dir):
            xbmcvfs.mkdir(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not xbmcvfs.exists(self.images_dir):
            xbmcvfs.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not xbmcvfs.exists(self.torrents_dir):
            xbmcvfs.mkdir(self.torrents_dir)
        
        self.cookies_dir = os.path.join(self.addon_data_dir, 'cookies')
        if not xbmcvfs.exists(self.cookies_dir):
            xbmcvfs.mkdir(self.cookies_dir)

        self.database_dir = os.path.join(self.addon_data_dir, 'database')
        if not xbmcvfs.exists(self.database_dir):
            xbmcvfs.mkdir(self.database_dir)
        
        self.sid_file = utility.fs_enc(os.path.join(self.cookies_dir, 'anilibria.sid' ))

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'sort':''}

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
#================================================
        try:
            session_time = float(Main.addon.getSetting('session_time'))
        except:
            session_time = 0

        if time.time() - session_time > 259200:
            Main.addon.setSetting('session_time', str(time.time()))
            xbmcvfs.delete(self.sid_file)
            Main.addon.setSetting('auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(auth_usage=bool(Main.addon.getSetting('auth_mode') == 'true'),
                                auth_status=bool(Main.addon.getSetting('auth') == 'true'),
                                proxy_data=proxy_data)
        self.network.auth_post_data = {'mail': Main.addon.getSetting('login'),
            'passwd': Main.addon.getSetting('password'), 'fa2code': '', 'csrf': '1'}
        self.network.sid_file = self.sid_file
        del WebTools

        if Main.addon.getSetting('auth_mode') == 'true':
            if not Main.addon.getSetting("login") or not Main.addon.getSetting("password"):
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('XBMC.Notification(Авторизация, Укажите логин и пароль)')            
                return

            if not self.network.auth_status:
                if not self.network.authorization():
                    self.params['mode'] = 'addon_setting'
                    xbmc.executebuiltin('XBMC.Notification(Ошибка, Проверьте логин и пароль)')
                    return
                else:
                    Main.addon.setSetting("auth", str(self.network.auth_status).lower())

        if not os.path.isfile(os.path.join(self.database_dir, 'anilibria.db')):
            db_file = os.path.join(self.database_dir, 'anilibria.db')
            db_url = 'https://github.com/NIV82/kodi_repo/raw/main/release/plugin.niv.anilibria/anilibria.db'
            try:                
                data = urllib.urlopen(db_url)
                chunk_size = 8192
                bytes_read = 0
                file_size = int(data.info().getheaders("Content-Length")[0])
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
                xbmc.executebuiltin('XBMC.Notification(База Данных, [B]БД успешно загружена[/B])')
                Main.addon.setSetting('database', 'true')
            except:
                xbmc.executebuiltin('XBMC.Notification(База Данных, Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
                Main.addon.setSetting('database', 'false')
                pass

        from database import DBTools
        if Main.addon.getSetting('database') == 'false':
            xbmcvfs.delete(os.path.join(self.database_dir, 'anilibria.db'))
            Main.addon.setSetting('database', 'true')
        self.database = DBTools(os.path.join(self.database_dir, 'anilibria.db'))
        del DBTools

    def create_title(self, title, series):
        if series:            
            series = series.decode( 'unicode-escape' ).encode( 'utf-8' )
            series = series.replace('\/','/')
            series = series.replace('Серия:','').strip()
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

    def create_info(self, anime_url):
        html = self.network.get_html('https://dark-libria.it/release/{}'.format(anime_url))
        
        if type(html) == int:
            return html
                
        info = dict.fromkeys(['anime_id', 'title_ru', 'title_en', 'year', 'dubbing', 'genre', 'plot'], '')

        data_array = html[html.find('<ul class="list-unstyled">'):html.find('<div class="col">')]
        data_array = utility.clean_list(data_array)
        data_array = data_array.replace('</span> </li>', '</span></li>').split('</span></li>')

        for data in data_array:
            data = utility.tag_list(data)

            if 'ID:' in data:
                info['anime_id'] = data[3:].lstrip()                
            if 'Название:' in data:
                info['title_ru'] = utility.rep_list(data[17:]).lstrip()
            if 'Оригинальное название:' in data:
                info['title_en'] = utility.rep_list(data[42:]).lstrip()
            if 'Сезон:' in data:
                info['year'] = data[-4:]
            if 'Озвучка:' in data:
                info['dubbing'] = utility.rep_list(data[15:]).lstrip()
            if 'Жанры:' in data:
                info['genre'] = data[11:].strip()
            if 'Описание:' in data:
                info['plot'] = utility.rep_list(data[17:]).lstrip()
        
        try:
            self.database.add_anime(info['anime_id'], info['title_ru'], info['title_en'], info['year'], info['dubbing'], info['genre'], info['plot'], anime_url)
        except:
            xbmc.executebuiltin("XBMC.Notification(Ошибка парсера, ERROR: 101, time=3000)")
            return 101
        return

    def create_image(self, anime_url):        
        cover = self.database.get_cover(anime_url)
        url = 'https://static.anilibria.tv/upload/release/350x500/{}.jpg'.format(cover)

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(cover, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                return utility.fs_dec(os.path.join(self.images_dir, local_img))
            else:
                file_name = utility.fs_dec(os.path.join(self.images_dir, local_img))
                return self.network.get_file(target_name=url, destination_name=file_name)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)

            info = {'title': title, 'year': anime_info[0], 'genre': anime_info[2], 'plot': anime_info[3]}

            if anime_info[1]:
                info['plot'] = '{}\n\nОзвучка: {}'.format(info['plot'], anime_info[1])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=clean_part")')])

        if Main.addon.getSetting('auth_mode') == 'true':
            if self.params['mode'] == 'common_part' or self.params['mode'] == 'search_part':
                li.addContextMenuItems([('[B]Добавить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}")'.format(anime_id)), ('[B]Удалить FAV (сайт)[/B]', 
                                         'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}")'.format(anime_id))])
        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urllib.urlencode(params))

        if Main.addon.getSetting('online_mode') == 'true':
            if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try:
            self.database.end()
        except:
            pass

    def exec_addon_setting(self):
        Main.addon.openSettings()

    def exec_favorites_part(self):
        url = 'https://www.anilibria.tv/release/{}.html'.format(self.params['id'])

        html = self.network.get_html(target_name=url)

        csrf_token = html[html.find('value=\'{')+7:html.find('}\'>')+1]
        rid = html[html.find('350x500/')+8:html.find('.jpg')]

        fav_url = 'https://www.anilibria.tv/public/favorites.php'
        post = 'rid={}&csrf_token={}'.format(rid, csrf_token)

        try:
            self.network.get_html(target_name=fav_url,post=post)
            xbmc.executebuiltin("XBMC.Notification(Избранное, Готово, time=3000)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Избранное, ERROR: 103, time=3000)")
            
        xbmc.executebuiltin('Container.Refresh')
    
    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, Успешно выполнено)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, [COLOR=yellow]ERROR: 102[/COLOR])")
            pass
        xbmc.executebuiltin('Container.Refresh')

    def exec_main_part(self):
        if Main.addon.getSetting('auth_mode') == 'true':
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites'})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part', 'sort': '1'})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'sort': '2'})
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
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

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]anilibria.tv[/COLOR]', data)
        return

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

    def exec_common_part(self):
        self.progress.create("Anilibria", "Инициализация")

        url = 'https://www.anilibria.tv/public/catalog.php'
        post = 'page={}&xpage=catalog&sort={}&finish=1'.format(self.params['page'], self.params['sort'])

        if self.params['param'] == 'catalog':
            search = '&search=%7B%22year%22%3A%22{}%22%2C%22genre%22%3A%22{}%22%2C%22season%22%3A%22{}%22%7D'.format(
                Main.addon.getSetting('year'), Main.addon.getSetting('genre'), Main.addon.getSetting('season'))
            post = 'page={}{}&xpage=catalog&sort={}&finish={}'.format(
                self.params['page'], search, info.sort[Main.addon.getSetting('sort')], info.status[Main.addon.getSetting('status')])
        
        if self.params['param'] == 'favorites':
            post = 'page={}&xpage=favorites&sort=2&finish=1'.format(self.params['page'])
        
        if self.params['param'] == 'search_part':
            url = 'https://www.anilibria.tv/public/search.php'
            post = 'search={}&small=1'.format(self.params['search_string'])

        html = self.network.get_html(target_name=url, post=post)     
        
        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return   

        data_array = html.split('<td>')
        data_array.pop(0)

        if len(data_array) > 0:
            i = 0

            for data in data_array:
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                anime_url = data[data.find('release\/')+9:data.find('.html')]
                series = data[data.find('anime_number\\">')+15:data.find('<\/span><span class=\\"anime_desc')]
                if self.params['param'] == 'search_part':
                    series = ''

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_url):
                    inf = self.create_info(anime_url)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_url), params={})
                        continue
                
                label = self.create_title(self.database.get_title(anime_url), series)

                self.create_line(title=label, anime_id=anime_url, params={'mode': 'select_part', 'id': anime_url})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})

        self.progress.close()
        
        if len(data_array) >= 12:
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                'mode': self.params['mode'], 'sort': self.params['sort'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        if Main.addon.getSetting('status') == '':
            Main.addon.setSetting(id='status', value='Все релизы')

        if Main.addon.getSetting('sort') == '':
            Main.addon.setSetting(id='sort', value='Новое')

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('season')), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(Main.addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if self.params['param'] == 'genre':
            result = self.dialog.select('Жанр:', info.genre)
            Main.addon.setSetting(id='genre', value=info.genre[result])
        
        if self.params['param'] == 'year':
            result = self.dialog.select('Год:', info.year)
            Main.addon.setSetting(id='year', value=info.year[result])
        
        if self.params['param'] == 'season':
            result = self.dialog.select('Сезон:', info.season)
            Main.addon.setSetting(id='season', value=info.season[result])

        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', info.sort.keys())
            Main.addon.setSetting(id='sort', value=info.sort.keys()[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Статус релиза:', info.status.keys())
            Main.addon.setSetting(id='status', value=info.status.keys()[result])

    def exec_select_part(self):
        html = self.network.get_html('https://dark-libria.it/release/{}'.format(self.params['id']))
        
        if Main.addon.getSetting('online_mode') == 'false':
            data_array = html[html.find('<tr class="torrent">')+20:html.find('</tbody>')]
            data_array = utility.clean_list(data_array)
            data_array = data_array.split('<tr class="torrent">')

            for data in data_array:
                torrent_url = data[data.find('/upload/torrents/'):data.find('.torrent')+8]
                data = data.replace('</td>','|')            
                data = utility.tag_list(data)
                data = utility.rep_list(data)
                data = data.split('|')

                label = 'Серии: {} , [COLOR=F0FFD700]{}[/COLOR] , [COLOR=F020F0F0]{}[/COLOR] , Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
                    data[0], data[2], data[1], data[5], data[6])
                
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'])
        else:
            info = dict.fromkeys(['title','sd', 'mid', 'hd', 'id'], '')
            data_array = html[html.find('"[')+2:html.find('}]"')]
            data_array = data_array.split('},')

            sd = []
            mid = []
            hd = []

            for data in data_array:
                data = data.decode('unicode-escape').encode('utf-8')
                data = data.split(',')                

                for d in data:
                    if 'title' in d:
                        info['title'] = d[d.find(': "')+3:d.rfind('"')]
                    if 'Среднее' in d:
                        info['mid'] = d[d.find('http'):d.rfind('m3u8')+4]
                        mid.append('{}|{}'.format(info['title'], info['mid']))
                    if 'Высокое' in d:
                        info['hd'] = d[d.find('http'):d.rfind('m3u8')+4]
                        hd.append('{}|{}'.format(info['title'], info['hd']))
                    if 'Низкое' in d:
                        info['sd'] = d[d.find('http'):d.rfind('m3u8')+4]
                        sd.append('{}|{}'.format(info['title'], info['sd']))

            if info['sd']:
                label = 'Качество: [COLOR=F020F0F0]Низкое[/COLOR]' 
                self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(sd)}, anime_id=self.params['id'])
            if info['mid']:
                label = 'Качество: [COLOR=F020F0F0]Среднее[/COLOR]'
                self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(mid)}, anime_id=self.params['id'])
            if info['hd']:
                label = 'Качество: [COLOR=F020F0F0]Высокое[/COLOR]'
                self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(hd)}, anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        url = 'https://dark-libria.it{}'.format(self.params['torrent_url'])
        file_id = url[url.rfind('/')+1:url.rfind('.')] 
        file_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_id))
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
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_id}, anime_id=self.params['id'], folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_id}, anime_id=self.params['id'], folder=False, size=info['length'])
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def exec_online_part(self):        
        data_array = self.params['param'].split('|||')

        for data in data_array:
            data = data.split('|')            
            self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

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
    anilibria = Main()
    anilibria.execute()
    del anilibria

gc.collect()