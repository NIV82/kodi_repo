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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from utility import fs_enc
from utility import clean_tags

if sys.version_info.major > 2:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import parse_qs
    from urllib.request import urlopen
    from html import unescape
else:
    from urllib import urlencode
    from urllib import urlopen
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

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

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

        self.sid_file = os.path.join(self.cookie_dir, 'redheadsound.sid')
        self.proxy_data = None
        self.site_url = addon.getSetting('site_url')
        #self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'redheadsound.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools()
        del WebTools
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'redheadsound.db'))
        del DataBase
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

        self.dialog.notification(heading='Red Head Sound', message=data_array[data],icon=icon,time=3000,sound=False)
        return
#========================#========================#========================#
    def create_context(self, extended):
        context_menu = []
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=clean_part")'))

        if 'url' in list(extended.keys()):
            context_menu.append(('[COLOR=white]Обновить описание[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_serial_part&url={}")'.format(extended['url'])))
        
        # context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=information_part&param=news")'))
        # context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=authorization_part&param=update")'))
        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.redheadsound/?mode=update_database_part")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title, extended={}, params={}, folder=True, online=None):
        li = xbmcgui.ListItem(title)

        if extended:
            info = self.database.get_serial(extended['serial_id'])
            info.update({
                'rating': extended['rating'][addon.getSetting('rating')],
                'status': extended['episodes']
                })

            li.setArt({'poster': extended['poster'],'icon': extended['poster'], 'thumb': extended['poster']})
            li.setInfo(type='video', infoLabels=info)
 
        #     if watched:
        #         info['playcount'] = 1


        li.addContextMenuItems(
            self.create_context(extended=extended)
            )

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))
        
        if online:
            url = online

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, serial_url=False, update=False):
        html = self.network.get_html(serial_url)

        data = html[html.find('class="page__header">')+21:html.find('<h2 class="page')]
        
        info = {
            'serial_id': 0,
            'title': '',
            'year': 0,
            'country': '',
            'duration': 0,
            'director': '',
            'actors': '',
            'genre': '',
            'mpaa': '',
            'plot': ''
        }

        serial_id = serial_url[serial_url.rfind('/')+1:serial_url.find('-')]
        info['serial_id'] = int(serial_id)
        del serial_id
        
        title = data[data.find('<h1>')+4:data.find('</h1>')]
        if '(' in title:
            title = title[:title.find('(')]
            info['title'] = u'{}'.format(title.strip())
            del title

        if u'<div>Год выпуска' in data:
            year = data[data.find(u'<div>Год выпуска'):]
            year = year[year.find('">')+2:year.find('</a>')]
            try:
                year = int(year.strip())
            except:
                pass
            info['year'] = year
            del year

        if u'<div>страна' in data:
            country = data[data.find(u'<div>страна'):]
            country = country[country.find('">')+2:country.find('</a>')]
            info['country'] = u'{}'.format(country.strip())
            del country

        if u'<div>Продолжительность' in data:
            duration = data[data.find(u'<div>Продолжительность'):]
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

        if u'<div>Режиссер' in data:
            director = data[data.find(u'<div>Режиссер'):]
            director = director[director.find('<span>')+6:director.find('</span>')]
            info['director'] = u'{}'.format(director.strip())
            del director

        if u'<div>Актеры' in data:
            actor = data[data.find(u'<div>Актеры'):]
            actor = actor[actor.find('<a href="'):actor.find('</li>')]
            actor = u'{}'.format(actor.strip())

            if '>' in actor[len(actor)-1]:
                actor = actor[:actor.rfind('</a>')]

            actor_list = []
            
            if '</a>,' in actor:
                actor = actor.split('</a>,')
                
                for i in actor:
                    i = i[i.find('">')+2:].strip()
                    actor_list.append(i)

            info['actors'] = u','.join(actor_list)
            del actor_list, actor

        if u'<div>Жанр' in data:
            genre = data[data.find(u'<div>Жанр'):]
            genre = genre[genre.find('<a href="'):genre.find('</li>')]
            genre = u'{}'.format(genre.strip())
            
            if '>' in genre[len(genre)-1]:
                genre = genre[:genre.rfind('</a>')]
            
            genre_list = []
            
            if '</a>' in genre:
                genre = genre.split('</a>')
                
                for i in genre:
                    i = i[i.find('">')+2:].strip()
                    genre_list.append(i)

            info['genre'] = u','.join(genre_list)
            del genre_list, genre

        if u'Возрастной рейтинг' in data:
            mpaa = data[data.find(u'Возрастной рейтинг'):]
            mpaa = mpaa[mpaa.find('<img src="/')+11:]
            mpaa = mpaa[:mpaa.find('"')]
            mpaa = mpaa[mpaa.rfind('/')+1:mpaa.rfind('.')]
            info['mpaa'] = u'{}'.format(mpaa)
            del mpaa

        if 'text full-text clearfix">' in data:
            plot = data[data.find('text full-text clearfix">')+25:]
            if '<div class="link-mess">' in plot:
                plot = plot[:plot.find('<div class="link-mess">')]
            info['plot'] = u'{}'.format(clean_tags(plot))
            del plot

        if update:
            self.database.update_serial(info)
        else:
            self.database.add_serial(info)
        
        return info
