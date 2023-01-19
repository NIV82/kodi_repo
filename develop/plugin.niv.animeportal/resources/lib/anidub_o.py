# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin

if sys.version_info.major > 2:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.parse import quote
    #from urllib.parse import unquote
    
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    #from urllib import unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape  

from utility import clean_tags

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity'
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Anidub:
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.params = params
        self.addon = addon
        self.icon = icon

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        if 'true' in self.addon.getSetting('anidub_unblock'):
            self.addon.setSetting('anidub_torrents','1')
        
        self.proxy_data = self.exec_proxy_data()
        self.site_url = self.create_site_url()
        #self.sid_file = os.path.join(self.cookie_dir, 'anidub.sid')
        #self.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))
        #self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(auth_usage=False, auth_status=False, proxy_data=self.proxy_data)
        del WebTools
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_anidub_o.db')):
            self.exec_update_file_part()
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
    def create_context(self, anime_id, tid=None):
        context_menu = []
        #context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anidub")'))

        if tid:
            context_menu.append(('[COLOR=lime]Открыть TORRENT[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=torrent_part&param={}&portal=anidub")'.format(tid)))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('Обновить аниме', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anidub")'.format(anime_id)))

        # if self.authorization:
        #     if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
        #         context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anidub")'.format(anime_id)))
        #         context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anidub")'.format(anime_id)))
        
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=anidub")'))
        #context_menu.append(('[COLOR=darkorange]Загрузить Обложки[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&param=cover_set&portal=anidub")'))
        #context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=update&portal=anidub")'))
        context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=anidub")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, rating=None, params={}, info={}, anime_id=None, folder=True, online=None, tid=None):
        li = xbmcgui.ListItem(title)

        if cover:
            li.setArt({'icon': cover,'thumb': cover,'poster': cover})

        if anime_id:
            anime_info = self.database.get_anime(anime_id)

            info = {
                'genre':anime_info[7], 
                'country':anime_info[18],
                'year':anime_info[3],
                'episode':anime_info[2],
                'director':anime_info[9],
                'mpaa':anime_info[5],
                'plot':anime_info[10],
                'title':title,
                'duration':anime_info[6],
                'studio':anime_info[19],
                'writer':anime_info[8],
                'tvshowtitle':title,
                'premiered':anime_info[3],
                'status':anime_info[1],
                'aired':anime_info[3],
                'rating':rating,
                }

        li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id, tid))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        html = self.network.get_html(url=url)

        # if not data_request.status_code == requests.codes.ok:
        #     self.database.add_anime(
        #         anime_id=anime_id,
        #         title_ru='anime_id: {}'.format(anime_id),
        #         title_en='anime_id: {}'.format(anime_id)
        #         )
        #     return

        #html = data_request.text

        info = {
            'anime_id': '', 'anime_tid': '', 'title_ru': '', 'title_en': '', 'title_jp': '', 'kind': '', 'status': '', 
            'episodes': 0, 'aired_on': 0, 'released_on': 0, 'rating': '', 'duration': 0, 'genres': '', 'writer': '', 
            'director': '', 'description': '', 'dubbing': '', 'translation': '', 'timing': '', 'sound': '', 
            'mastering': '', 'editing': '', 'other': '', 'country': '', 'studios': '', 'image': ''
            }

        # image = html[html.find('<img src="')+10:]
        # image = image[:image.find('"')]

        data = html[html.find('<h1>'):]
        data = data[:data.find('fplayer tabs-box')]
        del html

        info['anime_id'] = anime_id

        # title_data = data[data.find('<h1>')+4:data.find('</h1>')]
        # if '[' in title_data:
        #     title_data = title_data[:title_data.rfind('[')]
        #     title_data = title_data.strip()
        # info['title_jp'] = u'{}'.format(title_data)
        # del title_data

        if u'Описание</div>' in data:
            description = data[data.find('text clearfix">')+15:]
            description = description[:description.find('<div class="frates fx-row">')]
            description = unescape(description)

            if '<!--spoiler_title-->' in description:
                episodes = description[description.find('<!--spoiler_title-->')+20:]
                episodes = episodes.replace('<br>','\n')
                episodes = clean_tags(episodes)
                description = description[:description.find('<!--dle_spoiler')]
            else:
                episodes = ''

            description = clean_tags(description)
            info['description'] = u'{}\n{}'.format(description, episodes).strip()
            del description, episodes

        if '<a href="#">' in data:
            aired_on = data[data.find('<a href="#">')+12:]
            aired_on = aired_on[:aired_on.find('</a>')]
            if '<' in aired_on:
                aired_on = clean_tags(aired_on)
                            
            try:
                aired_on = int(aired_on)
            except:
                aired_on = 0
            
            info['aired_on'] = aired_on
            del aired_on

        if '<a href="#">' in data:
            country = data[data.find('<a href="#">')+12:]
            country = country[country.find('<span>')+6:]
            country = country[:country.find('</span>')]
            info['country'] = u'{}'.format(country.strip())
            del country

        if u'Жанр:</span>' in data:
            genres = data[data.find(u'Жанр:</span>')+12:]
            genres = genres[:genres.find('</li>')]
            genres = genres.lower()
            info['genres'] = u'{}'.format(genres.strip())
            del genres
            
        if u'Автор оригинала:</span>' in data:
            writer = data[data.find(u'Автор оригинала:</span>')+23:]
            writer = writer[:writer.find('</li>')]
            info['writer'] = u'{}'.format(writer.strip())
            del writer

        if u'Режиссёр:</span>' in data:
            director = data[data.find(u'Режиссёр:</span>')+16:]
            director = director[:director.find('</li>')]
            info['director'] = u'{}'.format(director.strip())
            del director

        if u'Студия:</span>' in data:
            studios = data[data.find(u'Студия:</span>')+14:]
            studios = studios[:studios.find('</li>')]
            info['studios'] = u'{}'.format(studios.strip())
            del studios

        if update:
            self.database.update_content(info)
        else:
            self.database.insert_content(info)

        del data, info        
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
    def exec_proxy_data(self):
        if 'renew' in self.params['param']:
            self.addon.setSetting('{}_proxy'.format(self.params['portal']),'')
            self.addon.setSetting('{}_proxy_time'.format(self.params['portal']),'')

        if 'false' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None
        
        try:
            proxy_time = float(self.addon.getSetting('{}_proxy_time'.format(self.params['portal'])))
        except:
            proxy_time = 0

        if time.time() - proxy_time > 604800:
            self.addon.setSetting('anidub_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

            try:
                proxy_pac = str(proxy_pac, encoding='utf-8')
            except:
                pass

            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('anidub_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('anidub_proxy'):
                proxy_data = {'https': self.addon.getSetting('anidub_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
                try:
                    proxy_pac = str(proxy_pac, encoding='utf-8')
                except:
                    pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('anidub_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data

    # def exec_proxy_data(self):
    #     if 'renew' in self.params['param']:
    #         self.addon.setSetting('{}_proxy'.format(self.params['portal']),'')
    #         self.addon.setSetting('{}_proxy_time'.format(self.params['portal']),'')

    #     if 'false' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
    #         return None
        
    #     try: proxy_time = float(self.addon.getSetting('{}_proxy_time'.format(self.params['portal'])))
    #     except: proxy_time = 0
    
    #     if time.time() - proxy_time > 604800:
    #         self.addon.setSetting('{}_proxy_time'.format(self.params['portal']), str(time.time()))
    #         proxy_request = requests.get(url='http://antizapret.prostovpn.org/proxy.pac', headers=headers)

    #         if proxy_request.status_code == requests.codes.ok:
    #             proxy_pac = proxy_request.text

    #             if sys.version_info.major > 2:                    
    #                 proxy = proxy_pac[proxy_pac.rfind('return "HTTPS')+13:]
    #                 proxy = proxy[:proxy.find(';')].strip()
    #                 proxy = 'https://{}'.format(proxy)
    #             else:
    #                 proxy = proxy_pac[proxy_pac.rfind('PROXY')+5:]
    #                 proxy = proxy[:proxy.find(';')].strip()

    #             self.addon.setSetting('{}_proxy'.format(self.params['portal']), proxy)
    #             proxy_data = {'https': proxy}
    #         else:
    #             proxy_data = None
    #     else:
    #         if self.addon.getSetting('{}_proxy'.format(self.params['portal'])):
    #             proxy_data = {'https': self.addon.getSetting('{}_proxy'.format(self.params['portal']))}
    #         else:
    #             proxy_request = requests.get(url='http://antizapret.prostovpn.org/proxy.pac', headers=headers)

    #             if proxy_request.status_code == requests.codes.ok:
    #                 proxy_pac = proxy_request.text
                    
    #                 if sys.version_info.major > 2:                    
    #                     proxy = proxy_pac[proxy_pac.rfind('return "HTTPS')+13:]
    #                     proxy = proxy[:proxy.find(';')].strip()
    #                     proxy = 'https://{}'.format(proxy)
    #                 else:
    #                     proxy = proxy_pac[proxy_pac.rfind('PROXY')+5:]
    #                     proxy = proxy[:proxy.find(';')].strip()

    #                 self.addon.setSetting('{}_proxy'.format(self.params['portal']), proxy)
    #                 proxy_data = {'https': proxy}
    #             else:
    #                 proxy_data = None

    #     return proxy_data
#========================#========================#========================#
    # def exec_authorization_part(self):
    #     if '0' in self.addon.getSetting('anidub_auth_mode'):
    #         return False

    #     if not self.addon.getSetting('anidub_username') or not self.addon.getSetting('anidub_password'):
    #         self.params['mode'] = 'addon_setting'
    #         self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
    #         return

    #     if 'update' in self.params['param']:
    #         self.addon.setSetting('anidub_auth', 'false')
    #         self.addon.setSetting('anidub_session','')
            
    #     try: temp_session = float(self.addon.getSetting('anidub_session'))
    #     except: temp_session = 0
        
    #     if time.time() - temp_session > 43200:
    #         self.addon.setSetting('anidub_session', str(time.time()))            
    #         try: os.remove(self.sid_file)
    #         except: pass            
    #         self.addon.setSetting('anidub_auth', 'false')

    #     auth_post_data = {
    #         "login_name": self.addon.getSetting('anidub_username'),
    #         "login_password": self.addon.getSetting('anidub_password'),
    #         "login": "submit"
    #         }

    #     import pickle

    #     if 'true' in self.addon.getSetting('anidub_auth'):
    #         try:
    #             with open(self.sid_file, 'rb') as read_file:
    #                 self.session.cookies.update(pickle.load(read_file))
    #             auth = True
    #         except:
    #             r = requests.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data)
                
    #             if 'dle_user_id' in str(r.cookies):
    #                 with open(self.sid_file, 'wb') as write_file:
    #                     pickle.dump(r.cookies, write_file)
                        
    #                 self.session.cookies.update(r.cookies)
    #                 auth = True
    #             else:
    #                 auth = False
    #     else:
    #         r = requests.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data)
            
    #         if 'dle_user_id' in str(r.cookies):
    #             with open(self.sid_file, 'wb') as write_file:
    #                 pickle.dump(r.cookies, write_file)
                    
    #             self.session.cookies.update(r.cookies)
    #             auth = True
    #         else:
    #             auth = False

    #     if not auth:
    #         self.params['mode'] = 'addon_setting'
    #         self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=self.icon,time=5000,sound=False)
    #         return
    #     else:
    #         self.addon.setSetting('anidub_auth', str(auth).lower())

    #     return auth
#========================#========================#========================#
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_file_part(self):
        # if 'cover_set' in self.params['param']:
        #     target_url = 'http://getfile.dokpub.com/yandex/get/https://disk.yandex.ru/d/sbeL3-5VPwVs2g'
        #     target_path = os.path.join(self.images_dir, 'anidub_set.zip')
        # else:
        #     try: self.database.end()
        #     except: pass
            
        #     target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_{}.db'.format(self.params['portal'])
        #     target_path = os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))
        try:
            self.database.end()
        except:
            pass
            
        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_anidub_o.db'
        target_path = os.path.join(self.database_dir, 'ap_anidub_o.db')

        try:
            os.remove(target_path)
        except:
            pass

        self.progress_bg.create(u'Загрузка Базы Данных')

        try:                
            data = urlopen(target_url)
            chunk_size = 8192
            bytes_read = 0

            try:
                file_size = int(data.info().getheaders("Content-Length")[0])
            except:
                file_size = int(data.getheader('Content-Length'))

            with open(target_path, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    try:
                        self.progress_bg.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                    except:
                        pass
            self.dialog.notification(heading='Загрузка файла',message='Успешно загружено',icon=self.icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Загрузка файла',message='Ошибка при загрузке',icon=self.icon,time=3000,sound=False)
            pass

        self.progress_bg.close()
#========================#========================#========================#
    # def exec_favorites_part(self):        
    #     if not self.params['node']:
    #         url = '{}mylists/page/{}/'.format(self.site_url, self.params['page'])
    #         data_request = self.session.get(url=url, proxies=self.proxy_data)

    #         if not data_request.status_code == requests.codes.ok:
    #             self.create_line(title='ERROR PAGE', params={'mode': 'main_part'})
    #             xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    #             return

    #         html = data_request.text
            
    #         if not '<div class="animelist">' in html:
    #             self.create_line(title='Контент не обнаружен', params={'mode': 'main_part'})
    #             xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    #             return

    #         self.progress_bg.create('{}'.format(self.params['portal'].upper()), u'Инициализация')
            
    #         navigation = html[html.find('<div class="navigation">'):html.find('<div class="animelist">')]
    #         navigation = clean_tags(navigation).replace(' ','|')
    #         page = int(navigation[navigation.rfind('|')+1:]) if navigation else -1
            
    #         data_array = html[html.find('<div class="animelist">')+23:html.rfind('<label for="mlist">')]
    #         data_array = data_array.split('<div class="animelist">')

    #         i = 0
                
    #         for data in data_array:
    #             data = unescape(data)

    #             i = i + 1
    #             p = int((float(i) / len(data_array)) * 100)
                
    #             anime_url = data[data.find('href="')+6:]
    #             anime_url = anime_url[:anime_url.find('.html')]
    #             anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
                
    #             if 'data-src="' in data:
    #                 anime_cover = data[data.find('data-src="')+10:]
    #                 anime_cover = anime_cover[:anime_cover.find('"')].replace('thumbs/','')
    #             else:
    #                 anime_cover = data[data.find('<img src="')+10:]
    #                 anime_cover = anime_cover[:anime_cover.find('"')].replace('small/','')
                    
    #             anime_cover = unescape(anime_cover)
                
    #             series = data[data.rfind('class="upd-title">')+18:]
    #             series = series[:series.find('</a>')]
    #             series = series[series.rfind('[')+1:series.rfind(']')]

    #             anime_rating = data[data.find('div class="mlate'):]
    #             anime_rating = anime_rating[anime_rating.find('<b>')+3:anime_rating.find('</b>')].strip()
                
    #             self.progress_bg.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

    #             if not self.database.anime_in_db(anime_id):
    #                 self.create_info(anime_id)
                    
    #             label = self.create_title(anime_id, series)
    #             anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))

    #             self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})
    #         self.progress_bg.close()

    #         if page and int(self.params['page']) < page:
    #             label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
    #             self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

    #         xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    #     if 'plus' in self.params['node']:
    #         try:
    #             url = '{}mylists/'.format(self.site_url)
    #             post = {'news_id': self.params['id'], 'status_id': 3}
    #             self.session.post(url=url, data=post)
    #             xbmc.executebuiltin("Container.Refresh()")
    #             self.dialog.notification(heading='Избранное',message='Выполнено',icon=self.icon,time=3000,sound=False)
    #         except:
    #             self.dialog.notification(heading='Избранное',message='Ошибка',icon=self.icon,time=3000,sound=False)

    #     if 'minus' in self.params['node']:
    #         try:
    #             url = '{}mylists/'.format(self.site_url)
    #             post = {'news_id': self.params['id'], 'status_id': 0}
    #             self.session.post(url=url, data=post)
    #             xbmc.executebuiltin("Container.Refresh()")
    #             self.dialog.notification(heading='Избранное',message='Выполнено',icon=self.icon,time=3000,sound=False)
    #         except:
    #             self.dialog.notification(heading='Избранное',message='Ошибка',icon=self.icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('anidub_search', '')
            self.dialog.notification(heading='Поиск',message='УСПЕШНО УДАЛЕНО',icon=self.icon,time=5000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='ОШИБКА',icon=self.icon,time=5000,sound=False)
            pass
#========================#========================#========================#
    def exec_information_part(self):
        data = u'[B][COLOR=darkorange]V-1.0.1[/COLOR][/B]\n\
    - Исправлены метки просмотренного в торрента файлах'
        self.dialog.textviewer('Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=u'[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        # if self.authorization:
        #     self.create_line(title=u'[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        self.create_line(title=u'[B][COLOR=lime]Аниме[/COLOR][/B]', params={'mode': 'common_part'})
        self.create_line(title=u'[B][COLOR=lime]Аниме ТВ[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_tv/'})
        self.create_line(title=u'[B][COLOR=lime]Аниме Фильмы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title=u'[B][COLOR=lime]Аниме OVA[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title=u'[B][COLOR=lime]Аниме ONA[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ona/'})
        self.create_line(title=u'[B][COLOR=lime]Аниме Онгоинг[/COLOR][/B]', params={'mode': 'common_part', 'param': 'anime_ongoing/'})
        self.create_line(title=u'[B][COLOR=lime]Многосерийный Сёнэн[/COLOR][/B]', params={'mode': 'common_part', 'param': 'shonen/'})
        self.create_line(title=u'[B][COLOR=lime]Завершенные сериалы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'full/'})
        self.create_line(title=u'[B][COLOR=lime]Незавершенные сериалы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'unclosed/'})
        self.create_line(title=u'[B][COLOR=gold]Японские Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'japan_dorama/'})
        self.create_line(title=u'[B][COLOR=gold]Корейские Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'korea_dorama/'})
        self.create_line(title=u'[B][COLOR=gold]Китайские Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'china_dorama/'})
        self.create_line(title=u'[B][COLOR=gold]Дорамы[/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = self.addon.getSetting('anidub_search').split('|')
            data_array.reverse()

            for data in data_array:
                if not data:
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': data})

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                
                data_array = self.addon.getSetting('{}_search'.format(self.params['portal'])).split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                self.addon.setSetting('{}_search'.format(self.params['portal']), data_array)
                self.params['param'] = 'search_string'
            else:
                return False

        if 'search_string' in self.params['param']:
            if self.params['search_string'] == '':
                return False
            
            url = '{}index.php?do=search'.format(self.site_url)
            post = {
                'do': 'search', 
                'subaction': 'search', 
                'search_start': self.params['page'], 
                'full_search': '0', 
                'result_from': '1', 
                'story': quote(self.params['search_string'])
                }

            post = urlencode(post)
            html = self.network.get_html(url=url, post=post)

            if not html:
                self.create_line(title=u'Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            if not '<div class="th-item">' in html and not '<div class="sect ignore' in html:
                self.create_line(title=u'Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            navigation = html[html.find('<div class="navigation">'):]
            navigation = navigation[:navigation.find('<!--/noindex-->')]
            navigation = navigation[:navigation.rfind('</a>')]
            navigation = navigation[navigation.rfind('>')+1:]

            self.progress.create('AniDub', 'Инициализация')

            try:
                if '<div class="th-item">' in html:
                    data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
                    data_array = data_array.split('<div class="th-item">')

                    for i, data in enumerate(data_array):
                        try:
                            anime_url = data[data.find('th-in" href="')+13:data.find('.html">')]

                            if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                                continue

                            anime_cover = data[data.find('<img src="')+10:]
                            anime_cover = anime_cover[:anime_cover.find('"')]
                            anime_cover = unescape(anime_cover)

                            anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]

                            anime_title = data[data.find('<div class="th-title">')+22:]
                            anime_title = anime_title[:anime_title.find('</div>')]

                            if '[' in anime_title:
                                anime_series = anime_title[anime_title.rfind('[')+1:]
                                if ']' in anime_series:
                                    anime_series = anime_series[:anime_series.find(']')]
                                anime_series = u' | [COLOR=gold]{}[/COLOR]'.format(anime_series)
                                anime_title = anime_title[:anime_title.rfind('[')].strip()
                            else:
                                anime_series = ''

                            if self.progress.iscanceled():
                                return
                            self.progress.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))

                            if not self.database.anime_in_db(anime_id):
                                self.create_info(anime_id)

                            label = u'{}{}'.format(anime_title, anime_series)
                            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, params={'mode': 'select_part', 'id': anime_id})
                        except:
                            self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки - сообщите автору[/B][/COLOR]')
            except:
                self.create_line(title=u'[COLOR=red][B]Ошибка обработки блока - сообщите автору[/B][/COLOR]')

            # if '<div class="sect ignore' in html:
            #     data_array = html[html.find('<div class="sect ignore')+23:html.rfind('<!-- END CONTENT -->')]
            #     data_array = data_array.split('<div class="sect ignore-select fullshort cat')
                
            #     i = 0
                
            #     for data in data_array:
            #         anime_url = data[data.find('js-tip" href="')+14:data.find('.html"')]
                    
            #         if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
            #             continue

            #         anime_cover = data[data.find('data-src="')+10:]
            #         anime_cover = unescape(anime_cover[:anime_cover.find('"')])
            #         anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
            #         anime_title = data[data.find('<h2>')+4:]
            #         anime_title = anime_title[:anime_title.find('</')]
            #         anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')] if '[' in anime_title else ''
            #         anime_rating = data[data.find('tingscore">')+11:]
            #         anime_rating = anime_rating[:anime_rating.find('<')]

            #         i = i + 1
            #         p = int((float(i) / len(data_array)) * 100)
                    
            #         self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                    
            #         if not self.database.anime_in_db(anime_id):
            #             self.create_info(anime_id)

            #         label = self.create_title(anime_id, anime_series)            
            #         anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))

            #         self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})

            self.progress.close()

            if navigation.isdigit() and int(self.params['page']) < int(navigation):
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': 'search_part', 'param': 'search_string', 'search_string': self.params['search_string'], 'page': int(self.params['page']) + 1})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page/{}/'.format(self.site_url, quote(self.params['param']), self.params['page'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not '<div class="th-item">' in html and not '<div class="sect ignore' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        navigation = html[html.find('<div class="navigation">'):]
        navigation = navigation[:navigation.find('<!--/noindex-->')]
        navigation = navigation[:navigation.rfind('</a>')]
        navigation = navigation[navigation.rfind('>')+1:]

        self.progress.create('AniDub', 'Инициализация')

        try:
            if '<div class="th-item">' in html:
                data_array = html[html.find('<div class="th-item">')+21:html.rfind('<!-- END CONTENT -->')]
                data_array = data_array.split('<div class="th-item">')

                for i, data in enumerate(data_array):
                    try:
                        anime_url = data[data.find('th-in" href="')+13:data.find('.html">')]

                        if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                            continue

                        anime_cover = data[data.find('<img src="')+10:]
                        anime_cover = anime_cover[:anime_cover.find('"')]
                        anime_cover = unescape(anime_cover)
                        if not 'http:' in anime_cover:
                            if not 'https:' in anime_cover:
                                anime_cover = u'http://online.anidub.life/{}'.format(anime_cover[1:])

                        anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]

                        anime_title = data[data.find('<div class="th-title">')+22:]
                        anime_title = anime_title[:anime_title.find('</div>')]
                        anime_title = unescape(anime_title)

                        if '[' in anime_title:
                            anime_series = anime_title[anime_title.rfind('[')+1:]
                            if ']' in anime_series:
                                anime_series = anime_series[:anime_series.find(']')]
                            anime_series = u' | [COLOR=gold]{}[/COLOR]'.format(anime_series)
                            anime_title = anime_title[:anime_title.rfind('[')].strip()
                        else:
                            anime_series = ''

                        if self.progress.iscanceled():
                            return
                        self.progress.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))

                        if not self.database.anime_in_db(anime_id):
                            self.create_info(anime_id)

                        label = u'{}{}'.format(anime_title, anime_series)
                        self.create_line(title=label, anime_id=anime_id, cover=anime_cover, params={'mode': 'select_part', 'id': anime_id})
                    except:
                        self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки - сообщите автору[/B][/COLOR]')
        except:
            self.create_line(title=u'[COLOR=red][B]Ошибка обработки блока - сообщите автору[/B][/COLOR]')

        # if '<div class="sect ignore' in html:
        #     data_array = html[html.find('<div class="sect ignore')+23:html.rfind('<!-- END CONTENT -->')]
        #     data_array = data_array.split('<div class="sect ignore-select fullshort cat')
            
        #     i = 0
            
        #     for data in data_array:
        #         anime_url = data[data.find('js-tip" href="')+14:data.find('.html"')]
                
        #         if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
        #             continue

        #         anime_cover = data[data.find('data-src="')+10:]
        #         anime_cover = unescape(anime_cover[:anime_cover.find('"')])
        #         anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]
        #         anime_title = data[data.find('<h2>')+4:]
        #         anime_title = anime_title[:anime_title.find('</')]
        #         anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')] if '[' in anime_title else ''
        #         anime_rating = data[data.find('tingscore">')+11:]
        #         anime_rating = anime_rating[:anime_rating.find('<')]

        #         i = i + 1
        #         p = int((float(i) / len(data_array)) * 100)
                
        #         self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                
        #         if not self.database.anime_in_db(anime_id):
        #             self.create_info(anime_id)

        #         label = self.create_title(anime_id, anime_series)            
        #         anime_code = data_encode('{}|{}'.format(anime_id, anime_cover))

        #         self.create_line(title=label, anime_id=anime_id, cover=anime_cover, rating=anime_rating, params={'mode': 'select_part', 'id': anime_code})

        self.progress.close()
        
        if navigation.isdigit() and int(self.params['page']) < int(navigation):
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        url = '{}index.php?newsid={}'.format(self.site_url, self.params['id'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not '<div class="fthree tabs-box">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        data_array = html[html.rfind('<div class="fthree tabs-box">')+29:html.find('<iframe')]
        data_array = data_array[:data_array.rfind('</span>')]
        data_array = data_array.split('</span>')

        series = {}

        for data in data_array:
            data = data[data.find('data="')+6:]

            video_url = data[:data.find('"')]    
            if '&quot;' in video_url:
                video_url = video_url[:video_url.find('&quot;')]
            video_url = u'{}'.format(video_url)
            
            video_title = data[data.rfind('>')+1:]
            video_title = u'{}'.format(video_title)

            series.update({video_title: video_url})

        torrent_url = None
        if u'Торрент:' in html:
            torrent_url = html[html.find(u'Торрент:'):]
            torrent_url = torrent_url[torrent_url.find('<a href=')+8:]
            torrent_url = torrent_url[:torrent_url.find('target=')].replace('"','')
            torrent_url = u'{}'.format(torrent_url.strip())

        for video_title, video_url in sorted(series.items(), key=lambda item: item[1]):
            self.create_line(title=video_title, tid=torrent_url, params={'mode': 'online_part', 'param': video_url, 'id': self.params['id']})
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if self.params['param']:            
            url = '{}'.format(self.params['param'])
            html = self.network.get_html(url=url)

            if 'player.src' in html:
                video_src = html[html.find('player.src([{src: "')+19:html.find(';player.persistvolume')]
                video_src = video_src[:video_src.find('"')]

                play_url = 'https://video.sibnet.ru{}|referer={}'.format(video_src, url)

                label = 'Смотреть'

            if 'class=videostatus><p>' in html:
                status = html[html.find('class=videostatus><p>')+21:html.find('</p></div><script')]
                label = '[COLOR=red][B][ {} ][/B][/COLOR]'.format(status.replace('.',''))
                play_url = ''

            self.create_line(title=label, params={}, online=play_url, folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if self.params['param']:
            if '0' in self.addon.getSetting('anidub_torrents'):
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'true')
                self.proxy_data = self.exec_proxy_data()
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'false')
                
                del self.network
                
                from network import WebTools
                self.network = WebTools(auth_usage=False, auth_status=False, proxy_data=self.proxy_data)
                del WebTools

            #url = self.params['param']

            html = self.network.get_html(url=self.params['param'])

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            if not '<div class="torrent_c">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            data_array = html[html.find('<div class="torrent_c">')+23:html.rfind(u'Управление')]
            data_array = data_array.split(u'Управление')

            line_array = {}

            for data in data_array:
                data = data[data.find('<div id='):]
                            
                torrent_id = data[data.find('torrent_')+8:]
                torrent_id = torrent_id[:torrent_id.find('_')]

                if '<div id=\'torrent_' in data:
                    quality = data[:data.find('<div id=\'torrent_')]
                    if quality:
                        quality = data[data.find('="')+2:]
                        quality = quality[:quality.find('"')]
                    else:
                        quality = 'uknown'

                    if u'Серии в торренте:' in data:
                        series = data[data.find(u'Серии в торренте:')+17:]
                        series = series[series.find('>')+1:]
                        series = series[:series.find('<')]
                        series = u'{} - [ {} ]'.format(quality, series)
                    else:
                        series = quality

                    seed = data[data.find('li_distribute_m">')+17:]
                    seed = seed[:seed.find('<')]

                    peer = data[data.find('li_swing_m">')+12:]
                    peer = peer[:peer.find('<')]

                    size = data[data.find(u'Размер: <span class="red">')+26:]
                    size = size[:size.find('<')]

                    line_label = u'[COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , [COLOR=lime]{}[/COLOR] | [COLOR=red]{}[/COLOR]'.format(size, series.upper(), seed, peer)

                    line_array.update(
                        {torrent_id: line_label}
                    )

            # for tid, label  in line_array.items():
            #     self.create_line(title=label, params={'mode': 'torrent_part', 'node': tid} )

            if len(line_array) < 2:
                tid = list(line_array.keys())
                self.params = {'mode': 'torrent_part', 'node': tid[0], 'param':'', 'portal': 'anidub'}
                self.exec_torrent_part()
            else:
                for tid, label  in line_array.items():
                    self.create_line(title=label, params={'mode': 'torrent_part', 'node': tid} )
        else:
            if '0' in self.addon.getSetting('anidub_torrents'):
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'true')
                self.proxy_data = self.exec_proxy_data()
                self.addon.setSetting('{}_unblock'.format(self.params['portal']), 'false')
      
            url = 'https://tr.anidub.com/engine/download.php?id={}'.format(self.params['node'])

            file_name = u'anidub_{}.torrent'.format(self.params['node'])
            full_name = os.path.join(self.torrents_dir, file_name)
        
            torrent_file = self.network.get_file(url=url, destination_name=full_name)

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
                    # self.create_line(title=series[i], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'selector_part', 'index': i, 'id': file_name}, folder=False, size=size[i])
                    self.create_line(title=series[i], params={'mode': 'selector_part', 'index': i, 'id': file_name}, folder=False, info={'size':size[i]})
            else:
                #self.create_line(title=info['name'], anime_id=anime_code[0], cover=anime_code[1], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, folder=False, size=info['length'])
                self.create_line(title=info['name'], params={'mode': 'selector_part', 'index': 0, 'id': file_name}, folder=False, info={'size':size[i]})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_selector_part(self):
        torrent_url = os.path.join(self.torrents_dir, self.params['id'])
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])
        
        if '0' in self.addon.getSetting(portal_engine):
            try:
                tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver', 'torrserver_tam', 'lt2http')
                engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
                purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(torrent_url), index, engine)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=3000,sound=False)

        if '1' in self.addon.getSetting(portal_engine):
            try:
                purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=3000,sound=False)