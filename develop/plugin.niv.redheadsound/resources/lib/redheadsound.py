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
        time=3000,
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
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'rhs.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(proxy_data=self.proxy_data)
        del WebTools
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'rhs.db'))
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
            
            result = u'{}\n{}'.format(result,d)

        result = eval(result)

        return(result)
#========================#========================#========================#
    def create_context(self, ext={}):
        context_menu = []
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=blue]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=clean_part")'))

        if 'url' in list(ext.keys()):
            context_menu.append(('[COLOR=white]Обновить описание[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_content_part&url={}")'.format(ext['url'])))

        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_database_part")'))
        return context_menu
#========================#========================#========================#
    def create_arts(self, arts):
        url = 'https://image-tmdb-org.translate.goog/t/p/original/'
        unlock_url = 'https://image-tmdb-org.translate.goog/t/p/original/'
        
        # arts = {
        #     'original': {
        #         'poster': res[0],
        #         'landscape': res[2],
        #         'fanart': res[4],
        #         'clearlogo': res[6],
        #         'thumb': res[0]
        #     },
        #     'preview': {
        #         'poster': res[1],
        #         'landscape': res[3],
        #         'fanart': res[5],
        #         'clearlogo': res[7],
        #         'thumb': res[1]
        #     }
        # }

        arts_set = arts.pop('original')
        for i in arts_set:
            if arts_set[i]:
                arts_set[i] = '{}{}'.format(unlock_url, arts_set[i])
        
        return arts_set
