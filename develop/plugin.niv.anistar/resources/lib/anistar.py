import os
import sys
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import quote_plus
from urllib.parse import parse_qs
from urllib.parse import unquote
from html import unescape

import network
import mainplayer
import kodik
import vkparse

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.niv.anistar')

import json

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

addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))

as_ignorlist = [
    '7013','6930','6917','6974','6974','4106','1704','1229','1207','1939','1954','2282','4263','4284','4288','4352','4362','4422','4931','5129','5130',
    '5154','5155','6917','6928', '6930','6932','6936','6968','6994','7013','7055','3999','4270','4282','4296','4300','4314','4348','4349','4364','4365',
    '4366','4367','4368','4369','4374','4377','4480','4493', '4556','6036','3218','3943','3974','4000','4091','8892','8747','8913','8917']

class Anistar:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        if '0' in addon.getSetting('anistar_adult'):
            addon.setSetting('anistar_adult_pass', '')

        self.proxy_data = None#self.exec_proxy_data()
        self.site_url = self.create_site_url()
        #self.sid_file = os.path.join(self.cookie_dir, 'anistar.sid')
        self.authorization = None#self.exec_authorization_part()
        self.adult = self.create_adult()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            #headers={'Referer' : self.site_url}
        )
        del WebTools
#========================#========================#========================#
    def create_site_url(self):
        current_mirror = f"as_mirror{addon.getSetting('as_mirrormode')}"

        if not addon.getSetting(current_mirror):
            select_url = addon.getSetting('as_mirror0')
        else:
            select_url = addon.getSetting(current_mirror)

        select_url = f"https://{select_url}/"

        return select_url
#========================#========================#========================#
    def create_adult(self):
        if '0' in addon.getSetting('as_adult'):
            return False

        if '1600' in addon.getSetting('as_adultpass'):
            return True
        else:
            return False
#========================#========================#========================#
    def create_context(self, params):
        context_menu = []
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=blue]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.anistar/?mode=clean_part")'))

        if 'id' in params and 'common_part' in self.params['mode']:
            if '0' in addon.getSetting('as_playmode'):
                context_menu.append(('Открыть Торрент', 'Container.Update("plugin://plugin.niv.anistar/?{}&node=torrent")'.format(urlencode(params))))
            if '1' in addon.getSetting('as_playmode'):
                context_menu.append(('Открыть Онлайн', 'Container.Update("plugin://plugin.niv.anistar/?{}&node=online")'.format(urlencode(params))))

        return context_menu
#========================#========================#========================#
    def create_line(self, title, anime_id=None, params={}, folder=True, **info):
        li = xbmcgui.ListItem(title)

        if info:
            try:
                cover = info.pop('cover')
            except:
                cover = None

            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})
            
            try:
                info['title'] = info['sorttitle']
            except:
                pass

            videoinfo = li.getVideoInfoTag()
            videoinfo.setTitle(info['title'])
            #videoinfo.setSortTitle(info['sorttitle'])
            videoinfo.setGenres(info['genre'])
            videoinfo.setPlot(info['plot'])

            videoinfo.setRating(info['rating'])
            videoinfo.setYear(info['year'])
            videoinfo.setDirectors(info['directors'])
            videoinfo.setCountries(info['country'])

        li.addContextMenuItems(self.create_context(params))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        if 'tam' in params:
            label = u'{} | {}'.format(info['title'], title)

            info_data = repr({'title':label})
            url='plugin://plugin.video.tam/?mode=open&info={}&url={}'.format(quote_plus(info_data), quote(params['tam']))
        else:
            url = '{}?{}'.format(sys.argv[0], urlencode(params))

        #xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
        return