#========================#========================#========================#
    def create_extended_select(self, html):
        info = {
            'serial_id': 0,
            #'url': '',
            'title': '',
            'poster': '',
            'episodes': '',
            'rating': {'imdb': 0.0, 'kinopoisk': 0.0},
        }

        serial_id = self.params['url'][self.params['url'].rfind('/')+1:]
        serial_id = serial_id[:serial_id.find('-')]
        info['serial_id'] = int(serial_id)
        del serial_id
        
        data = html[html.find('class="page__header">')+21:html.find('<h2 class="page')]
        del html
        
        title = data[data.find('<h1>')+4:data.find('</h1>')]
        if '(' in title:
            title = title[:title.find('(')]
            info['title'] = u'{}'.format(title.strip())
            del title

        if 'pmovie__poster img-fit-cover' in data:
            poster = data[data.find('<img src="/')+11:]
            poster = poster[:poster.find('"')]
            info['poster'] = u'https://redheadsound.ru/{}'.format(poster)
            del poster

        if u'<div>Эпизоды на сайте' in data:
            episodes = data[data.find(u'<div>Эпизоды на сайте'):]
            episodes = episodes[episodes.find('<span>')+6:episodes.find('</span>')]
            info['episodes'] = u'{}'.format(episodes.strip())
            del episodes

        if 'IMDb">' in data:
            imdb = data[data.find('IMDb">')+6:]
            imdb = imdb[imdb.find('">')+2:imdb.find('</a>')]
            try:
                info['rating'].update({'imdb': float(imdb.strip())})
            except:
                pass
            del imdb
            
        if u'КиноПоиск">' in data:
            kp = data[data.find(u'КиноПоиск">')+11:]
            kp = kp[kp.find('">')+2:kp.find('</a>')]
            try:
                info['rating'].update({'kinopoisk': float(kp.strip())})
            except:
                pass
            del kp
            
        del data
        return info
#========================#========================#========================#
    def create_extended_common(self, data):
        info = {
            'serial_id': 0,
            'title': '',
            'url': '',
            'poster': '',
            'season': '',
            'episodes': '',
            'rating': {'imdb': 0.0, 'kinopoisk': 0.0},
            'node': ''
        }

        title = data[data.find('title"><a href="')+16:]
        title = title[:title.find('</a>')].split('">')
        serial_id = title[0][title[0].rfind('/')+1:]
        serial_id = serial_id[:serial_id.find('-')]
        
        info['title'] = u'{}'.format(title[1])
        info['url'] = u'{}'.format(title[0])
        info['serial_id'] = int(serial_id)
        del title, serial_id
        
        poster = data[data.find('<img src="/')+11:]
        poster = poster[:poster.find('"')]
        info['poster'] = u'{}{}'.format(self.site_url, poster)
        
        del poster

        if u'Сезон:' in data:
            season = data[data.find(u'Сезон:'):]
            season = season[season.find('</span>')+7:season.find('</li>')]
            info['season'] = u'{}'.format(season.strip())
            del season

        if u'Серий на сайте:' in data:
            episodes = data[data.find(u'Серий на сайте:'):]
            episodes = episodes[episodes.find('</span>')+7:episodes.find('</li>')]
            info['episodes'] = u'{}'.format(episodes.strip())
            del episodes

        if 'IMDb">' in data:
            imdb = data[data.find('IMDb">')+6:]
            imdb = imdb[imdb.find('">')+2:imdb.find('</a>')]
            try:
                info['rating'].update({'imdb': float(imdb.strip())})
            except:
                pass
            del imdb
            
        if u'КиноПоиск">' in data:
            kp = data[data.find(u'КиноПоиск">')+11:]
            kp = kp[kp.find('">')+2:kp.find('</a>')]
            try:
                info['rating'].update({'kinopoisk': float(kp.strip())})
            except:
                pass
            del kp

        if '/serialy/' in info['url']:
            if info['season']:
                info['node'] = u' | [COLOR=blue]S{:>02}[/COLOR]'.format(info['season'])
                                        
            if info['episodes']:
                info['node'] = u'{} | [COLOR=gold]{}[/COLOR]'.format(info['node'], info['episodes'])

        if '/filmy/' in info['url']:
            info['node'] = u' | [COLOR=blue]Фильм[/COLOR]'

        if '/multfilmy/' in info['url']:
            info['node'] = u' | [COLOR=blue]Мультфильм[/COLOR]'
                
        return info
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try:
            self.database.end()
        except:
            pass
