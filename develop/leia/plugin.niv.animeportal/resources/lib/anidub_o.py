# -*- coding: utf-8 -*-

import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

if sys.version_info.major > 2:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Anidub:
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon = xbmcaddon.Addon(id='plugin.niv.animeportal')

        if sys.version_info.major > 2:
            self.addon_data_dir = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
            self.icon = xbmcvfs.translatePath(self.addon.getAddonInfo('icon'))
            self.fanart = xbmcvfs.translatePath(self.addon.getAddonInfo('fanart'))
        else:
            from utility import fs_enc
            self.addon_data_dir = fs_enc(xbmc.translatePath(self.addon.getAddonInfo('profile')))
            self.icon = fs_enc(xbmc.translatePath(self.addon.getAddonInfo('icon')))
            self.fanart = fs_enc(xbmc.translatePath(self.addon.getAddonInfo('fanart')))

        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.database_dir = os.path.join(self.addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.cookie_dir = os.path.join(self.addon_data_dir, 'cookie')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'portal': 'anidub_o'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = self.exec_proxy_data()
        self.site_url = self.create_site_url()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=bool(self.addon.getSetting('anidub_auth_online') == '1'),
            auth_status=bool(self.addon.getSetting('anidub_o_auth') == 'true'),
            proxy_data = self.proxy_data,
            portal='anidub_o')
        self.network.auth_post_data = urlencode(
            {'login_name': self.addon.getSetting('anidub_o_username'),
            'login_password': self.addon.getSetting('anidub_o_password'),
            'login': 'submit'}
            )

        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anidub_o.sid')
        del WebTools
