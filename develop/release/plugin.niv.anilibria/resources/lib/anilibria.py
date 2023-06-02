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
    #from urllib.request import urlopen
    #from urllib.request import Request
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    #from urllib import urlopen
    #from urllib2 import Request
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape  

version = xbmc.getInfoLabel('System.BuildVersion')[:2]
try:
    version = int(version)
except:
    version = 0

from utility import clean_tags

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

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

addon = xbmcaddon.Addon(id='plugin.niv.anilibria')

if sys.version_info.major > 2:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

class Anilibria:
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = None#self.create_proxy_data()
        #self.mirror = self.create_mirror()
        self.site_url = self.create_site_url()
        #self.sid_file = os.path.join(addon_data_dir, 'alv1.sid')
        #self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            # auth_usage=bool(addon.getSetting('alv1_authmode') == '1'),
            # auth_status=bool(addon.getSetting('auth') == 'true'),
            proxy_data = self.proxy_data
            )
        # self.network.auth_post_data = urlencode(
        #     {'login_name': addon.getSetting('alv1_username'),
        #     'login_password': addon.getSetting('alv1_password'),
        #     'login': 'submit'}
        #     )
        #self.network.auth_url = self.site_url
        #self.network.sid_file = self.sid_file
        del WebTools
#========================#========================#========================#
    def create_proxy_data(self):
        if '0' in addon.getSetting('alv1_unblock'):
            return None

        if sys.version_info.major > 2:
            from urllib.request import urlopen
        else:
            from urllib import urlopen

        try:
            proxy_time = float(addon.getSetting('alv1_proxytime'))
        except:
            proxy_time = 0

        if time.time() - proxy_time > 604800:
            addon.setSetting('alv1_proxytime', str(time.time()))
            proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()

            try:
                proxy_pac = str(proxy_pac, encoding='utf-8')
            except:
                pass

            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            addon.setSetting('alv1_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if addon.getSetting('alv1_proxy'):
                proxy_data = {'https': addon.getSetting('alv1_proxy')}
            else:
                proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()
                
                try:
                    proxy_pac = str(proxy_pac, encoding='utf-8')
                except:
                    pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                addon.setSetting('alv1_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    # def create_mirrror_url(self):
    #     site_url = addon.getSetting('anilibria_mirror0')
    #     current_mirror = 'anilibria_mirror{}'.format(addon.getSetting('anilibria_mirrormode'))        

    #     if current_mirror == 'anilibria_mirror0':
    #         return site_url

    #     if not addon.getSetting(current_mirror):
    #         try:
    #             self.create_mirror()
    #             site_url =  addon.getSetting(current_mirror)
    #             return site_url
    #         except:
    #             self.dialog.notification(
    #                 heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
    #             addon.setSetting('anilibria_mirrormode', '0')

    #             return site_url
    #     else:
    #         try:
    #             mirror_time = float(addon.getSetting('anilibria_mirror_time'))
    #         except:
    #             mirror_time = 0

    #         if time.time() - mirror_time > 259200:
    #             try:
    #                 self.create_mirror()
    #                 site_url =  addon.getSetting(current_mirror)
    #                 return site_url
    #             except:
    #                 self.dialog.notification(
    #                     heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
    #                 addon.setSetting('anilibria_mirrormode', '0')
    #                 return site_url

    #         site_url =  addon.getSetting(current_mirror)

    #     return site_url
    
    def create_site_url(self):
        site_url = addon.getSetting('alv1_mirror0')
        current_mirror = 'alv1_mirror{}'.format(addon.getSetting('alv1_mirrormode'))        
        
        if current_mirror == 'alv1_mirror0':
            return site_url

        if not addon.getSetting(current_mirror):
                try:
                    self.create_mirror()
                    site_url =  addon.getSetting(current_mirror)
                    return site_url
                except:
                    self.dialog.notification(
                        heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
                    addon.setSetting('alv1_mirrormode', '0')

                    return site_url
        else:
            site_url =  addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_mirror(self):
        try:
            mirror_time = float(addon.getSetting('alv1_mirrortime'))
        except:
            mirror_time = 0

        from network import get_web

        if time.time() - mirror_time > 259200:
            addon.setSetting('alv1_mirrortime', str(time.time()))

            html = get_web(url='https://darklibria.it/redirect/mirror/1')

            mirror_url = html[html.find('canonical" href="')+17:]
            mirror_url = mirror_url[:mirror_url.find('"')]
            addon.setSetting('alv1_mirror1', mirror_url)
        else:
            if addon.getSetting('alv1_mirror1'):
                mirror_url = addon.getSetting('alv1_mirror1')
            else:
                html = get_web(url='https://darklibria.it/redirect/mirror/1')

                mirror_url = html[html.find('canonical" href="')+17:]
                mirror_url = mirror_url[:mirror_url.find('"')]
                addon.setSetting('alv1_mirror1', mirror_url)

        return mirror_url
    
    # def create_mirror(self):
    #     try:
    #         mirror_time = float(addon.getSetting('alv1_mirrortime'))
    #     except:
    #         mirror_time = 0

    #     if time.time() - mirror_time > 259200:
    #         addon.setSetting('alv1_mirrortime', str(time.time()))

    #         from network import WebTools
    #         net = WebTools()
    #         del WebTools

    #         html = net.get_html(url='https://darklibria.it/redirect/mirror/1')

    #         mirror_url = html[html.find('canonical" href="')+17:]
    #         mirror_url = mirror_url[:mirror_url.find('"')]
    #         addon.setSetting('alv1_mirror1', mirror_url)
    #     else:
    #         if addon.getSetting('alv1_mirror1'):
    #             mirror_url = addon.getSetting('alv1_mirror1')
    #         else:
    #             from network import WebTools
    #             net = WebTools()
    #             del WebTools

    #             html = net.get_html(url='https://darklibria.it/redirect/mirror/1')

    #             mirror_url = html[html.find('canonical" href="')+17:]
    #             mirror_url = mirror_url[:mirror_url.find('"')]
    #             addon.setSetting('alv1_mirror1', mirror_url)

    #     return mirror_url
#========================#========================#========================#
    def create_info(self, data):
        info = dict.fromkeys(
            ['id', 'title', 'sorttitle', 'cover', 'genre', 'year', 'plot'], '')
        
        info['id'] = data['id']
        info['sorttitle'] = u'{}'.format(data['names'][0])
        info['cover'] = u'{}{}'.format(self.site_url, data['poster'])

        announce = ''
        if 'announce' in data.keys():
            if data['announce']:
                announce = u' | [COLOR=gold]{}[/COLOR]'.format(data['announce'])

        series = ''
        try:
            if data['series']:
                series = u' | [COLOR=gold]{}[/COLOR]'.format(data['series'])
        except:
            pass

        info['title'] = u'{}{}{}'.format(info['sorttitle'], series, announce)
        info['genre'] = data['genres']
        info['year'] = data['year']

        voices = ''
        try:
            if data['voices']:
                voices = u'\n\nНад релизом работали: {}'.format(
                    ','.join(data['voices'])
                )
        except:
            pass

        info['plot'] = u'{}{}'.format(
            clean_tags(data['description']), voices
        )

        return info
#========================#========================#========================#
    def create_context(self, anime_id=None):
        context_menu = []        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(
                ('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.anilibria/?mode=clean_part")'))
        if anime_id:
            if '0' in addon.getSetting('alv1_playmode'):
                context_menu.append(('Открыть Торрент', 'Container.Update("plugin://plugin.niv.anilibria/?mode=select_part&id={}&param=0")'.format(anime_id)))
            if '1' in addon.getSetting('alv1_playmode'):
                context_menu.append(('Открыть Онлайн', 'Container.Update("plugin://plugin.niv.anilibria/?mode=select_part&id={}&param=1")'.format(anime_id)))
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
                videoinfo.setSortTitle(info['sorttitle'])
                videoinfo.setYear(int(info['year']))
                videoinfo.setGenres(info['genre'])
                videoinfo.setPlot(info['plot'])
            else:
                li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        if 'tam' in params:
            url='plugin://plugin.video.tam/?mode=open&url={}'.format(quote(params['tam'])) 
        else:
            url = '{}?{}'.format(sys.argv[0], urlencode(params))

        #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('alv1_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=1000,sound=False)
            pass
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B]Поиск[/B]', params={'mode': 'search_part'})
        self.create_line(title='[B]Расписание[/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B]Новое[/B]', params={'mode': 'updates_part'})
        self.create_line(title='[B]Популярное[/B]', params={'mode': 'favorites_part'})
        self.create_line(title='[B]Каталог[/B]', params={'mode': 'catalog_part'})
        # if self.authorization:
        #     self.create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
        try:
            self.database.end()
        except:
            pass
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = addon.getSetting('alv1_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param': 'search_string', 'search_string': data})

        if 'search_word' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading(u'Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = skbd.getText()
                data_array = addon.getSetting('alv1_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), self.params['search_string'])
                addon.setSetting('alv1_search', data_array)
                self.params['param'] = 'search_string'
            else:
                return False
            
        if 'search_string' in self.params['param']:
            if not self.params['search_string']:
                return False

            url = '{}/public/api/index.php'.format(self.site_url)
            post_data = {
                "query":"search",
                "search": self.params['search_string'],
                "filter":"id,names,series,poster,genres,voices,year,description",
                }
            post_data = urlencode(post_data)
            html = self.network.get_bytes(url=url, post=post_data)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            import json
            anime_data = json.loads(html)

            if not anime_data['status']:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            if len(anime_data['data']) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            try:
                for data in anime_data['data']:
                    try:
                        info = self.create_info(data)

                        anime_id = info.pop('id')
                        label = info.pop('title')

                        self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_schedule_part(self):
        url = '{}/public/api/index.php'.format(self.site_url)
        post_data = {
            "query":"schedule",
            "filter": "id,names,announce,poster,genres,voices,year,description",
            }
        post_data = urlencode(post_data)
        html = self.network.get_bytes(url=url, post=post_data)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        import json
        anime_data = json.loads(html)

        if not anime_data['status']:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        week = [u'Понедельник', u'Вторник', u'Среда',
        u'Четверг', u'Пятница', u'Суббота', u'Воскресенье']

        try:
            for week_day in anime_data['data']:
                day = week[int(week_day['day'])-1]

                self.create_line(
                    title=u'[COLOR=blue][B]Релизы - {} :[/B][/COLOR]'.format(day), folder=False)
                
                try:
                    for data in week_day['items']:
                        try:
                            info = self.create_info(data)

                            anime_id = info.pop('id')
                            label = info.pop('title')

                            self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                        except:
                            self.create_line(title='Ошибка строки - сообщите автору')
                except:
                    self.create_line(title='Ошибка блока - сообщите автору')
        except:
            self.create_line(title='Ошибка Расписания - сообщите автору')
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_updates_part(self):
        url = '{}/public/api/index.php'.format(self.site_url)
        post_data = {
            "query":"list",
            "page":self.params['page'],
            "perPage":"50",
            "filter": "id,names,series,poster,genres,voices,year,description"
            }
        post_data = urlencode(post_data)
        html = self.network.get_bytes(url=url, post=post_data)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        import json            
        anime_data = json.loads(html)

        if not anime_data['status']:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        array = anime_data['data']['items']
        
        if len(array) < 1:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        try:
            for data in array:
                try:
                    info = self.create_info(data)

                    anime_id = info.pop('id')
                    label = info.pop('title')

                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                except:
                    self.create_line(title='Ошибка строки - сообщите автору')
        except:
            self.create_line(title='Ошибка блока - сообщите автору')

        try:
            current_page = anime_data['data']['pagination']['page']
            all_pages = anime_data['data']['pagination']['allPages']

            if current_page < all_pages:
                label = u'Страница [COLOR=gold]{}[/COLOR] из {} | Следующая - [COLOR=gold]{}[/COLOR]'.format(
                    current_page, all_pages, int(self.params['page']) + 1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        except:
            pass

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_favorites_part(self):
        url = '{}/public/api/index.php'.format(self.site_url)
        post_data = {
            "query":"catalog",
            "xpage":"catalog",
            "sort":"2",
            "page":self.params['page'],
            #"perPage":"50",
            "filter":"id,names,series,poster,genres,voices,year,description",
            }
        post_data = urlencode(post_data)
        html = self.network.get_bytes(url=url, post=post_data)
        
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        import json            
        anime_data = json.loads(html)

        if not anime_data['status']:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        array = anime_data['data']['items']
        
        if len(array) < 1:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        try:
            for data in array:
                try:
                    info = self.create_info(data)

                    anime_id = info.pop('id')
                    label = info.pop('title')

                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                except:
                    self.create_line(title='Ошибка строки - сообщите автору')
        except:
            self.create_line(title='Ошибка блока - сообщите автору')

        if len(array) == 12:
            label = u'Страница [COLOR=gold]{}[/COLOR] | Следующая - [COLOR=gold]{}[/COLOR]'.format(
                self.params['page'], int(self.params['page']) + 1)                
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_catalog_part(self):
        anilibria_genre = ['', 'Боевые искусства', 'Вампиры', 'Демоны', 'Детектив', 'Драма', 'Игры', 'Исторический', 
                           'Киберпанк', 'Комедия', 'Магия', 'Меха', 'Мистика', 'Музыка', 'Повседневность', 'Приключения', 
                           'Психологическое', 'Романтика', 'Сверхъестественное', 'Сёдзе', 'Сёдзе-ай', 'Сейнен', 'Сёнен', 
                           'Спорт', 'Супер сила', 'Триллер', 'Ужасы', 'Фантастика', 'Фэнтези', 'Школа', 'Экшен', 'Этти']
        anilibria_year = ['', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', 
                          '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2001', '1999', '1998', '1996']
        anilibria_season = ['', 'зима', 'весна', 'лето', 'осень']
        anilibria_sort = {'Новое': '1', 'Популярное': '2'}
        anilibria_status = {'В работе': '1', 'Завершен': '2'}

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('alv1_genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('alv1_year')), params={'mode': 'catalog_part', 'param': 'year'})            
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('alv1_season')), params={'mode': 'catalog_part', 'param': 'season'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('alv1_sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('alv1_status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'genre' in self.params['param']:
            result = self.dialog.select('Жанр:', anilibria_genre)
            addon.setSetting(id='alv1_genre', value=anilibria_genre[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Год:', anilibria_year)
            addon.setSetting(id='alv1_year', value=anilibria_year[result])

        if 'season' in self.params['param']:
            result = self.dialog.select('Сезон:', anilibria_season)
            addon.setSetting(id='alv1_season', value=anilibria_season[result])

        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(anilibria_sort.keys()))
            addon.setSetting(id='alv1_sort', value=tuple(anilibria_sort.keys())[result])

        if 'status' in self.params['param']:
            result = self.dialog.select('Статус релиза:', tuple(anilibria_status.keys()))
            addon.setSetting(id='alv1_status', value=tuple(anilibria_status.keys())[result])

        if 'catalog' in self.params['param']:
            genre = ''
            if addon.getSetting('alv1_genre'):
                genre = addon.getSetting('alv1_genre')

            year = ''
            if addon.getSetting('alv1_year'):
                year = addon.getSetting('alv1_year')

            season = ''
            if addon.getSetting('alv1_season'):
                season = addon.getSetting('alv1_season')
            
            sort = anilibria_sort[addon.getSetting('alv1_sort')]
            status = anilibria_status[addon.getSetting('alv1_status')]

            url = '{}/public/api/index.php'.format(self.site_url)
            post_data = '\
                query=catalog\
                &xpage=catalog\
                &page={}\
                &filter=id%2Cnames%2Cseries%2Cposter%2Cgenres%2Cvoices%2Cyear%2Cdescription\
                &search=%7B%22year%22%3A%22{}%22%2C%22genre%22%3A%22{}%22%2C%22season%22%3A%22{}%22%7D\
                &sort={}\
                &finish={}'.format(self.params['page'], year, quote(genre), quote(season), sort, status)
            post_data = post_data.replace('%27','%22').replace(' ','')

            html = self.network.get_bytes(url=url, post=post_data)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            import json            
            anime_data = json.loads(html)

            if not anime_data['status']:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            array = anime_data['data']['items']

            if len(array) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            try:
                for data in array:
                    try:
                        info = self.create_info(data)

                        anime_id = info.pop('id')
                        label = info.pop('title')

                        self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

            if len(array) == 12:
                label = u'Страница [COLOR=gold]{}[/COLOR] | Следующая - [COLOR=gold]{}[/COLOR]'.format(
                    self.params['page'], int(self.params['page']) + 1)                
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        if '0' in addon.getSetting('alv1_playmode'):
            if '0' in self.params['param']:
                self.params['mode'] = 'torrent_part'
                self.exec_torrent_part()
            else:
                self.params['mode'] = 'online_part'
                self.exec_online_part()
        if '1' in addon.getSetting('alv1_playmode'):
            if '1' in self.params['param']:
                self.params['mode'] = 'online_part'
                self.exec_online_part()
            else:
                self.params['mode'] = 'torrent_part'
                self.exec_torrent_part()
#========================#========================#========================#
    def exec_online_part(self):
        url = '{}/public/api/index.php'.format(self.site_url)
        post_data = {
            "query":"release",
            "id":self.params['id'],
            "filter": "id,names,series,poster,genres,voices,year,description,playlist"
            }
        post_data = urlencode(post_data)
        html = self.network.get_bytes(url=url, post=post_data)

        import json
        anime_data = json.loads(html)

        array = anime_data['data']
        playlist = array.pop('playlist')

        info = self.create_info(array)

        anime_id = info.pop('id')
        info.pop('title')

        current_quality = (addon.getSetting('alv1_quality')).lower()

        playlist.reverse()
        for node in playlist:
            if node['name']:
                label = u'Серия {} - {}'.format(node['id'], node['name'])
            else:
                label = u'{}'.format(node['title'])
            
            if current_quality in list(node.keys()):
                ep_hls = node[current_quality]
            elif 'fullhd' in list(node.keys()):
                label = u'{} | {}'.format(label, 'FULLHD')
                ep_hls = node['fullhd']
            elif 'hd' in list(node.keys()):
                label = u'{} | {}'.format(label, 'HD')
                ep_hls = node['hd']
            elif 'sd' in list(node.keys()):
                label = u'{} | {}'.format(label, 'SD')
                ep_hls = node['sd']
            else:
                ep_hls = ''
            
            #info['sorttitle'] = label
            if not ep_hls:
                label = u'Нет видео под серию'
                self.create_line(title=label, folder=False)
            else:
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'play_part', 'param': ep_hls, 'id': anime_id}, folder=False, **info)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_play_part(self):
        li = xbmcgui.ListItem(path=self.params['param'])

        if '0' in addon.getSetting('alv1_inputstream'):
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
            li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
#========================#========================#========================#
    def exec_torrent_part(self):
        url = '{}/public/api/index.php'.format(self.site_url)
        post_data = {
            "query":"release",
            "id":self.params['id'],
            "filter": "id,names,series,poster,genres,voices,year,description,torrents"
            }
        post_data = urlencode(post_data)
        html = self.network.get_bytes(url=url, post=post_data)

        import json
        anime_data = json.loads(html)

        array = anime_data['data']
        torrentlist = array.pop('torrents')

        info = self.create_info(array)

        anime_id = info.pop('id')
        info.pop('title')

        for node in torrentlist:
            #torrent_id = node['id']
            
            torrent_peer = ''
            if 'leechers' in node.keys() and 'seeders' in node.keys():
                torrent_peer = u' | [COLOR=lime]{}[/COLOR] / [COLOR=red]{}[/COLOR]'.format(
                    node['seeders'], node['leechers'])

            torrent_quality = ''
            if 'quality' in node.keys():
                if node['quality']:
                    torrent_quality = u' | [COLOR=blue]{}[/COLOR]'.format(node['quality'])

            torrent_series = ''
            if 'series' in node.keys():
                if node['series']:
                    torrent_series = u'Серии: {}'.format(node['series'])

            #torrent_size = node['size']
            torrent_url = u'{}{}'.format(self.site_url, node['url'])

            label = u'{}{}{}'.format(torrent_series, torrent_quality, torrent_peer)

            self.create_line(title=label, anime_id=anime_id, params={'tam': torrent_url}, **info)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
def start():
    anilibria = Anilibria()
    anilibria.execute()
    del anilibria