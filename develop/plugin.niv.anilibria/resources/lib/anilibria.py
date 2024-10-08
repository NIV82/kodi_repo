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

py_version = sys.version_info.major

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

if py_version < 3:
    from urllib import urlencode
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote
    from urlparse import parse_qs
else:
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import parse_qs
    from urllib.parse import unquote

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.niv.anilibria')

if py_version < 3:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))
else:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
           
class Anilibria:
    # xbmcplugin.setContent(handle, 'tvshows')
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)
            
        self.params = {'mode': 'main_part', 'param': '', 'page': '1'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = None
        self.site_url = 'https://api.anilibria.tv/v3/'
        self.mirror = self.create_mirrror_url()

        self.proxy_data = self.create_proxy_data()
        #self.sid_file = os.path.join(addon_data_dir, 'anilibria.sid')
        #self.authorization = self.exec_authorization_part()
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=bool(addon.getSetting('auth_mode') == '1'),
            auth_status=bool(addon.getSetting('auth') == 'true'),
            proxy_data = self.proxy_data
            )
        # self.network.auth_post_data = urlencode(
        #     {'login_name': addon.getSetting(username'),
        #     'login_password': addon.getSetting('password'),
        #     'login': 'submit'}
        #     )
        #self.network.auth_url = self.site_url
        #self.network.sid_file = self.sid_file
        del WebTools
