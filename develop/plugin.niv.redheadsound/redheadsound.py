# -*- coding: utf-8 -*-

import gc
import os
import sys
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

# def fs_dec(path):
#     sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
#     return path.decode(sys_enc).encode('utf-8')

def fs_enc(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode('utf-8').encode(sys_enc)

if sys.version_info.major > 2:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import parse_qs
    from html import unescape
else:
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

addon = xbmcaddon.Addon(id='plugin.niv.redheadsound')

if sys.version_info.major > 2:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

try:
    xbmcaddon.Addon('script.module.requests')
except:
    xbmcgui.Dialog().notification(
        heading='Установка Библиотеки',
        message='script.module.requests',
        icon=icon,time=3000,sound=False
        )
    xbmc.executebuiltin('RunPlugin("plugin://script.module.requests")')

import requests
session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://redheadsound.ru/'
    }

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
#     'Accept': '*/*',
#     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#     'Accept-Charset': 'utf-8',
#     'Accept-Encoding': 'identity',
#     'Referer': 'https://redheadsound.ru/'
#     }

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

class RedHeadSound:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()
        
        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)
        
        self.cookie_dir = os.path.join(addon_data_dir, 'cookies')
        if not os.path.exists(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.database_dir = os.path.join(addon_data_dir, 'database')
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.sid_file = os.path.join(self.cookie_dir, 'redheadsound.sid')
        self.proxy_data = None
        self.site_url = addon.getSetting('site_url')
        #self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        # if not os.path.isfile(os.path.join(self.database_dir, 'redheadsound.db')):
        #     self.exec_update_database_part()
#========================#========================#========================#
        # from database import DataBase
        # self.database = DataBase(os.path.join(self.database_dir, 'redheadsound.db'))
        # del DataBase
#========================#========================#========================#
    def create_notification(self, data):
        
        data_array = {
            'done': 'Выполнено',
            'err': 'Ошибка',
            'log': 'Введите Логин и Пароль',
            'chk': 'Проверьте Логин и Пароль',
            'add': 'Добавлено',
            'del': 'Удалено'
            }

        self.dialog.notification(heading='Red Head Sound',message=data_array[data],icon=icon,time=3000,sound=False)
        return
#========================#========================#========================#
    def create_line(self, title, poster=False, data=False, watched=False, params=None, folder=True, online=None,):
        li = xbmcgui.ListItem(title)

        if poster:
            li.setArt({"poster": poster,"icon": poster, "thumb": poster})

        if data:
            #'season',
  
            if data['translate']:
                data['plot'] = '{}\n\n[B]Перевод[/B]: {}'.format(data['plot'], data['translate'])
            if data['dubbing']:
                data['plot'] = '{}\n[B]Озвучивание[/B]: {}'.format(data['plot'], data['dubbing'])
            if data['quality']:
                data['plot'] = '{}\n[B]Качество[/B]: {}'.format(data['plot'], data['quality'])

            info = {
                'title': data['title'],
                'year': data['year'],
                'country': data['country'],
                'duration': data['duration'],
                'director': data['director'],
                'rating' : data['rating'][addon.getSetting('rating')],
                'cast' : data['cast'],
                'genre': data['genre'],
                'mpaa': data['mpaa'],
                'status': data['episodes'],
                'plot': data['plot']
                }

            li.setArt({'poster': data['poster'],'icon': data['poster'], 'thumb': data['poster']})

            li.setInfo(type='video', infoLabels=info)
 
        #     if watched:
        #         info['playcount'] = 1
            
        # li.addContextMenuItems(
        #     self.create_context(serial_id = serial_id, se_code = se_code, ismovie=ismovie)
        #     )

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))
        
        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info_common(self, data):
        info = {
            'title': '',
            'url': '',
            'poster': '',
            'year': 0,
            'season': '',
            'episodes': '',
            'duration': 0,
            'country': '',
            'genre': '',
            'translate': '',
            'dubbing': '',
            'director': [],
            'cast': '',
            'quality': '',
            'rating': {'imdb': 0.0, 'kinopoisk': 0.0},
            'mpaa': '',
            'plot': '',
            'node': ''
        }

        
        title = data[data.find('title"><a href="')+16:]
        title = title[:title.find('</a>')].split('">')
        info['title'] = title[1]
        info['url'] = title[0]
        del title
        
        poster = data[data.find('<img src="/')+11:]
        poster = poster[:poster.find('"')]
        info['poster'] = 'https://redheadsound.ru/{}'.format(poster)
        del poster

        if 'Год выпуска' in data:
            year = data[data.find('Год выпуска'):]
            year = year[year.find('">')+2:year.find('</a>')]
            try:
                year = int(year.strip())
            except:
                pass
            info['year'] = year
            del year

        if 'Сезон:' in data:
            season = data[data.find('Сезон:'):]
            season = season[season.find('</span>')+7:season.find('</li>')]
            info['season'] = season.strip()
            del season

        if 'Серий на сайте:' in data:
            episodes = data[data.find('Серий на сайте:'):]
            episodes = episodes[episodes.find('</span>')+7:episodes.find('</li>')]
            info['episodes'] = episodes.strip()
            del episodes

        if 'Продолжительность:' in data:
            duration = data[data.find('Продолжительность:'):]
            duration = duration[duration.find('</span>')+7:duration.find('</li>')]
            
            if ':' in duration:
                duration = duration.split(':')

                if len(duration) > 2:
                    try:
                        duration = int(duration[0]) * 60 * 60 + int(duration[1]) * 60 + int(duration[2])
                    except:
                        duration = 0
                else:
                    try:
                        duration = int(duration[0]) * 60
                    except:
                        duration = 0
            else:
                duration = 0

            info['duration'] = duration
            del duration
        
        if 'Страна:' in data:
            country = data[data.find('Страна:'):]
            country = country[country.find('">')+2:country.find('</a>')]
            info['country'] = country.strip()
            del country

        if 'Жанр:' in data:
            genre = data[data.find('Жанр:'):]
            genre = genre[genre.find('<a href="'):genre.find('</li>')]
            genre = genre.strip()
            
            if '>' in genre[len(genre)-1]:
                genre = genre[:genre.rfind('</a>')]
            
            genre_list = []
            
            if '</a>' in genre:
                genre = genre.split('</a>')
                
                for i in genre:
                    i = i[i.find('">')+2:].strip()
                    genre_list.append(i)

            info['genre'] = genre_list
            del genre_list, genre
        
        if 'Перевод:' in data:
            translate = data[data.find('Перевод:'):]
            translate = translate[translate.find('</span>')+7:translate.find('</li>')]
            info['translate'] = translate.strip()
            del translate

        if 'Роли дублировали:' in data:
            dubbing = data[data.find('Роли дублировали:'):]
            dubbing = dubbing[dubbing.find('</span>')+7:dubbing.find('</li>')]
            info['dubbing'] = dubbing.strip()
            del dubbing

        if 'Режиссер:' in data:
            director = data[data.find('Режиссер:'):]
            director = director[director.find('</span>')+7:director.find('</li>')]
            info['director'] = director.strip().split(', ')
            del director
            
        if 'Актеры:' in data:
            actor = data[data.find('Актеры:'):]
            actor = actor[actor.find('<a href="'):actor.find('</li>')]
            actor = actor.strip()
            
            if '>' in actor[len(actor)-1]:
                actor = actor[:actor.rfind('</a>')]

            actor_list = []
            
            if '</a>,' in actor:
                actor = actor.split('</a>,')
                
                for i in actor:
                    i = i[i.find('">')+2:].strip()
                    actor_list.append(i)

            info['cast'] = actor_list
            del actor_list, actor

        if 'Качество:' in data:
            quality = data[data.find('Качество:'):]
            quality = quality[quality.find('<span>')+6:]
            quality = quality[:quality.find('</span>')] 
            info['quality'] = quality.strip()
            del quality

        if 'IMDb">' in data:
            imdb = data[data.find('IMDb">')+6:]
            imdb = imdb[imdb.find('">')+2:imdb.find('</a>')]
            try:
                info['rating'].update({'imdb': float(imdb.strip())})
            except:
                pass
            del imdb
            
        if 'КиноПоиск">' in data:
            kp = data[data.find('КиноПоиск">')+11:]
            kp = kp[kp.find('">')+2:kp.find('</a>')]
            try:
                info['rating'].update({'kinopoisk': float(kp.strip())})
            except:
                pass
            del kp

        if '/serialy/' in info['url']:
            if info['season']:
                info['node'] = ' | [COLOR=blue]S{:>02}[/COLOR]'.format(info['season'])
                                        
            if info['episodes']:
                info['node'] = '{} | [COLOR=gold]{}[/COLOR]'.format(info['node'], info['episodes'])

        if '/filmy/' in info['url']:
            info['node'] = ' | [COLOR=blue]Фильм[/COLOR]'

        if '/multfilmy/' in info['url']:
            info['node'] = ' | [COLOR=blue]Мультфильм[/COLOR]'
                
        return info
