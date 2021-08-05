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

from utility import unescape, tag_list, fix_list

class Anilibria:
    #def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress):
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
        self.auth_mode = bool(self.addon.getSetting('anilibria_auth_mode') == '1')
#================================================
        try: anilibria_session = float(self.addon.getSetting('anilibria_session'))
        except: anilibria_session = 0

        if time.time() - anilibria_session > 28800:
            self.addon.setSetting('anilibria_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anilibria.sid'))
            except: pass
            self.addon.setSetting('anilibria_auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('anilibria_auth') == 'true'),
            proxy_data=self.proxy_data,
            portal='anilibria')
        self.auth_post_data = {
            "mail": self.addon.getSetting('anilibria_username'),
            "passwd": self.addon.getSetting('anilibria_password')
            }
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = self.site_url.replace('api/index.php','login.php')
        self.network.sid_file = os.path.join(self.cookie_dir, 'anilibria.sid')
        del WebTools
#================================================  
        if self.auth_mode:
            if not self.addon.getSetting("anilibria_username") or not self.addon.getSetting("anilibria_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting("anilibria_auth", str(self.network.auth_status).lower())
#================================================
        # if not os.path.isfile(os.path.join(self.database_dir, 'anilibria.db')):
        #     self.exec_update_part()
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_part()
#================================================
        from database import Anilibria_DB
        self.database = Anilibria_DB(os.path.join(self.database_dir, 'anilibria.db'))
        del Anilibria_DB
#================================================
    def create_proxy_data(self):
        #if self.addon.getSetting('anidub_unblock') == '0':
        if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            # try: proxy_pac = str(proxy_pac, encoding='utf-8')
            # except: pass
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

                # try: proxy_pac = str(proxy_pac, encoding='utf-8')
                # except: pass

                try: proxy_pac = proxy_pac.decode('utf-8')
                except: pass
                
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#================================================
    def create_site_url(self):
        site_url = self.addon.getSetting('anilibria_mirror_0')
        current_mirror = 'anilibria_mirror_{}'.format(self.addon.getSetting('anilibria_mirror_mode'))        

        if not self.addon.getSetting(current_mirror):
            try:
                self.exec_mirror_part()
                site_url = '{}public/api/index.php'.format(self.addon.getSetting(current_mirror))
            except:
                site_url = "{}public/api/index.php".format(site_url)
        else:
            site_url = '{}public/api/index.php'.format(self.addon.getSetting(current_mirror))
        return site_url
  
    def create_post(self):
        anilibria_status = {"Все релизы":"1", "Завершенные релизы":"2"}
        anilibria_sort = {"Новое":'1', "Популярное":"2"}

        if self.params['param'] == 'fav_add':
            post = 'query=favorites&id={}&action=add&filter=id%2Cseries%2Cannounce'.format(self.params['id'])
        if self.params['param'] == 'fav_del':
            post = 'query=favorites&id={}&action=delete&filter=id%2Cseries%2Cannounce'.format(self.params['id'])
        if self.params['param'] == 'favorites':
            post = 'query=favorites&filter=id%2Cseries%2Cannounce'
        if self.params['param'] == 'search_part':
            post = 'query=search&search={}&filter=id%2Cseries%2Cannounce'.format(self.params['search_string'])
        if self.params['mode'] == 'schedule_part':
            post = 'query=schedule&filter=id%2Cseries%2Cannounce'
        if self.params['param'] == 'updated':
            post = 'query=catalog&page={}&xpage=catalog&sort=1&filter=id%2Cseries%2Cannounce'.format(self.params['page'])
        if self.params['param'] == 'popular':
            post = 'query=catalog&page={}&xpage=catalog&sort=2&filter=id%2Cseries%2Cannounce'.format(self.params['page'])
        if self.params['param'] == 'catalog':
            post = 'query=catalog&page={}&filter=id%2Cseries%2Cannounce&xpage=catalog&search=%7B%22year%22%3A%22{}%22%2C%22genre%22%3A%22{}%22%2C%22season%22%3A%22{}%22%7D&sort={}&finish={}'.format(
                self.params['page'],self.addon.getSetting('anilibria_year'),self.addon.getSetting('anilibria_genre'),self.addon.getSetting('anilibria_season'),
                anilibria_sort[self.addon.getSetting('anilibria_sort')],anilibria_status[self.addon.getSetting('anilibria_status')])
        if self.params['mode'] == 'online_part':
            post = 'query=release&id={}&filter=playlist'.format(self.params['id'])
        if self.params['mode'] == 'torrent_part':
            post = 'query=release&id={}&filter=torrents'.format(self.params['id'])
      
        return post

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

        if self.addon.getSetting('anilibria_titles') == '0':
            label = '{}{}'.format(title[0], series)
        if self.addon.getSetting('anilibria_titles') == '1':
            label = '{}{}'.format(title[1], series)
        if self.addon.getSetting('anilibria_titles') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image(self, anime_id):
        site_url = self.site_url.replace('public/api/index.php','')
        url = '{}upload/release/350x500/{}.jpg'.format(site_url, anime_id)

        if self.addon.getSetting('anilibria_covers') == '0':
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
        
        context_menu.append(('[B][COLOR=darkorange]Обновить Базу Данных[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=anilibria")'))
        context_menu.append(('[B][COLOR=darkorange]Обновить Зеркала[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anilibria")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=red]Очистить историю[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anilibria")'))

        if self.auth_mode and 'common_part' in self.params['mode'] or self.auth_mode and 'schedule_part' in self.params['mode']:
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=white]Добавить FAV (сайт)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_add&portal=anilibria")'.format(anime_id)))
            context_menu.append(('[B][COLOR=white]Удалить FAV (сайт)[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_del&portal=anilibria")'.format(anime_id)))
        
        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append(('[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anilibria")'))
        context_menu.append(('[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=anilibria")'))
        context_menu.append(('[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=anilibria")'))
        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))

        return context_menu

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

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = 'anilibria'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):
        post = 'query=release&id={}&filter=id%2Cnames%2Cgenres%2Cvoices%2Cyear%2Cdescription'.format(anime_id)
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
        description = tag_list(description)
        description = unescape(description)
        description = fix_list(description)
        
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
        self.addon.openSettings()

    def exec_mirror_part(self):
        from network import WebTools
        self.net = WebTools(auth_usage=False,auth_status=False,proxy_data=self.proxy_data)
        del WebTools

        html = self.net.get_html(target_name='https://darklibria.it/mirror')

        mirror = html[html.find('lg mb-1" href="')+15:html.rfind('" target="_blank" rel="nofollow">')]
        mirror_1 = mirror[:mirror.find('" target=')]
        mirror_2 = mirror[mirror.rfind('href="')+6:]

        self.addon.setSetting('anilibria_mirror_1', mirror_1)
        self.addon.setSetting('anilibria_mirror_2', mirror_2)
        return

    def exec_update_part(self):
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
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
            pass

    # def exec_update_part(self):
    #     try: self.database.end()
    #     except: pass
        
    #     #try: os.remove(os.path.join(self.database_dir, 'anidub.db'))
    #     try: os.remove(os.path.join(self.database_dir, '{}.db'.format(self.params['portal'])))
    #     except: pass

    #     #db_file = os.path.join(self.database_dir, 'anidub.db')
    #     db_file = os.path.join(self.database_dir, '{}.db'.format(self.params['portal']))
    #     #db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anidub.db'
    #     db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/{}.db'.format(self.params['portal'])
    #     try:                
    #         data = urlopen(db_url)
    #         chunk_size = 8192
    #         bytes_read = 0

    #         try: file_size = int(data.info().getheaders("Content-Length")[0])
    #         except: file_size = int(data.getheader('Content-Length'))

    #         self.progress.create('Загрузка Базы Данных')
    #         with open(db_file, 'wb') as write_file:
    #             while True:
    #                 chunk = data.read(chunk_size)
    #                 bytes_read = bytes_read + len(chunk)
    #                 write_file.write(chunk)
    #                 if len(chunk) < chunk_size:
    #                     break
    #                 percent = bytes_read * 100 / file_size
    #                 self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
    #             self.progress.close()
    #         #label_1 = '{} - База Данных'.format(self.params['portal'].upper())
    #         #label_2 = 'База Данных [COLOR=lime]успешно загружена[/COLOR]'
    #         xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
    #             self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
    #         #self.dialog.ok('AniDUB - База Данных','БД успешно загружена')
    #     except:
    #         xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
    #             self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
    #         #self.dialog.ok('AniDUB - База Данных','Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
    #         pass
        
    # def exec_update_part(self):
    #     try: self.database.end()
    #     except: pass

    #     try: os.remove(os.path.join(self.database_dir, 'anilibria.db'))
    #     except: pass

    #     db_file = os.path.join(self.database_dir, 'anilibria.db')        
    #     db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anilibria.db'
    #     try:                
    #         data = urlopen(db_url)
    #         chunk_size = 8192
    #         bytes_read = 0

    #         try: file_size = int(data.info().getheaders("Content-Length")[0])
    #         except: file_size = int(data.getheader('Content-Length'))

    #         self.progress.create('Загрузка Базы Данных')
    #         with open(db_file, 'wb') as write_file:
    #             while True:
    #                 chunk = data.read(chunk_size)
    #                 bytes_read = bytes_read + len(chunk)
    #                 write_file.write(chunk)
    #                 if len(chunk) < chunk_size:
    #                     break
    #                 percent = bytes_read * 100 / file_size
    #                 self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
    #             self.progress.close()
    #         self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
    #     except:
    #         self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
    #         pass

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
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=lime]успешно выполнено[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=yellow]ERROR: 102[/COLOR]', 5000, self.icon))
            pass

    def exec_information_part(self):
        from info import animeportal_data as info
            
        start = '[{}]'.format(self.params['param'])
        end = '[/{}]'.format(self.params['param'])
        data = info[info.find(start)+6:info.find(end)].strip()

        self.dialog.textviewer(u'Информация', data)
        return

    def exec_main_part(self):
        if self.auth_mode:
            self.create_line(title='[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites'})
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=yellow][ Новое ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated'})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular'})
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        #self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('anilibria_search').split('|')
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
                data_array = self.addon.getSetting('anilibria_search').split('|')
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('anilibria_search', data_array)

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
            week_day = ('Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье')[i]

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

            label = self.create_title(self.database.get_title(anime_id), series, None)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        self.progress.close()
        
        if len(data_array) >= 12:
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                             'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        anilibria_year = ("", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012",
                "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2001", "1998", "1996")
        anilibria_season = ("","зима", "весна", "лето", "осень")
        anilibria_genre = ("","экшен","фэнтези","комедия","приключения","романтика","сёнен","драма","школа",
                "сверхъестественное","фантастика","сейнен","магия","этти","детектив","повседневность","ужасы",
                "супер сила","психологическое","исторический","меха","мистика","демоны","игры","сёдзе","триллер",
                "вампиры","спорт","боевые искусства","музыка")
        anilibria_status = {"Все релизы":"1", "Завершенные релизы":"2"}
        anilibria_sort = {"Новое":'1', "Популярное":"2"}

        if self.addon.getSetting('anilibria_status') == '':
            self.addon.setSetting(id='anilibria_status', value='Все релизы')

        if self.addon.getSetting('anilibria_sort') == '':
            self.addon.setSetting(id='anilibria_sort', value='Новое')

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('anilibria_genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('anilibria_year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('anilibria_season')), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('anilibria_sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('anilibria_status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if self.params['param'] == 'genre':
            result = self.dialog.select('Жанр:', anilibria_genre)
            self.addon.setSetting(id='anilibria_genre', value=anilibria_genre[result])
        
        if self.params['param'] == 'year':
            result = self.dialog.select('Год:', anilibria_year)
            self.addon.setSetting(id='anilibria_year', value=anilibria_year[result])
        
        if self.params['param'] == 'season':
            result = self.dialog.select('Сезон:', anilibria_season)
            self.addon.setSetting(id='anilibria_season', value=anilibria_season[result])            

        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', tuple(anilibria_sort.keys()))
            self.addon.setSetting(id='anilibria_sort', value=tuple(anilibria_sort.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Статус релиза:', tuple(anilibria_status.keys()))
            self.addon.setSetting(id='anilibria_status', value=tuple(anilibria_status.keys())[result])
            
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
            file_name = '{}_{}'.format(self.params['portal'], self.params['param'])            
            full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))
            
            torrent_file = self.network.get_file(target_name=full_url, destination_name=full_name)

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