#========================#========================#========================#
        self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_anidub_o.db')):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_anidub_o.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = 'anidub_o_mirror_{}'.format(self.addon.getSetting('anidub_o_mirror_mode'))

        if not self.addon.getSetting(current_mirror):
            site_url = self.addon.getSetting('anidub_o_mirror_0')
        else:
            site_url = self.addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_context(self, anime_id, hash=None, title=None):
        context_menu = []
        if title:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                if '/' in title:
                    title = title[:title.find('/')].strip()
                context_menu.append((u'[COLOR=lime]Искать на Торрент Трекере[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=search_part&param=search_string&search_string={}&portal=anidub_t")'.format(title)))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append((u'Очистить историю поиска', u'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub_o")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append((u'Обновить аниме', u'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anidub_o")'.format(anime_id)))

        if self.authorization and hash:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append((u'[COLOR=cyan]Избранное - Добавить[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&param=plus&id={}&hash={}&portal=anidub_o")'.format(anime_id,hash)))
                context_menu.append((u'[COLOR=cyan]Избранное - Удалить[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&param=minus&id={}&hash={}&portal=anidub_o")'.format(anime_id,hash)))
        
        context_menu.append((u'[COLOR=darkorange]Обновить Базу Данных[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=anidub_o")'))
        context_menu.append((u'[COLOR=darkorange]Обновить Авторизацию[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=update&portal=anidub_o")'))
        context_menu.append((u'[COLOR=darkorange]Обновить Прокси[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=anidub_o")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params={}, info={}, anime_id=None, folder=True, online=None, hash=None):
        li = xbmcgui.ListItem(title)

        if cover:
            li.setArt({'icon': cover,'thumb': cover,'poster': cover})

        if anime_id:
            info.update(self.database.obtain_content(anime_id))
            info.update({'title':title, 'tvshowtitle':title})

            extended_info = self.database.extend_content(anime_id)
            info['plot'] = u'{}\n{}'.format(info['plot'], extended_info)

        li.setInfo(type='video', infoLabels=info)
        li.addContextMenuItems(self.create_context(anime_id, hash, title))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        from utility import clean_tags
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
    def exec_authorization_part(self):
        if '0' in self.addon.getSetting('anidub_auth_online'):
            return False

        if not self.addon.getSetting('anidub_o_username') or not self.addon.getSetting('anidub_o_password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(
                heading='Авторизация', message='Введите Логин и Пароль', icon=self.icon, time=3000, sound=False)
            return

        if 'update' in self.params['param']:
            self.addon.setSetting('anidub_o_auth', 'false')
            self.addon.setSetting('anidub_o_session', '')
            
        try:
            temp_session = float(self.addon.getSetting('anidub_o_session'))
        except:
            temp_session = 0
        
        if time.time() - temp_session > 86400:
            self.addon.setSetting('anidub_o_session', str(time.time()))
            try:
                os.remove(os.path.join(self.cookie_dir, 'anidub_o.sid'))
            except:
                pass            
            self.addon.setSetting('anidub_o_auth', 'false')
        
        authorization = self.network.auth_check()


        if not authorization:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(
                heading='Авторизация', message='Проверьте Логин и Пароль', icon=self.icon, time=3000, sound=False)
            return
        else:
            self.addon.setSetting('anidub_o_auth', str(authorization).lower())

        return authorization
#========================#========================#========================#
    def exec_proxy_data(self):
        if '0' in self.addon.getSetting('anidub_o_unblock'):
            return None

        if 'renew' in self.params['param']:
            self.addon.setSetting('anidub_o_proxy', '')
            self.addon.setSetting('anidub_o_proxy_time', '')

        try:
            proxy_time = float(self.addon.getSetting('anidub_o_proxy_time'))
        except:
            proxy_time = 0

        if time.time() - proxy_time > 604800:
            self.addon.setSetting('anidub_o_proxy_time', str(time.time()))
            proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()

            try:
                proxy_pac = str(proxy_pac, encoding='utf-8')
            except:
                pass

            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('anidub_o_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('anidub_o_proxy'):
                proxy_data = {'https': self.addon.getSetting('anidub_o_proxy')}
            else:
                proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()
                
                try:
                    proxy_pac = str(proxy_pac, encoding='utf-8')
                except:
                    pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('anidub_o_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_file_part(self):
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
    def exec_favorites_part(self):
        url = '{}engine/ajax/controller.php?mod=favorites&fav_id={}&action={}&skin=kinolife-blue&alert=1&user_hash={}'.format(
            self.site_url, self.params['id'], self.params['param'], self.params['hash'])

        result = self.network.get_html(url=url)

        if u'успешно добавлена' in result:
            self.dialog.notification(heading='Избранное',message='Добавлено',icon=self.icon,time=3000,sound=False)
        elif u'успешно убрана' in result:
            self.dialog.notification(heading='Избранное',message='Удалено',icon=self.icon,time=3000,sound=False)
        else:
            self.dialog.notification(heading='Избранное',message='Ошибка',icon=self.icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('anidub_o_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=self.icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=self.icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=u'[B][COLOR=red]Поиск[/COLOR][/B]', params={'mode': 'search_part'})
        if self.authorization:
            self.create_line(title=u'[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
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

            data_array = self.addon.getSetting('anidub_o_search').split('|')
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
                
                data_array = self.addon.getSetting('anidub_o_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                self.addon.setSetting('anidub_o_search', data_array)
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

            user_hash = None
            if self.authorization:
                user_hash = html[html.find('dle_login_hash'):]
                user_hash = user_hash[user_hash.find('\'')+1:]
                user_hash = user_hash[:user_hash.find('\'')]

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
                            self.create_line(title=label, anime_id=anime_id, cover=anime_cover, hash=user_hash, params={'mode': 'select_part', 'id': anime_id})
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

        user_hash = None
        if self.authorization:
            user_hash = html[html.find('dle_login_hash'):]
            user_hash = user_hash[user_hash.find('\'')+1:]
            user_hash = user_hash[:user_hash.find('\'')]

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
                                anime_cover = u'{}{}'.format(self.site_url, anime_cover[1:])

                        anime_id = anime_url[anime_url.rfind('/')+1:anime_url.find('-')]

                        anime_title = data[data.find('<div class="th-title">')+22:]
                        anime_title = anime_title[:anime_title.find('</div>')]
                        anime_title = unescape(anime_title)

                        if '[' in anime_title:
                            anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                            anime_series = u' | [COLOR=gold]{}[/COLOR]'.format(anime_series)
                            anime_title = anime_title[:anime_title.rfind('[')]
                            if '[' in anime_title:
                                anime_form = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                                anime_series = u' | [COLOR=gold]{}[/COLOR]{}'.format(anime_form, anime_series)
                                anime_title = anime_title[:anime_title.rfind('[')]
                                del anime_form
                        else:
                            anime_series = ''

                        if self.progress.iscanceled():
                            return
                        self.progress.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))

                        if not self.database.anime_in_db(anime_id):
                            self.create_info(anime_id)

                        label = u'{}{}'.format(anime_title, anime_series)
                        self.create_line(title=label, anime_id=anime_id, cover=anime_cover, hash=user_hash, params={'mode': 'select_part', 'id': anime_id})
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

        for video_title, video_url in sorted(series.items(), key=lambda item: item[1]):
            self.create_line(title=video_title, params={'mode': 'online_part', 'param': video_url, 'id': self.params['id']})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if self.proxy_data:
            del self.network
            from network import WebTools
            self.network = WebTools(auth_usage=False, auth_status=False)
            del WebTools

        if self.params['param']:
            url = '{}'.format(self.params['param'])
            html = self.network.get_html(url=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            if not 'player.src' in html:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

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