#========================#========================#========================#
    def create_mirrror_url(self):

        site_url = addon.getSetting('mirror_0')

        cm = addon.getSetting('mirror_mode')
        if cm:
            current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))
        else:
            current_mirror = ''

        if not current_mirror:
            return site_url
        
        if current_mirror == 'mirror_0':
            return site_url

        if not addon.getSetting(current_mirror):
            try:
                self.create_mirror()
                site_url =  addon.getSetting(current_mirror)
                return site_url
            except:
                self.dialog.notification(
                    heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
                addon.setSetting('mirror_mode', '0')

                return site_url
        else:
            try:
                mirror_time = float(addon.getSetting('mirror_time'))
            except:
                mirror_time = 0

            if time.time() - mirror_time > 259200:
                try:
                    self.create_mirror()
                    site_url =  addon.getSetting(current_mirror)
                    return site_url
                except:
                    self.dialog.notification(
                        heading='Получение Адреса', message='Ошибка получения зеркала', icon=icon, time=1000, sound=False)
                    addon.setSetting('mirror_mode', '0')
                    return site_url

            site_url =  addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_mirror(self):
        try:
            mirror_time = float(addon.getSetting('mirror_time'))
        except:
            mirror_time = 0

        from network import get_web

        if time.time() - mirror_time > 259200:
            addon.setSetting('mirror_time', str(time.time()))

            html = get_web(url='https://darklibria.it/redirect/mirror/1', bytes=False)

            mirror_url = html[html.find('canonical" href="')+17:]
            mirror_url = mirror_url[:mirror_url.find('"')]
            addon.setSetting('mirror_1', mirror_url)
        else:
            if addon.getSetting('mirror_1'):
                mirror_url = addon.getSetting('mirror_1')
            else:
                html = get_web(url='https://darklibria.it/redirect/mirror/1', bytes=False)

                mirror_url = html[html.find('canonical" href="')+17:]
                mirror_url = mirror_url[:mirror_url.find('"')]
                addon.setSetting('mirror_1', mirror_url)

        return mirror_url
#========================#========================#========================#
    def create_context(self, anime_id=None):
        context_menu = []
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.anilibria/?mode=clean_part")'))

        if anime_id:
            if '0' in addon.getSetting('playmode'):
                context_menu.append(('Открыть Торрент', 'Container.Update("plugin://plugin.niv.anilibria/?mode=select_part&id={}&param=0")'.format(anime_id)))
            if '1' in addon.getSetting('playmode'):
                context_menu.append(('Открыть Онлайн', 'Container.Update("plugin://plugin.niv.anilibria/?mode=select_part&id={}&param=1")'.format(anime_id)))

        # if self.authorization:
        #     if self.params['mode'] in ('common_part','schedule_part','favorites_part'):
        #         context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}&param=PUT&portal={}")'.format(anime_id, self.params['portal'])))
        #         context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}&param=DELETE&portal={}")'.format(anime_id, self.params['portal'])))
        #     if 'catalog_part' in self.params['mode'] and 'catalog' in self.params['param'] or 'search_part' in self.params['mode'] and 'search_string' in self.params['param']:
        #         context_menu.append(('[COLOR=cyan]Избранное - Добавить[/COLOR]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}&param=PUT&portal={}")'.format(anime_id, self.params['portal'])))
        #         context_menu.append(('[COLOR=cyan]Избранное - Удалить[/COLOR]', 'Container.Update("plugin://plugin.niv.anilibria/?mode=favorites_part&id={}&param=DELETE&portal={}")'.format(anime_id, self.params['portal'])))

        return context_menu
#========================#========================#========================#
    def create_line(self, title, anime_id=None, params={}, folder=True, **info):
        li = xbmcgui.ListItem(title)

        if info:
            try:
                cover = info.pop('cover')
            except:
                cover = None

            try:
                info['title'] = info['sorttitle']
            except:
                pass

            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})

            # if py_version > 2:
            #     videoinfo = li.getVideoInfoTag()
            #     videoinfo.setTitle(info.get('title')) #title	string - Title.
            #     videoinfo.setOriginalTitle(info.get('originaltitle')) #string - Original title.
            #     videoinfo.setPlot(info.get('plot')) #plot	string - Plot
            #     videoinfo.setTagLine(info.get('tagline')) #tagLine	string - Tagline
            #     videoinfo.setStudios(info.get('studio')) #studios	list - Studios
            #     videoinfo.setGenres(info.get('genre')) #genre	list - Genres.
            #     videoinfo.setCountries(info.get('country')) #countries	list - Countries.
            #     videoinfo.setWriters(info.get('credits')) #writers	list - Writers.
            #     videoinfo.setDirectors(info.get('director')) #setDirectors(directors)
            #     #videoinfo.setYear() #year	integer - Year.

            #     videoinfo.setPremiered(info.get('premiered')) #premiered	string - Premiere date
            #     videoinfo.setTags(info.get('tag')) #tags	list - Tags
            #     videoinfo.setMpaa(info.get('mpaa')) #mpaa	string - MPAA rating
            #     videoinfo.setTrailer(info.get('trailer')) #[string] Trailer path
            #     videoinfo.setDuration(info.get('duration')) #[unsigned int] Duration
            # else:
            #     li.setInfo(type='video', infoLabels=info)

            if py_version > 2:
            #if version == 20:
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

        # if 'tam' in params:
        #     label = u'{} | {}'.format(info['title'], title)

        #     #if version <= 18:
        #     if py_version < 3:
        #         try:
        #             label = label.encode('utf-8')
        #         except:
        #             pass

        #     info_data = repr({'title':label})
        #     url='plugin://plugin.video.tam/?mode=open&info={}&url={}'.format(quote_plus(info_data), quote(params['tam']))
        # else:
        #     url = '{}?{}'.format(sys.argv[0], urlencode(params))
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=folder)
        return
