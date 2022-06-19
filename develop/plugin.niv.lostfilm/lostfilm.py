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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

if sys.version_info.major > 2:
    from urllib.parse import urlencode, quote, unquote, parse_qs
    from urllib.request import urlopen
    from html import unescape
else:
    from urllib import urlencode, urlopen, quote, unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

from utility import clean_tags, fs_enc

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

if sys.version_info.major > 2:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

class Lostfilm:    
    def __init__(self):
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

        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()
    
        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'code': ''}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.site_url = self.create_site_url()
        
        if 'false' in addon.getSetting('clean_old_torrents'):
            for torrent_file in os.listdir(self.torrents_dir):
                file_path = os.path.join(self.torrents_dir, torrent_file)
                os.remove(file_path)
            addon.setSetting('clean_old_torrents', 'true')
#========================#========================#========================#
        try: session = float(addon.getSetting('auth_session'))
        except: session = 0

        if time.time() - session > 28800:
            addon.setSetting('auth_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'lostfilm.sid'))
            except: pass
            addon.setSetting('auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(auth_status=bool(addon.getSetting('auth') == 'true'))
        self.network.auth_post_data = 'act=users&type=login&mail={}&pass={}&need_captcha=1&rem=1'.format(
            addon.getSetting('username'), addon.getSetting('password'))
        self.network.auth_url = '{}ajaxik.users.php'.format(self.site_url)
        self.network.sid_file = os.path.join(self.cookie_dir, 'lostfilm.sid')
        del WebTools
#========================#========================#========================#
        if not addon.getSetting('username') or not addon.getSetting('password'):
            self.params['mode'] = 'addon_setting'
            self.dialog.notification(heading='Авторизация',message='ВВЕДИТЕ ЛОГИН И ПАРОЛЬ',icon=icon,time=5000,sound=False)
            return

        if not self.network.auth_status:
            if not self.network.authorization():
                self.params['mode'] = 'addon_setting'
                self.dialog.notification(heading='Авторизация',message='ПРОВЕРЬТЕ ЛОГИН И ПАРОЛЬ',icon=icon,time=5000,sound=False)
                return
            else:
                addon.setSetting('auth', str(self.network.auth_status).lower())                    
                addon.setSetting('user_session', self.create_session())
#========================#========================#========================#
        if not os.path.isfile(os.path.join(self.database_dir, 'lostfilm.db')):
            self.exec_update_database_part()
#========================#========================#========================#
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'lostfilm.db'))
        del DataBase
#========================#========================#========================#
    def create_session(self):
        ht = self.network.get_html('{}my'.format(self.site_url))
        
        user_session = ht[ht.find('session = \'')+11:ht.find('UserData.newbie')]
        user_session = user_session[:user_session.rfind('\'')].strip()
        
        addon.setSetting('user_session', user_session)
        return user_session
#========================#========================#========================#
    def create_site_url(self):
        site_url = addon.getSetting('mirror_0')
        current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))

        if not addon.getSetting(current_mirror):
            site_url = addon.getSetting('mirror_0')
        else:
            site_url = addon.getSetting(current_mirror)

        return site_url
#========================#========================#========================#
    def create_colorize(self, data):
        setting_id = {
            'Поиск':'search_color',
            'Расписание':'schedule_color',
            'Избранное':'favorites_color',
            'Новинки':'new_color',
            'Все сериалы':'serials_color',
            'Каталог Сериалов':'catalog_color',
            'Поиск по названию':'search_name_color',
            'Архив Торрентов': 'archive_color'
            }
        
        color_id = {'0':'none','1':'red','2':'lime','3':'blue','4':'gold','5':'orange'}

        data_color = color_id[
            addon.getSetting(setting_id[data])
            ]

        label = '[B][COLOR={}]{}[/COLOR][/B]'.format(data_color, data)
        
        return label
#========================#========================#========================#
    def create_image(self, se_code):
        serial_episode = se_code[len(se_code)-3:len(se_code)]
        serial_episode = int(serial_episode.replace('999','1'))
        
        serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
        serial_image = int(se_code[:len(se_code)-6])

        if 'schedule_part' in self.params['mode']:
            if serial_season == 1 and serial_episode == 1:
                image = 'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image)
                return image
                
            if serial_episode == 1 and serial_season > 1:
                serial_season = serial_season - 1

        if serial_season == 999:
            image = 'https://static.lostfilm.top/Images/{}/Posters/poster.jpg'.format(serial_image)
            return image
            
        image = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(
            serial_image, serial_season)

        return image
