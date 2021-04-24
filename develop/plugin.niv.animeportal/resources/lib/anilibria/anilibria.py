# -*- coding: utf-8 -*-

import gc
import os
import sys
import time

import utility

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
from urllib.request import urlopen
from html import unescape

from anilibria import info

class Anilibria:
    addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.site_url = "https://www.anilibria.tv/public/api/index.php"
        if Anilibria.addon.getSetting('anilibria_mirror'):
            self.site_url = '{}public/api/index.php'.format(Anilibria.addon.getSetting('anilibria_mirror'))

        self.addon_data_dir = xbmcvfs.translatePath(Anilibria.addon.getAddonInfo('profile'))
        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'sort':''}
        self.auth_post_data = {
            "mail": Anilibria.addon.getSetting('login'),
            "passwd": Anilibria.addon.getSetting('password')
            }

        args = utility.get_params()
        for a in args:
            self.params[a] = unquote(args[a])

        if Anilibria.addon.getSetting('animeportal_unblock') == '0':
            proxy_data = None
        else:
            proxy_data = self.create_proxy_data()
#================================================
        try: session_time = float(Anilibria.addon.getSetting('session_time'))
        except: session_time = 0

        if time.time() - session_time > 28800:
            Anilibria.addon.setSetting('session_time', str(time.time()))
            try: os.remove(os.path.join(self.addon_data_dir, 'anilibria.sid'))
            except: pass
            Anilibria.addon.setSetting('auth', 'false')
#================================================
        from anilibria.network import WebTools
        self.network = WebTools(auth_usage=bool(Anilibria.addon.getSetting('auth_mode') == 'true'),
                                auth_status=bool(Anilibria.addon.getSetting('auth') == 'true'),
                                proxy_data=proxy_data)
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = 'https://{}/public/login.php'.format(
            Anilibria.addon.getSetting('mirror_{}'.format(Anilibria.addon.getSetting('mirrors'))))
        self.network.sid_file = os.path.join(self.addon_data_dir, 'anilibria.sid')
        del WebTools