#========================#========================#========================#
    def create_info(self, data):
        from utility import clean_tags

        info = {
            'anime_id': '',
            'cover': '',
            'title': '',
            'sorttitle': '',
            'genre': [],
            'rating': 0,
            'year': 0,
            'country': [],
            'directors':[],
            'plot': ''
        }

        anime_id = data[:data.find('>')]
        if not '/' in anime_id:
            return False
        anime_id = anime_id[anime_id.rfind('/')+1:]
        anime_id = anime_id[:anime_id.find('-')]
        
        info['anime_id'] = anime_id

        info['cover'] = '{}/uploads/posters/{}/original.jpg'.format(
            self.site_url, info['anime_id']
        )

        title = data[data.find('>')+1:]
        title = title[:title.find('</a>')]
        if '/' in title:
            title = title[:title.find('/')]
        title = unescape(title).strip()
        info['sorttitle'] = u'{}'.format(title)

        info['title'] = info['sorttitle']
        
        if 'itemprop="ratingValue">' in data:
            rating = data[data.find('itemprop="ratingValue">')+23:]
            rating = rating[:rating.find('</span>')]
            try:
                rating = float(rating.replace(',','.'))
            except:
                rating = 0
            info['rating'] = rating

        data = data[data.find('<li>')+4:]

        if u'Год выпуска:' in data:
            year = data[data.find('/">')+3:]
            year = year[:year.find('</a>')]
            try:
                year = int(year)
            except:
                year = 0

            info['year'] = year

        if u'Страна:' in data:
            country = data[data.find(u'Страна:')+7:]
            country = country[:country.find('</li>')]
            country = clean_tags(country).replace(', ',',')
            info['country'] = country.split(',')

        if u'Жанр:' in data:
            genre = data[data.find(u'Жанр:')+5:]
            genre = genre[:genre.find('</li>')]
            genre = clean_tags(genre).replace(', ',',')
            info['genre'] = genre.split(',')

        if u'Режиссёр:' in data:
            director = data[data.find(u'Режиссёр:')+9:]
            director = director[:director.find('</li>')]
            director = clean_tags(director).replace(', ',',')
            info['directors'] = director.split(',')
        
        if u'Автор оригинала:' in data:
            author = data[data.find(u'Автор оригинала:')+16:]
            author = author[:author.find('</li>')]
            author = clean_tags(author).replace(', ',',')
            info['directors'].extend(author.split(','))
        
        if '<div class="descripts">' in data:
            plot = data[data.find('<div class="descripts">')+23:]

            if '</p>' in plot:
                plot = plot[:plot.rfind('</p>')]
            else:
                if '<!--spoiler_text_end-->' in plot:
                    plot = plot[:plot.find('<!--spoiler_text_end-->')]
                else:
                    plot = plot[:plot.find('</div>')]

            if '<p class="reason">' in plot:
                annonce = plot[plot.find('<p class="reason">')+18:]
                info['title'] = u'{} | {}'.format(info['title'], annonce)
                plot = plot[:plot.find('<p class="reason">')]

            plot = unescape(plot)
            plot = plot.replace('<!--spoiler_title-->','\n')
            plot = plot.replace('<!--spoiler_title_end-->','\n')
            plot = plot.replace('<br />','\n')
            plot = clean_tags(plot)
            if '<!' in plot:
                plot = plot[:plot.find('<!')]
            info['plot'] = u'{}'.format(plot.strip())

        return info
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    # def exec_authorization_part(self):
    #     if '0' in addon.getSetting('anistar_auth_mode'):
    #         return False

    #     if not addon.getSetting('anistar_username') or not addon.getSetting('anistar_password'):
    #         self.params['mode'] = 'addon_setting'
    #         self.dialog.notification(heading='Авторизация',message='Введите Логин и Пароль',icon=icon,time=3000,sound=False)
    #         return

    #     if 'renew' in self.params['param']:
    #         addon.setSetting('anistar_auth', 'false')
    #         addon.setSetting('anistar_session','')
            
    #     try: temp_session = float(addon.getSetting('anistar_session'))
    #     except: temp_session = 0
        
    #     if time.time() - temp_session > 43200:
    #         addon.setSetting('anistar_session', str(time.time()))            
    #         try: os.remove(self.sid_file)
    #         except: pass            
    #         addon.setSetting('anistar_auth', 'false')

    #     auth_post_data = {
    #         "login_name": addon.getSetting('anistar_username'),
    #         "login_password": addon.getSetting('anistar_password'),
    #         "login": "submit"
    #         }

    #     import pickle

    #     if 'true' in addon.getSetting('anistar_auth'):
    #         try:
    #             with open(self.sid_file, 'rb') as read_file:
    #                 session.cookies.update(pickle.load(read_file))
    #             auth = True
    #         except:
    #             try:
    #                 r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)
    #             except Exception as e:
    #                 if '10054' in str(e):
    #                     self.exec_mirror_part()
    #                     r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)

    #             if 'dle_user_id' in str(r.cookies):
    #                 with open(self.sid_file, 'wb') as write_file:
    #                     pickle.dump(r.cookies, write_file)
                        
    #                 session.cookies.update(r.cookies)
    #                 auth = True
    #             else:
    #                 auth = False
    #     else:
    #         try:
    #             r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)
    #         except Exception as e:
    #             if '10054' in str(e):
    #                 self.exec_mirror_part()
    #                 r = session.post(url=self.site_url, proxies=self.proxy_data, data=auth_post_data, headers=headers)

    #         if 'dle_user_id' in str(r.cookies):
    #             with open(self.sid_file, 'wb') as write_file:
    #                 pickle.dump(r.cookies, write_file)
                    
    #             session.cookies.update(r.cookies)
    #             auth = True
    #         else:
    #             auth = False

    #     if not auth:
    #         self.params['mode'] = 'addon_setting'
    #         self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=icon,time=3000,sound=False)
    #         return
    #     else:
    #         addon.setSetting('anistar_auth', str(auth).lower())

    #     return auth