#========================#========================#========================#
    def create_info(self, node):
        info = dict.fromkeys(
            ['id', 'title', 'sorttitle', 'cover', 'genre', 'year', 'plot'], '')

        info['id'] = node['id']
        info['sorttitle'] = node['names']['ru']
        info['cover'] = u'{}{}'.format(self.mirror, node['posters']['original']['url'])

        announce = ''
        try:
            if node['announce']:
                announce = u'{}'.format(node['announce'])
        except:
            pass
        
        ep_last = ''
        try:
            if node['player']['episodes']['last']:
                ep_last = u'{}'.format(node['player']['episodes']['last'])
        except:
            pass

        ep_all = ''
        try:
            if node['type']['episodes']:
                ep_all = u' из {}'.format(node['type']['episodes'])
        except:
            pass
        
        episodes = ''
        if ep_all and ep_last:
            episodes = u' | [COLOR=gold]{}{}[/COLOR]'.format(ep_last, ep_all)
        if announce:
            episodes = u' | [COLOR=gold]{}[/COLOR]'.format(announce)

        info['title'] = u'{}{}'.format(node['names']['ru'], episodes)
        info['genre'] = node['genres']
        info['year'] = node['season']['year']

        ext_info = ''
        try:
            team_ru = {
                'voice': 'Озвучивание', 
                'translator': 'Перевод', 
                'editing': 'Редактирование', 
                'decor': 'Оформление',
                'timing': 'Синхронизация'
                }

            for i in node['team']:
                keys_ru = team_ru[i]
                values = node['team'][i]

                if values:
                    values = ', '.join(values)
                    ext_info = u'{}{}: {}\n'.format(ext_info, keys_ru, values)

            ext_info = u'\n\n{}'.format(ext_info)
        except:
            pass

        info['plot'] = u'{}{}'.format(node['description'], ext_info)

        return info
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    def create_proxy_data(self):
        if '0' in addon.getSetting('unblock'):
            return None

        import unblock

        try:
            proxy_time = float(addon.getSetting('proxy_time'))
        except:
            proxy_time = 0

        if time.time() - proxy_time > 604800:
            addon.setSetting('proxy_time', str(time.time()))
            
            proxy = unblock.get_antizapret_proxy()
            #proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()

            # try:
            #     proxy_pac = str(proxy_pac, encoding='utf-8')
            # except:
            #     pass

            #proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            addon.setSetting('proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if addon.getSetting('proxy'):
                proxy_data = {'https': addon.getSetting('proxy')}
            else:
                #proxy_pac = urlopen("https://antizapret.prostovpn.org:8443/proxy.pac").read()
                
                # try:
                #     proxy_pac = str(proxy_pac, encoding='utf-8')
                # except:
                #     pass

                #proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                proxy = unblock.get_antizapret_proxy()

                addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    # def exec_authorization_part(self):
    #     if '0' in addon.getSetting('{}_auth_mode'.format(self.params['portal'])):
    #         return False

    #     if not addon.getSetting('{}_username'.format(self.params['portal'])) or not addon.getSetting('{}_password'.format(self.params['portal'])):
    #         self.params['mode'] = 'addon_setting'
    #         self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=icon,time=3000,sound=False)
    #         return

    #     if 'renew_auth' in self.params['param']:
    #         addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
    #         addon.setSetting('{}_session'.format(self.params['portal']),'')
    #         addon.setSetting('{}_session_id'.format(self.params['portal']),'')
            
    #     try: temp_session = float(addon.getSetting('{}_session'.format(self.params['portal'])))
    #     except: temp_session = 0
        
    #     if time.time() - temp_session > 604800:
    #         addon.setSetting('{}_session'.format(self.params['portal']), str(time.time()))            
    #         try: os.remove(self.sid_file)
    #         except: pass            
    #         addon.setSetting('{}_auth'.format(self.params['portal']), 'false')
        
    #     if 'true' in addon.getSetting('auth'):
    #         return True
    #     else:
    #         auth_url = 'https://www.anilibria.tv/public/login.php'
        
    #         auth_post_data = {
    #             'mail': addon.getSetting('{}_username'.format(self.params['portal'])),
    #             'passwd': addon.getSetting('{}_password'.format(self.params['portal']))
    #         }
            
    #         try:
    #             r = requests.post(url=auth_url, proxies=self.proxy_data, data=auth_post_data)
    #         except:
    #             addon.setSetting('unblock','true')
    #             self.proxy_data = self.exec_proxy_data()
    #             r = requests.post(url=auth_url, proxies=self.proxy_data, data=auth_post_data)
    #             addon.setSetting('unblock','false')
            
    #         response = r.text
            
    #         if 'success' in response:
    #             auth = True
    #             sessionid = response[response.find('sessionId":"')+12:]
    #             sessionid = sessionid[:sessionid.find('"')]
                
    #             addon.setSetting('alv3_sessionid', sessionid)
    #         else:
    #             auth = False
    
    #         if not auth:
    #             self.params['mode'] = 'addon_setting'
    #             self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=icon,time=3000,sound=False)
    #             return
    #         else:
    #             addon.setSetting('{}_auth'.format(self.params['portal']), str(auth).lower())

    #     return auth