#========================#========================#========================#
    def create_info_select(self, data):
        info = {
            'title': '',
            'url': '',
            'poster': '',
            'year': 0,
            'country': '',
            'translate': '',
            'season': '',
            'episodes': '',
            'duration': 0,
            'dubbing': '',
            'director': [],
            'rating': {'imdb': 0.0, 'kinopoisk': 0.0},
            'cast': '',
            'genre': '',
            'mpaa': '',
            'quality': '',
            'plot': ''
        }

        title = data[data.find('<h1>')+4:data.find('</h1>')]
        if '(' in title:
            title = title[:title.find('(')]
            info['title'] = title.strip()
            del title

        if 'pmovie__poster img-fit-cover' in data:
            poster = data[data.find('<img src="/')+11:]
            poster = poster[:poster.find('"')]
            info['poster'] = 'https://redheadsound.ru/{}'.format(poster)
            del poster

        if '<div>Год выпуска' in data:
            year = data[data.find('<div>Год выпуска'):]
            year = year[year.find('">')+2:year.find('</a>')]
            try:
                year = int(year.strip())
            except:
                pass
            info['year'] = year
            del year

        if '<div>страна' in data:
            country = data[data.find('<div>страна'):]
            country = country[country.find('">')+2:country.find('</a>')]
            info['country'] = country.strip()
            del country

        if '<div>перевод' in data:
            translate = data[data.find('<div>перевод'):]
            translate = translate[translate.find('<span>')+6:translate.find('</span>')]
            info['translate'] = translate.strip()
            del translate

        if '<div>Сезон' in data:
            season = data[data.find('<div>Сезон'):]
            season = season[season.find('<span>')+6:season.find('</span>')]
            info['season'] = season.strip()
            del season

        if '<div>Эпизоды на сайте' in data:
            episodes = data[data.find('<div>Эпизоды на сайте'):]
            episodes = episodes[episodes.find('<span>')+6:episodes.find('</span>')]
            info['episodes'] = episodes.strip()
            del episodes

        if '<div>Продолжительность' in data:
            duration = data[data.find('<div>Продолжительность'):]
            duration = duration[duration.find('<span>')+6:duration.find('</span>')]
            
            if ':' in duration:
                duration = duration.split(':')

                if len(duration) > 2:
                    try:
                        duration = int(duration[0]) * 60 * 60 + int(duration[1]) * 60 + int(duration[2])
                    except:
                        duration = 0
                else:
                    try:
                        duration = int(duration[0]) * 60
                    except:
                        duration = 0
            else:
                duration = 0

            info['duration'] = duration
            del duration

        if '<div>Роли дублировали' in data:
            dubbing = data[data.find('<div>Роли дублировали'):]
            dubbing = dubbing[dubbing.find('<span>')+6:dubbing.find('</span>')]
            info['dubbing'] = dubbing.strip()
            del dubbing

        if '<div>Режиссер' in data:
            director = data[data.find('<div>Режиссер'):]
            director = director[director.find('<span>')+6:director.find('</span>')]
            info['director'] = director.strip().split(', ')
            del director

        if 'IMDb">' in data:
            imdb = data[data.find('IMDb">')+6:]
            imdb = imdb[imdb.find('">')+2:imdb.find('</a>')]
            try:
                info['rating'].update({'imdb': float(imdb.strip())})
            except:
                pass
            del imdb
            
        if 'КиноПоиск">' in data:
            kp = data[data.find('КиноПоиск">')+11:]
            kp = kp[kp.find('">')+2:kp.find('</a>')]
            try:
                info['rating'].update({'kinopoisk': float(kp.strip())})
            except:
                pass
            del kp

        if '<div>Актеры' in data:
            actor = data[data.find('<div>Актеры'):]
            actor = actor[actor.find('<a href="'):actor.find('</li>')]
            actor = actor.strip()
            
            if '>' in actor[len(actor)-1]:
                actor = actor[:actor.rfind('</a>')]

            actor_list = []
            
            if '</a>,' in actor:
                actor = actor.split('</a>,')
                
                for i in actor:
                    i = i[i.find('">')+2:].strip()
                    actor_list.append(i)

            info['cast'] = actor_list
            del actor_list, actor

        if '<div>Жанр' in data:
            genre = data[data.find('<div>Жанр'):]
            genre = genre[genre.find('<a href="'):genre.find('</li>')]
            genre = genre.strip()
            
            if '>' in genre[len(genre)-1]:
                genre = genre[:genre.rfind('</a>')]
            
            genre_list = []
            
            if '</a>' in genre:
                genre = genre.split('</a>')
                
                for i in genre:
                    i = i[i.find('">')+2:].strip()
                    genre_list.append(i)

            info['genre'] = genre_list
            del genre_list, genre

        if 'Возрастной рейтинг' in data:
            mpaa = data[data.find('Возрастной рейтинг'):]
            mpaa = mpaa[mpaa.find('<img src="/')+11:]
            mpaa = mpaa[:mpaa.find('"')]
            mpaa = mpaa[mpaa.rfind('/')+1:mpaa.rfind('.')]
            info['mpaa'] = '{}+'.format(mpaa)
            del mpaa

        if 'Качество' in data:
            quality = data[data.find('Качество:'):]
            quality = quality[quality.find('<span>')+6:]
            quality = quality[:quality.find('</span>')]
            info['quality'] = quality.strip()
            del quality

        if 'text full-text clearfix">' in data:
            plot = data[data.find('text full-text clearfix">')+25:]
            plot = plot[plot.find('<span>')+6:plot.find('</span>')]
            info['plot'] = plot.strip()
            del plot

        return info
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='Поиск', params={'mode': 'search_part'})
        self.create_line(title='Новинки', params={'mode': 'common_part', 'param': ''})
        self.create_line(title='Сериалы', params={'mode': 'common_part', 'param': 'serialy/'})
        self.create_line(title='Фильмы', params={'mode': 'common_part', 'param':'filmy/'})
        self.create_line(title='Мультфильмы', params={'mode': 'common_part', 'param': 'multfilmy/'})
        self.create_line(title='Короткометражки', params={'mode': 'common_part', 'param': 'korotkometrazhka/'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='Поиск по названию', params={'mode': 'search_part', 'param': 'search_word'})
            
            data_array = addon.getSetting('search').split('|')
            data_array.reverse()
            
            try:
                for data in data_array:
                    if data == '':
                        continue
                    self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param':'search_string', 'search_string': data})
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
                'story': self.params['search_string']
                }

            data_request = session.post(url=self.site_url, data=post_data, proxies=self.proxy_data, headers=headers)
            
            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            if sys.version_info.major > 2:
                html = data_request.text
            else:
                html = data_request.content
                
            if not '<article class="card d-flex">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
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
                        
                        info_data = self.create_info_common(data)
                        
                        label = '[B]{}[/B]{}'.format(info_data['title'], info_data['node'])

                        self.create_line(title=label, data=info_data, params={'mode': 'select_part', 'id': info_data['url']})
                    except:
                        self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
            except:
                self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
                
            self.progress_bg.close()