#========================#========================#========================#
    def create_line(self, title, meta_info={}, params={}, folder=True, image=None):
        li = xbmcgui.ListItem(label=title)

        if meta_info:
            arts = self.create_arts(meta_info.pop('arts'))
            info = meta_info.pop('info')

            li.setArt(arts)

            if sys.version_info.major < 3:
                    #li.setCast(cast)
                    #info.update({'status': status})
                    li.setInfo(type='video', infoLabels=info)
            else:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setTitle(info.get('title'))
                videoinfo.setOriginalTitle(info.get('originaltitle'))
                videoinfo.setPlot(info.get('plot'))
                videoinfo.setPremiered(info.get('premiered'))
                # videoinfo.setTagLine(info.get('tagline'))
                # videoinfo.setStudios(info.get('studio'))
                # videoinfo.setGenres(info.get('genre'))
                # videoinfo.setCountries(info.get('country'))
                # videoinfo.setDirectors(info.get('director'))
                #videoinfo.setYear(info.get('premiered'))
                # videoinfo.setTags(info.get('tag'))
                # videoinfo.setMpaa(info.get('mpaa'))
                # videoinfo.setTrailer(info.get('trailer'))
                # videoinfo.setDuration(info.get('duration'))
                #videoinfo.setCast(cast)
                #videoinfo.setPlaycount(info['playcount'])
                #videoinfo.setTvShowStatus(status)

        #li.addContextMenuItems(self.create_context(ext))
        if image:
            li.setArt({"icon": image})

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, imdb_id):
        if not imdb_id:
            return False

        # with open('111.test', 'r') as rf:
        #     html = rf.read()
        url = 'https://api-themoviedb-org.translate.goog/3/find/{}?api_key=af3a53eb387d57fc935e9128468b1899&language=ru-RU&external_source=imdb_id'.format(imdb_id)
        #html = get_web(url=url)
        html = self.network.get_html(url=url)

        # with open('111.test', 'w') as wf:
        #     wf.write(html)
            
        data = json.loads(html)

        if data['movie_results']:
            data = data['movie_results'][0]
            is_movie = True
        elif data['tv_results']:
            data = data['tv_results'][0]
            is_movie = False
        else:
            data = None

        if not data:
            return False


        if is_movie:
            info = {
                'title': data.get('title'),
                'originaltitle': data.get('original_title'),
                'plot': data.get('overview'),
                'country': data.get('origin_country'),
                'premiered': data.get('release_date')
                }
        else:
            info = {
                'title': data.get('name'),
                'originaltitle': data.get('original_name'),
                'plot': data.get('overview'),
                #'country': data.get('origin_country'),
                'premiered': data.get('first_air_date')
                }
        
        for i in info:
            if info[i] == None:
                info[i] = ''
        
        unique_id = {
            'tmdb': data.get('id'),
            'imdb': imdb_id,
            'media_type': data.get('media_type')
            }
        
        for i in unique_id:
            if unique_id[i] == None:
                unique_id[i] = ''

        arts = {
            'poster_url': data.get('poster_path'),
            'poster_preview': '',
            'landscape_url': '',
            'landscape_preview': '',
            'fanart_url': data.get('backdrop_path'),
            'fanart_preview': '',
            'clearlogo_url': '',
            'clearlogo_preview':''
            }
        
        for i in arts:
            if arts[i] == None:
                arts[i] = ''
            if arts[i]:
                arts[i] = arts[i].replace('/','')

        meta_info = {'media': info, 'unique_id': unique_id, 'available_arts': arts}

        self.database.insert_content(meta_info=meta_info)

        return
    # def create_info(self, serial_url=False, update=False):
    #     from utility import clean_tags

    #     html = self.network.get_html(serial_url)

    #     data = html[html.find('class="page__header">')+21:html.find('<h2 class="page')]
        
    #     info = {
    #         'serial_id': 0,
    #         'title': '',
    #         'year': 0,
    #         'country': '',
    #         'duration': 0,
    #         'director': '',
    #         'actors': '',
    #         'genre': '',
    #         'mpaa': '',
    #         'plot': ''
    #     }

    #     serial_id = serial_url[serial_url.rfind('/')+1:serial_url.find('-')]
    #     info['serial_id'] = int(serial_id)
    #     del serial_id
        
    #     title = data[data.find('<h1>')+4:data.find('</h1>')]
    #     if '(' in title:
    #         title = title[:title.find('(')]
    #         info['title'] = u'{}'.format(title.strip())
    #         del title

    #     if u'<div>Год выпуска' in data:
    #         year = data[data.find(u'<div>Год выпуска'):]
    #         year = year[year.find('">')+2:year.find('</a>')]
    #         try:
    #             year = int(year.strip())
    #         except:
    #             pass
    #         info['year'] = year
    #         del year

    #     if u'<div>страна' in data:
    #         country = data[data.find(u'<div>страна'):]
    #         country = country[country.find('">')+2:country.find('</a>')]
    #         info['country'] = u'{}'.format(country.strip())
    #         del country

    #     if u'<div>Продолжительность' in data:
    #         duration = data[data.find(u'<div>Продолжительность'):]
    #         duration = duration[duration.find('<span>')+6:duration.find('</span>')]
            
    #         if ':' in duration:
    #             duration = duration.split(':')

    #             if len(duration) > 2:
    #                 try:
    #                     duration = int(duration[0]) * 60 * 60 + int(duration[1]) * 60 + int(duration[2])
    #                 except:
    #                     duration = 0
    #             else:
    #                 try:
    #                     duration = int(duration[0]) * 60
    #                 except:
    #                     duration = 0
    #         else:
    #             duration = 0

    #         info['duration'] = duration
    #         del duration

    #     if u'<div>Режиссер' in data:
    #         director = data[data.find(u'<div>Режиссер'):]
    #         director = director[director.find('<span>')+6:director.find('</span>')]
    #         info['director'] = u'{}'.format(director.strip())
    #         del director

    #     if u'<div>Актеры' in data:
    #         actor = data[data.find(u'<div>Актеры'):]
    #         actor = actor[actor.find('<a href="'):actor.find('</li>')]
    #         actor = u'{}'.format(actor.strip())

    #         if '>' in actor[len(actor)-1]:
    #             actor = actor[:actor.rfind('</a>')]

    #         actor_list = []
            
    #         if '</a>,' in actor:
    #             actor = actor.split('</a>,')
                
    #             for i in actor:
    #                 i = i[i.find('">')+2:].strip()
    #                 actor_list.append(i)

    #         info['actors'] = u','.join(actor_list)
    #         del actor_list, actor

    #     if u'<div>Жанр' in data:
    #         genre = data[data.find(u'<div>Жанр'):]
    #         genre = genre[genre.find('<a href="'):genre.find('</li>')]
    #         genre = u'{}'.format(genre.strip())
            
    #         if '>' in genre[len(genre)-1]:
    #             genre = genre[:genre.rfind('</a>')]
            
    #         genre_list = []
            
    #         if '</a>' in genre:
    #             genre = genre.split('</a>')
                
    #             for i in genre:
    #                 i = i[i.find('">')+2:].strip()
    #                 genre_list.append(i)

    #         info['genre'] = u','.join(genre_list)
    #         del genre_list, genre

    #     if u'Возрастной рейтинг' in data:
    #         mpaa = data[data.find(u'Возрастной рейтинг'):]
    #         mpaa = mpaa[mpaa.find('<img src="/')+11:]
    #         mpaa = mpaa[:mpaa.find('"')]
    #         mpaa = mpaa[mpaa.rfind('/')+1:mpaa.rfind('.')]
    #         info['mpaa'] = u'{}'.format(mpaa)
    #         del mpaa

    #     if 'text full-text clearfix">' in data:
    #         plot = data[data.find('text full-text clearfix">')+25:]
    #         if '<div class="link-mess">' in plot:
    #             plot = plot[:plot.find('<div class="link-mess">')]
    #         info['plot'] = u'{}'.format(clean_tags(plot))
    #         del plot

    #     if update:
    #         self.database.update_content(info)
    #     else:
    #         self.database.insert_content(info)
        
    #     return info
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try:
            self.database.end()
        except:
            pass
