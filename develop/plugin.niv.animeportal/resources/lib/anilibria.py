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

from utility import tag_list, fix_list, digit_list, clean_tags

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    
class Anilibria:
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

        self.proxy_data = None
        # self.proxy_data = self.create_proxy_data()
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
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('{}_auth'.format(self.params['portal'])) == 'true'),
            proxy_data=self.proxy_data, portal=self.params['portal'])
        self.auth_post_data = 'mail={}&passwd={}'.format(
            self.addon.getSetting('{}_username'.format(self.params['portal'])),
            self.addon.getSetting('{}_password'.format(self.params['portal']))
            )
        self.network.auth_post_data = self.auth_post_data
        self.network.auth_url = self.site_url.replace('api/index.php','login.php')
        self.network.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))
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
    def create_site_url(self):
        site_url = self.addon.getSetting('{}_mirror_0'.format(self.params['portal']))
        current_mirror = '{}_mirror_{}'.format(self.params['portal'], self.addon.getSetting('{}_mirror_mode'.format(self.params['portal'])))

        if not self.addon.getSetting(current_mirror):
            try:
                self.exec_mirror_part()
                site_url = '{}public/api/index.php'.format(self.addon.getSetting(current_mirror))
            except:
                site_url = '{}public/api/index.php'.format(site_url)
        else:
            site_url = '{}public/api/index.php'.format(self.addon.getSetting(current_mirror))

        return site_url
#========================#========================#========================#
    def create_post(self):
        from info import anilibria_status, anilibria_sort

        if self.params['param'] == 'fav_add':
            post = 'query=favorites&id={}&action=add&filter=id%2Cseries%2Cannounce'.format(self.params['id'])
        if self.params['param'] == 'fav_del':
            post = 'query=favorites&id={}&action=delete&filter=id%2Cseries%2Cannounce'.format(self.params['id'])
        if self.params['param'] == 'favorites':
            post = 'query=favorites&filter=id%2Cseries%2Cannounce%2Cposter'
        if self.params['param'] == 'search_part':
            post = 'query=search&search={}&filter=id%2Cseries%2Cannounce%2Cposter'.format(self.params['search_string'])
        if self.params['mode'] == 'schedule_part':
            post = 'query=schedule&filter=id%2Cseries%2Cannounce%2Cposter'
        if self.params['param'] == 'updated':
            post = 'query=catalog&page={}&xpage=catalog&sort=1&filter=id%2Cseries%2Cannounce%2Cposter'.format(self.params['page'])
        if self.params['param'] == 'popular':
            post = 'query=catalog&page={}&xpage=catalog&sort=2&filter=id%2Cseries%2Cannounce%2Cposter'.format(self.params['page'])
        if self.params['param'] == 'catalog':
            post = 'query=catalog&page={}&filter=id%2Cseries%2Cannounce%2Cposter&xpage=catalog&search=%7B%22year%22%3A%22{}%22%2C%22genre%22%3A%22{}%22%2C%22season%22%3A%22{}%22%7D&sort={}&finish={}'.format(
                self.params['page'],
                self.addon.getSetting('{}_year'.format(self.params['portal'])),
                self.addon.getSetting('{}_genre'.format(self.params['portal'])),
                self.addon.getSetting('{}_season'.format(self.params['portal'])),
                anilibria_sort[self.addon.getSetting('{}_sort'.format(self.params['portal']))],
                anilibria_status[self.addon.getSetting('{}_status'.format(self.params['portal']))])
        if self.params['mode'] == 'online_part':
            post = 'query=release&id={}&filter=playlist%2Cposter'.format(self.params['id'])
        if self.params['mode'] == 'torrent_part':
            post = 'query=release&id={}&filter=torrents%2Cposter'.format(self.params['id'])

        return post
#========================#========================#========================#
    def create_title(self, anime_id, series, announce=''):
        title = self.database.get_title(anime_id)

        year = self.database.get_year(anime_id)
        year = '[COLOR=blue]{}[/COLOR] | '.format(year) if year else ''

        if series:
            series = u' | [COLOR=gold]{}[/COLOR]'.format(series.strip()) if series else ''
            
        if announce:
            announce = u' | [COLOR=gold]{}[/COLOR]'.format(announce.strip()) if announce else ''
            
        if '0' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}{}{}'.format(year, title[0], series, announce)
        if '1' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{}{}{}'.format(year, title[1], series, announce)
        if '2' in self.addon.getSetting('{}_titles'.format(self.params['portal'])):
            label = u'{}{} / {}{}{}'.format(year, title[0], title[1], series, announce)
            
        if 'anime_id:' in label:
            label = u'[COLOR=red]ERROR[/COLOR] | Ошибка 403-404 | [COLOR=gold]{}[/COLOR]'.format(
                title[0].replace('anime_id: ',''))
            
        return label
