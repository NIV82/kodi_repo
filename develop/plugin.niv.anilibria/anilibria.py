# -*- coding: utf-8 -*-

import gc, os, sys, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

try:
    from urllib import urlencode, urlopen, quote, unquote
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility, info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.anilibria')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()
        self.skin_used = xbmc.getSkinDir()

        self.site_url = 'https://{}/public/api/index.php'.format(
            Main.addon.getSetting('mirror_{}'.format(Main.addon.getSetting('mirrors'))))        

        try: self.addon_data_dir = utility.fs_enc(xbmc.translatePath(Main.addon.getAddonInfo('profile')))
        except: self.addon_data_dir = xbmcvfs.translatePath(Main.addon.getAddonInfo('profile'))

        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)
        
        self.cookies_dir = os.path.join(self.addon_data_dir, 'cookies')
        if not os.path.exists(self.cookies_dir):
            os.mkdir(self.cookies_dir)

        self.database_dir = os.path.join(self.addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.cache_dir = os.path.join(self.addon_data_dir, 'cache')
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'sort':''}
        self.auth_post_data = {
            "mail": Main.addon.getSetting('login'),
            "passwd": Main.addon.getSetting('password')
            }

        args = utility.get_params()
        for a in args:
            self.params[a] = unquote(args[a])

        if Main.addon.getSetting('unblock') == '0':
            proxy_data = None
        else:
            proxy_data = self.create_proxy_data()
#================================================
        try: session_time = float(Main.addon.getSetting('session_time'))
        except: session_time = 0

        if time.time() - session_time > 28800:
            Main.addon.setSetting('session_time', str(time.time()))
            try: os.remove(os.path.join(self.cookies_dir, 'anilibria.sid'))
            except: pass
            Main.addon.setSetting('auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(auth_usage=bool(Main.addon.getSetting('auth_mode') == 'true'),
                                auth_status=bool(Main.addon.getSetting('auth') == 'true'),
                                proxy_data=proxy_data)
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = 'https://{}/public/login.php'.format(
            Main.addon.getSetting('mirror_{}'.format(Main.addon.getSetting('mirrors'))))
        self.network.sid_file = os.path.join(self.cookies_dir, 'anilibria.sid')
        del WebTools
