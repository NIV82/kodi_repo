# -*- coding: utf-8 -*-

import os
import sys
import time

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
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlencode
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape  

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.niv.animeportal')

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

if version >= 19:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

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

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'portal': 'anistar'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        if '0' in addon.getSetting('anistar_adult'):
            addon.setSetting('anistar_adult_pass', '')

        self.proxy_data = None#self.exec_proxy_data()
        self.site_url = self.create_site_url()
        #self.sid_file = os.path.join(self.cookie_dir, '{}.sid'.format(self.params['portal']))
        self.authorization = None#self.exec_authorization_part()
        self.adult = self.create_adult()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            portal='anistar'
            )
        del WebTools
#========================#========================#========================#
    def create_mirror(self):
        try:
            mirror_time = float(addon.getSetting('as_mirrortime'))
        except:
            mirror_time = 0

        from network import get_web

        if time.time() - mirror_time > 86400:
            addon.setSetting('as_mirrortime', str(time.time()))

            html = get_web(url='https://vpn.anistar.org', bytes=False)

            mirror_url = html[html.find(u'><a href="')+10:]
            mirror_url = mirror_url[:mirror_url.find('"')]
            mirror_url = mirror_url.strip()

            addon.setSetting('as_mirror1', mirror_url)
        else:
            if addon.getSetting('as_mirror1'):
                mirror_url = addon.getSetting('as_mirror1')
            else:
                html = get_web(url='https://vpn.anistar.org', bytes=False)

                mirror_url = html[html.find(u'><a href="')+10:]
                mirror_url = mirror_url[:mirror_url.find('"')]
                mirror_url = mirror_url.strip()

                addon.setSetting('as_mirror1', mirror_url)
        return mirror_url