#========================#========================#========================#
    def create_image(self, cover):
        anime_cover = cover.replace('\/','/').replace('/', '', 1)
        anime_url = self.site_url.replace('public/api/index.php','').replace('//www.','//static.')
        cover = '{}{}'.format(anime_url, anime_cover)
        return cover

        # if '0' in self.addon.getSetting('{}_covers'.format(self.params['portal'])):
        #     return url
        # else:
        #     local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
        #     if local_img in os.listdir(self.images_dir):
        #         local_path = os.path.join(self.images_dir, local_img)
        #         return local_path
        #     else:
        #         file_name = os.path.join(self.images_dir, local_img)
        #         return self.network.get_file(target_name=url, destination_name=file_name)
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        
        context_menu.append((u'[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal={}")'.format(self.params['portal'])))
        context_menu.append((u'[COLOR=darkorange]Обновить Зеркала[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal={}")'.format(self.params['portal'])))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append((u'[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal={}")'.format(self.params['portal'])))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal={}")'.format(anime_id, self.params['portal'])))

        if self.auth_mode and 'common_part' in self.params['mode'] or self.auth_mode and 'schedule_part' in self.params['mode']:
            context_menu.append((u'[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_add&portal={}")'.format(anime_id, self.params['portal'])))
            context_menu.append((u'[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&id={}&param=fav_del&portal={}")'.format(anime_id, self.params['portal'])))
        
        context_menu.append((u'[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal={}")'.format(self.params['portal'])))
        context_menu.append((u'[COLOR=lime]Настройки воспроизведения[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal={}")'.format(self.params['portal'])))
        context_menu.append((u'[COLOR=lime]Описание ошибок плагина[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal={}")'.format(self.params['portal'])))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(cover)

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
                'aired':anime_info[3],
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        if '0' in self.addon.getSetting('anilibria_api'):
            url = self.site_url
            post = urlencode({"query": "release", "id": anime_id,
                             "filter": "id,names,genres,voices,year,description"})
            post = post.replace('%27','%22')
            
            html = self.network.get_html(target_name=url, post=post)
            html = unescape(html)

            anime_id = html[html.find('id":')+4:html.find(',"names')]
            names = html[html.find('names":["')+9:html.find('"],"statusCode')]
            names = names.split('","')
            genres = html[html.find('genres":["')+10:html.find('"],"voices')]                   
            voices = html[html.find('voices":["')+10:html.find('"],"year')]
            year = html[html.find('year":"')+7:html.find('","season')]
            description = html[html.find('description":"')+14:html.find('","blockedInfo')]
            description = clean_tags(description)
            description = fix_list(description)
            
            try:
                self.database.add_anime(
                    anime_id = anime_id,
                    title_ru = names[0],
                    title_en = names[1],
                    genres = genres.replace('"','').replace(',', ', '),
                    dubbing = voices.replace('"','').replace(',', ', '),
                    aired_on = year,
                    description = fix_list(description),
                    update=update
                    )
            except:
                return 101
        else:
            url = 'https://api.anilibria.tv/v2/getTitle?id={}{}'.format(
                anime_id, '&filter=id,names,type.code,type.length,genres,team,season.year,description')

            html = self.network.get_html(target_name=url)
            
            if not html:
                self.database.add_anime(
                    anime_id=anime_id,
                    title_ru='anime_id: {}'.format(anime_id),
                    title_en='anime_id: {}'.format(anime_id)
                    )
                return

            html = unescape(html)

            anime_id = html[html.find(':')+1:html.find(',')]
            title_ru = html[html.find('ru":"')+5:html.find('","en')]
            title_en = html[html.find('en":"')+5:html.find('","alt')]
            kind = html[html.find('code":')+6:html.find(',"length')]
            length = html[html.find('length":')+8:html.find('},"genres')]
            genres = html[html.find('genres":[')+9:html.find('],"team')]
            voice = html[html.find('voice":[')+8:html.find('],"translator')]
            translator = html[html.find('translator":[')+13:html.find('],"editing')]
            editing = html[html.find('editing":[')+10:html.find('],"decor')]
            decor = html[html.find('decor":[')+8:html.find('],"timing')]
            timing = html[html.find('timing":[')+9:html.find(']},"season')]
            year = html[html.find('year":')+6:html.find('},"descrip')]
            description = html[html.find('description":"')+14:html.rfind('"}')]

            try:
                self.database.add_anime(
                    anime_id = anime_id,
                    title_ru = title_ru,
                    title_en = title_en,
                    kind = kind,
                    duration = digit_list(length),
                    genres = genres.replace('"','').replace(',', ', '),
                    dubbing = voice.replace('"','').replace(',', ', '),
                    translation = translator.replace('"','').replace(',', ', '),
                    editing = editing.replace('"','').replace(',', ', '),
                    mastering = decor.replace('"','').replace(',', ', '),
                    timing = timing.replace('"','').replace(',', ', '),
                    aired_on = year,
                    description = fix_list(description),
                    update=update
                    )                    
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
    def exec_mirror_part(self):
        proxy_data = {'https': 'proxy-nossl.antizapret.prostovpn.org:29976'}

        from network import WebTools
        self.net = WebTools(auth_usage=False, auth_status=False, proxy_data=proxy_data, portal=self.params['portal'])
        del WebTools

        html = self.net.get_html(target_name='https://darklibria.it/redirect/mirror/1')
        
        mirror = html[html.find('mt-1" href="')+12:html.find('" target="_blank" rel="')]

        self.addon.setSetting('{}_mirror_1'.format(self.params['portal']), '{}/'.format(mirror))
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
    def exec_favorites_part(self):
        html = self.network.get_html(self.site_url, self.create_post())
       
        if 'status":false' in html:
            if 'fav_add' in self.params['param']:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, self.icon))
            if 'fav_del' in self.params['param']:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=gold]ERROR: 103[/COLOR]', 5000, self.icon))

        if 'status":true' in html:
            if 'fav_add' in self.params['param']:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО ДОБАВЛЕНО[/COLOR]', 5000, self.icon))
            if 'fav_del' in self.params['param']:
                xbmc.executebuiltin('Notification({},{},{},{})'.format('Избранное', '[COLOR=lime]УСПЕШНО УДАЛЕНО[/COLOR]', 5000, self.icon))
        
        xbmc.executebuiltin('Container.Refresh')
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
        #from utility_module import create_line
        
        # if self.auth_mode:
        #     create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites', 'portal': 'anilibria'})
        # create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part', 'portal': 'anilibria'})
        # create_line(title='[B][COLOR=white]Расписание[/COLOR][/B]', params={'mode': 'schedule_part', 'portal': 'anilibria'})
        # create_line(title='[B][COLOR=yellow]Новое[/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated', 'portal': 'anilibria'})
        # create_line(title='[B][COLOR=blue]Популярное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular', 'portal': 'anilibria'})
        # create_line(title='[B][COLOR=lime]Каталог[/COLOR][/B]', params={'mode': 'catalog_part', 'portal': 'anilibria'})
        
        if self.auth_mode:
            self.create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites'})
        self.create_line(title='[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=white]Расписание[/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B][COLOR=yellow]Новое[/COLOR][/B]', params={'mode': 'common_part', 'param': 'updated'})
        self.create_line(title='[B][COLOR=blue]Популярное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular'})
        self.create_line(title='[B][COLOR=lime]Каталог[/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')
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
                data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)

                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        self.progress.create('{}'.format(self.params['portal'].upper()), 'Инициализация')

        from info import anilibria_week

        html = self.network.get_html(target_name=self.site_url, post=self.create_post())

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        # if not '<div class="th-item">' in html:
        #     self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
        #     xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        #     return

        data_array = html.split(']},{')

        i = 0

        for data in data_array:
            data = data[data.find('"id"'):].split('},{')
            week_day = anilibria_week[i]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.create_line(title='[B][COLOR=lime]{}[/COLOR][/B]'.format(week_day), params={})

            for node in data:
                anime_id = node[node.find(':')+1:node.find(',')]              
                series = node[node.find('series":"')+9:node.find('","poster')]
                cover = node[node.find('poster":"')+9:node.find('","announce')]
                announce = node[node.find('announce":')+10:node.find(',"status')]
                announce = announce.replace('null','').replace('"','')

                if self.progress.iscanceled():
                    break
                self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.anime_in_db(anime_id):
                    self.create_info(anime_id)

                label = self.create_title(anime_id, series, announce)
                self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part', 'id': anime_id, 'node':cover})
        
        self.progress.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        self.progress.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
        html = self.network.get_html(self.site_url, self.create_post())

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
            
        # if not '<div class="th-item">' in html:
        #     self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
        #     xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        #     return
        
        data_array = html[html.find('"id"'):].split('},{')

        i = 0

        for data in data_array:
            data = unescape(data)

            anime_id = data[data.find(':')+1:data.find(',')]
            series = data[data.find('series":"')+9:data.find('","poster"')]
            cover = data[data.find('poster":"')+9:data.find('","announce')]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if self.progress.iscanceled():
                break
            self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                self.create_info(anime_id)

            label = self.create_title(anime_id, series)
            
            self.create_line(title=label, anime_id=anime_id, cover=cover, params={'mode': 'select_part', 'id': anime_id})

        self.progress.close()
        
        if len(data_array) >= 12:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        from info import anilibria_year, anilibria_season, anilibria_genre, anilibria_status, anilibria_sort

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_genre'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_year'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_season'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_sort'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                self.addon.getSetting('{}_status'.format(self.params['portal']))), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if self.params['param'] == 'genre':
            result = self.dialog.select('Жанр:', anilibria_genre)
            self.addon.setSetting(id='{}_genre'.format(self.params['portal']), value=anilibria_genre[result])
        
        if self.params['param'] == 'year':
            result = self.dialog.select('Год:', anilibria_year)
            self.addon.setSetting(id='{}_year'.format(self.params['portal']), value=anilibria_year[result])
        
        if self.params['param'] == 'season':
            result = self.dialog.select('Сезон:', anilibria_season)
            self.addon.setSetting(id='{}_season'.format(self.params['portal']), value=anilibria_season[result])            

        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', tuple(anilibria_sort.keys()))
            self.addon.setSetting(id='{}_sort'.format(self.params['portal']), value=tuple(anilibria_sort.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Статус релиза:', tuple(anilibria_status.keys()))
            self.addon.setSetting(id='{}_status'.format(self.params['portal']), value=tuple(anilibria_status.keys())[result])
#========================#========================#========================#   
    def exec_select_part(self):
        self.create_line(title=u'[B]Онлайн просмотр[/B]', params={'mode': 'online_part', 'id': self.params['id']})
        self.create_line(title=u'[B]Торрент просмотр[/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            html = self.network.get_html(self.site_url, self.create_post())
            array = {'480p': [], '720p': [], '1080p': []}

            cover = html[html.find('poster":"')+9:html.find('","status')]
            data_array = html[html.find('[{"id"')+2:].split('},{')
            
            for data in data_array:
                name = data[data.find('title":"')+8:data.find('","')]
                name = digit_list(name)

                sd = data[data.find('sd":"')+5:data.find('","hd')]
                hd = data[data.find('hd":"')+5:data.find('","fullhd')]
                fhd = data[data.find('fullhd":"')+9:data.find('"}')]

                if sd:
                    array['480p'].append('{}||{}'.format(name, sd.replace('\/','/')))
                if hd:
                    array['720p'].append('{}||{}'.format(name, hd.replace('\/','/')))
                if fhd:
                    array['1080p'].append('{}||{}'.format(name, fhd.replace('\/','/')))

            for i in array.keys():
                if array[i]:
                    array[i].reverse()
                    label = u'[B]Качество: {}[/B]'.format(i)
                    self.create_line(title=label, params={'mode': 'online_part', 'param': ','.join(array[i]), 'id': self.params['id'], 'node': cover})
        
        if self.params['param']:
            data_array = self.params['param'].split(',')
            for data in data_array:
                data = data.split('||')
                label = u'Серия: {}'.format(data[0])
                self.create_line(title=label, params={}, anime_id=self.params['id'], cover=self.params['node'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            html = self.network.get_html(self.site_url, self.create_post())

            cover = html[html.find('poster":"')+9:html.find('","status')]
            data_array = html[html.find('[{"id"')+2:].split('},{')

            for data in data_array:
                torrent_id = data[data.find(':')+1:data.find(',')]
                leechers = data[data.find('leechers":')+10:data.find(',"seeders')]
                seeders = data[data.find('seeders":')+9:data.find(',"completed')]            
                quality = data[data.find('quality":"')+10:data.find('","series')]
                series = data[data.find('series":"')+9:data.find('","size')]

                torrent_size = data[data.find('size":')+6:data.find(',"url')]
                torrent_size = float('{:.2f}'.format(int(torrent_size)/1024.0/1024/1024))

                label = u'Серии: {} : {} , [COLOR=F0FFD700]{} GB[/COLOR], Сидов: [COLOR=F000F000]{}[/COLOR] , Пиров: [COLOR=F0F00000]{}[/COLOR]'.format(
                    series, quality, torrent_size, seeders, leechers)
                self.create_line(title=label, params={'mode': 'torrent_part', 'param': torrent_id, 'id': self.params['id'], 'node': cover})

        if self.params['param']:
            host_site = self.site_url.replace('public/api/index.php','')

            full_url = '{}public/torrent/download.php?id={}'.format(host_site,self.params['param'])
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
                    self.create_line(title=series[i], cover=self.params['node'], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], cover=self.params['node'], params={'mode': 'play_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
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