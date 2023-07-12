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
    from urllib.parse import quote_plus
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape  

handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
xbmcplugin.setContent(handle, 'tvshows')

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

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'portal': 'anidub'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = self.exec_proxy_data()
        self.site_url = addon.getSetting('adt_mirror0')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=bool(addon.getSetting('adt_authmode') == '1'),
            auth_status=bool(addon.getSetting('adt_auth') == 'true'),
            proxy_data = self.proxy_data,
            portal='anidub')
        self.network.auth_post_data = urlencode(
            {'login_name': addon.getSetting('adt_username'),
            'login_password': addon.getSetting('adt_password'),
            'login': 'submit'}
            )
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(addon_data_dir, 'adt.sid')
        del WebTools
#========================#========================#========================#
        self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(addon_data_dir, 'adt.db')):
            self.exec_update_file_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(addon_data_dir, 'adt.db'))
        del DataBase
#========================#========================#========================#
    def create_context(self, anime_id, title=None):
        context_menu = []
        
        if title:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                if '/' in title:
                    title = title[:title.find('/')].strip()
                context_menu.append((u'[COLOR=lime]Искать на Online Сайте[/COLOR]', u'Container.Update("plugin://plugin.niv.animeportal/?mode=search_part&param=search_string&search_string={}&portal=anidub_o")'.format(title)))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anidub")'))

        if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
            context_menu.append(('Обновить аниме', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=anidub")'.format(anime_id)))

        if self.authorization:
            if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
                context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&param=plus&id={}&portal=anidub")'.format(anime_id)))
                context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&param=minus&id={}&portal=anidub")'.format(anime_id)))

        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=anidub")'))
        context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=update&portal=anidub")'))
        context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=anidub")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title, anime_id=None, params={}, folder=True, **info):
        li = xbmcgui.ListItem(title)

        if info:
            if anime_id:
                extended_info = self.database.extend_content(anime_id)
                info['plot'] = u'{}\n{}'.format(info['plot'], extended_info)

            try:
                cover = info.pop('cover')
            except:
                cover = None

            try:
                info['title'] = info['sorttitle']
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
                videoinfo.setRating(float(info['rating']))

                videoinfo.setStudios([info['studio']])
                videoinfo.setWriters(info['writer'])
                videoinfo.setDirectors(info['director'])
            else:
                li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id, title))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']

        if 'tam' in params:
            label = u'{} | {}'.format(info['title'], title)

            if version <= 18:
                try:
                    label = label.encode('utf-8')
                except:
                    pass

            info_data = repr({'title':label})
            url='plugin://plugin.video.tam/?mode=open&info={}&url={}'.format(quote_plus(info_data), quote(params['tam']))
        else:
            url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, update=False):
        url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
        html = self.network.get_html(url=url)

        info = {
            'anime_id': '', 'anime_tid': '', 'title_ru': '', 'title_en': '', 'title_jp': '', 'kind': '', 'status': '', 
            'episodes': 0, 'aired_on': 0, 'released_on': 0, 'rating': '', 'duration': 0, 'genres': '', 'writer': '', 
            'director': '', 'description': '', 'dubbing': '', 'translation': '', 'timing': '', 'sound': '', 
            'mastering': '', 'editing': '', 'other': '', 'country': '', 'studios': '', 'image': ''
            }

        from utility import clean_tags
        
        data = html[html.find('<div class="xfinfodata">')+24:html.find('<div class="story_b clr')]

        info['anime_id'] = anime_id

        if u'Год:' in data:
            aired_on = data[data.find(u'Год:'):]
            aired_on = aired_on[aired_on.find('/xfsearch/')+10:]
            aired_on = aired_on[:aired_on.find('/')]
                                    
            try:
                aired_on = int(aired_on)
            except:
                aired_on = 0
            info['aired_on'] = aired_on

        if u'Жанр:' in data:
            genres = data[data.find('itemprop="genre">')+17:]
            genres = genres[:genres.find('</span><br>')]
            genres = clean_tags(genres)
            info['genres'] = u'{}'.format(genres)

        if u'Страна:' in data:
            country = data[data.find(u'Страна:')+7:]
            country = country[:country.find('</span>')]
            country = clean_tags(country)
            info['country'] = u'{}'.format(country)

        if u'Режиссер:' in data:
            director = data[data.find(u'Режиссер:')+9:]
            director = director[:director.find('</span>')]
            director = clean_tags(director)
            info['director'] = u'{}'.format(director)

        if u'Сценарист:' in data:
            writer = data[data.find(u'Сценарист:')+10:]
            writer = writer[:writer.find('</span>')]
            writer = clean_tags(writer)
            info['writer'] = u'{}'.format(writer)

        if u'Озвучивание:' in data:
            dubbing = data[data.find(u'Озвучивание:')+12:]
            dubbing = dubbing[:dubbing.find('</span>')]
            dubbing = clean_tags(dubbing)
            info['dubbing'] = u'{}'.format(dubbing)

        if u'Перевод:' in data:
            translation = data[data.find(u'Перевод:')+8:]
            translation = translation[:translation.find('</span>')]
            translation = clean_tags(translation)
            info['translation'] = u'{}'.format(translation)

        if u'Тайминг и работа со звуком:' in data:
            timing = data[data.find(u'Тайминг и работа со звуком:')+27:]
            timing = timing[:timing.find('</span>')]
            timing = clean_tags(timing)
            info['timing'] = u'{}'.format(timing)

        if u'Студия:' in data:
            studios = data[data.find(u'Студия:'):]
            studios = studios[studios.find('alt="')+5:]
            studios = studios[:studios.find('"')]
            info['studios'] = u'{}'.format(studios)

        if u'Описание:' in data:
            description = data[data.find(u'Описание:')+9:]
            if '<br/>' in description:
                description = description[:description.find('<br/>')]
            if '<!--dle_spoiler' in description:
                description = description[:description.find('<!--dle_spoiler')]
            if '<!--/colorstart-->' in description:
                description = description[:description.find('<!--/colorstart-->')]

            description = description.replace('<br />', '\n')
            description = unescape(description)
            description = clean_tags(description)
            info['description'] = u'{}'.format(description)

        if update:
            self.database.update_content(info)
        else:
            self.database.insert_content(info)

        return 
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try:
            self.database.end()
        except:
            pass
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    def exec_authorization_part(self):
        if '0' in addon.getSetting('adt_authmode'):
            return False

        if not addon.getSetting('adt_username') or not addon.getSetting('adt_password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(
                heading='Авторизация', message='Введите Логин и Пароль', icon=icon, time=3000, sound=False)
            return

        if 'update' in self.params['param']:
            addon.setSetting('adt_auth', 'false')
            addon.setSetting('adt_session', '')
            
        try:
            temp_session = float(addon.getSetting('adt_session'))
        except:
            temp_session = 0
        
        if time.time() - temp_session > 86400:
            addon.setSetting('adt_session', str(time.time()))
            try:
                os.remove(os.path.join(addon_data_dir, 'adt.sid'))
            except:
                pass            
            addon.setSetting('adt_auth', 'false')
        
        authorization = self.network.auth_check()

        if not authorization:
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(
                heading='Авторизация', message='Проверьте Логин и Пароль', icon=icon, time=3000, sound=False)
            return
        else:
            addon.setSetting('adt_auth', str(authorization).lower())

        return authorization
