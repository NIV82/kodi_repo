# -*- coding: utf-8 -*-

import os
import sys
#import time
import json

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

if sys.version_info.major < 3:
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urllib import urlopen
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
else:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.request import urlopen
    from urllib.parse import parse_qs
    from html import unescape

#from network import get_web

addon = xbmcaddon.Addon(id='plugin.niv.redheadsound')
handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')

if sys.version_info.major < 3:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))
    plugin_dir = fs_enc(xbmc.translatePath('special://home/addons/plugin.niv.redheadsound'))
else:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
    plugin_dir = xbmcvfs.translatePath('special://home/addons/plugin.niv.redheadsound')

try:
    xbmcaddon.Addon('inputstream.adaptive')
except:
    xbmcgui.Dialog().notification(
        heading='Установка Библиотеки - [COLOR=darkorange]inputstream.adaptive[/COLOR]',
        message='inputstream.adaptive',
        icon=None,
        time=1000,
        sound=False
        )
    xbmc.executebuiltin('RunPlugin("plugin://inputstream.adaptive")')

#xbmcplugin.setContent(handle, 'tvshows')

class RedHeadSound:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()
        
        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)
        
        self.cookie_dir = os.path.join(addon_data_dir, 'cookies')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.database_dir = os.path.join(addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.playlist_dir = os.path.join(addon_data_dir, 'playlist')
        if not os.path.exists(self.playlist_dir):
            os.mkdir(self.playlist_dir)

        self.context_menu = []
        self.params = {'mode': 'main_part', 'param': '', 'url': '', 'page': '1'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = None
        #self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()

        if os.path.exists(os.path.join(self.database_dir, 'redheadsound.db')):
            try:
                os.remove(os.path.join(self.database_dir, 'redheadsound.db'))
            except:
                pass

        if os.path.exists(os.path.join(self.database_dir, 'rhs.db')):
            try:
                os.remove(os.path.join(self.database_dir, 'rhs.db'))
            except:
                pass
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'rhs_tmdb.db')):
            self.create_database()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(proxy_data=self.proxy_data)
        del WebTools
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'rhs_tmdb.db'))
        del DataBase
#========================#========================#========================#
    def create_site_url(self):
        site_url = addon.getSetting('mirror_0')
        current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))
        current_url = addon.getSetting(current_mirror)

        if not current_url:
            return site_url
        else:
            return current_url