#========================#========================#========================#
    def create_title(self, serial_title='', episode_title='', data_code='', serial_id='', watched=False):
        if serial_title:
            serial_title = u'[B]{}[/B]'.format(serial_title)
        
        if episode_title:
            if serial_title:
                serial_title = u'{}: '.format(serial_title)
            
            episode_title = u'{}'.format(episode_title)

        if data_code:
            serial_season = int(data_code[len(data_code)-6:len(data_code)-3])
            serial_season = 'S{:>02}'.format(serial_season)
            serial_season = serial_season.replace('S999', 'A00')

            serial_episode = int(data_code[len(data_code)-3:len(data_code)])
            serial_episode = 'E{:>02}'.format(serial_episode)

            if watched:
                data_code = '[COLOR=goldenrod]{}{} | [/COLOR]'.format(serial_season, serial_episode)
            else:
                data_code = '[COLOR=blue]{}[/COLOR][COLOR=lime]{}[/COLOR] | '.format(serial_season, serial_episode)

        if serial_id:
            serial_id = '[COLOR=blue]{}[/COLOR] | '.format(self.database.get_year(serial_id))
        
        if watched:
            label = u'{}{}[COLOR=goldenrod]{}{}[/COLOR]'.format(serial_id, data_code, serial_title, episode_title)
        else:
            label = u'{}{}{}{}'.format(serial_id, data_code, serial_title, episode_title)
            
        return label
#========================#========================#========================#
    def create_context(self, serial_id='', se_code=''):
        serial_episode = se_code[len(se_code)-3:len(se_code)]
        serial_image = se_code[:len(se_code)-6]

        context_menu = []
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=clean_part")'))

        if serial_id and self.params['mode'] in ('common_part','favorites_part','catalog_part','schedule_part','search_part','serials_part'):
            context_menu.append(('[COLOR=cyan]Избранное - Добавить \ Удалить [/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=favorites_part&id={}")'.format(serial_id)))

        if serial_id:
            context_menu.append(('[COLOR=white]Обновить описание[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_serial_part&id={}")'.format(serial_id)))

        if se_code and not '999' in serial_episode:
            context_menu.append(('[COLOR=blue]Перейти к Сериалу[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=select_part&id={}&code={}001999")'.format(serial_id,serial_image)))
            context_menu.append(('[COLOR=white]Открыть торрент файл[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=torrent_part&id={}&code={}")'.format(serial_id,se_code)))
            context_menu.append(('[COLOR=yellow]Отметить как просмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=on&id={}")'.format(se_code)))
            context_menu.append(('[COLOR=yellow]Отметить как непросмотренное[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=mark_part&param=off&id={}")'.format(se_code)))

        context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=update_database_part")'))
        
        context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.lostfilm/?mode=information_part&param=news")'))
        return context_menu
