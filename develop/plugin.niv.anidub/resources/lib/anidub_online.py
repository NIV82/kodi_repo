# -*- coding: utf-8 -*-

import os
import sys
import time
import json

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

version = xbmc.getInfoLabel('System.BuildVersion')[:2]
try:
    version = int(version)
except:
    version = 0

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

if version >= 19:
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

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.niv.anidub')

if version >= 19:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

class Anidub:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.sid_file = os.path.join(addon_data_dir, 'ado.sid')
        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()        
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=bool(addon.getSetting('online_authmode') == '1'),
            auth_status=bool(addon.getSetting('online_auth') == 'true'),
            proxy_data = self.proxy_data
            )
        self.network.auth_post_data = urlencode(
            {'login_name': addon.getSetting('online_username'),
            'login_password': addon.getSetting('online_password'),
            'login': 'submit'}
            )
        self.network.auth_url = self.site_url
        self.network.sid_file = self.sid_file
        del WebTools
#========================#========================#========================#
        self.authorization = self.create_authorization()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(addon_data_dir, 'ado.db')):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(addon_data_dir, 'ado.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = 'online_mirror_{}'.format(addon.getSetting('online_mirrormode'))

        if not addon.getSetting(current_mirror):
            site_url = addon.getSetting('online_mirror_0')
        else:
            site_url = addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_authorization(self):
        if '0' in addon.getSetting('online_authmode'):
            return False

        if not addon.getSetting('ado_username') or not addon.getSetting('ado_password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(
                heading='Авторизация', message='Введите Логин и Пароль', icon=icon, time=3000, sound=False)
            return

        try:
            temp_session = float(addon.getSetting('online_session'))
        except:
            temp_session = 0
        
        if time.time() - temp_session > 86400:
            addon.setSetting('online_session', str(time.time()))
            try:
                os.remove(self.sid_file)
            except:
                pass            
            addon.setSetting('online_auth', 'false')
        
        authorization = self.network.auth_check()
        
        if not authorization:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(
                heading='Авторизация', message='Проверьте Логин и Пароль', icon=icon, time=3000, sound=False)
            return
        else:
            addon.setSetting('online_auth', str(authorization).lower())

        return authorization
#========================#========================#========================#
    def create_proxy_data(self):
        if '0' in addon.getSetting('online_unblock'):
            return None

        if '1' in addon.getSetting('online_unblock'):
            proxy_data = {'https': addon.getSetting('online_unblock_1')}
            return proxy_data

        try:
            proxy_time = float(addon.getSetting('online_proxytime'))
        except:
            proxy_time = 0

        pac_url = addon.getSetting('online_unblock_2')
        import network

        if time.time() - proxy_time > 604800:
            addon.setSetting('online_proxytime', str(time.time()))

            content = network.get_web(url=pac_url, bytes=False)

            proxy = content[content.find('PROXY ')+6:]
            proxy = proxy[:proxy.find(';')]
            proxy = proxy.strip()

            addon.setSetting('online_proxy', proxy)
            proxy_data = {'https': proxy}

        else:
            if addon.getSetting('online_proxy'):
                proxy_data = {'https': addon.getSetting('online_proxy')}
            else:
                content = network.get_web(url=pac_url, bytes=False)

                proxy = content[content.find('PROXY ')+6:]
                proxy = proxy[:proxy.find(';')]
                proxy = proxy.strip()

                addon.setSetting('online_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def create_context(self, anime_id, hash=None, title=None):
        context_menu = []
        # if title:
        #     if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
        #         if '/' in title:
        #             title = title[:title.find('/')].strip()
        #         context_menu.append(('Искать на Торрент Трекере', 'Container.Update("plugin://plugin.niv.anidub/?mode=search_part&param=search_string&search_string={}&portal=anidub_t")'.format(title)))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.anidub/?mode=clean_part")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('Обновить аниме', 'Container.Update("plugin://plugin.niv.anidub/?mode=update_anime_part&id={}")'.format(anime_id)))

        # if self.authorization and hash:
        #     if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
        #         context_menu.append(('Избранное - Добавить', 'Container.Update("plugin://plugin.niv.anidub/?mode=favorites_part&param=plus&id={}&hash={}")'.format(anime_id,hash)))
        #         context_menu.append(('[COLOR=cyan]Избранное - Удалить', 'Container.Update("plugin://plugin.niv.anidub/?mode=favorites_part&param=minus&id={}&hash={}")'.format(anime_id,hash)))
        
        context_menu.append(('Обновить Базу Данных', 'Container.Update("plugin://plugin.niv.anidub/?mode=update_file_part")'))
        context_menu.append(('Обновить Авторизацию', 'Container.Update("plugin://plugin.niv.anidub/?mode=update_authorization")'))
        context_menu.append(('Обновить Прокси', 'Container.Update("plugin://plugin.niv.anidub/?mode=update_proxy_data")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title, anime_id=None, params={}, folder=True, online=None, hash=None, **info):
        li = xbmcgui.ListItem(title)

        if info:
            try:
                cover = info.pop('cover')
            except:
                cover = None

            try:
                info['title'] = info['sorttitle']
                info['tvshowtitle'] = info['sorttitle']
            except:
                pass

            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})

            if version == 20:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setTitle(info['title'])
                #videoinfo.setSortTitle(info['sorttitle'])
                videoinfo.setYear(int(info['year']))
                videoinfo.setGenres(info['genre'])
                videoinfo.setPlot(info['plot'])
                #videoinfo.setRating(float(info['rating']))
                videoinfo.setStudios([info['studio']])
                videoinfo.setWriters(info['writer'])
                videoinfo.setDirectors(info['director'])
            else:
                li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id, hash, title))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online:
            url = online

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
        return
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        from utility import clean_tags
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        html = self.network.get_html(url=url)

        info = {
            'anime_id': '', 'anime_tid': '', 'title_ru': '', 'title_en': '', 'title_jp': '', 'kind': '', 'status': '', 
            'episodes': 0, 'aired_on': 0, 'released_on': 0, 'rating': '', 'duration': 0, 'genres': '', 'writer': '', 
            'director': '', 'description': '', 'dubbing': '', 'translation': '', 'timing': '', 'sound': '', 
            'mastering': '', 'editing': '', 'other': '', 'country': '', 'studios': '', 'image': ''
            }

        data = html[html.find('<h1>'):]
        data = data[:data.find('fplayer tabs-box')]

        info['anime_id'] = anime_id

        if u'Описание</div>' in data:
            description = data[data.find('text clearfix">')+15:]
            #description = description[:description.find('<div class="frates fx-row">')]
            description = description[:description.find('</div>')]
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

        if '<a href="#">' in data:
            country = data[data.find('<a href="#">')+12:]
            country = country[country.find('<span>')+6:]
            country = country[:country.find('</span>')]
            country = clean_tags(country)
            info['country'] = u'{}'.format(country.strip())
            del country

        if u'Жанр:</span>' in data:
            genres = data[data.find(u'Жанр:</span>')+12:]
            genres = genres[:genres.find('</li>')]
            genres = clean_tags(genres)
            genres = genres.lower()
            info['genres'] = u'{}'.format(genres.strip())
            
        if u'Автор оригинала:</span>' in data:
            writer = data[data.find(u'Автор оригинала:</span>')+23:]
            writer = writer[:writer.find('</li>')]
            writer = clean_tags(writer)
            info['writer'] = u'{}'.format(writer.strip())
            del writer

        if u'Режиссёр:</span>' in data:
            director = data[data.find(u'Режиссёр:</span>')+16:]
            director = director[:director.find('</li>')]
            director = clean_tags(director)
            info['director'] = u'{}'.format(director.strip())
            del director

        if u'Студия:</span>' in data:
            studios = data[data.find(u'Студия:</span>')+14:]
            studios = studios[:studios.find('</li>')]
            studios = clean_tags(studios)
            info['studios'] = u'{}'.format(studios.strip())
            del studios

        if update:
            self.database.update_content(info)
        else:
            self.database.insert_content(info)
    
        return 
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    def exec_update_authorization(self):
        addon.setSetting('online_auth', 'false')
        addon.setSetting('online_session', '')

        from network import WebTools
        self.network = WebTools(
            auth_usage=True,
            auth_status=False,
            proxy_data = self.proxy_data
            )

        self.network.auth_post_data = urlencode({
            'login_name': addon.getSetting('ado_username'),
            'login_password': addon.getSetting('ado_password'),
            'login': 'submit'})
        
        self.network.auth_url = self.site_url
        self.network.sid_file = self.sid_file
        del WebTools

        self.create_authorization()
        return