#========================#========================#========================#
    def exec_update_content_part(self):
        self.create_info(serial_url=self.params['url'], update=True)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.dialog.notification(heading='Red Head Sound', message='Выполнено',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Red Head Sound', message='Ошибка',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_update_proxy_data(self):
        addon.setSetting('proxy','')
        addon.setSetting('proxy_time','')

        self.create_proxy_data()
        return
#========================#========================#========================#
    def exec_update_database_part(self):
        try:
            self.database.end()
        except:
            pass

        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/rhs.db'
        target_path = os.path.join(self.database_dir, 'rhs.db')
        
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

            self.progress_bg.create(u'Загрузка файла')
            
            try:
                with open(target_path, 'wb') as write_file:
                    while True:
                        chunk = data.read(chunk_size)
                        bytes_read = bytes_read + len(chunk)
                        write_file.write(chunk)
                        if len(chunk) < chunk_size:
                            break
                        self.progress_bg.update(int(bytes_read * 100 / file_size), u'Загружено: {} из {} MB'.format(
                            '{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
            except:
                self.dialog.notification(heading='Red Head Sound', message='Ошибка', icon=icon,time=3000,sound=False)
                pass

            self.progress_bg.close()
            
            self.dialog.notification(heading='Red Head Sound', message='Выполнено', icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='Red Head Sound', message='Ошибка', icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        xbmcplugin.setContent(handle, '')
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
            self.create_line(title=u'Поиск по названию', params={'mode': 'search_part', 'param': 'search_word'})
            
            data_array = addon.getSetting('search').split('|')
            data_array.reverse()
            
            try:
                for data in data_array:
                    if data == '':
                        continue

                    try:
                        label = u'[COLOR=gray]{}[/COLOR]'.format(data.decode('utf-8'))
                    except:
                        label = u'[COLOR=gray]{}[/COLOR]'.format(data)

                    self.create_line(title=label, params={'mode': 'search_part', 'param':'search_string', 'search_string': data})
            except:
                addon.setSetting('search', '')

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
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
                self.create_line(title=u'Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            if not '<article class="card d-flex">' in html:
                self.create_line(title=u'Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return

            self.progress_bg.create(u'RedHeadSound', u'Инициализация')

            ext = {
                'serial_id': '',
                'title': '',
                'url': '',
                'poster': '',
                'rating': ''
            }

            try:
                data_array = html[html.find('<article class="card d-flex">')+29:html.rfind('</article>')]
                data_array = data_array.split('<article class="card d-flex">')

                for i, data in enumerate(data_array):
                    try:
                        data = data[:data.find('</article>')]

                        if '<div id="adfox' in data:
                            continue

                        content = data[data.find('title"><a href="')+16:]
                        content = content[:content.find('</a>')].split('">')
                        ext['title'] = u'{}'.format(content[1])
                        ext['url'] = u'{}'.format(content[0])

                        serial_id = content[0][content[0].rfind('/')+1:]
                        serial_id = serial_id[:serial_id.find('-')]
                        ext['serial_id'] = serial_id

                        poster = data[data.find('<img src="/')+11:]
                        poster = poster[:poster.find('"')]
                        ext['poster'] = u'{}{}'.format(self.site_url, poster.strip())

                        season = ''
                        if u'Сезон:' in data:
                            season = data[data.find(u'Сезон:'):]
                            season = season[season.find('</span>')+7:season.find('</li>')]
                            season = u' | [COLOR=blue]S{:>02}[/COLOR]'.format(season.strip())

                        episodes = ''
                        if u'Серий на сайте:' in data:
                            episodes = data[data.find(u'Серий на сайте:'):]
                            episodes = episodes[episodes.find('</span>')+7:episodes.find('</li>')]
                            episodes = u' | [COLOR=gold]{}[/COLOR]'.format(episodes.strip())

                        if u'КиноПоиск">' in data:
                            rating = data[data.find(u'КиноПоиск">')+11:]
                            rating = rating[rating.find('">')+2:rating.find('</a>')]
                            ext['rating'] = float(rating.strip())

                        node = ''
                        if '/filmy/' in ext['url']:
                                node = u' | [COLOR=blue]Фильм[/COLOR]'            
                        if '/multfilmy/' in ext['url']:
                                node = u' | [COLOR=blue]Мультфильм[/COLOR]'
                        
                        label = u'{}{}{}{}'.format(ext['title'],season,episodes,node)

                        self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))
                        
                        if not self.database.content_in_db(ext['serial_id']):
                            self.create_info(serial_url=ext['url'])

                        self.create_line(title=label, ext=ext, params={
                                         'mode': 'select_part', 'id': ext['serial_id'], 'url': ext['url']})
                    except:
                        self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]')
            except:
                self.create_line(title=u'[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]')
                
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
                    label = u'[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                        int(self.params['page']), int(self.params['page'])+1)                
                    self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'search_string': self.params['search_string'], 'page': (int(self.params['page']) + 1)})
            
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])

        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title=u'Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<article class="card d-flex">' in html:
            self.create_line(title=u'Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        self.progress_bg.create(u'RedHeadSound', u'Инициализация')

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

                    content_url = data[data.find('title"><a href="')+16:]
                    content_url = content_url[:content_url.find('"')]

                    season = ''
                    if u'Сезон:' in data:
                        season = data[data.find(u'Сезон:'):]
                        season = season[season.find('</span>')+7:season.find('</li>')]
                        season = u' | [COLOR=blue]S{:>02}[/COLOR]'.format(season.strip())

                    episodes = ''
                    if u'Серий на сайте:' in data:
                        episodes = data[data.find(u'Серий на сайте:'):]
                        episodes = episodes[episodes.find('</span>')+7:episodes.find('</li>')]
                        episodes = u' | [COLOR=gold]{}[/COLOR]'.format(episodes.strip())

                    node = ''
                    #ismovie = False
                    if '/filmy/' in content_url:
                        node = u' | [COLOR=blue]Фильм[/COLOR]'
                        #ismovie = True
                    if '/multfilmy/' in content_url:
                        node = u' | [COLOR=blue]Мультфильм[/COLOR]'

                    if not self.database.imdb_in_db(unique_imdb=imdb_id):
                        self.create_info(imdb_id = imdb_id)

                    meta_info = self.database.get_metainfo(unique_imdb=imdb_id)

                    label = u'{}{}{}{}'.format(meta_info['info']['title'],season,episodes,node)

                    self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))

                    # self.create_line(title=label, params={'mode': 'select_part', 'id': imdb_id, 'url': content_url, 'ismovie':ismovie}, meta_info=meta_info)
                    self.create_line(title=label, params={'mode': 'select_part', 'id': imdb_id, 'url': content_url}, meta_info=meta_info)
                except:
                    self.create_line(title=u'[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]')
        except:
            self.create_line(title=u'[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]')
            
        self.progress_bg.close()
        
        if 'jc-center ai-center">' in html:
            paginator = html[html.find('jc-center ai-center">')+21:]
            paginator = paginator[:paginator.find('</div>')]
            
            if '<a href="' in paginator:
                label = u'[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                    int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
            
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        url = self.params['url']
        html = self.network.get_html(url=url)

        if not html:
            self.create_line(title=u'Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        if not '<iframe data-src="' in html:
            self.create_line(title=u'Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        player_links = self.create_players(data=html)
        player_choice = addon.getSetting('player')

        if '0' in player_choice:
            player_url = player_links['cdnvideohub']
            if not player_url:
                player_url = player_links['redheadsound']

        if '1' in player_choice:
            player_url = player_links['redheadsound']
            if not player_url:
                player_url = player_links['cdnvideohub']

        meta_info = self.database.get_metainfo(unique_imdb= self.params['id'])
    
        html2 = self.network.get_html(url=player_url)

        data_array = html2[html2.find('new Playerjs(')+13:html2.rfind(');')]

        import json

        quality_list = {}

        try:
            files = json.loads(data_array)
        except:
            files = self.normailze_json(data_array)
            files = json.dumps(files)
            files = json.loads(files)

        if 'title' in files:
            file_title = files['title']
            file_data = files['file']
                
            file_data = file_data.split(',')
                
            for node in file_data:
                file_quality = node[1:node.find('p')].strip()

                if not file_quality in quality_list:
                    quality_list.update({file_quality:[]})
                        
                file_url = node[node.find('/'):]        
                quality_list[file_quality].append((file_title, file_url))
        else:
            files = files['file']
                    
            for f in files:
                file_title = f['title']
                file_data = f['file']
                file_data = file_data.replace('\/','/')
                            
                file_data = file_data.split(',')

                for node in file_data:
                    if ']' in node:
                        file_quality = node[1:node.find('p')].strip()
                        file_url = node[node.find('/'):]
                    else:
                        file_quality = '1080'
                        file_url = node

                    if not file_quality in quality_list:
                        quality_list.update({file_quality:[]})

                    quality_list[file_quality].append((file_title, file_url))

        select_quality = int(addon.getSetting('quality'))

        option_quality = ['480','720','1080']
        current_quality = option_quality[select_quality]

        if current_quality in quality_list:
            result_quality = current_quality
        else:
            if '1080' in quality_list:
                result_quality = '1080'
            elif '720' in quality_list:
                result_quality = '720'
            elif ' 480' in quality_list:
                result_quality = '480'

        for i in quality_list[result_quality]:
            series_label = i[0]
            if not 'https' in i[1]:
                series_url = 'https://redheadsound.video{}'.format(i[1])
            else:
                series_url = i[1]

            series_url = 'https://bl.webcaster.pro/file/playlist/rhs2204583/5779_2883631739/1080/e9c67c925ffbd9171e362ba06c9a31df/1708454438.m3u8'
            self.create_line(title=series_label, params={'mode': 'play_part', 'param': series_url}, meta_info=meta_info, folder=False)
                                    
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_play_part(self):
        li = xbmcgui.ListItem(path=self.params['param'])

        if '0' in addon.getSetting('inputstream_adaptive'):
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
            li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)
        
def start():
    redheadsound = RedHeadSound()
    redheadsound.execute()
    del redheadsound