#========================#========================#========================#
    def create_line(self, title, serial_id='', se_code='', watched=False, params=None, folder=True):
        li = xbmcgui.ListItem(title)

        if serial_id and se_code:
            cover = self.create_image(se_code)

            li.setArt({"poster": cover,"icon": cover})

            se_info = self.database.get_serial(serial_id)

            info = {
                'genre':se_info[1],
                'country':se_info[3],
                'year': se_info[0][0:4],
                'plot':se_info[4],
                'title':title,
                'studio':se_info[2],
                'tvshowtitle':title,
                'premiered':se_info[0],
                'aired':se_info[0]
            }

            if self.database.cast_in_db(serial_id):
                cast = self.database.get_cast(serial_id)
                if cast['actors']:
                    li.setCast(cast['actors'])
                if cast['directors']:
                    info['director'] = cast['directors']
                if cast['writers']:
                    info['writer'] = cast['writers']
            
            if watched:
                info['playcount'] = 1

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(
            self.create_context(serial_id = serial_id, se_code = se_code)
            )

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, serial_id, update=False):
        url = '{}series/{}/'.format(self.site_url, serial_id)

        html = self.network.get_html(url)

        if not html:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru='serial_id: {}'.format(serial_id)
                )
            return

        info = dict.fromkeys(['title_ru', 'aired_on', 'genres', 'studios', 'country', 'description', 'image_id'], '')
                    
        info['image_id'] = html[html.find('/Images/')+8:html.find('/Posters/')]
        
        info['title_ru'] = html[html.find('itemprop="name">')+16:html.find('</h1>')]
        info['title_ru'] = info['title_ru'].replace('/', '-')
        

        description = html[html.find(u'Описание</h2>'):html.find('<div class="social-pane">')]
        if u'Сюжет</strong><br />' in description:
            description = description[description.find(u'Сюжет</strong><br />')+20:]
        else:
            description = description[description.find('description">')+13:]
        description = description[:description.find('</div>')]
        description = unescape(description)
        info['description'] = clean_tags(description)

        data_array = html[html.find('dateCreated"'):html.find('</a></span><br />')]
        data_array = data_array.split('<br />')

        for data in data_array:
            if 'dateCreated' in data:
                aired_on = data[data.find('content="')+9:data.find('" />')]
                info['aired_on'] = aired_on.replace('-', '.')
            if 'search&c=' in data:
                data = data[data.find('">')+2:]
                info['studios'] = data[:data.find('</a>')]
                info['country'] = data[data.find('(')+1:data.find(')')]
            if 'prop="genre' in data:
                genre = []
                data = data[data.find('<a href="'):].split('</a>')
                for d in data:
                    d = d[d.find('">')+2:].strip()
                    genre.append(d)
                info['genres'] = ', '.join(genre)
                
        try:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru=info['title_ru'],
                aired_on=info['aired_on'],
                genres=info['genres'],
                studios=info['studios'],
                country=info['country'],
                description=info['description'],
                image_id=info['image_id'],
                update=update                
            )
        except:
            self.database.add_serial(
                serial_id=serial_id,
                title_ru='serial_id: {}'.format(serial_id)
                )
            return 101

        cast = {'actors': [], 'directors': [], 'producers': [], 'writers': []}
        
        html2 = self.network.get_html('{}cast'.format(url))

        info_array = html2[html2.find('<div class="header-simple">'):html2.find('rightt-pane">')]        
        info_array = info_array.split('<div class="hor-breaker dashed"></div>')

        for cast_info in info_array:
            title = cast_info[cast_info.find('simple">')+8:cast_info.find('</div>')]
            title = title.replace(u'Актеры', 'actors').replace(u'Режиссеры', 'directors')
            title = title.replace(u'Продюсеры', 'producers').replace(u'Сценаристы', 'writers')
            
            cast_info = cast_info[:cast_info.rfind('</a>')]
            cast_info = cast_info.split('</a>')

            for c in cast_info:
                person = c[c.find('name-ru">')+9:]
                person = person[:person.find('</div>')]

                node = u'{}'.format(person.strip())

                if 'actors' in title:
                    role = c[c.find('role-ru">')+9:]
                    role = role[:role.find('</div>')]

                    node = u'{}|{}'.format(person.strip(), role.strip())

                cast[title].append(node)

        try:
            self.database.add_cast(
                serial_id=serial_id,
                actors='||'.join(cast['actors']),
                directors=','.join(cast['directors']),
                producers=','.join(cast['producers']),
                writers=','.join(cast['writers']),
                update=update
            )
        except:
            return 101
        
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
    def exec_update_serial_part(self):
        self.create_info(serial_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'lostfilm.db'))
        except: pass

        db_file = os.path.join(self.database_dir, 'lostfilm.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/lostfilm.db'
        try:                
            data = urlopen(db_url)
            chunk_size = 8192
            bytes_read = 0

            try: file_size = int(data.info().getheaders("Content-Length")[0])
            except: file_size = int(data.getheader('Content-Length'))

            self.progress_bg.create('Downloading DB', 'Downloading...')

            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress_bg.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
            self.progress_bg.close()
            self.dialog.notification(heading='База Данных',message='ЗАГРУЖЕНА',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='База Данных',message='ОШИБКА',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_mark_part(self, notice=True, se_code=None, mode=False):
        se_code = se_code if se_code else self.params['id']
        mode = mode if mode else self.params['param']

        html = self.network.get_html(
            target_name='{}ajaxik.php'.format(self.site_url),
            post = 'session={}&act=serial&type=markepisode&val={}&auto=0&mode={}'.format(
                addon.getSetting('user_session'), se_code, mode))
        
        if notice:
            if '"on' in str(html) or 'off' in str(html):
                self.dialog.notification(heading='LostFilm',message='ВЫПОЛНЕНО',icon=icon,time=3000,sound=False)
            if 'error' in str(html):
                self.dialog.notification(heading='LostFilm',message='ОШИБКА',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_favorites_part(self):
        post = 'session={}&act=serial&type=follow&id={}'.format(
            addon.getSetting('user_session'), self.database.get_image_id(self.params['id']))
        html = self.network.get_html('{}ajaxik.php'.format(self.site_url), post)

        if '"on' in str(html):
            self.dialog.notification(heading='LostFilm',message='ДОБАВЛЕНО',icon=icon,time=3000,sound=False)
        if 'off' in str(html):
            self.dialog.notification(heading='LostFilm',message='УДАЛЕНО',icon=icon,time=3000,sound=False)
        if 'error' in str(html):
            self.dialog.notification(heading='LostFilm',message='ОШИБКА',icon=icon,time=3000,sound=False)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('search', '')
            self.dialog.notification(heading='LostFilm',message='ВЫПОЛНЕНО',icon=icon,time=3000,sound=False)
        except:
            self.dialog.notification(heading='LostFilm',message='ОШИБКА',icon=icon,time=3000,sound=False)
            pass
#========================#========================#========================#
    def exec_information_part(self):
        lostfilm_data = u'[B][COLOR=darkorange]Version 0.8.0[/COLOR][/B]\n\
    - Мелкие исправления, оптимизация\n\
    - Переработана система получения качества\n\
        *Названия как на сайте (1080 и т.д.)\n\
        *Парсер теперь загребает все существующие виды качества\n\
    - Торрент файлы теперь сохраняются с Оригинальным названием\n\
        *Оригинальные названия удобнее для Архива торрентов\n\
    \n[B][COLOR=blue]Ожидается:[/COLOR][/B]\n\
    - Мелкие исправления, оптимизация\n'

        self.dialog.textviewer('Информация', lostfilm_data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title=self.create_colorize('Поиск'), params={'mode': 'search_part'})
        self.create_line(title=self.create_colorize('Расписание'), params={'mode': 'schedule_part'})
        self.create_line(title=self.create_colorize('Избранное'), params={'mode': 'catalog_part', 'param': 'favorites'})
        self.create_line(title=self.create_colorize('Новинки'), params={'mode': 'common_part', 'param':'new/'})
        self.create_line(title=self.create_colorize('Все сериалы'), params={'mode': 'serials_part'})
        self.create_line(title=self.create_colorize('Каталог Сериалов'), params={'mode': 'catalog_part'})
        self.create_line(title=self.create_colorize('Архив Торрентов'), params={'mode': 'archive_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=self.create_colorize('Поиск по названию'), params={'mode': 'search_part', 'param': 'search_word'})
            data_array = addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='[COLOR=gray]{}[/COLOR]'.format(data), params={'mode': 'search_part', 'param':'search_string', 'search_string': data})

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

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            url = '{}search/?q={}'.format(self.site_url, quote(self.params['search_string']))
            html = self.network.get_html(target_name=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            if not '<div class="hor-breaker dashed">' in html:
                self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            data_array = html[html.find('<div class="hor-breaker dashed">')+32:html.rfind('<div class="hor-breaker dashed">')]
            data_array = data_array.split('<div class="hor-breaker dashed">')
            
            i = 0

            for data in data_array:
                serial_title = data[data.find('name-ru">')+9:]
                serial_title = serial_title[:serial_title.find('</div>')]
                
                serial_id = data[data.find('series/')+7:]
                serial_id = serial_id[:serial_id.find('"')]
                serial_id = serial_id.strip()
                
                image_id = data[data.find('/Images/')+8:data.find('/Posters/')]

                se_code = '{}001999'.format(image_id)
                
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                
                if not self.database.serial_in_db(serial_id):
                    self.create_info(serial_id)

                label = self.create_title(serial_title=serial_title, serial_id=serial_id)
                self.create_line(title=label, serial_id=serial_id, se_code=se_code, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})

            self.progress_bg.close()
            
            if '<div class="next-link active">' in html:
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                    int(self.params['page']), int(self.params['page'])+1)
                self.create_line(title=label, params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        url = '{}schedule/'.format(self.site_url)
        html = self.network.get_html(target_name=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('LostFilm', 'Инициализация')
        
        data_array = html[html.find('<th colspan="6">')+16:html.rfind('<td class="placeholder">')]        
        data_array = data_array.split('<th colspan="6">')

        i = 0

        for data in data_array:
            title = data[:data.find('</th>')]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.create_line(title=u'[B]{}[/B]'.format(title.capitalize()), params={})

            data = data.split('<td class="alpha"')
            data.pop(0)
            
            a = 0
            
            for d in data:
                serial_id = d[d.find('/series/')+8:d.find('\',false')]
                serial_id = serial_id.strip()
                
                image_id = d[d.find('/Images/')+8:d.find('/Posters/')]
                
                serial_title = d[d.find('class="ru">')+11:]
                serial_title = serial_title[:serial_title.find('</div>')]        

                episode_title = d[d.find('<td class="gamma'):]
                episode_title = episode_title[episode_title.find(';">')+3:episode_title.find('<br />')]

                code = d[d.rfind('{}/'.format(serial_id))+len(serial_id)+1:d.rfind('/\'')]
                code = code.replace('season_','').replace('episode_','')
                code = code.replace('additional','999').split('/')

                se_code = '{}{:>03}{:>03}'.format(image_id,int(code[0]),int(code[1]))

                day_release = d[d.rfind('false);">')+9:d.rfind('<br />')].strip()
                
                if '<p>' in d:
                    when_release = d[d.find('<p>')+3:d.find('</p>')]
                else:
                    when_release = d[d.rfind('<span>')+6:d.rfind('</span>')]
                    when_release = u'Дней осталось: {}'.format(when_release)
                
                a = a + 1

                self.progress_bg.update(p, u'[COLOR=lime]День:[/COLOR] {} из {} | [COLOR=blue]Элементы:[/COLOR] {} из {} '.format(
                    i, len(data_array), a, len(data)))

                if not self.database.serial_in_db(serial_id):
                    self.create_info(serial_id)

                label = self.create_title(serial_title, episode_title, se_code)
                label = u'{} | [COLOR=gold]{} - {}[/COLOR]'.format(label, day_release, when_release)

                self.create_line(title=label, serial_id=serial_id, se_code=se_code, params={'mode': 'select_part', 'id': serial_id, 'code': se_code})

        self.progress_bg.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        url = '{}{}page_{}'.format(self.site_url, self.params['param'], self.params['page'])
        html = self.network.get_html(target_name=url)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        if not '<div class="hor-breaker dashed">' in html:
            self.create_line(title='Контент отсутствует', params={'mode': self.params['mode']})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        self.progress_bg.create('LostFilm', 'Инициализация')
        
        data_array = html[html.find('breaker dashed">')+16:html.rfind('<div class="hor-breaker dashed">')]
        data_array = data_array.split('<div class="hor-breaker dashed">')
        
        i = 0

        for data in data_array:
            is_watched = True if 'haveseen-btn checked' in data else False

            serial_title = data[data.find('name-ru">')+9:]
            serial_title = serial_title[:serial_title.find('</div>')]

            serial_id = data[data.find('series/')+7:]
            serial_id = serial_id[:serial_id.find('/')]
            serial_id = serial_id.strip()
            
            se_code = data[data.find('episode="')+9:data.find('" data-code')]

            episode_title = None
            if 'alpha">' in data:
                episode_title = data[data.find('alpha">')+7:]
                episode_title = episode_title[:episode_title.find('</div>')]

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

            if not self.database.serial_in_db(serial_id):
                self.create_info(serial_id)

            label = self.create_title(serial_title, episode_title, se_code, watched=is_watched)

            self.create_line(title=label, serial_id=serial_id, se_code=se_code, watched=is_watched, folder=False, params={
                        'mode': 'play_part', 'id': serial_id, 'param': se_code})

        self.progress_bg.close()
        
        if '<div class="next-link active">' in html:
            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(
                int(self.params['page']), int(self.params['page'])+1)
            self.create_line(title=label, params={
                'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_catalog_part(self):
        if self.params['page'] == '1':
            self.params['page'] = '0'
        
        from info import genre, year, channel, types, status, sort
        
        if self.params['param'] == '':
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Год: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Канал: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('channel')), params={'mode': 'catalog_part', 'param': 'channel'})            
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('types')), params={'mode': 'catalog_part', 'param': 'types'})            
            self.create_line(title='Сортировка: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sort')), params={'mode': 'catalog_part', 'param': 'sort'})            
            self.create_line(title='Статус релиза: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('status')), params={'mode': 'catalog_part', 'param': 'status'})            
            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

        if 'genre' in self.params['param']:
            result = self.dialog.select('Жанр:', tuple(genre.keys()))
            addon.setSetting(id='genre', value=tuple(genre.keys())[result])

        if 'year' in self.params['param']:
            result = self.dialog.select('Год:', tuple(year.keys()))
            addon.setSetting(id='year', value=tuple(year.keys())[result])

        if 'channel' in self.params['param']:
            result = self.dialog.select('Канал:', tuple(channel.keys()))
            addon.setSetting(id='channel', value=tuple(channel.keys())[result])

        if 'types' in self.params['param']:
            result = self.dialog.select('Тип:', tuple(types.keys()))
            addon.setSetting(id='types', value=tuple(types.keys())[result])

        if 'sort' in self.params['param']:
            result = self.dialog.select('Сортировать по:', tuple(sort.keys()))
            addon.setSetting(id='sort', value=tuple(sort.keys())[result])

        if 'status' in self.params['param']:
            result = self.dialog.select('Статус релиза:', tuple(status.keys()))
            addon.setSetting(id='status', value=tuple(status.keys())[result])
        
        if 'catalog' in self.params['param'] or 'favorites' in self.params['param']:

            from info import genre, year, channel, types, sort, status

            if 'catalog' in self.params['param']:
                lostfilm_genre = '&g={}'.format(genre[addon.getSetting('genre')]) if genre[addon.getSetting('genre')] else ''
                lostfilm_year = '&y={}'.format(year[addon.getSetting('year')]) if year[addon.getSetting('year')] else ''
                lostfilm_channel = '&c={}'.format(channel[addon.getSetting('channel')]) if channel[addon.getSetting('channel')] else ''
                lostfilm_types = '&r={}'.format(types[addon.getSetting('types')]) if types[addon.getSetting('types')] else ''
                lostfilm_sort = sort[addon.getSetting('sort')]
                lostfilm_status = status[addon.getSetting('status')]
                lostfilm_page = self.params['page']
                
                post = 'act=serial&type=search&o={}{}{}{}{}&s={}&t={}'.format(
                    lostfilm_page,lostfilm_genre,lostfilm_year,lostfilm_channel,lostfilm_types,lostfilm_sort,lostfilm_status)
            
            if 'favorites' in self.params['param']:
                post = 'act=serial&type=search&o={}&s=2&t=99'.format(self.params['page'])

            html = self.network.get_html('{}ajaxik.php'.format(self.site_url), post)
            
            if not html:
                self.create_line(title='[B][COLOR=white]Контент не найден[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            if not 'data":[{' in html:
                self.create_line(title='[B][COLOR=white]Контента больше нет[/COLOR][/B]', params={'mode': self.params['mode']})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            html = html[html.find('":[')+3:html.find('],"')]
            
            data_array = html.split('},{')

            i = 0

            for data in data_array:
                serial_title = data[data.find('title":"')+8:data.find('","title_orig')]
                
                try: serial_title = serial_title.encode('utf-8').decode('unicode_escape')
                except: pass

                serial_id = data[data.find('series\/')+8:data.find('","alias')]
                serial_id = serial_id.strip()
                image_id = data[data.find('id":"')+5:data.find('","has_icon')]
                
                se_code = '{}001999'.format(image_id)

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, 'Обработано - {} из {} '.format(i, len(data_array)))
                
                if not self.database.serial_in_db(serial_id):
                    self.create_info(serial_id)

                label = self.create_title(serial_id=serial_id, serial_title=serial_title)
                self.create_line(title=label, serial_id=serial_id, se_code=se_code, params={
                    'mode': 'select_part', 'id': serial_id, 'code': se_code})

            self.progress_bg.close()

            if len(data_array) >= 10:                    
                page_count = (int(self.params['page']) / 10) + 1
                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(page_count), int(page_count)+1)
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 10)})
                
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_serials_part(self):
        self.progress_bg.create('LostFilm', 'Инициализация')

        data_array = self.database.get_serials_id()

        i = 0
        
        for data in data_array:
            
            try:
                serial_id = data[0]
                se_code = '{}001999'.format(data[2])
            except:
                label = '[COLOR=red][B]{}[/B][/COLOR]'.format(serial_id)
                self.create_line(title=label, params={})
                continue

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
            
            label = self.create_title(serial_id=serial_id, serial_title=data[1])
            self.create_line(title=label, serial_id=serial_id, se_code=se_code, params={
                'mode': 'select_part', 'id': serial_id, 'code': se_code})

        self.progress_bg.close()
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        if not addon.getSetting('parser_mode'):
            addon.setSetting('parser_mode', '0')

        if '0' in addon.getSetting('parser_mode'):
            self.exec_select_part_fast()
        if '1' in addon.getSetting('parser_mode'):
            self.exec_select_part_slow()