###################################################################################################
# доделать next page
###################################################################################################                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])

        data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
        
        if not data_request.status_code == requests.codes.ok:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        if sys.version_info.major > 2:
            html = data_request.text
        else:
            html = data_request.content
        
        if not '<article class="card d-flex">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
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
                    
                    info_data = self.create_info_common(data)
                    
                    label = '[B]{}[/B]{}'.format(info_data['title'], info_data['node'])

                    self.create_line(title=label, data=info_data, params={'mode': 'select_part', 'id': info_data['url']})
                except:
                    self.create_line(title='[COLOR=red][B]Ошибка обработки строки[/B][/COLOR]', params={})
        except:
            self.create_line(title='[COLOR=red][B]Ошибка - сообщите автору[/B][/COLOR]', params={})
            
        self.progress_bg.close()
        
        if 'jc-center ai-center">' in html:
            paginator = html[html.find('jc-center ai-center">')+21:]
            paginator = paginator[:paginator.find('</div>')]
            
            if '<a href="' in paginator:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                    int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        if not self.params['param']:
            url = self.params['id']

            data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)

            if not data_request.status_code == requests.codes.ok:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
        
            if sys.version_info.major > 2:
                html = data_request.text
            else:
                html = data_request.content

            if not '<iframe data-src="' in html:
                self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            info_data = html[html.find('class="page__header">')+21:html.find('<h2 class="page')]
            info_data = self.create_info_select(info_data)

            video_url = html[html.find('<iframe data-src="')+18:]
            video_url = video_url[:video_url.find('"')]

            data_request2 = session.get(url=video_url, proxies=self.proxy_data, headers=headers)

            player_data = data_request2.text

            data_array = player_data[player_data.find('new Playerjs(')+13:player_data.rfind(');')]

            import json

            quality_list = {}

            files = json.loads(data_array)
            
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
                    
                    
                    file_data = file_data.split(',')
                    
                    for node in file_data:
                        file_quality = node[1:node.find('p')].strip()

                        if not file_quality in quality_list:
                            quality_list.update({file_quality:[]})
                            
                        file_url = node[node.find('/'):]        
                        quality_list[file_quality].append((file_title, file_url))
            
            current_quality = addon.getSetting('quality')

            if 'Выбрать' in current_quality or current_quality not in quality_list:
                choice = list(quality_list.keys())
                
                result = self.dialog.select('Доступное качество: ', choice)
                result_quality = choice[int(result)]
            else:
                result_quality = current_quality
            
            for i in quality_list[result_quality]:
                series_label = i[0]
                series_url = 'https://redheadsound.video{}'.format(i[1])

                self.create_line(title=series_label, params={}, data=info_data, online=series_url, folder=False)
                    
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

if __name__ == "__main__":
    redheadsound = RedHeadSound()
    redheadsound.execute()
    del redheadsound

gc.collect()