#========================#========================#========================#
    def exec_update_serial_part(self):
        self.create_info(serial_url=self.params['url'], update=True)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.create_notification('done')
        except:
            self.create_notification('err')
            pass
#========================#========================#========================#
    def exec_update_database_part(self):
        try:
            self.database.end()
        except:
            pass

        target_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/redheadsound.db'
        target_path = os.path.join(self.database_dir, 'redheadsound.db')
        
        try:
            os.remove(target_path)
        except:
            pass
        
        try:
            data = urlopen(target_url)
            chunk_size = 8192
            bytes_read = 0

            try:
                file_size = int(data.info().getheaders("Content-Length")[0])
            except:
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
                self.create_notification('err')
                pass
            
            self.progress_bg.close()
            
            self.create_notification('done')
        except:
            self.create_notification('err')
            pass
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
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            if not '<article class="card d-flex">' in html:
                self.create_line(title=u'Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
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

                        extended_info = self.create_extended_common(data)

                        self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))
                        
                        if not self.database.serial_in_db(extended_info['serial_id']):
                            self.create_info(serial_url=extended_info['url'])

                        label = u'[B]{}[/B]{}'.format(extended_info['title'], extended_info['node'])

                        self.create_line(title=label, extended=extended_info, params={'mode': 'select_part', 'url': extended_info['url']})
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
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        data_print(url)

        html = self.network.get_html(url=url)
        
        if not html:
            self.create_line(title=u'Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        if not '<article class="card d-flex">' in html:
            self.create_line(title=u'Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
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

                    extended_info = self.create_extended_common(data)

                    self.progress_bg.update(int((float(i+1) / len(data_array)) * 100), u'Обработано - {} из {}'.format(i, len(data_array)))
                    
                    if not self.database.serial_in_db(extended_info['serial_id']):
                        self.create_info(serial_url=extended_info['url'])

                    label = u'[B]{}[/B]{}'.format(extended_info['title'], extended_info['node'])

                    self.create_line(title=label, extended=extended_info, params={'mode': 'select_part', 'url': extended_info['url']})

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
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        if not self.params['param']:
            url = self.params['url']

            html = self.network.get_html(url=url)
            
            if not html:
                self.create_line(title=u'Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            if not '<iframe data-src="' in html:
                self.create_line(title=u'Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            extended_info = self.create_extended_select(html=html)

            video_url = html[html.find('<iframe data-src="')+18:]
            video_url = video_url[:video_url.find('"')]

            html2 = self.network.get_html(url=video_url)

            data_array = html2[html2.find('new Playerjs(')+13:html2.rfind(');')]

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
                
                result = self.dialog.select(u'Доступное качество: ', choice)
                result_quality = choice[int(result)]
            else:
                result_quality = current_quality
            
            for i in quality_list[result_quality]:
                series_label = i[0]
                series_url = 'https://redheadsound.video{}'.format(i[1])

                self.create_line(title=series_label, extended=extended_info, params={}, online=series_url, folder=False)
                                    
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

if __name__ == "__main__":
    redheadsound = RedHeadSound()
    redheadsound.execute()
    del redheadsound

gc.collect()