#========================#========================#========================#
    # def exec_favorites_part(self):
    #     url = '{}engine/ajax/favorites.php?fav_id={}&action={}&skin=new36'.format(self.site_url, self.params['id'], self.params['node'])

    #     if 'plus' in self.params['node']:
    #         try:
    #             data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
    #             self.dialog.notification(heading='Избранное',message='Выполнено',icon=icon,time=3000,sound=False)
    #         except:
    #             self.dialog.notification(heading='Избранное',message='Ошибка',icon=icon,time=3000,sound=False)

    #     if 'minus' in self.params['node']:
    #         try:
    #             data_request = session.get(url=url, proxies=self.proxy_data, headers=headers)
    #             self.dialog.notification(heading='Избранное',message='Выполнено',icon=icon,time=3000,sound=False)
    #         except:
    #             self.dialog.notification(heading='Избранное',message='Ошибка',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('as_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=1000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        # if self.authorization:
        #     self.create_line(title=u'[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title='[B]Поиск[/B]', params={'mode': 'search_part'})
        self.create_line(title='[B]Расписание[/B]', params={'mode': 'schedule_part'})

        self.create_line(title='[B]Новинки[/B]', params={'mode': 'common_part', 'param': 'new'})
        self.create_line(title='[B]RPG[/B]', params={'mode': 'common_part', 'param': 'rpg'})
        if self.adult:
            self.create_line(title='[B]Хентай[/B]', params={'mode': 'common_part', 'param': 'hentai/'})
        self.create_line(title='[B]Дорамы[/B]', params={'mode': 'common_part', 'param': 'dorams'})
        self.create_line(title='[B]Мультфильмы[/B]', params={'mode': 'common_part', 'param': 'cartoons'})
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = addon.getSetting('as_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': data})

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                data_array = addon.getSetting('as_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array.append(self.params['search_string'])
                addon.setSetting('as_search', '|'.join(data_array))
                self.params['param'] = 'search_string'
            else:
                return False

        if 'search_string' in self.params['param']:
            if not self.params['search_string']:
                return False

            search_string = self.params['search_string']

            search_string = search_string.encode('cp1251')

            search_string = quote(search_string)

            url = '{}/index.php?do=search'.format(self.site_url)

            post_data = [
                ('do', 'search'),
                ('subaction', 'search'),
                ('search_start', self.params['page']),
                ('full_search', 1),
                #('result_from', 1),
                ('story', search_string),
                ('catlist[]', 35),
                ('catlist[]', 175),
                ('catlist[]', 39),
                ('catlist[]', 113),
                ('catlist[]', 76),
            ]

            html = self.network.get_bytes(url=url, post=post_data)

            if not html['reason'] == 'OK':
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            html = html['content'].decode('windows-1251').encode('utf-8')
            html = html.decode('utf-8')

            data_array = html[html.find('title_left">')+12:]
            data_array = data_array[:data_array.rfind('<div class="panel-bottom-shor">')]
            data_array = data_array.split('<div class="title_left">')
            data_array.pop(0)

            if len(data_array) < 1:
                self.create_line(title='Контент отсутствует', folder=False)
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            try:
                for data in data_array:
                    try:
                        if u'/m/">Манга</a>' in data:
                            self.create_line(title='Манга, пропускаем обработку', folder=False)
                            continue
                        
                        if u'>Хентай</a>' in data:
                            if self.adult:
                                pass
                            else:
                                self.create_line(title='*** Взрослый контент (18+), закрыто настройками', folder=False)
                                continue

                        info = self.create_info(data)
                        
                        anime_id = info.pop('anime_id')
                        
                        if anime_id in as_ignorlist:
                            self.create_line(title='*** Блок рекламы и подобного, не обрабатывается', folder=False)
                            continue

                        label = info.pop('title')
                        info_data = json.dumps(info)
                        
                        self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                    except:
                        self.create_line(title='Ошибка обработки строки - сообщите автору')
            except:
                self.create_line(title='Ошибка обработки блока - сообщите автору')

            if 'button_nav r"><a' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'search_string': self.params['search_string'],'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_schedule_part(self):
        url = '{}/raspisanie-vyhoda-seriy-ongoingov.html'.format(self.site_url)
        html = self.network.get_bytes(url=url)
        
        if not html['reason'] == 'OK':
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
            
        html = html['content'].decode('windows-1251').encode('utf-8')
        html = html.decode('utf-8')

        week_title = []

        today_title = html[html.find('<span>[')+7:]
        today_title = today_title[:today_title.find(']</span>')]
        today_title = u'Выйдут Сегодня - {}'.format(today_title)
        week_title.append(today_title)

        week_list = html[html.find('<div class=\'cal-list\'>')+22:]
        week_list = week_list[:week_list.find('</div>')]
        week_list = week_list.strip()
        week_list = week_list.splitlines()

        for day in week_list:
            day = day[day.find('>')+1:]
            day = day[:day.find('</span>')]
            day = day.replace('<span>', ' - ')
            day = week_title.append(
                u'{}'.format(day)
            )

        data_array = html[html.find('<div class="top-w" >')+20:]
        data_array = data_array[:data_array.find('function calanime')]
        data_array = data_array.split('<div id="day')

        for data in data_array:
            day = data[:data.find('"')]
            try:
                day = int(day)
                data = data[data.find('<div class="top-w" >')+20:]
            except:
                day = 0
            
            week_day = week_title[day]
            day_label = u'[B][COLOR=lime]{}[/COLOR][/B]'.format(week_day)
            self.create_line(title=day_label, folder=False)

            data = data.split('<div class="top-w" >')

            for d in data:                
                title = d[d.find('title-top">')+11:]
                title = title[:title.find('</span>')]
                if '/' in title:
                    title = title[:title.find('/')]

                if '<smal>' in d:
                    annonce = d[d.find('<smal>')+6:]
                    annonce = annonce[:annonce.find('</smal>')]
                    title = u'{} | [COLOR=gold]{}[/COLOR]'.format(title, annonce)
                
                label = u'{}'.format(title)

                self.create_line(title=label, folder=False)

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}/{}/page/{}/'.format(self.site_url, self.params['param'],self.params['page'])

        html = self.network.get_bytes(url=url)

        if not html['reason'] == 'OK':
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        html = html['content'].decode('windows-1251').encode('utf-8')
        html = html.decode('utf-8')

        data_array = html[html.find('title_left">')+12:]
        data_array = data_array[:data_array.rfind('<div class="panel-bottom-shor">')]
        data_array = data_array.split('<div class="title_left">')

        if len(data_array) < 1:
            self.create_line(title='Контент отсутствует', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        try:
            for data in data_array:
                try:
                    if u'/m/">Манга</a>' in data:
                        self.create_line(title='Манга, пропускаем обработку', folder=False)
                        continue

                    if u'>Хентай</a>' in data:
                        if self.adult:
                            pass
                        else:
                            self.create_line(title='*** Взрослый контент (18+), закрыто настройками', folder=False)
                            continue

                    info = self.create_info(data)
                    
                    anime_id = info.pop('anime_id')

                    if anime_id in as_ignorlist:
                        self.create_line(title='*** Блок рекламы и подобного, не обрабатывается', folder=False)
                        continue

                    label = info.pop('title')
                    info_data = json.dumps(info)
                    
                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part', 'param': info_data}, **info)
                except:
                    self.create_line(title='Ошибка обработки строки - сообщите автору')
        except:
            self.create_line(title='Ошибка обработки блока - сообщите автору')
            
        if 'button_nav r"><a' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        if '0' in addon.getSetting('as_playmode'):
            if 'node' in self.params and self.params['node'] == 'torrent':
                self.params['mode'] = 'torrent_part'
                self.exec_torrent_part()
            else:            
                self.params['mode'] = 'online_part'
                self.exec_online_part()
        if '1' in addon.getSetting('as_playmode'):
            if 'node' in self.params and self.params['node'] == 'online':
                self.params['mode'] = 'online_part'
                self.exec_online_part()
            else:
                self.params['mode'] = 'torrent_part'
                self.exec_torrent_part()
        return
#========================#========================#========================#
    def exec_online_part(self):
        global info
        info = json.loads(self.params['param'])

        url = '{}/index.php?newsid={}'.format(self.site_url, self.params['id'])

        page_data = self.network.get_bytes(url=url)

        if not page_data['reason'] == 'OK':
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        html = page_data['content']

        result = html[html.find(b'<div class="vide_be'):]
        result = result[:result.find(b'<span style=')]
        result = result[result.find(b'<div class="video_as"'):]
        result = result.decode(page_data['charset'])

        vurl = []

        data_array = result.split('</div>')
        for data in data_array:
            if 'src="' in data:
                data = data[data.find('src="')+5:]
                data = data[:data.find('"')]
                if 'about:' in data:
                    continue

                vurl.append(data)

        if vurl:
            vurl = vurl[0]

        if 'kodik.' in vurl:
            self._parse_kodiktrbox(klink=vurl)
        elif 'videoas.' in vurl:
            self._parse_mainplayer(mlink=vurl)
        elif 'playlist_anistar2' in vurl:
            self._parse_anistarplayer(alink=vurl)
        else:
            self.create_line(title='Не обраружен плеер или обработчик', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        xbmcplugin.endOfDirectory(handle, succeeded=True)

    def _parse_anistarplayer(self, alink=None):
        if not 'https' in alink:
            alink = f"{self.site_url}{alink}"

        playlist = self.network.get_bytes(url=alink)

        if not playlist['reason'] == 'OK':
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        play_data = playlist['content']

        if not play_data.find(b'<div id="PlayList">') > -1:
            self.create_line(title='Видео не обнаружено', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        data_array = play_data[play_data.find(b'<div id="PlayList">')+19:]
        data_array = data_array[:data_array.find(b'</div>')]
        data_array = data_array[:data_array.rfind(b'</span>')+1]
        data_array = data_array.strip()
        data_array = data_array.decode(playlist['charset'])
        data_array = data_array.splitlines()

        for pl in data_array:
            node_title = pl[pl.find('">')+2:]
            node_title = node_title[:node_title.find('<')]

            if 'vkvideo' in pl:
                node_title = f"{node_title} | vk"
            elif 'vk.com' in pl:
                node_title = f"{node_title} | vk_old"
            elif 'rutube' in pl:
                node_title = f"{node_title} | rutube"
            elif 'sibnet' in pl:
                node_title = f"{node_title} | sibnet"
            else:
                node_title = f"{node_title} | uknown"

            #node_link = pl[pl.find("playvk(")+7:]
            node_link = pl[pl.find('(')+1:]
            node_link = node_link[:node_link.find(',')]
            node_link = node_link.replace("'", '').replace('"', '')
            node_link = node_link.strip()

            self.create_line(
                title=node_title,
                anime_id=self.params['id'],
                params={
                    'mode': 'play_part',
                    'param': node_link,
                    'id': self.params['id']
                    },
                folder=False,
                **info
                )

    def _parse_mainplayer(self, mlink):
        if not mlink.startswith('https'):
            if mlink.startswith('/'):
                mlink = mlink[1:]
            mlink = f"{self.site_url}{mlink}"

        mp_data = mainplayer.parse_mainplayer(mlink=mlink)

        for node in mp_data:
            self.create_line(
                title=node['title'],
                anime_id=self.params['id'],
                params={
                    'mode': 'play_part',
                    'param': node['file'] or node['file_h'],
                    'id': self.params['id']
                    },
                folder=False,
                **info
                )

    def _parse_kodiktrbox(self, klink):
        klink = klink[klink.find('//')+2:]

        if klink.endswith('&episode=1'):
            klink = klink[0:len(klink)-10]

        khost = klink.split('/')

        klink = f"https://{klink}"

        trbox = kodik.get_translate_box(url=klink)

        for tr in trbox:
            turl = f"https://{khost[0]}/serial/{tr['media_id']}/{tr['media_hash']}/{khost[4]}"
            tlabel = f"{tr['title']} | {tr['translation_type']} | EP-{tr['episode_count']}"

            self.create_line(
                title=tlabel,
                anime_id=self.params['id'],
                params={
                    'mode': 'kodik_part',
                    'param': turl,
                    'info': json.dumps(info),
                    'id': self.params['id']
                    },
                **info
            )

    def _parse_sibnet(self, url):
        result = {'url':'Видео недоступно', 'thumb':'', 'type': 'sibnet'}

        sibnet_data = self.network.get_bytes(url)

        if not sibnet_data['reason'] == 'OK':
            return result

        html = sibnet_data['content']

        try:
            if b'<div class=videostatus><p>' in html:
                s = html[html.find(b'<div class=videostatus><p>')+26:]
                s = s[:s.find(b'</p>')]
                s = s.decode(sibnet_data['charset'])
            elif b'src([{src: "' in html:
                s = html[html.find(b'src([{src: "')+12:]
                s = s[:s.find(b'"')]
                s = s.decode(sibnet_data['charset'])
                result['url'] = f"https://video.sibnet.ru{s}|referer={url}"

                if b'meta property="og:image" content="' in html:
                    thumb = html[html.find(b'meta property="og:image" content="')+34:]
                    thumb = thumb[:thumb.find(b'"')]
                    thumb = thumb.decode(sibnet_data['charset'])
                    result['thumb'] = f"https:{thumb}"
        except:
            pass

        return result

    def exec_kodik_part(self):
        info = json.loads(self.params['info'])
        serial_url = self.params['param']
        playlist_array = kodik.get_playlist(serial_url)

        for node in playlist_array:
            self.create_line(
                title=node['title'],
                anime_id=self.params['id'],
                params={
                    'mode': 'play_part',
                    'param': node['file'],
                    'id': self.params['id']
                    },
                folder=False,
                **info
                )

        xbmcplugin.endOfDirectory(handle, succeeded=True)

    def exec_torrent_part(self):
        info = json.loads(self.params['param'])

        url = '{}/index.php?newsid={}'.format(self.site_url, self.params['id'])

        html = self.network.get_bytes(url=url)

        if not html['reason'] == 'OK':
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        html = html['content'].decode('windows-1251').encode('utf-8')
        html = html.decode('utf-8')

        if not '<div class="title">' in html:
            self.create_line(title='Контент отсутствует', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        data_array = html[html.find('<div class="title">')+19:]
        data_array = data_array[:data_array.rfind('<div class="bord_a1">')]
        data_array = data_array.split('<div class="title">')

        if len(data_array) < 1:
            self.create_line(title='Контент отсутствует', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        dubs = addon.getSetting('as_dubbing')

        try:
            for data in data_array:
                try:
                    title = data[data.find('info_d1">')+9:]
                    title = title[:title.find('<')]

                    if '1' in dubs:
                        if u'Многоголос' in title:
                            continue
                    elif '2' in dubs:
                        if not u'Многоголос' in title:
                            continue
                    else:
                        pass

                    torrent_url = data[data.find('gettorrent.php?id=')+18:]
                    torrent_url = torrent_url[:torrent_url.find('">')]
                    torrent_url = u'{}/engine/gettorrent.php?id={}'.format(self.site_url, torrent_url)

                    seed = ''
                    if u'Раздают:' in data:
                        seed = data[data.find(u'Раздают:')+8:]
                        seed = seed[seed.find('">')+2:]
                        seed = seed[:seed.find('<')]
                        seed = u' | seed: {}'.format(seed)

                    leech = ''
                    if u'Качают:' in data:
                        leech = data[data.find(u'Качают:')+7:]
                        leech = leech[leech.find('">')+2:]
                        leech = leech[:leech.find('<')]
                        if seed:
                            seed = u'{} , leech: {}'.format(seed, leech)

                    label = u'{}{}'.format(title, seed)
                    self.create_line(title=label, params={'tam': torrent_url}, **info)
                except:
                    self.create_line(title='Ошибка обработки строки - сообщите автору')
        except:
            self.create_line(title='Ошибка обработки блока - сообщите автору')

        xbmcplugin.endOfDirectory(handle)
        return
#========================#========================#========================#
    def _parse_playurl(self, data):
        vsd = data[data.find('360=')+4:]
        vsd = vsd[:vsd.find('&')]

        vhd = data[data.find('720=')+4:]
        if '&' in vhd:
            vhd = vhd[:vhd.find('&')]

        #vhd = f"{vhd}|Referer:{self.site_url}"
        vhd = f"{vhd}"

        return {'SD': vsd, 'HD': vhd, 'type': 'mainplayer'}

    def _validate_url(self, link):
        if 'vkvideo' in link:
            vkp = vkparse.ParseVK(vkvideo_url=link)
            return vkp.get_playdata()
        elif 'kodik.' in link:
            vkp = kodik.get_playurl(url=link)
            return vkp
        elif 'sibnet' in link:
            vkp = self._parse_sibnet(url=link)
            return vkp
        else:
            parse_url = self._parse_playurl(link)
            return parse_url

    def _download_playlist(self, video_url):
        network.set_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
            'Referer': f"{self.site_url}"
            })

        playlist_path = f"{addon_data_dir}\playlist"
        try:
            os.remove(playlist_path)
        except:
            pass

        download_path = self.network.get_file(
            url=video_url,
            fpath=playlist_path
            )

        return download_path

#========================#========================#========================#
    def exec_play_part(self):
        video_playdata = self._validate_url(self.params['param'])

        if video_playdata['type'] == 'vk':
            ctab = {'SD': 'url480', 'HD': 'url720', 'FHD': 'url1080', 'HLS': 'hls'}
            quality = ctab[addon.getSetting('vkquality')]
            video_url = video_playdata[quality]

        if video_playdata['type'] == 'mainplayer':
            webvideo_url = video_playdata[addon.getSetting('quality')]

            video_url = self._download_playlist(video_url=webvideo_url)

        if video_playdata['type'] == 'kodik':
            quality = addon.getSetting('kodikquality')
            if not quality:
                quality = '720'
            video_url = video_playdata[quality]

        if video_playdata['type'] == 'sibnet':
            video_url = video_playdata['url']

        li = xbmcgui.ListItem(path=video_url)

        if '0' in addon.getSetting('inputstream_adaptive'):
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.stream_selection_type', 'ask-quality')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)

def start():
    anistar = Anistar()
    anistar.execute()