#================================================
        if Anilibria.addon.getSetting('auth_mode') == 'true':
            if not Anilibria.addon.getSetting("login") or not Anilibria.addon.getSetting("password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - Укажите логин и пароль')
                return

            if not self.network.auth_status:
                if not self.network.authorization():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - Проверьте логин и пароль')
                    return
                else:
                    Anilibria.addon.setSetting("auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.addon_data_dir, 'anilibria_v1.db')):
            self.exec_update_part()
#================================================
        from anilibria.database import DBTools
        self.database = DBTools(os.path.join(self.addon_data_dir, 'anilibria_v1.db'))
        del DBTools
#================================================
        if not Anilibria.addon.getSetting('anilibria_mirror'):
            self.exec_mirror_part()
#================================================
    def create_proxy_data(self):
        try: proxy_time = float(Anilibria.addon.getSetting('proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 36000:
            Anilibria.addon.setSetting('proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
            
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
            
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            Anilibria.addon.setSetting('proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if Anilibria.addon.getSetting('proxy'):
                proxy_data = {'https': Anilibria.addon.getSetting('proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Anilibria.addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}
        return proxy_data

    def create_post(self):
        if self.params['param'] == 'fav_add':
            post = urlencode({"query":"favorites","id":self.params['id'],"action":"add","filter":"id,series,announce"})
        if self.params['param'] == 'fav_del':
            post = urlencode({"query":"favorites","id":self.params['id'],"action":"delete","filter":"id,series,announce"})
        if self.params['param'] == 'favorites':
            post = urlencode({"query":"favorites","filter":"id,series,announce"})
        if self.params['param'] == 'search_part':
            post = urlencode({"query":"search","search":unquote(self.params['search_string']),"filter":"id,series,announce"})
        if self.params['mode'] == 'schedule_part':            
            post = urlencode({"query":"schedule","filter":"id,series,announce"})
        if self.params['param'] == 'updated':
            post = urlencode({"query":"catalog","page":self.params['page'],"xpage":"catalog","sort":"1","filter":"id,series,announce"})
        if self.params['param'] == 'popular':
            post = urlencode({"query":"catalog","page":self.params['page'],"xpage":"catalog","sort":"2","filter":"id,series,announce"})
        if self.params['param'] == 'catalog':
            post = urlencode({"query": "catalog", "page": self.params['page'], "filter":"id,series,announce", "xpage": "catalog",
                    "search": {"year": Anilibria.addon.getSetting('year'), "genre": Anilibria.addon.getSetting('genre'), "season": Anilibria.addon.getSetting('season')},
                    "sort": info.sort[Anilibria.addon.getSetting('sort')], "finish":info.status[Anilibria.addon.getSetting('status')]})
        if self.params['mode'] == 'online_part':
            post = urlencode({"query":"release","id":self.params['id'],"filter":"playlist"})
        if self.params['mode'] == 'torrent_part':
            post = urlencode({"query":"release","id":self.params['id'],"filter":"torrents"})
        return post.replace('%27','%22')

    def create_title(self, title, series, announce=None):
        if series:
            res = 'Серии: {}'.format(series)
            if announce:
                res = '{} ] - [ {}'.format(res, announce)
            series = ' - [COLOR=gold][ {} ][/COLOR]'.format(res)
            if xbmc.getSkinDir() == 'skin.aeon.nox.silvo' and self.params['mode'] == 'common_part':
                series = ' - [ {} ]'.format(res)
        else:
            series = ''

        if Anilibria.addon.getSetting('animeportal_titles') == '0':
            label = '{}{}'.format(title[0], series)
        if Anilibria.addon.getSetting('animeportal_titles') == '1':
            label = '{}{}'.format(title[1], series)
        if Anilibria.addon.getSetting('animeportal_titles') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image(self, anime_id):
        site_url = self.site_url.replace('public/api/index.php','')
        url = '{}upload/release/350x500/{}.jpg'.format(site_url, anime_id)

        if Anilibria.addon.getSetting('animeportal_covers') == '0':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)

            li.setArt({"thumb": cover, "poster": cover, "tvshowposter": cover, "fanart": cover,
                       "clearart": cover, "clearlogo": cover, "landscape": cover, "icon": cover})

            anime_info = self.database.get_anime(anime_id)

            info = {'genre': anime_info[0],'year': anime_info[2],'plot': anime_info[3],'title': title, 'tvshowtitle': title}
            info['plot'] = '{}\n\n[COLOR=steelblue]Над релизом работали[/COLOR]: {}'.format(info['plot'], anime_info[1])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anilibria")')])

        if Anilibria.addon.getSetting('auth_mode') == 'true' and self.params['mode'] == 'common_part' or self.params['mode'] == 'schedule_part':
            li.addContextMenuItems([
                ('[B]Добавить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_add&portal=anilibria")'.format(anime_id)),
                ('[B]Удалить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_del&portal=anilibria")'.format(anime_id))
                ])

        if self.params['mode'] == 'information_part':
            li.addContextMenuItems([
                ('[B]Обновить Базу Данных[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anilibria")'),
                ('[B]Обновить Зеркала[/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anilibria")')
                ])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):
        post = urlencode({"query":"release","id":anime_id,"filter":"id,names,genres,voices,year,description"})
        post = post.replace('%27','%22')

        html = self.network.get_html(self.site_url, post)

        anime_id = html[html.find('id":')+4:html.find(',"names')]
        names = html[html.find('names":["')+9:html.find('"],"statusCode')]
        names = unescape(names).split('","')
        genres = html[html.find('genres":["')+10:html.find('"],"voices')]
        genres = genres.split('","')            
        voices = html[html.find('voices":["')+10:html.find('"],"year')]
        voices = voices.split('","')
        year = html[html.find('year":"')+7:html.find('","season')]

        description = html[html.find('description":"')+14:html.find('","blockedInfo')]
        description = utility.tag_list(description)
        description = unescape(description)
        description = utility.fix_list(description)
        
        try:
            self.database.add_anime(
                anime_id,
                names[0],
                names[1],
                ', '.join(genres),
                ', '.join(voices),
                year,
                description
                )
        except:
            return 101
        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        Anilibria.addon.openSettings()

    def exec_mirror_part(self):
        url = 'https://darklibria.it/mirror'
        html = self.network.get_html(url)

        mirror = html[html.rfind('btn-lg mb-1" href="')+19:html.rfind('" target="_blank" rel="nofollow">')]
        Anilibria.addon.setSetting('anilibria_mirror', mirror)
        # url = 'https://darklibria.it/mirror'
        # html = self.network.get_html(url)

        # info = html[html.find('btn-lg mb-1" href="')+19:html.find('Сделать личное зеркало 2')]
        # data_array = info.split('href="')
        # i = 0
        # for data in data_array:
        #     i = i + 1
        #     mirror = data[:data.find('/" target')]
        #     mirror = mirror.replace('https://','')
        #     Anilibria.addon.setSetting('mirror_{}'.format(i), mirror)
        
        # if Anilibria.addon.getSetting('mirrors') =='0':
        #     if Anilibria.addon.getSetting('mirror_1'):
        #         Anilibria.addon.setSetting('mirrors', '1')
        return

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.addon_data_dir, 'anilibria_v1.db'))
        except: pass        

        db_file = os.path.join(self.addon_data_dir, 'anilibria_v1.db')        
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anilibria_v1.db'
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
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
            Anilibria.addon.setSetting('database', 'true')
        except:
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
            Anilibria.addon.setSetting('database', 'false')
            pass

    def exec_favorites_part(self):
        html = self.network.get_html(self.site_url, self.create_post())
        label = self.create_title(self.database.get_title(self.params['id']), None)

        if 'status":false' in html:
            if self.params['param'] == 'fav_add':
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - уже в вашем списке[/COLOR]'.format(label))
            if self.params['param'] == 'fav_del':
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - уже удалено из списка[/COLOR]'.format(label))

        if 'status":true' in html:
            if self.params['param'] == 'fav_add':
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно добавлено[/COLOR]'.format(label))
            if self.params['param'] == 'fav_del':
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно удалено[/COLOR]'.format(label))

    def exec_clean_part(self):
        try:
            Anilibria.addon.setSetting('search', '')
            self.dialog.ok('Поиск','Удаление истории - Выполнено')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=yellow]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        if Anilibria.addon.getSetting('auth_mode') == 'true':
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites','portal':self.params['portal']})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part','portal':self.params['portal']})
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part','portal':self.params['portal']})
        self.create_line(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated','portal':self.params['portal']})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular','portal':self.params['portal']})
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part','portal':self.params['portal']})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part','portal':self.params['portal']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if not Anilibria.addon.getSetting('search'):
            Anilibria.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search', 'portal':'anilibria'})

            data_array = Anilibria.addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data),'portal':'anilibria'})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = Anilibria.addon.getSetting('search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                Anilibria.addon.setSetting('search', data_array)

                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_schedule_part(self):
        self.progress.create("Anilibria", "Инициализация")

        html = self.network.get_html(self.site_url, self.create_post())

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        data_array = html.split(']},{')

        i = 0

        for data in data_array:
            data = data[data.find('"id"'):].split('},{')
            week_day = info.week[i]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.create_line(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(week_day), params={})

            for node in data:
                anime_id = node[node.find(':')+1:node.find(',')]
                series = node[node.find('series":"')+9:node.find('","announce')]
                announce = node[node.find('announce":')+10:node.find(',"status')]
                announce = announce.replace('null','').replace('"','')

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id)
                    continue

                label = self.create_title(self.database.get_title(anime_id), series, announce)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        
        self.progress.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return

    def exec_common_part(self):
        self.progress.create("Anilibria", "Инициализация")
        html = self.network.get_html(self.site_url, self.create_post())

        data_array = html[html.find('"id"'):].split('},{')

        i = 0

        for data in data_array:
            anime_id = data[data.find(':')+1:data.find(',')]
            series = data[data.find('series":"')+9:data.find('","announce')]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.is_anime_in_db(anime_id):
                inf = self.create_info(anime_id)
                continue

            label = self.create_title(self.database.get_title(anime_id), series, None)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id, 'portal':self.params['portal']})

        self.progress.close()
        
        if len(data_array) >= 12:
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                             'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1), 'portal': self.params['portal']})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        if Anilibria.addon.getSetting('status') == '':
            Anilibria.addon.setSetting(id='status', value='Все релизы')

        if Anilibria.addon.getSetting('sort') == '':
            Anilibria.addon.setSetting(id='sort', value='Новое')

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(Anilibria.addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre','portal':'anilibria'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(Anilibria.addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year','portal':'anilibria'})
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(Anilibria.addon.getSetting('season')), params={'mode': 'catalog_part', 'param': 'season','portal':'anilibria'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(Anilibria.addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort','portal':'anilibria'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(Anilibria.addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status','portal':'anilibria'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog','portal':'anilibria'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if self.params['param'] == 'genre':
            result = self.dialog.select('Жанр:', info.genre)
            Anilibria.addon.setSetting(id='genre', value=info.genre[result])
        
        if self.params['param'] == 'year':
            result = self.dialog.select('Год:', info.year)
            Anilibria.addon.setSetting(id='year', value=info.year[result])
        
        if self.params['param'] == 'season':
            result = self.dialog.select('Сезон:', info.season)
            Anilibria.addon.setSetting(id='season', value=info.season[result])

        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', tuple(info.sort.keys()))
            Anilibria.addon.setSetting(id='sort', value=tuple(info.sort.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Статус релиза:', tuple(info.status.keys()))
            Anilibria.addon.setSetting(id='status', value=tuple(info.status.keys())[result])

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news','portal':'anilibria'})
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett','portal':'anilibria'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play','portal':'anilibria'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp','portal':'anilibria'})
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs','portal':'anilibria'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]anilibria.tv[/COLOR]', data)
        return

    def exec_select_part(self):
        self.create_line(title='[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id'],'portal':'anilibria'})
        self.create_line(title='[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id'],'portal':'anilibria'})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_online_part(self):
        if not self.params['param']:
            html = self.network.get_html(self.site_url, self.create_post())

            array = {'480p': [], '720p': [], '1080p': []}

            data_array = html[html.find('[{"id"')+2:].split('},{')
            
            for data in data_array:
                name = data[data.find('title":"')+8:data.find('","sd')]

                sd = data[data.find('sd":"')+5:data.find('","hd')]
                hd = data[data.find('hd":"')+5:data.find('","fullhd')]
                fhd = data[data.find('fullhd":"')+9:data.find('","src')]

                if sd:
                    array['480p'].append('{}||{}'.format(name, sd.replace('\/','/')))
                if hd:
                    array['720p'].append('{}||{}'.format(name, hd.replace('\/','/')))
                if fhd:
                    array['1080p'].append('{}||{}'.format(name, fhd.replace('\/','/')))

            for i in array.keys():
                if array[i]:
                    array[i].reverse()
                    label = '[B]Качество: {}[/B]'.format(i)
                    self.create_line(title=label, params={'mode': 'online_part', 'param': ','.join(array[i]), 'id': self.params['id']})
        
        if self.params['param']:
            data_array = self.params['param'].split(',')
            for data in data_array:
                data = data.split('||')
                self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        if not self.params['param']:
            html = self.network.get_html(self.site_url, self.create_post())

            data_array = html[html.find('[{"id"')+2:].split('},{')

            for data in data_array:
                torrent_id = data[data.find(':')+1:data.find(',')]
                leechers = data[data.find('leechers":')+10:data.find(',"seeders')]
                seeders = data[data.find('seeders":')+9:data.find(',"completed')]            
                quality = data[data.find('quality":"')+10:data.find('","series')]
                series = data[data.find('series":"')+9:data.find('","size')]

                torrent_size = data[data.find('size":')+6:data.find(',"url')]
                torrent_size = float('{:.2f}'.format(int(torrent_size)/1024.0/1024/1024))

                label = 'Серии: {} : {} , [COLOR=F0FFD700]{} GB[/COLOR], Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
                    series, quality, torrent_size, seeders, leechers)
                self.create_line(title=label, params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id']})

        if self.params['param']:
            host_site = self.site_url.replace('public/api/index.php','')            
            full_url = '{}upload/torrents/{}.torrent'.format(host_site, self.params['param'])
            file_name = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['param']))
            torrent_file = self.network.get_file(target_name=full_url, destination_name=file_name)

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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': self.params['param']}, anime_id=self.params['id'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': self.params['param']}, anime_id=self.params['id'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if Anilibria.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Anilibria.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Anilibria.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
        if Anilibria.addon.getSetting("Engine") == '2':
            url = 'file:///{}'.format(url.replace('\\','/'))

            import player

            if Anilibria.addon.getSetting('DownloadDirectory') == '':
                download_dir = self.addon_data_dir
            else:
                download_dir = Anilibria.addon.getSetting('DownloadDirectory')
            
            player.play_t2h(int(sys.argv[1]), 15, url, index, download_dir)


# if __name__ == "__main__":
#     anilibria = Anilibria()
#     anilibria.execute()
#     del anilibria

# gc.collect()