#================================================
        if Main.addon.getSetting('auth_mode') == 'true':
            if not Main.addon.getSetting("login") or not Main.addon.getSetting("password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - Укажите логин и пароль')
                return

            if not self.network.auth_status:
                if not self.network.authorization():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - Проверьте логин и пароль')
                    return
                else:
                    Main.addon.setSetting("auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'anilibria_v1.db')):
            self.exec_update_part()
#================================================
        from database import DBTools
        if Main.addon.getSetting('database') == 'false':
            os.remove(os.path.join(self.database_dir, 'anilibria_v1.db'))
            Main.addon.setSetting('database', 'true')
        self.database = DBTools(os.path.join(self.database_dir, 'anilibria_v1.db'))
        del DBTools
#================================================
        if not Main.addon.getSetting('mirror_1'):
            self.exec_mirror_part()
#================================================
    def create_proxy_data(self):
        try: proxy_time = float(Main.addon.getSetting('proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 36000:
            Main.addon.setSetting('proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
            
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
            
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            Main.addon.setSetting('proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if Main.addon.getSetting('proxy'):
                proxy_data = {'https': Main.addon.getSetting('proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Main.addon.setSetting('proxy', proxy)
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
                    "search": {"year": Main.addon.getSetting('year'), "genre": Main.addon.getSetting('genre'), "season": Main.addon.getSetting('season')},
                    "sort": info.sort[Main.addon.getSetting('sort')], "finish":info.status[Main.addon.getSetting('status')]})
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

        if Main.addon.getSetting('title_mode') == '0':
            label = '{}{}'.format(title[0], series)
        if Main.addon.getSetting('title_mode') == '1':
            label = '{}{}'.format(title[1], series)
        if Main.addon.getSetting('title_mode') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image(self, anime_id):
        site_url = self.site_url.replace('public/api/index.php','')
        url = '{}upload/release/350x500/{}.jpg'.format(site_url, anime_id)

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                try: local_path = utility.fs_dec(os.path.join(self.images_dir, local_img))
                except: local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                try: file_name = utility.fs_dec(os.path.join(self.images_dir, local_img))
                except: file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)

            li.setArt({
                "thumb": cover,
                "poster": cover,
                "tvshowposter": cover,
                # "banner": cover,
                "fanart": cover,
                "clearart": cover,
                "clearlogo": cover,
                "landscape": cover,
                "icon": cover
                })

            anime_info = self.database.get_anime(anime_id)
            #genres, voices, year, description
            info = {'genre': anime_info[0],'year': anime_info[2],'plot': anime_info[3],'title': title, 'tvshowtitle': title}
            info['plot'] = '{}\n\n[COLOR=steelblue]Над релизом работали[/COLOR]: {}'.format(info['plot'], anime_info[1])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=clean_part")')])

        if Main.addon.getSetting('auth_mode') == 'true' and self.params['mode'] == 'common_part' or self.params['mode'] == 'schedule_part':
            li.addContextMenuItems([
                ('[B]Добавить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}&param=fav_add")'.format(anime_id)),
                ('[B]Удалить FAV (сайт)[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}&param=fav_del")'.format(anime_id))
                ])

        if self.params['mode'] == 'information_part':
            li.addContextMenuItems([
                ('[B]Обновить Базу Данных[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=update_part")'),
                ('[B]Обновить Зеркала[/B]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=mirror_part")')
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
        names = utility.rep_list(names).split('","')
        genres = html[html.find('genres":["')+10:html.find('"],"voices')]
        genres = genres.split('","')            
        voices = html[html.find('voices":["')+10:html.find('"],"year')]
        voices = voices.split('","')
        year = html[html.find('year":"')+7:html.find('","season')]

        description = html[html.find('description":"')+14:html.find('","blockedInfo')]
        description = utility.tag_list(description)
        description = utility.rep_list(description)
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
        Main.addon.openSettings()

    def exec_mirror_part(self):
        url = 'https://darklibria.it/mirror'
        html = self.network.get_html(url)

        info = html[html.find('btn-lg mb-1" href="')+19:html.find('Сделать личное зеркало 2')]
        data_array = info.split('href="')
        i = 0
        for data in data_array:
            i = i + 1
            mirror = data[:data.find('/" target')]
            mirror = mirror.replace('https://','')
            Main.addon.setSetting('mirror_{}'.format(i), mirror)
        
        if Main.addon.getSetting('mirrors') =='0':
            if Main.addon.getSetting('mirror_1'):
                Main.addon.setSetting('mirrors', '1')
        return

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'anilibria_v1.db'))
        except: pass        

        db_file = os.path.join(self.database_dir, 'anilibria_v1.db')        
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
            Main.addon.setSetting('database', 'true')
        except:
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
            Main.addon.setSetting('database', 'false')
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
            Main.addon.setSetting('search', '')
            self.dialog.ok('Поиск','Удаление истории - Выполнено')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=yellow]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        if Main.addon.getSetting('auth_mode') == 'true':
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites'})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated'})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular'})
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
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = Main.addon.getSetting('search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                Main.addon.setSetting('search', data_array)

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
        xbmc.log(str(self.site_url), xbmc.LOGFATAL)
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
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        self.progress.close()
        
        if len(data_array) >= 12:
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

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
            result = self.dialog.select('Сортировать по:', tuple(info.sort.keys()))
            Main.addon.setSetting(id='sort', value=tuple(info.sort.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Статус релиза:', tuple(info.status.keys()))
            Main.addon.setSetting(id='status', value=tuple(info.status.keys())[result])

    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]anilibria.tv[/COLOR]', data)
        return

    def exec_select_part(self):
        self.create_line(title='[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id']})
        self.create_line(title='[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
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

        if Main.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Main.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        
        if Main.addon.getSetting("Engine") == '2':
            url = 'file:///{}'.format(url.replace('\\','/'))

            import player

            if Main.addon.getSetting('DownloadDirectory') == '':
                download_dir = self.addon_data_dir
            else:
                download_dir = Main.addon.getSetting('DownloadDirectory')
            
            player.play_t2h(int(sys.argv[1]), 15, url, index, download_dir)


if __name__ == "__main__":
    anilibria = Main()
    anilibria.execute()
    del anilibria

gc.collect()