#========================#========================#========================#
    def create_database(self):
        try:
            self.database.end()
        except:
            pass

        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/rhs_tmdb.db'
        target_path = os.path.join(self.database_dir, 'rhs_tmdb.db')
        
        try:
            os.remove(target_path)
        except:
            pass
        
        try:
            data = urlopen(target_url)
            chunk_size = 8192
            bytes_read = 0

            if sys.version_info.major < 3:
                file_size = int(data.info().getheaders("Content-Length")[0])
            else:
                file_size = int(data.getheader('Content-Length'))

            self.progress_bg.create('Загрузка файла')
            
            try:
                with open(target_path, 'wb') as write_file:
                    while True:
                        chunk = data.read(chunk_size)
                        bytes_read = bytes_read + len(chunk)
                        write_file.write(chunk)
                        if len(chunk) < chunk_size:
                            break
                        self.progress_bg.update(int(bytes_read * 100 / file_size), 'Загружено: {} из {} MB'.format(
                            '{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
            except:
                self.dialog.notification(heading='Red Head Sound', message='Ошибка', icon=icon,time=1000,sound=False)
                pass

            self.progress_bg.close()
            
            self.dialog.notification(heading='Red Head Sound', message='Выполнено', icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='Red Head Sound', message='Ошибка', icon=icon,time=1000,sound=False)
            pass
#========================#========================#========================#
    def create_players(self, data):
        node_start = '<iframe data-src="'
        node_end = '</iframe>'

        if node_start in data:
            data = data[data.find(node_start):]

        start = data.find(node_start)
        end = data.find(node_end)

        result = []

        while start < end and start > -1:
            res = data[start:end+len(node_end)]
            data = data.replace(res, '')

            res = res[res.find('"')+1:]
            res = res[:res.find('"')]

            if 'player_mobile' in res: 
                res = res[:res.find('?player')]

                if res in result:
                    pass
                else:
                    result.append(res)
            else:
                result.append(res)

            start = data.find(node_start)
            end = data.find(node_end)
        
        players = {'redheadsound':'', 'cdnvideohub':''}

        for i in result:
            if 'redheadsound' in i:
                players['redheadsound'] = i
            if 'cdnvideohub' in i:
                players['cdnvideohub'] = i

        return players
    
    # def create_proxy_data(self):
    #     if '0' in addon.getSetting('unblock'):
    #         return None

    #     from urllib.request import urlopen

    #     try:
    #         proxy_time = float(addon.getSetting('proxy_time'))
    #     except:
    #         proxy_time = 0

    #     if time.time() - proxy_time > 604800:
    #         addon.setSetting('proxy_time', str(time.time()))
    #         proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()

    #         try:
    #             proxy_pac = str(proxy_pac, encoding='utf-8')
    #         except:
    #             pass

    #         proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
    #         addon.setSetting('proxy', proxy)
    #         proxy_data = {'https': proxy}
    #     else:
    #         if addon.getSetting('proxy'):
    #             proxy_data = {'https': addon.getSetting('proxy')}
    #         else:
    #             proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()
                
    #             try:
    #                 proxy_pac = str(proxy_pac, encoding='utf-8')
    #             except:
    #                 pass

    #             proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
    #             addon.setSetting('proxy', proxy)
    #             proxy_data = {'https': proxy}

    #     return proxy_data
#========================#========================#========================#
    def normailze_json(self, data):
        data = data.replace('\'','"')
        data = data.splitlines()

        result = ''

        for d in data:
            if 'preroll' in d or 'pauseroll' in d or 'midroll' in d:
                continue
            if 'id:' in d:
                d = d.replace('id:','"id":')
            if 'file:' in d:
                d = d.replace('file:','"file":')
            
            result = '{}\n{}'.format(result,d)

        result = eval(result)

        return(result)
#========================#========================#========================#
    def create_arts(self, arts):
        if '0' in addon.getSetting('tmdb_images'):
            art_set = arts.get('preview')
        elif '1' in addon.getSetting('tmdb_images'):
            art_set = arts.get('original')

        if '0' in addon.getSetting('tmdb_unblock'):
            for i in art_set:
                art_set[i] = art_set[i].replace('image.tmdb.org', 'image-tmdb-org.translate.goog')

        return art_set
#========================#========================#========================#
    def create_cast(self, cast_info):
        actors = []
        for cast in cast_info:
            if '0' in addon.getSetting('tmdb_unblock'):
                #url=url.replace('api.themoviedb.org','api-themoviedb-org.translate.goog')
                cast['thumbnail'] = cast['thumbnail'].replace('image.tmdb.org', 'image-tmdb-org.translate.goog')

            if sys.version_info.major == 3:                
                actors.append(xbmc.Actor(
                    name=cast['name'],
                    role=cast['role'],
                    order=cast['order'],
                    thumbnail=cast['thumbnail']))
            else:
                actors.append(cast)
        
        return actors
#========================#========================#========================#
    def create_line(self, title, meta_info={}, params={}, folder=True, image=None):
        li = xbmcgui.ListItem(label=title)

        if meta_info:
            arts = self.create_arts(meta_info['arts'])
            info = meta_info['info']
            cast = self.create_cast(cast_info=meta_info['cast'])

            li.setArt(arts)

            if sys.version_info.major < 3:
                    li.setCast(cast)
                    #info.update({'status': status})
                    li.setInfo(type='video', infoLabels=info)
            else:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setTitle(info.get('title')) #title	string - Title.
                videoinfo.setOriginalTitle(info.get('originaltitle')) #string - Original title.
                videoinfo.setPlot(info.get('plot')) #plot	string - Plot
                videoinfo.setTagLine(info.get('tagline')) #tagLine	string - Tagline
                videoinfo.setStudios(info.get('studio')) #studios	list - Studios
                videoinfo.setGenres(info.get('genre')) #genre	list - Genres.
                videoinfo.setCountries(info.get('country')) #countries	list - Countries.
                videoinfo.setWriters(info.get('credits')) #writers	list - Writers.
                videoinfo.setDirectors(info.get('director')) #setDirectors(directors)
                #videoinfo.setYear() #year	integer - Year.

                videoinfo.setPremiered(info.get('premiered')) #premiered	string - Premiere date
                videoinfo.setTags(info.get('tag')) #tags	list - Tags
                videoinfo.setMpaa(info.get('mpaa')) #mpaa	string - MPAA rating
                videoinfo.setTrailer(info.get('trailer')) #[string] Trailer path
                videoinfo.setDuration(info.get('duration')) #[unsigned int] Duration

                videoinfo.setCast(cast) ##actors	list - Cast / Actors

                #videoinfo.setPlaycount(info['playcount'])
                #videoinfo.setTvShowStatus(status)

        #li.addContextMenuItems(self.create_context(ext))
        li.addContextMenuItems(self.context_menu)

        if image:
            li.setArt({"icon": image})

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, uniqueid, update=False):
            #{'imdb': 'tt13159924', 'media_type': 'series', 'kinopoisk': '1431133'}
            unblock = False
            if '0' in addon.getSetting('tmdb_unblock'):
                unblock = True

            from tmdbparser.tmdb import TMDBScraper
            scraper = TMDBScraper(
                language='ru-RU',
                certification_country='us',
                # search_language='en-US'
                search_language='ru-RU',
                unblock=unblock
            )
            del TMDBScraper

            if uniqueid.get('tmdb'):
                meta_info = scraper.get_details(uniqueids=uniqueid)

                if update:
                    self.database.update_content(meta_info=meta_info)
                else:
                    self.database.insert_content(meta_info=meta_info)                    
            else:
                if not uniqueid.get('imdb'):
                    return False
                
                external_id = scraper.get_by_external_id(external_ids=uniqueid, return_ids=True)
                self.create_info(uniqueid=external_id, update=update)

            return
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try:
            self.database.end()
        except:
            pass
#========================#========================#========================#
    def exec_update_database(self):
        self.create_database()
        return
#========================#========================#========================#
    def exec_update_content(self):
        uniqueid = eval(self.params['uniqueid'])

        self.create_info(uniqueid=uniqueid, update=True)

        return
#========================#========================#========================#
    def exec_information_part(self):
        update_info = '[B][COLOR=darkorange]Version 0.2.7[/COLOR][/B]\n\n\
- Исправлен парсер ссылки imdb'
        self.dialog.textviewer('Информация', update_info)
        return
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.dialog.notification(heading='RedHeadSound', message='Выполнено',icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='RedHeadSound', message='Ошибка',icon=icon,time=1000,sound=False)
            pass
#========================#========================#========================#
    def exec_update_proxy_data(self):
        addon.setSetting('proxy','')
        addon.setSetting('proxy_time','')

        #self.create_proxy_data()
        return
#========================#========================#========================#
    def exec_main_part(self):
        xbmcplugin.setContent(handle, '')
        
        self.context_menu = [
            ('Новости обновлений', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=information_part")'),
            #('Обновить Авторизацию', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_authorization")'),
            ('Обновить Базу Данных', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_database")')
            #('Обновить Прокси', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_proxy_data")'),
        ]

        self.create_line(title='Поиск', params={'mode': 'search_part'},
                         image=os.path.join(plugin_dir, 'resources', 'media', 'search.png'))
        self.create_line(title='Новинки', params={'mode': 'common_part', 'param': ''},
                         image=os.path.join(plugin_dir, 'resources', 'media', 'new.png'))
        self.create_line(title='Сериалы', params={'mode': 'common_part', 'param': 'serialy/'},
                         image=os.path.join(plugin_dir, 'resources', 'media', 'series.png'))
        self.create_line(title='Фильмы', params={'mode': 'common_part', 'param':'filmy/'},
                         image=os.path.join(plugin_dir, 'resources', 'media', 'movies.png'))
        self.create_line(title='Мультфильмы', params={'mode': 'common_part', 'param': 'multfilmy/'},
                         image=os.path.join(plugin_dir, 'resources', 'media', 'mult.png'))
        self.create_line(title='Короткометражки', params={'mode': 'common_part', 'param': 'korotkometrazhka/'},
                         image=os.path.join(plugin_dir, 'resources', 'media', 'short.png'))
        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            xbmcplugin.setContent(handle, '')

            self.create_line(title='Поиск по названию', params={'mode': 'search_part', 'param': 'search_word'},
                             image=os.path.join(plugin_dir, 'resources', 'media', 'search.png'))
            
            data_array = addon.getSetting('search').split('|')
            data_array.reverse()

            self.context_menu = [
                ('Очистить историю', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=clean_part")')
                ]
            
            try:
                for data in data_array:
                    if data == '':
                        continue

                    try:
                        label = '[COLOR=gray]{}[/COLOR]'.format(data.decode('utf-8'))
                    except:
                        label = '[COLOR=gray]{}[/COLOR]'.format(data)

                    self.create_line(title=label, params={'mode': 'search_part', 'param':'search_string', 'search_string': data},
                                     image=os.path.join(plugin_dir, 'resources', 'media', 'tags.png'))
            except:
                addon.setSetting('search', '')

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                data_array = addon.getSetting('search').split('|')
                
                while len(data_array) >= 7:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])

                addon.setSetting('search', data_array)

                self.params['param'] = 'search_string'
            else:
                return False

        if 'search_string' in self.params['param']:            
            if self.params['search_string'] == '':
                return False
            
            post_data = {
            'do': 'search',
            'subaction': 'search',
            'search_start': self.params['page'],
            'full_search': '0',
            'result_from': (int(self.params['page'])-1) * 10 + 1,
            'story': self.params['search_string']
            }
            
            html = self.network.get_html(url=self.site_url, post=urlencode(post_data))
                
            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            if not '<article class="card d-flex">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return

            self.progress_bg.create('RedHeadSound', 'Инициализация')

            try:
                data_array = html[html.find('<article class="card d-flex">')+29:html.rfind('</article>')]
                data_array = data_array.split('<article class="card d-flex">')
                for i, data in enumerate(data_array):
                    try:
                        data = data[:data.find('</article>')]

                        if '<div id="adfox' in data:
                            continue

                        imdb_id = data[data.find('data-text="IMDb">')+17:]
                        imdb_id = imdb_id[imdb_id.find('title/')+6:]
                        imdb_id = imdb_id[:imdb_id.find('"')].strip()
                        imdb_id = imdb_id.replace('/','')

                        if imdb_id == 'tt11213558':
                            imdb_id = 'tt10954600'

                        kinopoisk = ''
                        if 'data-text="КиноПоиск">' in data:
                            kinopoisk = data[data.find('data-text="КиноПоиск">')+22:]
                            kinopoisk = kinopoisk[kinopoisk.find('kinopoisk.ru/')+13:]
                            kinopoisk = kinopoisk[kinopoisk.find('/')+1:]
                            kinopoisk = kinopoisk[:kinopoisk.find('"')]
                            kinopoisk = kinopoisk.replace('/','').strip()
                            if '?' in kinopoisk:
                                kinopoisk = kinopoisk[:kinopoisk.find('?')]

                        content_url = data[data.find('title"><a href="')+16:]
                        content_url = content_url[:content_url.find('"')]

                        uniqueid = {'imdb': imdb_id, 'media_type': '', 'kinopoisk': kinopoisk}

                        season = ''
                        if 'Сезон:' in data:
                            season = data[data.find('Сезон:'):]
                            season = season[season.find('</span>')+7:season.find('</li>')]
                            season = ' | [COLOR=blue]S{:>02}[/COLOR]'.format(season.strip())

                        episodes = ''
                        if 'Серий на сайте:' in data:
                            episodes = data[data.find('Серий на сайте:'):]
                            episodes = episodes[episodes.find('</span>')+7:episodes.find('</li>')]
                            episodes = ' | [COLOR=gold]{}[/COLOR]'.format(episodes.strip())

                        node = ''
                        if '/filmy/' in content_url:
                            node = ' | [COLOR=blue]Фильм[/COLOR]'
                        if '/multfilmy/' in content_url:
                            node = ' | [COLOR=blue]Мультфильм[/COLOR]'

                        if not self.database.imdb_in_db(unique_imdb=imdb_id):
                            self.create_info(uniqueid = uniqueid)

                        meta_info = self.database.get_metainfo(unique_imdb=imdb_id)

                        label = '{}{}{}{}'.format(meta_info['info']['title'],season,episodes,node)

                        self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), 'Обработано - {} из {}'.format(i, len(data_array)))

                        self.context_menu = [
                            #('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                            ('Обновить описание', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_content&uniqueid={}")'.format(uniqueid)),
                            #('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)),
                            #('Отметить как просмотренное', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=mark_part&param=on&id={}")'.format(se_code)),
                            #('Отметить как непросмотренное', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=mark_part&param=off&id={}")'.format(se_code))
                            ]
                        
                        self.create_line(title=label, params={'mode': 'select_part', 'id': imdb_id, 'url': content_url}, meta_info=meta_info)
                    except:
                        self.create_line(title='Ошибка обработки строки')
            except:
                self.create_line(title='Ошибка - сообщите автору')
                
            self.progress_bg.close()

            if 'pagination__pages d-flex jc-center' in html:
                page = html[html.find('pages d-flex jc-center">')+24:]
                page = page[:page.find('</div>')]
                page = page[page.rfind('href="#">')+9:page.rfind('</a>')]
                
                try:
                    page = int(page)
                except:
                    page = 0
                
                if page > int(self.params['page']):
                    label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                        int(self.params['page']), int(self.params['page'])+1)                
                    self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'search_string': self.params['search_string'], 'page': (int(self.params['page']) + 1)})
            
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])

        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<article class="card d-flex">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        self.progress_bg.create('RedHeadSound', 'Инициализация')
        
        try:
            data_array = html[html.find('<article class="card d-flex">')+29:html.rfind('</article>')]
            data_array = data_array.split('<article class="card d-flex">')

            for i, data in enumerate(data_array):
                try:
                    data = data[:data.find('</article>')]

                    if '<div id="adfox' in data:
                        continue

                    imdb_id = data[data.find('data-text="IMDb">')+17:]
                    imdb_id = imdb_id[imdb_id.find('title/')+6:]
                    imdb_id = imdb_id[:imdb_id.find('"')].strip()
                    imdb_id = imdb_id.replace('/','')
                    if '?' in imdb_id:
                        imdb_id = imdb_id[:imdb_id.find('?')]
                    if imdb_id == 'tt11213558':
                        imdb_id = 'tt10954600'

                    kinopoisk = ''
                    if 'data-text="КиноПоиск">' in data:
                        kinopoisk = data[data.find('data-text="КиноПоиск">')+22:]
                        kinopoisk = kinopoisk[kinopoisk.find('kinopoisk.ru/')+13:]
                        kinopoisk = kinopoisk[kinopoisk.find('/')+1:]
                        kinopoisk = kinopoisk[:kinopoisk.find('"')]
                        kinopoisk = kinopoisk.replace('/','').strip()
                        if '?' in kinopoisk:
                            kinopoisk = kinopoisk[:kinopoisk.find('?')]

                    content_url = data[data.find('title"><a href="')+16:]
                    content_url = content_url[:content_url.find('"')]

                    uniqueid = {'imdb': imdb_id, 'media_type': '', 'kinopoisk': kinopoisk}

                    season = ''
                    if 'Сезон:' in data:
                        season = data[data.find('Сезон:'):]
                        season = season[season.find('</span>')+7:season.find('</li>')]
                        season = ' | [COLOR=blue]S{:>02}[/COLOR]'.format(season.strip())

                    episodes = ''
                    if 'Серий на сайте:' in data:
                        episodes = data[data.find('Серий на сайте:'):]
                        episodes = episodes[episodes.find('</span>')+7:episodes.find('</li>')]
                        episodes = ' | [COLOR=gold]{}[/COLOR]'.format(episodes.strip())

                    node = ''
                    if '/filmy/' in content_url:
                        node = ' | [COLOR=blue]Фильм[/COLOR]'
                    if '/multfilmy/' in content_url:
                        node = ' | [COLOR=blue]Мультфильм[/COLOR]' 

                    if not self.database.imdb_in_db(unique_imdb=imdb_id):
                        self.create_info(uniqueid = uniqueid)

                    meta_info = self.database.get_metainfo(unique_imdb=imdb_id)

                    label = '{}{}{}{}'.format(meta_info['info']['title'],season,episodes,node)

                    self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), 'Обработано - {} из {}'.format(i, len(data_array)))

                    self.context_menu = [
                        #('Избранное Добавить \ Удалить', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=favorites_part&serial_id={}")'.format(serial_id)),
                        ('Обновить описание', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_content&uniqueid={}")'.format(uniqueid)),
                        #('Открыть торрент файл', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)),
                        #('Отметить как просмотренное', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=mark_part&param=on&id={}")'.format(se_code)),
                        #('Отметить как непросмотренное', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=mark_part&param=off&id={}")'.format(se_code))
                        ]
                    
                    self.create_line(title=label, params={'mode': 'select_part', 'id': imdb_id, 'url': content_url}, meta_info=meta_info)
                except:
                    self.create_line(title='Ошибка обработки строки')
        except:
            self.create_line(title='Ошибка - сообщите автору')
            
        self.progress_bg.close()
        
        if 'jc-center ai-center">' in html:
            paginator = html[html.find('jc-center ai-center">')+21:]
            paginator = paginator[:paginator.find('</div>')]
            
            if '<a href="' in paginator:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                    int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
            
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        url = self.params['url']

        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<iframe data-src="' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        link = []
        while html.find('<iframe data-src="') > -1:
            link_data = html[html.find('<iframe data-src="'):]
            link_data = link_data[:link_data.find('</iframe>')]
            html = html.replace(link_data, '')
            link_data = link_data[link_data.find('"')+1:]
            link_data = link_data[:link_data.find('"')]
            link.append(link_data)

        videodata = []
        for l in link:
            data_array = self.network.get_bytes(url=l)

            if not data_array['connection_reason'] == 'OK':
                continue
                #return _error('Ошибка запроса')
            data_array = data_array['content'].decode('utf-8')

            playlist = data_array[data_array.find('playerOptions'):]
            playlist = playlist[:playlist.find('};')]
            playlist = playlist.split('ad: [')

            for node in playlist:
                if not node.find('sources:') > -1:
                    continue
                node = node[node.find('sources')+7:]

                src = node[node.find('src":"')+6:]
                src = src[:src.find('"')]
                src = src.replace(r'\u0026', '&')

                title = node[node.find('title: "')+8:]
                title = title[:title.find('"')]

                videodata.append(
                    {'title': title, 'src': src}
                )

        meta_info = self.database.get_metainfo(unique_imdb = self.params['id'])

        for vd in videodata:
            self.create_line(title=vd['title'], params={'mode': 'play_part', 'param': vd['src']}, meta_info=meta_info, folder=False)

        xbmcplugin.endOfDirectory(handle, succeeded=True)

    # def exec_select_part(self):
    #     url = self.params['url']

    #     html = self.network.get_html(url=url)

    #     if not html:
    #         self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
    #         xbmcplugin.endOfDirectory(handle, succeeded=True)
    #         return

    #     if not '<iframe data-src="' in html:
    #         self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
    #         xbmcplugin.endOfDirectory(handle, succeeded=True)
    #         return

    #     player_links = self.create_players(data=html)
    #     player_choice = addon.getSetting('player')

    #     if '0' in player_choice:
    #         player_url = player_links['cdnvideohub']
    #         if not player_url:
    #             player_url = player_links['redheadsound']

    #     if '1' in player_choice:
    #         player_url = player_links['redheadsound']
    #         if not player_url:
    #             player_url = player_links['cdnvideohub']

    #     meta_info = self.database.get_metainfo(unique_imdb = self.params['id'])
    
    #     html2 = self.network.get_html(url=player_url)

    #     data_array = html2[html2.find('new Playerjs(')+13:]
    #     data_array = data_array[:data_array.find(');')]

    #     try:
    #         files = json.loads(data_array)
    #     except:
    #         files = self.normailze_json(data_array)
    #         files = json.dumps(files)
    #         files = json.loads(files)

    #     if 'title' in files:
    #         file_title = files['title']
    #         file_url = files['file']
    #         file_url = file_url.replace('\/','/')

    #         self.create_line(title=file_title, params={'mode': 'play_part', 'param': file_url}, meta_info=meta_info, folder=False)
    #     else:
    #         files = files['file']

    #         if 'folder' in files[0]:
    #             for f in files:
    #                 folder_title = f['title']
    #                 self.create_line(title=folder_title)

    #                 folder_files = f['folder']

    #                 for node in folder_files:
    #                     file_title = node['title']
    #                     file_url = node['file']
    #                     file_url = file_url.replace('\/','/')


    #                     self.create_line(title=file_title, params={'mode': 'play_part', 'param': file_url}, meta_info=meta_info, folder=False)
            
    #         else:
    #             for i in files:
    #                 file_title = i['title']
    #                 file_url = i['file']
    #                 file_url = file_url.replace('\/','/')

    #                 self.create_line(title=file_title, params={'mode': 'play_part', 'param': file_url}, meta_info=meta_info, folder=False)

    #     xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def process_url(self, raw_url):
        playlist = {}
        if '[' in raw_url:
            raw_url = raw_url.split(',')

            for node in raw_url:
                file_quality = node[1:node.find('p')].strip()
                file_url = node[node.find('/'):]
                file_url = 'https://redheadsound.video{}'.format(file_url)

                playlist.update({file_quality: file_url})
        else:
            html = self.network.get_html(url=raw_url)
            if not html:
                return False
            
            qlist = ['/240/','/360/','/480/','/720/','/1080/']
            data = html.splitlines()
            for node in data:
                if node.startswith('#'):
                    continue

                file_quality = ''

                for q in qlist:
                    if q in node:
                        file_quality = q.replace('/','')

                playlist.update({file_quality: node})

        user_quality = addon.getSetting('quality')
        values = ['240', '360', '480', '720', '1080']
        user_value = values[int(user_quality)]

        if user_value in playlist:
            return playlist[user_value]
        else:
            quality = list(playlist.keys())
            res = self.dialog.select('Доступное качество', list(playlist.keys()))

            if res == -1:
                return False
            
            quality_res = quality[res]        
            quality_url = playlist[quality_res]
            
            return quality_url
#========================#========================#========================#
    def exec_play_part(self):
        #video_url = self.process_url(raw_url=self.params['param'])

        video_url = self.params['param']
        if not video_url:
            return

        li = xbmcgui.ListItem(path=video_url)

        if '0' in addon.getSetting('inputstream_adaptive'):
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            #li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')

            li.setProperty('inputstream.adaptive.stream_selection_type', 'ask-quality')

            #li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)
        
def start():
    redheadsound = RedHeadSound()
    redheadsound.execute()
    del redheadsound