#========================#========================#========================#
    def exec_select_part_fast(self, data_string=''):
        atl_names = bool(addon.getSetting('use_atl_names') == 'true')
        
        if not self.params['param']:
            url = '{}series/{}/seasons'.format(self.site_url, self.params['id'])
            html = self.network.get_html(target_name=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return    

            image_id = self.params['code'][:len(self.params['code'])-6]

            data_array = html[html.find('<h2>')+4:html.rfind('holder"></td>')+13]
            data_array = data_array.split('<h2>')

            if len(data_array) < 2:
                self.params={'mode': 'select_part', 'param': '{}001999'.format(image_id), 'id': self.params['id']}
                self.exec_select_part_fast(data_string=html)
                return

            self.progress_bg.create('LostFilm', 'Инициализация')
    
            i = 0
            
            for data in data_array:
                title = data[:data.find('</h2>')]

                season = title.replace(u'сезон','').strip()
                season = season.replace(u'Дополнительные материалы', '999')

                se_code = '{}{:>03}999'.format(image_id, int(season))

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                if 'PlayEpisode(' in data:
                    label = u'[B]{}[/B]'.format(title)
                    self.create_line(title=label, serial_id=self.params['id'], se_code=se_code ,params={
                        'mode': 'select_part', 'param': '{}'.format(se_code), 'id': self.params['id']})
                else:
                    if not atl_names:
                        label = u'[COLOR=dimgray][B]{}[/B][/COLOR]'.format(title)
                        self.create_line(title=label, params={
                            'mode': 'select_part', 'param': '{}'.format(se_code), 'id': self.params['id']})

            self.progress_bg.close()

        if self.params['param']:                
            code = self.params['param']
            image_id = code[:len(code)-6]
            season_id = code[len(code)-6:len(code)-3]
            
            if data_string:
                html = data_string
            else:
                url = '{}series/{}/season_{}'.format(self.site_url, self.params['id'], int(season_id))
                html = self.network.get_html(target_name=url)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            try:
                post = 'act=serial&type=getmarks&id={}'.format(image_id)
                watched_data = self.network.get_html('{}ajaxik.php'.format(self.site_url), post)
            except:
                watched_data = []

            self.progress_bg.create('LostFilm', 'Инициализация')
            
            serial_title = html[html.find('ativeHeadline">')+15:html.find('</h2>')]
            
            data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
            data_array = data_array.split('<td class="alpha">')

            i = 0
            
            for data in data_array:
                se_code = data[data.find('episode="')+9:]
                se_code = se_code[:se_code.find('"')]

                episode_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
                if '<br>' in episode_title:
                    episode_title = episode_title[episode_title.find('">')+2:episode_title.find('<br>')].strip()        
                if '<br />' in episode_title:
                    episode_title = episode_title[episode_title.find('<div>')+5:episode_title.find('<br />')].strip()
                if not episode_title:
                    continue
                
                is_watched = True if se_code in watched_data else False

                i = i + 1
                p = int((float(i) / len(data_array)) * 100)
                
                self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))
                
                if 'data-code=' in data:
                    label = self.create_title(episode_title=episode_title, watched=is_watched, data_code=se_code)
                    if atl_names:
                        label = u'{}.{}'.format(serial_title, label)                    

                    self.create_line(title=label, serial_id=self.params['id'], se_code=se_code, watched=is_watched, folder=False, params={
                                     'mode': 'play_part', 'id': self.params['id'], 'param': se_code})
                else:
                    if not atl_names:
                        label = '[COLOR=dimgray]S{:>02}E{:02} | {}[/COLOR]'.format(
                            int(season_id), len(data_array), episode_title)
                        self.create_line(title=label, folder=False, params={})

            self.progress_bg.close()

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part_slow(self):
        url = '{}series/{}/seasons'.format(self.site_url, self.params['id'])
        html = self.network.get_html(target_name=url)

        image_id = self.params['code'][:len(self.params['code'])-6]
        
        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return

        try:
            post = 'act=serial&type=getmarks&id={}'.format(int(image_id))
            watched_data = self.network.get_html('{}ajaxik.php'.format(self.site_url), post)
        except:
            watched_data = []

        self.progress_bg.create('LostFilm', 'Инициализация')
       
        data_array = html[html.find('<h2>')+4:html.rfind('<td class="placeholder"></td>')]
        data_array = data_array.split('<h2>')

        i = 0
        
        for data in data_array:
            title = data[:data.find('</h2>')]
            
            if 'season_series_' in data:
                self.create_line(title=u'[B]{}[/B]'.format(title), params={})
            else:
                self.create_line(title=u'[B][COLOR=dimgray]{}[/COLOR][/B]'.format(title), params={})
                
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            data = data[data.find('<div class="have'):]
            data = data.split('<td class="alpha">')

            a = 0
            
            for d in data:
                se_code = d[d.find('episode="')+9:]
                se_code = se_code[:se_code.find('"')]
                        
                episode_title = d[d.find('<td class="gamma'):d.find('<td class="delta"')]
                if '<br>' in episode_title:
                    episode_title = episode_title[episode_title.find('">')+2:episode_title.find('<br>')].strip()        
                if '<br />' in episode_title:
                    episode_title = episode_title[episode_title.find('<div>')+5:episode_title.find('<br />')].strip()
                if not episode_title:
                    continue

                is_watched = True if se_code in watched_data else False

                a = a + 1
                
                self.progress_bg.update(p, u'[COLOR=lime]Сезон:[/COLOR] {} из {} | [COLOR=blue]Серия:[/COLOR] {} из {} '.format(
                    i, len(data_array), a, len(data)))
                
                if 'data-code=' in d:
                    label = self.create_title(episode_title=episode_title, watched=is_watched, data_code=se_code)
                    self.create_line(title=label, serial_id=self.params['id'], se_code=se_code, watched=is_watched, folder=False, params={
                        'mode': 'play_part', 'id': self.params['id'], 'param': se_code})
                else:
                    label = u'[COLOR=dimgray]{}[/COLOR]'.format(episode_title)
                    self.create_line(title=label, folder=False, params={})

        self.progress_bg.close()
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            se_code = self.params['code']
            serial_episode = int(se_code[len(se_code)-3:len(se_code)])
            serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
            image_id = int(se_code[:len(se_code)-6])

            url = '{}v_search.php?c={}&s={}&e={}'.format(
                self.site_url, image_id, serial_season, serial_episode)

            html = self.network.get_html(target_name=url)
                
            new_url = html[html.find('url=http')+4:html.find('&newbie=')]
            html = self.network.get_html(new_url)

            data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
            data_array = data_array.split('<div class="inner-box--label">')

            quality = {}
                        
            for data in data_array:
                quality_data = data[:data.find('</div>')].strip()
                    
                torrent_url = data[data.find('<a href="')+9:]
                torrent_url = torrent_url[:torrent_url.find('">')]
                
                quality[quality_data] = torrent_url

            current_quality = addon.getSetting('quality')

            try:
                url = quality[current_quality]
            except:
                url = ''

            if not url:
                choice = list(quality.keys())
                        
                result = self.dialog.select('Доступное качество: ', choice)
                result_quality = choice[int(result)]
                url = quality[result_quality]

            file_name = self.network.get_file(target_url=url, target_path=self.torrents_dir, se_code=se_code)
            torrent_file = os.path.join(self.torrents_dir, file_name)

            import bencode
                
            with open(torrent_file, 'rb') as read_file:
                torrent_data = read_file.read()

            torrent = bencode.bdecode(torrent_data)

            valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
            
            if 'files' in torrent['info']:                
                series = {}
                    
                for i, x in enumerate(torrent['info']['files']):
                    extension = x['path'][-1][x['path'][-1].rfind('.'):]
                        
                    if extension in valid_media:
                        series[i] = x['path'][-1]

                for i in sorted(series, key=series.get):                    
                    self.create_line(title=series[i], serial_id=self.params['id'], se_code=se_code, folder=False, params={
                        'mode': 'torrent_part', 'id': file_name, 'param': i})
            else:
                self.create_line(title=torrent['info']['name'], serial_id=self.params['id'], se_code=se_code, folder=False, params={
                    'mode': 'torrent_part', 'id': file_name, 'param': 0})
                
        if self.params['param']:
            torrent_file = os.path.join(self.torrents_dir, self.params['id'])

            import player
            confirm = player.selector(torrent_url=torrent_file, torrent_index = self.params['param'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_archive_part(self):
        if not self.params['param']:
            data_array = os.listdir(self.torrents_dir)

            for data in data_array:
                se_code = data[:data.find('_')]
                file_name = data[data.find('_')+1:].replace('.torrent', '')

                serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
                image_id = int(se_code[:len(se_code)-6])                
                serial_id = self.database.get_serial_id(image_id)
                    
                self.create_line(title=file_name, serial_id=serial_id, se_code=se_code, params={'mode': 'archive_part', 'param': data, 'code': se_code, 'id': serial_id})

        if self.params['param']:
            torrent_file = os.path.join(self.torrents_dir, self.params['param'])

            import bencode
                
            with open(torrent_file, 'rb') as read_file:
                torrent_data = read_file.read()

            torrent = bencode.bdecode(torrent_data)

            valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
            
            if 'files' in torrent['info']:
                
                series = {}
                    
                for i, x in enumerate(torrent['info']['files']):
                    extension = x['path'][-1][x['path'][-1].rfind('.'):]
                        
                    if extension in valid_media:
                        series[i] = x['path'][-1]

                for i in sorted(series, key=series.get):
                    self.create_line(title=series[i], serial_id=self.params['id'], se_code=self.params['code'], folder=False, params={
                        'mode': 'torrent_part', 'id': self.params['param'], 'param': i})
            else:
                self.create_line(title=torrent['info']['name'], serial_id=self.params['id'], se_code=self.params['code'], folder=False, params={
                    'mode': 'torrent_part', 'id': self.params['param'], 'param': 0})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_play_part(self):
        se_code = self.params['param']
        serial_episode = int(se_code[len(se_code)-3:len(se_code)])
        serial_season = int(se_code[len(se_code)-6:len(se_code)-3])
        image_id = int(se_code[:len(se_code)-6])

        url = '{}v_search.php?c={}&s={}&e={}'.format(
            self.site_url, image_id, serial_season, serial_episode)
        html = self.network.get_html(target_name=url)
        
        new_url = html[html.find('url=http')+4:html.find('&newbie=')]
        html = self.network.get_html(new_url)

        data_array = html[html.find('<div class="inner-box--label">')+30:html.find('<div class="inner-box--info')]
        data_array = data_array.split('<div class="inner-box--label">')

        quality = {}
                        
        for data in data_array:
            quality_data = data[:data.find('</div>')].strip()
                    
            torrent_url = data[data.find('<a href="')+9:]
            torrent_url = torrent_url[:torrent_url.find('">')]
                
            quality[quality_data] = torrent_url

        try:
            url = quality[addon.getSetting('quality')]
        except:
            choice = list(quality.keys())
            result = self.dialog.select('Доступное качество: ', choice)
            result_quality = choice[int(result)]
            url = quality[result_quality]

        file_name = self.network.get_file(target_url=url, target_path=self.torrents_dir, se_code=se_code)
        torrent_file = os.path.join(self.torrents_dir, file_name)

        import player
        confirm = player.selector(
            series_index=serial_episode,
            torrent_url=torrent_file,
            )

        if confirm:
            html = self.network.get_html(
                target_name='{}ajaxik.php'.format(self.site_url),
                post = 'session={}&act=serial&type=markepisode&val={}&auto=0&mode={}'.format(
                    addon.getSetting('user_session'), self.params['param'], 'on'))

if __name__ == "__main__":
    lostfilm = Lostfilm()
    lostfilm.execute()
    del lostfilm

gc.collect()