#========================#========================#========================#
    def create_site_url(self):
        site_url = addon.getSetting('as_mirror0')

        cm = addon.getSetting('as_mirrormode')

        if '0' in cm:
            return site_url

        if '1' in cm:
            current_mirror = 'as_mirror1'

            if not addon.getSetting(current_mirror):
                try:
                    self.create_mirror()
                    site_url =  addon.getSetting(current_mirror)
                    return site_url
                except:
                    self.dialog.notification(
                        heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
                addon.setSetting('as_mirrormode', '0')
                return site_url
            else:
                try:
                    mirror_time = float(addon.getSetting('as_mirrortime'))
                except:
                    mirror_time = 0

                if time.time() - mirror_time > 86400:
                    try:
                        self.create_mirror()
                        site_url =  addon.getSetting(current_mirror)
                        return site_url
                    except:
                        self.dialog.notification(
                            heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
                        addon.setSetting('as_mirrormode', '0')
                        return site_url

                site_url =  addon.getSetting(current_mirror)

        return site_url
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
            context_menu.append(('[COLOR=blue]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anistar")'))

        if 'id' in params and 'common_part' in self.params['mode']:
            if '0' in addon.getSetting('as_playmode'):
                context_menu.append(('Открыть Торрент', 'Container.Update("plugin://plugin.niv.animeportal/?{}&node=torrent")'.format(urlencode(params))))
            if '1' in addon.getSetting('as_playmode'):
                context_menu.append(('Открыть Онлайн', 'Container.Update("plugin://plugin.niv.animeportal/?{}&node=online")'.format(urlencode(params))))

        # if self.authorization and not self.params['param'] == '':
        #     context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anistar")'.format(anime_id)))
        #     context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anistar")'.format(anime_id)))

        # context_menu.append(('[COLOR=darkorange]Обновить Зеркала[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anistar")'))
        # context_menu.append(('[COLOR=darkorange]Обновить Авторизацию[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=authorization_part&param=renew&portal=anistar")'))
        # context_menu.append(('[COLOR=darkorange]Обновить Прокси[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=proxy_data&param=renew&portal=anistar")'))
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

            if version == 20:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setTitle(info['title'])
                #videoinfo.setSortTitle(info['sorttitle'])
                videoinfo.setGenres(info['genre'])
                videoinfo.setPlot(info['plot'])

                videoinfo.setRating(info['rating'])
                videoinfo.setYear(info['year'])
                videoinfo.setDirectors(info['directors'])
                videoinfo.setCountries(info['country'])
            else:
                li.setInfo(type='video', infoLabels=info)

        params['portal'] = self.params['portal']

        li.addContextMenuItems(self.create_context(params))

        if folder==False:
            li.setProperty('isPlayable', 'true')

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

            if version <= 18:
                search_string = search_string.decode('utf-8').encode('cp1251')
            else:
                search_string = search_string.encode('cp1251')

            search_string = quote(search_string)

            url = '{}/index.php?do=search'.format(self.site_url)

            post_data = 'do=search&subaction=search&search_start={}&full_search=1\
            &story={}&catlist%5B%5D=35&catlist%5B%5D=175&catlist%5B%5D=39\
            &catlist%5B%5D=113&catlist%5B%5D=76'.format(
                self.params['page'], search_string)

            html = self.network.get_bytes(url=url, post=post_data)

            if not html:
                self.create_line(title='Ошибка получения данных', folder=False)
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            html = html.decode('windows-1251').encode('utf-8')
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
        
        if not html:
            self.create_line(title='Ошибка получения данных', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
            
        html = html.decode('windows-1251').encode('utf-8')
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

        if not html:
            self.create_line(title='Ошибка получения данных', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        html = html.decode('windows-1251').encode('utf-8')
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
        info = json.loads(self.params['param'])

        url = '{}/index.php?newsid={}'.format(self.site_url, self.params['id'])

        html = self.network.get_bytes(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        html = html.decode('windows-1251').encode('utf-8')
        html = html.decode('utf-8')

        if 'vid_2" style="display:block;"><iframe src="' in html:
            video_url = html[html.find('<iframe src="')+13:]
            video_url = video_url[:video_url.find('"')]
            video_url = '{}{}'.format(self.site_url, video_url)
        elif 'id="vid_5"><iframe src="' in html:
            video_url = html[html.find('id="vid_5"><iframe src="')+24:]
            video_url = video_url[:video_url.find('"')]
            if 'youtube.com' in video_url:
                self.create_line(title='youtube ссылка - обработчик пока отсутствует', folder=False)
                xbmcplugin.endOfDirectory(handle)
                return
        else:
            self.create_line(title='Онлайн ссылки не обраружены', folder=False)
            xbmcplugin.endOfDirectory(handle)
            return

        html = self.network.get_html(url=video_url)

        if not html:
            self.create_line(title='Ошибка получения данных', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        data_array = html[html.find('playlst=[')+9:]
        data_array = data_array[:data_array.find('];')]
        data_array = data_array[:data_array.rfind('},')]
        data_array = data_array.split('},')

        if len(data_array) < 1:
            self.create_line(title='Контент отсутствует', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        current_quality = (addon.getSetting('as_quality'))
        dubs = addon.getSetting('as_dubbing')

        try:
            for data in data_array:
                try:
                    title = data[data.find('title:"')+7:]
                    title = title[:title.find('"')]

                    dubb = data[data.find('type_dub:')+9:]
                    dubb = dubb[:dubb.find(',')]
                    dubb = dubb.replace('\'','').strip()

                    if '1' in dubs:
                        if '2' in dubb:
                            continue
                    elif '2' in dubs:
                        if '1' in dubb:
                            continue
                    else:
                        pass
                    
                    video_quality = {'360':'', '720':''}

                    file_url = data[data.find('file:"')+6:]
                    file_url = unquote(file_url)

                    if '360=' in file_url:
                        q = file_url[file_url.find('360=')+4:]
                        q = q[:q.find('&')]
                        video_quality['360'] = q

                        if '720=' in file_url:
                            video_quality['720'] = q.replace('360','720')

                    label = u'{}'.format(title)

                    if video_quality[current_quality]:
                        episode_hls = video_quality[current_quality]
                    elif video_quality['720']:
                        episode_hls = video_quality['720']
                        label = u'{} | 720'.format(label)
                    elif video_quality['360']:
                        episode_hls = video_quality['360']
                        label = u'{} | 360'.format(label)
                    else:
                        self.create_line(title='Ссылка для проигрывателя не обнаружена', folder=False)
                        xbmcplugin.endOfDirectory(handle)
                        continue

                    self.create_line(title=label, anime_id=self.params['id'], params={'mode': 'play_part', 'param': episode_hls, 'id': self.params['id']}, folder=False, **info)
                except:
                    self.create_line(title='Ошибка обработки строки - сообщите автору')
        except:
            self.create_line(title='Ошибка обработки блока - сообщите автору')

        xbmcplugin.endOfDirectory(handle)
        return
#========================#========================#========================#
    def exec_torrent_part(self):
        info = json.loads(self.params['param'])

        url = '{}/index.php?newsid={}'.format(self.site_url, self.params['id'])

        html = self.network.get_bytes(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', folder=False)
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        html = html.decode('windows-1251').encode('utf-8')
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
    def exec_play_part(self):
        li = xbmcgui.ListItem(path=self.params['param'])

        if '0' in addon.getSetting('as_inputstream'):
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
            li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)
#========================#========================#========================#
def start():
    anistar = Anistar()
    anistar.execute()