#========================#========================#========================#
    # def exec_favorites_part(self):
    #     if not self.params['param']:
    #         session_id = addon.getSetting('alv3_sessionid')
    #         filters = '&filter=id,posters.medium,type,player.series.string'
    #         url = '{}/v2/getFavorites?session={}{}'.format(self.site_url, session_id, filters)

    #         html = self.network.get_html(url=url)

    #         if not html:
    #             self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
    #             xbmcplugin.endOfDirectory(handle, succeeded=True)
    #             return
            
    #         if not '},{' in html:
    #             if not '}]' in html:
    #                 self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
    #                 xbmcplugin.endOfDirectory(handle, succeeded=True)
    #                 return
                
    #         self.progress_bg.create('{}'.format(self.params['portal'].upper()), 'Инициализация')
            
    #         data_array = html.split('},{')

    #         i = 0
            
    #         for data in data_array:
    #             anime_id = data[data.find(':')+1:data.find(',')]
    #             type_code = data[data.find('code":')+6:data.find(',"string')]
    #             series_max = data[data.find('series":')+8:data.find(',"length')]
    #             series_cur = data[data.rfind('string":"')+9:data.rfind('"}')]    
    #             poster = data[data.find('url":"')+6:data.find('","raw_base64')]

    #             if type_code == '0':
    #                 series_cur = u'Фильм'
    #                 series_max = ''
                    
    #             i = i + 1
    #             p = int((float(i) / len(data_array)) * 100)
                
    #             self.progress_bg.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))
            
    #             if not self.database.anime_in_db(anime_id):
    #                 self.create_info(anime_id)

    #             label = self.create_title(anime_id=anime_id,series_cur=series_cur,series_max=series_max)
    #             self.create_line(title=label, anime_id=anime_id, cover=poster ,params={'mode': 'select_part', 'id': anime_id})

    #         self.progress_bg.close()

    #         if len(data_array) >= int(self.params['limit']):
    #             label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)
    #             self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
    #         xbmcplugin.endOfDirectory(handle, succeeded=True)        
    #     else:
    #         if 'PUT' in self.params['param']:
    #             url = '{}addFavorite?session={}&title_id={}'.format(
    #                 self.site_url, addon.getSetting('alv3_sessionid'), self.params['id'])
    #             data_request = session.put(url=url, proxies=self.proxy_data, headers=headers)

    #         if 'DELETE' in self.params['param']:
    #             url = '{}delFavorite?session={}&title_id={}'.format(
    #                 self.site_url, addon.getSetting('alv3_sessionid'), self.params['id'])
    #             data_request = session.delete(url=url, proxies=self.proxy_data, headers=headers)

    #         html = data_request.text
                
    #         if 'success":true' in html:
    #             self.dialog.notification(heading='Избранное',message='Выполнено',icon=icon,time=3000,sound=False)
    #         else:
    #             self.dialog.notification(heading='Избранное',message='Ошибка',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=1000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B]Поиск[/B]', params={'mode': 'search_part'})
        self.create_line(title='[B]Расписание[/B]', params={'mode': 'schedule_part'})
        self.create_line(title='[B]Новое за месяц[/B]', params={'mode': 'updates_part'})
        self.create_line(title='[B]Популярное[/B]', params={'mode': 'favorites_part'})
        self.create_line(title='[B]Каталог[/B]', params={'mode': 'catalog_part'})
        # if self.authorization:
        #     self.create_line(title='[B][COLOR=white]Избранное[/COLOR][/B]', params={'mode': 'favorites_part'})
        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = addon.getSetting('search').split('|')
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
                data_array = addon.getSetting('search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array.append(self.params['search_string'])
                addon.setSetting('search', '|'.join(data_array))
                self.params['param'] = 'search_string'
            else:
                return False
            
        if 'search_string' in self.params['param']:
            if not self.params['search_string']:
                return False

            api_filter = '&filter=id,names.ru,posters.original,type.episodes,genres,team,season.year,description,player.episodes.last'
            url = '{}searchTitles?search={}&limit=-1{}'.format(
                self.site_url, quote(self.params['search_string']), api_filter)

            html = self.network.get_bytes(url=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return
            
            array = json.loads(html)

            self.progress_bg.create('AniLibria', 'Инициализация')

            try:
                for x, data in enumerate(array['list']):
                    try:
                        info = self.create_info(data)

                        anime_id = info.pop('id')
                        label = info.pop('title')

                        self.progress_bg.update(int((float(x+1) / len(array['list'])) * 100), u'Обработано - {} из {}'.format(x, len(array['list'])))

                        self.create_line(title=label, anime_id=anime_id ,params={'id': anime_id, 'mode': 'select_part'}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

            self.progress_bg.close()

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_schedule_part(self):
        api_filter = '?filter=id,names.ru,announce,posters.original,genres,team,season.year,description'
        url = '{}title/schedule{}'.format(self.site_url, api_filter)

        html = self.network.get_bytes(url=url)
        
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        week_array = json.loads(html)

        week = [u'Понедельник',u'Вторник',u'Среда',u'Четверг',u'Пятница',u'Суббота',u'Воскресенье']

        try:
            for days in week_array:
                day = week[days['day']]
                self.create_line(
                    title=u'[COLOR=lime]Релизы - {} :[/COLOR]'.format(day), folder=False)

                try:
                    for data in days['list']:
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

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_updates_part(self):
        api_filter = '&filter=id,names.ru,posters.original,type.episodes,genres,team,season.year,description,player.episodes.last'
        url = '{}title/updates?since={}&limit=-1{}'.format(
            self.site_url, int(time.time() - 30*24*60*60), api_filter)

        html = self.network.get_bytes(url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        array = json.loads(html)

        self.progress_bg.create('AniLibria', 'Инициализация')

        try:
            for x, data in enumerate(array['list']):
                try:
                    info = self.create_info(data)

                    anime_id = info.pop('id')
                    label = info.pop('title')

                    self.progress_bg.update(int((float(x+1) / len(array['list'])) * 100), u'Обработано - {} из {}'.format(x, len(array['list'])))

                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                except:
                    self.create_line(title='Ошибка строки - сообщите автору')
        except:
            self.create_line(title='Ошибка блока - сообщите автору')

        self.progress_bg.close()

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_favorites_part(self):
        api_filter = '&filter=id,names.ru,posters.original,type.string,type.episodes,genres,team,season.year,description,player.episodes.last'
        api_page = '&page={}&items_per_page=50'.format(self.params['page'])
        url = '{}title/search/advanced?query={{id}}&order_by=in_favorites{}&sort_direction=1{}'.format(
            self.site_url, api_filter, api_page)
        html = self.network.get_bytes(url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        array = json.loads(html)

        self.progress_bg.create('AniLibria', 'Инициализация')

        try:
            for x, data in enumerate(array['list']):
                try:
                    info = self.create_info(data)

                    anime_id = info.pop('id')
                    label = info.pop('title')

                    self.progress_bg.update(int((float(x+1) / len(array['list'])) * 100), u'Обработано - {} из {}'.format(x, len(array['list'])))

                    self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                except:
                    self.create_line(title='Ошибка строки - сообщите автору')
        except:
            self.create_line(title='Ошибка блока - сообщите автору')

        self.progress_bg.close()
        
        try:
            if int(array['pagination']['current_page']) < int(array['pagination']['pages']):
                label = u'Страница [COLOR=gold]{}[/COLOR] из {} | Следующая - [COLOR=gold]{}[/COLOR]'.format(
                    array['pagination']['current_page'], array['pagination']['pages'], int(self.params['page']) + 1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
        except:
            pass

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_catalog_part(self):
        anilibria_genre = ['', 'Боевые искусства', 'Вампиры', 'Демоны', 'Детектив', 'Драма', 'Игры', 'Исторический', 
                           'Киберпанк', 'Комедия', 'Магия', 'Меха', 'Мистика', 'Музыка', 'Повседневность', 'Приключения', 
                           'Психологическое', 'Романтика', 'Сверхъестественное', 'Сёдзе', 'Сёдзе-ай', 'Сейнен', 'Сёнен', 
                           'Спорт', 'Супер сила', 'Триллер', 'Ужасы', 'Фантастика', 'Фэнтези', 'Школа', 'Экшен', 'Этти']
        anilibria_year = ['', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', 
                          '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2001', '1999', '1998', '1996']
        anilibria_status = {'Все релизы': '','В работе': '1', 'Завершен': '2'}
        anilibria_sort = {'Новое': 'updated', 'Популярное': 'in_favorites'}
        anilibria_season = {'':'','зима':'1','весна':'2','лето':'3','осень':'4'}

        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('season')), params={'mode': 'catalog_part', 'param': 'season'})

            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})            
            xbmcplugin.endOfDirectory(handle, succeeded=True)

        if 'genre' in self.params['param']:
            result = self.dialog.select('Жанр:', anilibria_genre)
            addon.setSetting(id='genre', value=anilibria_genre[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Год:', anilibria_year)
            addon.setSetting(id='year', value=anilibria_year[result])

        if 'season' in self.params['param']:
            result = self.dialog.select('Сезон:', tuple(anilibria_season.keys()))
            addon.setSetting(id='season', value=tuple(anilibria_season.keys())[result])

        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(anilibria_sort.keys()))
            addon.setSetting(id='sort', value=tuple(anilibria_sort.keys())[result])

        if 'status' in self.params['param']:
            result = self.dialog.select('Статус релиза:', tuple(anilibria_status.keys()))
            addon.setSetting(id='status', value=tuple(anilibria_status.keys())[result])

        if 'catalog' in self.params['param']:
            year = ''
            if addon.getSetting('year'):
                year = '%20and%20{{season.year}}=={}'.format(addon.getSetting('year'))
            
            season = ''
            if addon.getSetting('season'):
                season = '%20and%20{{season.code}}=={}'.format(
                    anilibria_season[addon.getSetting('season')])

            genre = ''
            if addon.getSetting('genre'):
                genre = '%20and%20"{}"%20in%20{{genres}}'.format(quote(addon.getSetting('genre')))

            status = ''
            if anilibria_status[addon.getSetting('status')]:
                status = '%20and%20{{status.code}}=={}'.format(anilibria_status[addon.getSetting(
                    'status')])

            sort = '&order_by={}&sort_direction=1'.format(anilibria_sort[addon.getSetting('sort')])

            api_filter = '&filter=id,names.ru,posters.original,type.string,type.episodes,genres,team,season.year,description,player.episodes.last'
            api_page = '&page={}&items_per_page=50'.format(self.params['page'])

            request = '{}{}{}{}'.format(status, year, season, genre)

            if request:
                url = '{}title/search/advanced?query={}{}{}{}'.format(self.site_url, request[9:], sort, api_filter, api_page)
            else:
                url = '{}title/search/advanced?query={{id}}{}{}{}'.format(self.site_url, sort, api_filter, api_page)

            html = self.network.get_bytes(url)

            if not html:
                self.create_line(title='Ошибка получения данных', folder=False)
                xbmcplugin.endOfDirectory(handle, succeeded=True)
                return

            array = json.loads(html)

            self.progress_bg.create('AniLibria', 'Инициализация')

            try:
                for x, data in enumerate(array['list']):
                    try:
                        info = self.create_info(data)

                        anime_id = info.pop('id')
                        label = info.pop('title')

                        self.progress_bg.update(int((float(x+1) / len(array['list'])) * 100), u'Обработано - {} из {}'.format(x, len(array['list'])))

                        self.create_line(title=label, anime_id=anime_id, params={'id': anime_id, 'mode': 'select_part'}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

            self.progress_bg.close()

            try:
                if int(array['pagination']['current_page']) < int(array['pagination']['pages']):
                    label = u'Страница [COLOR=gold]{}[/COLOR] из {} | Следующая - [COLOR=gold]{}[/COLOR]'.format(
                        array['pagination']['current_page'], array['pagination']['pages'], int(self.params['page']) + 1)
                    self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
            except:
                pass

            xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        if '0' in addon.getSetting('playmode'):
            if '0' in self.params['param']:
                self.params['mode'] = 'torrent_part'
                self.exec_torrent_part()
            else:
                self.params['mode'] = 'online_part'
                self.exec_online_part()
        if '1' in addon.getSetting('playmode'):
            if '1' in self.params['param']:
                self.params['mode'] = 'online_part'
                self.exec_online_part()
            else:
                self.params['mode'] = 'torrent_part'
                self.exec_torrent_part()
#========================#========================#========================#
    def exec_online_part(self):
        api_filter = '&filter=id,names.ru,posters.original,genres,team,season.year,description,player.host,player.list'
        url = '{}title?id={}{}'.format(self.site_url, self.params['id'], api_filter)
        html = self.network.get_bytes(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        array = json.loads(html)

        if len(array['player']['list']) < 1:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        info = self.create_info(array)
        anime_id = info.pop('id')
        info.pop('title')

        current_quality = (addon.getSetting('quality')).lower()

        try:
            for x,i in enumerate(array['player']['list']):
                try:
                    data = array['player']['list'][i]

                    if data['name']:
                        label = u'{} - {}'.format(data['episode'], data['name'])
                    else:
                        label = u'Эпизод - {}'.format(data['episode'])

                    if data['hls'][current_quality]:
                        episode_hls = data['hls'][current_quality]
                    elif data['hls']['fhd']:
                        episode_hls = data['hls']['fhd']
                        label = u'{} | {}'.format(label, 'FHD')
                    elif data['hls']['hd']:
                        episode_hls = data['hls']['hd']
                        label = u'{} | {}'.format(label, 'HD')
                    elif data['hls']['sd']:
                        episode_hls = data['hls']['sd']
                        label = u'{} | {}'.format(label, 'SD')
                    else:
                        continue

                    complete_url = u'https://{}{}'.format(array['player']['host'], episode_hls)

                    self.create_line(title=label, anime_id=anime_id, params={'mode': 'play_part', 'param': complete_url, 'id': anime_id}, folder=False, **info)
                except:
                    self.create_line(title='Ошибка обработки строки - сообщите автору')
        except:
            self.create_line(title='Ошибка обработки блока - сообщите автору')

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_torrent_part(self):
        api_filter = '&filter=id,names.ru,posters.original,genres,team,season.year,description,torrents.list'
        url = '{}title?id={}{}'.format(self.site_url, self.params['id'], api_filter)
        html = self.network.get_bytes(url=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return

        array = json.loads(html)

        if len(array['torrents']['list']) < 1:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(handle, succeeded=True)
            return
        
        info = self.create_info(array)
        anime_id = info.pop('id')
        info.pop('title')

        info_data = json.dumps(info)

        try:
            for i in array['torrents']['list']:
                try:
                    torrent_id = i['torrent_id']
                    info['size'] = i['total_size']
                    #torrent_url = u'{}{}'.format(self.mirror, i['url'])

                    episodes = ''
                    if i['episodes']['string']:
                        episodes = u'Серии: {}'.format(i['episodes']['string'])

                    quality = ''
                    if i['quality']['string']:
                        quality = u' | [COLOR=blue]{}[/COLOR]'.format(i['quality']['string'])

                    torrent_peer = ''
                    if i['seeders'] and i['leechers']:
                        torrent_peer = u' | [COLOR=lime]{}[/COLOR] / [COLOR=red]{}[/COLOR]'.format(
                            i['seeders'], i['leechers'])

                    label = u'{}{}{}'.format(episodes, quality, torrent_peer)

                    # self.create_line(title=label, anime_id=anime_id, params={'tam': torrent_url}, **info)
                    self.create_line(title=label, anime_id=anime_id, params={'mode': 'bencode_part', 'torrent_id': torrent_id, 'anime_id': anime_id, 'info_data': info_data}, **info)
                except:
                    self.create_line(title='Ошибка обработки строки - сообщите автору')
        except:
            self.create_line(title='Ошибка обработки блока - сообщите автору')

        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_bencode_part(self):
        from network import get_web

        anime_id = self.params['anime_id']
        torrent_id = self.params['torrent_id']
        torrent_url = u'{}/public/torrent/download.php?id={}'.format(self.mirror, torrent_id)
        
        info_data = json.loads(self.params['info_data'])
        #data_print(info)

        #url = self.params['torrent_url']

        # data_request = self.network.get_bytes(url=torrent_url)
        data_request = get_web(url=torrent_url)

        torrent_file = os.path.join(self.torrents_dir, torrent_id)
            
        with open(torrent_file, 'wb') as write_file:
            write_file.write(data_request)

        import bencode
            
        with open(torrent_file, 'rb') as read_file:
            torrent_data = read_file.read()

        torrent = bencode.bdecode(torrent_data)

        info = torrent['info']
        series = {}
        size = {}
            
        if 'files' in info:
            for i, x in enumerate(info['files']):
                size[i] = x['length']
                series[i] = x['path'][-1]
            for i in sorted(series, key=series.get):
                #info = {'sorttitle': series[i], 'size': size[i], 'year': 0, 'genre': [], 'plot':''}
                # self.create_line(title=series[i], anime_id=anime_id, params={'mode': 'selector_part', 'index': i, 'torrent_id': torrent_id}, folder=False, size=size[i])
                self.create_line(title=series[i], anime_id=anime_id, params={'mode': 'selector_part', 'index': i, 'torrent_id': torrent_id}, folder=False, **info_data)
        else:
            #info = {'sorttitle': info['name'], 'size': size[i], 'year': 0, 'genre': [], 'plot':''}
            # self.create_line(title=info['name'], anime_id=anime_id, params={'mode': 'selector_part', 'index': 0, 'torrent_id': torrent_id}, folder=False, size=info['length'])
            self.create_line(title=info['name'], anime_id=anime_id, params={'mode': 'selector_part', 'index': 0, 'torrent_id': torrent_id}, folder=False, **info_data)
        
        xbmcplugin.endOfDirectory(handle, succeeded=True)
        return
#========================#========================#========================#
    def exec_selector_part(self):
        torrent_url = os.path.join(self.torrents_dir, self.params['torrent_id'])
        index = int(self.params['index'])
        torrent_engine = addon.getSetting('engine')
        
        if '0' in torrent_engine:
            try:
                tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver', 'torrserver_tam', 'lt2http')
                engine = tam_engine[int(addon.getSetting('tam'))]
                purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(torrent_url), index, engine)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=1000,sound=False)

        if '1' in torrent_engine:
            try:
                purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=1000,sound=False)

        if '2' in torrent_engine:
            pass
        
        if '3' in torrent_engine:
            try:
                xbmcaddon.Addon('script.module.torrent2http')
            except:
                xbmcgui.Dialog().notification(
                    heading='Установка Библиотеки - [COLOR=darkorange]script.module.torrent2http[/COLOR]',
                    message='script.module.torrent2http',
                    icon=None,
                    time=3000,
                    sound=False
                    )
                xbmc.executebuiltin('RunPlugin("plugin://script.module.torrent2http")')

            preload_size = 20
            try:
                if py_version < 3:
                    import player_legacy as player
                else:
                    import player
                #import player

                uri = 'file:///' + torrent_url.replace('\\', '/')
                # player_legacy.play_t2h(handle, preload_size, uri, index, download_path=addon_data_dir)
                player.play_t2h(handle, preload_size, uri, index, download_path=addon_data_dir)
            except:
                self.dialog.notification(heading='Проигрыватель',message='Ошибка',icon=self.icon,time=1000,sound=False)
#========================#========================#========================#
    def exec_play_part(self):
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

        li = xbmcgui.ListItem(path=self.params['param'])

        if '0' in addon.getSetting('inputstream'):
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
            li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)
#========================#========================#========================#
def start():
    anilibria = Anilibria()
    anilibria.execute()