#========================#========================#========================#
    def exec_update_proxy_data(self):
        addon.setSetting('online_proxy', '')
        addon.setSetting('online_proxytime', '')

        self.create_proxy_data()
        return
#========================#========================#========================#
    def exec_update_anime_part(self):        
        self.create_info(anime_id=self.params['id'], update=True)
        return
#========================#========================#========================#
    def exec_update_file_part(self):
        try:
            self.database.end()
        except:
            pass
            
        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ado.db'
        target_path = os.path.join(addon_data_dir, 'ado.db')

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
            self.dialog.notification(heading='Загрузка файла',message='Успешно загружено',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Загрузка файла',message='Ошибка при загрузке',icon=icon,time=3000,sound=False)
            pass

        self.progress_bg.close()
        return
#========================#========================#========================#
    def exec_favorites_part(self):
        url = '{}engine/ajax/controller.php?mod=favorites&fav_id={}&action={}&skin=kinolife-blue&alert=1&user_hash={}'.format(
            self.site_url, self.params['id'], self.params['param'], self.params['hash'])

        result = self.network.get_html(url=url)

        if u'успешно добавлена' in result:
            self.dialog.notification(heading='Избранное',message='Добавлено',icon=icon,time=3000,sound=False)
        elif u'успешно убрана' in result:
            self.dialog.notification(heading='Избранное',message='Удалено',icon=icon,time=3000,sound=False)
        else:
            self.dialog.notification(heading='Избранное',message='Ошибка',icon=icon,time=3000,sound=False)
        
        return
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('online_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=3000,sound=False)
            pass
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=u'[B]Поиск[/B]', params={'mode': 'search_part'})
        if self.authorization:
            self.create_line(title=u'[B]Избранное[/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title=u'[B]Аниме[/B]', params={'mode': 'common_part'})
        self.create_line(title=u'[B]Аниме ТВ[/B]', params={'mode': 'common_part', 'param': 'anime_tv/'})
        self.create_line(title=u'[B]Аниме Фильмы[/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title=u'[B]Аниме OVA[/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title=u'[B]Аниме ONA[/B]', params={'mode': 'common_part', 'param': 'anime_ona/'})
        self.create_line(title=u'[B]Аниме Онгоинг[/B]', params={'mode': 'common_part', 'param': 'anime_ongoing/'})
        self.create_line(title=u'[B]Многосерийный Сёнэн[/B]', params={'mode': 'common_part', 'param': 'shonen/'})
        self.create_line(title=u'[B]Завершенные сериалы[/B]', params={'mode': 'common_part', 'param': 'full/'})
        self.create_line(title=u'[B]Незавершенные сериалы[/B]', params={'mode': 'common_part', 'param': 'unclosed/'})
        self.create_line(title=u'[B]Японские Дорамы[/B]', params={'mode': 'common_part', 'param': 'japan_dorama/'})
        self.create_line(title=u'[B]Корейские Дорамы[/B]', params={'mode': 'common_part', 'param': 'korea_dorama/'})
        self.create_line(title=u'[B]Китайские Дорамы[/B]', params={'mode': 'common_part', 'param': 'china_dorama/'})
        self.create_line(title=u'[B]Дорамы[/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = addon.getSetting('online_search').split('|')
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
                
                data_array = addon.getSetting('online_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                addon.setSetting('online_search', data_array)
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
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            if not '<div class="th-item">' in html and not '<div class="sect ignore' in html:
                self.create_line(title=u'Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
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

            self.progress_bg.create('AniDub', 'Инициализация')

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

                            if not 'https://' in anime_cover:
                                if not 'http://' in anime_cover:
                                    anime_cover = u'{}{}'.format(self.site_url, anime_cover[1:])

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

                            anime_title = anime_title
                            if '/' in anime_title:
                                anime_title = anime_title[:anime_title.find('/')]
                            anime_title = anime_title.strip()

                            self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))

                            if not self.database.anime_in_db(anime_id):
                                self.create_info(anime_id)

                            info = self.database.obtain_content(anime_id)

                            info['cover'] = anime_cover
                            info['sorttitle'] = anime_title
                            info_data = json.dumps(info)

                            label = u'{}{}'.format(anime_title, anime_series)
                            #self.create_line(title=label, anime_id=anime_id, cover=anime_cover, hash=user_hash, params={'mode': 'select_part', 'id': anime_id})
                            self.create_line(title=label, anime_id=anime_id, hash=user_hash, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                        except:
                            self.create_line(title=u'Ошибка обработки строки - сообщите автору')
            except:
                self.create_line(title=u'Ошибка обработки блока - сообщите автору')

            self.progress_bg.close()

            if navigation.isdigit() and int(self.params['page']) < int(navigation):
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': 'search_part', 'param': 'search_string', 'search_string': self.params['search_string'], 'page': int(self.params['page']) + 1})

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        #xbmc.executebuiltin('Dialog.Close(busydialog)', wait=True)

        url = '{}{}page/{}/'.format(self.site_url, quote(self.params['param']), self.params['page'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<div class="th-item">' in html and not '<div class="sect ignore' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
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

        self.progress_bg.create('AniDub', 'Инициализация')

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
                        
                        if not 'https://' in anime_cover:
                            if not 'http://' in anime_cover:
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

                        anime_title = anime_title
                        if '/' in anime_title:
                            anime_title = anime_title[:anime_title.find('/')]
                        anime_title = anime_title.strip()

                        self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))

                        if not self.database.anime_in_db(anime_id):
                            self.create_info(anime_id)

                        info = self.database.obtain_content(anime_id)

                        info['cover'] = anime_cover
                        info['sorttitle'] = anime_title
                        info_data = json.dumps(info)

                        label = u'{}{}'.format(anime_title, anime_series)
                        self.create_line(title=label, anime_id=anime_id, hash=user_hash, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                    except:
                        self.create_line(title=u'Ошибка обработки строки - сообщите автору')
        except:
            self.create_line(title=u'Ошибка обработки блока - сообщите автору')

        self.progress_bg.close()
        
        if navigation.isdigit() and int(self.params['page']) < int(navigation):
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        info = json.loads(self.params['param'])
        url = '{}index.php?newsid={}'.format(self.site_url, self.params['id'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<div class="fthree tabs-box">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
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
            self.create_line(title=video_title, params={'mode': 'play_part', 'param': video_url, 'id': self.params['id']}, folder=False, **info)

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_play_part(self):
        url = '{}'.format(self.params['param'])
        html = self.network.get_html(url=url)

        if not html:
            self.dialog.notification(heading='Видео Ссылка', message='Ошибка получения данных', icon=icon, time=3000, sound=False)

        if not 'player.src' in html:
            self.dialog.notification(heading='Видео Ссылка', message='Контент отсутствует', icon=icon, time=3000, sound=False)

        if 'class=videostatus><p>' in html:            
            status = html[html.find('class=videostatus><p>')+21:html.find('</p></div><script')]
            label = '[ {} ]'.format(status.replace('.',''))
            self.dialog.notification(heading='Видео Ссылка', message=label, icon=icon, time=3000, sound=False)

        if 'player.src' in html:
            video_src = html[html.find('player.src([{src: "')+19:html.find(';player.persistvolume')]
            video_src = video_src[:video_src.find('"')]

            play_url = 'https://video.sibnet.ru{}|referer={}'.format(video_src, url)

            li = xbmcgui.ListItem(path=play_url)            
            xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
def start():
    anidub = Anidub()
    anidub.execute()