#========================#========================#========================#
    def exec_proxy_data(self):
        if '0' in addon.getSetting('adt_unblock'):
            return None

        if 'renew' in self.params['param']:
            addon.setSetting('adt_proxy', '')
            addon.setSetting('adt_proxytime', '')

        try:
            proxy_time = float(addon.getSetting('adt_proxytime'))
        except:
            proxy_time = 0

        if time.time() - proxy_time > 604800:
            addon.setSetting('adt_proxytime', str(time.time()))
            proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()

            try:
                proxy_pac = str(proxy_pac, encoding='utf-8')
            except:
                pass

            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            addon.setSetting('adt_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if addon.getSetting('adt_proxy'):
                proxy_data = {'https': addon.getSetting('adt_proxy')}
            else:
                proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()
                
                try:
                    proxy_pac = str(proxy_pac, encoding='utf-8')
                except:
                    pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                addon.setSetting('adt_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
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
            
        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/adt.db'
        target_path = os.path.join(addon_data_dir, 'adt.db')

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
#========================#========================#========================#
    def exec_favorites_part(self):
        url = 'https://tr.anidub.com/engine/ajax/favorites.php?fav_id={}&action={}&size=small&skin=Anidub'.format(self.params['id'], self.params['param'])

        result = self.network.get_html(url=url)

        if 'minus' in result:
            self.dialog.notification(heading='Избранное',message='Добавлено',icon=icon,time=3000,sound=False)
        elif 'plus' in result:
            self.dialog.notification(heading='Избранное',message='Удалено',icon=icon,time=3000,sound=False)
        else:
            self.dialog.notification(heading='Избранное',message='Ошибка',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('adt_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B]Поиск[/B]', params={'mode': 'search_part'})
        if self.authorization:
           self.create_line(title='[B]Избранное[/B]', params={'mode': 'common_part', 'param':'favorites/'})
        self.create_line(title='[B]Популярное за неделю[/B]', params={'mode': 'popular_part'})
        self.create_line(title='[B]Новое[/B]', params={'mode': 'common_part'})
        self.create_line(title='[B]TV Онгоинги[/B]', params={'mode': 'common_part', 'param': 'anime_tv/anime_ongoing/'})
        self.create_line(title='[B]TV 100+[/B]', params={'mode': 'common_part', 'param': 'anime_tv/shonen/'})
        self.create_line(title='[B]TV Законченные[/B]', params={'mode': 'common_part', 'param': 'anime_tv/full/'})
        self.create_line(title='[B]Аниме OVA[/B]', params={'mode': 'common_part', 'param': 'anime_ova/'})
        self.create_line(title='[B]Аниме фильмы[/B]', params={'mode': 'common_part', 'param': 'anime_movie/'})
        self.create_line(title='[B]Дорамы[/B]', params={'mode': 'common_part', 'param': 'dorama/'})
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})
            self.create_line(title='[B]Поиск по жанрам[/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title='[B]Поиск по году[/B]', params={'mode': 'search_part', 'param': 'years'})
            self.create_line(title='[B]Поиск по алфавиту[/B]', params={'mode': 'search_part', 'param': 'alphabet'})

            data_array = addon.getSetting('adt_search').split('|')
            data_array.reverse()
            for data in data_array:
                if not data:
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': quote(data)})

        if 'genres' in self.params['param']:
            anidub_genres = ('сёнэн','романтика','драма','комедия','этти','меха','фантастика',
            'фэнтези','повседневность','школа','война','сёдзё','детектив','ужасы','история','триллер',
            'приключения','киберпанк','мистика','музыкальный','спорт','пародия','для детей','махо-сёдзё',
            'сказка','сёдзё-ай','сёнэн-ай','боевые искусства','самурайский боевик')
            for i in anidub_genres:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(i))})

        if 'years' in self.params['param']:
            for year in range(2023, 1969, -1):
                year = str(year)
                self.create_line(title='{}'.format(year), params={'mode': 'common_part', 'param': 'xfsearch/{}/'.format(quote(year))})

        if 'alphabet' in self.params['param']:
            anidub_alphabet = ('а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н',
            'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'э', 'ю', 'я')
            for i in anidub_alphabet:
                self.create_line(title='{}'.format(i), params={'mode': 'common_part', 'param': 'catalog/{}/'.format(quote(i))}) 

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                
                data_array = addon.getSetting('adt_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                addon.setSetting('adt_search', data_array)
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
            
            if not 'search_post">' in html:
                self.create_line(title=u'Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return

            self.progress_bg.create('AniDub', 'Инициализация')

            try:
                data_array = html[html.find('search_post">')+13:html.rfind('class="result-link">')]
                data_array = data_array.split('search_post">')

                for i, data in enumerate(data_array):
                    try:
                        anime_info = data[data.find('<a href="')+9:data.find('</a>')]
                        anime_url = anime_info[:anime_info.find('.html')]
                        
                        if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                            continue

                        anime_id = anime_url[anime_url.rfind('/')+1:]
                        anime_id = anime_id[:anime_id.find('-')]

                        anime_title = anime_info[anime_info.find('>')+1:]
                        anime_title = unescape(anime_title)

                        if '[' in anime_title:
                            anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                            anime_series = u' | [COLOR=gold]{}[/COLOR]'.format(anime_series)
                            anime_title = anime_title[:anime_title.rfind('[')]
                            if '[' in anime_title:
                                anime_form = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                                anime_series = u' | [COLOR=gold]{}[/COLOR]{}'.format(anime_form, anime_series)
                                anime_title = anime_title[:anime_title.rfind('[')]
                        else:
                            anime_series = ''

                        anime_title = anime_title
                        if '/' in anime_title:
                            anime_title = anime_title[:anime_title.find('/')]
                        anime_title = anime_title.strip()

                        anime_cover = data[data.rfind('<img src="')+10:]
                        anime_cover = anime_cover[:anime_cover.find('"')]
                        anime_cover = unescape(anime_cover).strip()

                        if u'рейтинг <b>' in data:
                            anime_rating = data[data.find(u'<sup>рейтинг <b>')+16:]
                            anime_rating = anime_rating[:anime_rating.find(u'из 5')]
                            try:
                                anime_rating = float(anime_rating)
                            except:
                                anime_rating = 0
                        else:
                            anime_rating = 0

                        self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))
                        
                        if not self.database.anime_in_db(anime_id):
                            self.create_info(anime_id)

                        info = self.database.obtain_content(anime_id)

                        info['cover'] = anime_cover
                        info['rating'] = anime_rating
                        info['sorttitle'] = anime_title
                        info_data = json.dumps(info)

                        label = u'{}{}'.format(anime_title, anime_series)
                        self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                    except:
                        self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки - сообщите автору[/B][/COLOR]')
            except:
                self.create_line(title=u'[COLOR=red][B]Ошибка обработки блока - сообщите автору[/B][/COLOR]')

            self.progress_bg.close()

            if '<span class="n_next rcol"><a ' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': 'search_part', 'param': 'search_string', 'search_string': self.params['search_string'], 'page': int(self.params['page']) + 1})

        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_popular_part(self):
        url = '{}'.format(self.site_url)
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        if not 'sb-light-skin">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        self.progress_bg.create('Популярное за неделю:', 'Инициализация')

        try:
            data_array = html[html.find('sb-light-skin">')+15:html.rfind('<div id="content" class="wrap">')]
            data_array = data_array.split('<li class="sb-light-skin">')
                    
            for i, data in enumerate(data_array):
                try:
                    anime_info = data[data.rfind('<a href="')+9:]
                    anime_info = anime_info[:anime_info.find('</span></a>')]

                    anime_url = anime_info[:anime_info.find('.html')]

                    if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                        continue

                    anime_id = anime_url[anime_url.rfind('/')+1:]
                    anime_id = anime_id[:anime_id.find('-')]

                    anime_title = anime_info[anime_info.rfind('>')+1:]
                    anime_title = anime_title.replace('...', '')
                    anime_title = unescape(anime_title)

                    if '[' in anime_title:
                        anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                        anime_series = u' | [COLOR=gold]{}[/COLOR]'.format(anime_series)
                        anime_title = anime_title[:anime_title.rfind('[')]
                        if '[' in anime_title:
                            anime_form = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                            anime_series = u' | [COLOR=gold]{}[/COLOR]{}'.format(anime_form, anime_series)
                            anime_title = anime_title[:anime_title.rfind('[')]
                    else:
                        anime_series = ''
                    
                    anime_title = anime_title
                    if '/' in anime_title:
                        anime_title = anime_title[:anime_title.find('/')]
                    anime_title = anime_title.strip()
                    
                    anime_cover = data[data.rfind('<img src="')+10:]
                    anime_cover = anime_cover[:anime_cover.find('"')]
                    anime_cover = unescape(anime_cover).strip()

                    if u'<sup>рейтинг' in data:
                        anime_rating = data[data.find(u'<sub>')+5:]
                        anime_rating = anime_rating[:anime_rating.find(u'из 5')]
                        try:
                            anime_rating = float(anime_rating)
                        except:
                            anime_rating = 0
                    else:
                        anime_rating = 0
                    
                    self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))
                                    
                    if not self.database.anime_in_db(anime_id):
                        self.create_info(anime_id)

                    info = self.database.obtain_content(anime_id)
                    info['cover'] = anime_cover
                    info['rating'] = anime_rating
                    info['sorttitle'] = anime_title

                    info_data = json.dumps(info)

                    label = u'{}{}'.format(anime_title, anime_series)
                
                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                except:
                    self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки - сообщите автору[/B][/COLOR]')
        except:
            self.create_line(title=u'[COLOR=red][B]Ошибка обработки блока - сообщите автору[/B][/COLOR]')

        self.progress_bg.close()
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page/{}/'.format(self.site_url, quote(self.params['param']), self.params['page'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<h2>' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        self.progress_bg.create('AniDub', 'Инициализация')

        try:
            data_array = html[html.find('<h2>')+4:html.rfind('</article>')]
            data_array = data_array.split('<h2>')

            for i, data in enumerate(data_array):
                try:
                    anime_info = data[data.find('<a href="')+9:data.find('</a>')]
                    anime_url = anime_info[:anime_info.find('.html')]
                    
                    if any(param in anime_url for param in ('/manga/','/ost/','/podcast/','/anons_ongoing/','/games/','/videoblog/','/anidub_news/')):
                        continue

                    anime_id = anime_url[anime_url.rfind('/')+1:]
                    anime_id = anime_id[:anime_id.find('-')]

                    anime_title = anime_info[anime_info.find('>')+1:]
                    anime_title = unescape(anime_title)

                    if '[' in anime_title:
                        anime_series = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                        anime_series = u' | [COLOR=gold]{}[/COLOR]'.format(anime_series)
                        anime_title = anime_title[:anime_title.rfind('[')]
                        if '[' in anime_title:
                            anime_form = anime_title[anime_title.rfind('[')+1:anime_title.rfind(']')]
                            anime_series = u' | [COLOR=gold]{}[/COLOR]{}'.format(anime_form, anime_series)
                            anime_title = anime_title[:anime_title.rfind('[')]
                    else:
                        anime_series = ''

                    anime_title = anime_title
                    if '/' in anime_title:
                        anime_title = anime_title[:anime_title.find('/')]
                    anime_title = anime_title.strip()

                    anime_cover = data[data.rfind('<img src="')+10:]
                    anime_cover = anime_cover[:anime_cover.find('"')]
                    anime_cover = unescape(anime_cover).strip()

                    if u'рейтинг <b>' in data:
                        anime_rating = data[data.find(u'<sup>рейтинг <b>')+16:]
                        anime_rating = anime_rating[:anime_rating.find(u'из 5')]
                        try:
                            anime_rating = float(anime_rating)
                        except:
                            anime_rating = 0
                    else:
                        anime_rating = 0

                    self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))
                    
                    if not self.database.anime_in_db(anime_id):
                        self.create_info(anime_id)

                    info = self.database.obtain_content(anime_id)

                    info['cover'] = anime_cover
                    info['rating'] = anime_rating
                    info['sorttitle'] = anime_title
                    info_data = json.dumps(info)

                    label = u'{}{}'.format(anime_title, anime_series)
                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                except:
                    self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки - сообщите автору[/B][/COLOR]')
        except:
            self.create_line(title=u'[COLOR=red][B]Ошибка обработки блока - сообщите автору[/B][/COLOR]')

        self.progress_bg.close()

        if '<span class="n_next rcol"><a ' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={
                'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#    
    def exec_select_part(self):
        info = json.loads(self.params['param'])
        url = 'https://tr.anidub.com/index.php?newsid={}'.format(self.params['id'])
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<div class="torrent_c">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        try:
            data_array = html[html.find('<div class="torrent_c">')+23:html.rfind(u'Управление')]
            data_array = data_array.split(u'Управление')

            for data in data_array:
                try:
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

                        label = u'[COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , [COLOR=lime]{}[/COLOR] | [COLOR=red]{}[/COLOR]'.format(size, series.upper(), seed, peer)
                        
                        url = 'https://tr.anidub.com/engine/download.php?id={}'.format(torrent_id)

                        self.create_line(title=label, params={'tam': url}, **info)
                except:
                    self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки - сообщите автору[/B][/COLOR]')
        except:
            self.create_line(title=u'[COLOR=red][B]Ошибка обработки блока - сообщите автору[/B][/COLOR]')

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
def start():
    anidub = Anidub()
    anidub.execute()