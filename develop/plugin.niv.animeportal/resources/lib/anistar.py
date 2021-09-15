# -*- coding: utf-8 -*-

import os, sys, time
import xbmc, xbmcgui, xbmcplugin

try:
    from urllib import urlencode, urlopen, quote, unquote
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen
    from html import unescape

#import info
#from utility import tag_list, unescape, clean_list
from utility import tag_list, clean_list

class Anistar:
    #def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress):
    def __init__(self, addon_data_dir, params, addon, icon):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.params = params
        self.addon = addon
        self.icon = icon.replace('icon', self.params['portal'])

        self.images_dir = os.path.join(addon_data_dir, 'images')
        self.torrents_dir = os.path.join(addon_data_dir, 'torrents')
        self.database_dir = os.path.join(addon_data_dir, 'database')
        self.cookie_dir = os.path.join(addon_data_dir, 'cookie')

        if self.addon.getSetting('anistar_adult') == 'false':
            try: self.addon.setSetting('anistar_adult_pass', '')
            except: pass

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('anistar_auth_mode') == '1')
#========================#========================#========================#
        try: anistar_session = float(self.addon.getSetting('anistar_session'))
        except: anistar_session = 0

        if time.time() - anistar_session > 28800:
            self.addon.setSetting('anistar_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'anistar.sid'))
            except: pass
            self.addon.setSetting('anistar_auth', 'false')
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            auth_usage=self.auth_mode,
            auth_status=bool(self.addon.getSetting('anistar_auth') == 'true'),
            proxy_data=self.proxy_data,
            portal='anistar')
        self.auth_post_data = {
            'login_name': self.addon.getSetting('anistar_username'),
            'login_password': self.addon.getSetting('anistar_password'),
            'login': 'submit'}
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = self.site_url
        self.network.sid_file = os.path.join(self.cookie_dir, 'anistar.sid')
        del WebTools
#========================#========================#========================#
        if self.auth_mode:
            if not self.addon.getSetting("anistar_username") or not self.addon.getSetting("anistar_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok(u'Авторизация',u'Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok(u'Авторизация',u'Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting("anistar_auth", str(self.network.auth_status).lower())
#========================#========================#========================#
        # if not os.path.isfile(os.path.join(self.database_dir, 'anistar.db')):
        #     self.exec_update_database_part()
        if not os.path.isfile(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))):
            self.exec_update_database_part()
#========================#========================#========================#
        # from database import Anistar_DB
        # self.database = Anistar_DB(os.path.join(self.database_dir, 'anistar.db'))
        # del Anistar_DB
        from database import DataBase
        self.database = DataBase(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        del DataBase
#========================#========================#========================#
        # self.anistar_genres=[('thriller/','Боевик'),('vampires/','Вампиры'),('ani-garem/','Гарем'),('detective/','Детектив'),('drama/','Драма'),('history/','История'),('cyberpunk/','Киберпанк'),('comedy/','Комедия'),('maho-shoujo/','Махо-седзе'),('fur/','Меха'),('parodies/','Пародии'),('senen/','Сёнен'),('sports/','Спорт'),('mysticism/','Мистика'),('music/','Музыкальное'),('everyday-life/','Повседневность'),('adventures/','Приключения'),('romance/','Романтика'),('shoujo/','Сёдзе'),('senen-ay/','Сёнен-ай'),('horror/','Триллер'),('horor/','Ужасы'),('fantasy/','Фантастика'),('fentezi/','Фэнтези'),('school/','Школа'),('echchi-erotic/','Эччи'),('action/','Экшен'),('metty/','Этти'),('seinen/','Сейнен'),('demons/','Демоны'),('magic/','Магия'),('super-power/','Супер сила'),('military/','Военное'),('kids/','Детское'),('supernatural/','Сверхъестественное'),('psychological/','Психологическое'),('historical/','Исторический'),('samurai/','Самураи'),('martial-arts/','Боевые искусства'),('police/','Полиция'),('space/','Космос'),('game/','Игры'),('josei/','Дзёсэй'),('shoujo-ai/','Сёдзе Ай')]
        # self.anistar_ignor_list = ['7013','6930','6917','6974','6974','4106','1704','1229','1207','1939','1954','2282','4263','4284','4288','4352','4362','4422','4931','5129','5130','5154','5155','6917','6928','6930','6932','6936','6968','6994','7013','7055','3999','4270','4282','4296','4300','4314','4348','4349','4364','4365','4366','4367','4368','4369','4374','4377','4480','4493','4556','6036','3218','3943','3974','4000','4091']
#========================#========================#========================#
    def create_proxy_data(self):
        #if self.addon.getSetting('anidub_unblock') == '0':
        if '0' in self.addon.getSetting('{}_unblock'.format(self.params['portal'])):
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            # try: proxy_pac = str(proxy_pac, encoding='utf-8')
            # except: pass
            try: proxy_pac = proxy_pac.decode('utf-8')
            except: pass
            
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                # try: proxy_pac = str(proxy_pac, encoding='utf-8')
                # except: pass

                try: proxy_pac = proxy_pac.decode('utf-8')
                except: pass
                
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#========================#========================#========================#
    def create_site_url(self):
        site_url = self.addon.getSetting('anistar_mirror_0')
        current_mirror = 'anistar_mirror_{}'.format(self.addon.getSetting('anistar_mirror_mode'))        

        if not self.addon.getSetting(current_mirror):
            try:
                self.exec_mirror_part()
                site_url = '{}'.format(self.addon.getSetting('anistar_mirror'))
            except:
                site_url = self.addon.getSetting('anistar_mirror_0')
        else:
            site_url = '{}'.format(self.addon.getSetting(current_mirror))
        return site_url
#========================#========================#========================#
    def create_title_info(self, title):
        info = dict.fromkeys(['title_ru', 'title_en'], '')

        alphabet=set(u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')

        #title = unescape(title)
        title = tag_list(title)
        title = title.replace('|', '/')
        title = title.replace('\\', '/')
        
        v = title.split('/', 1)

        if len(v) == 1:
            v.append('')

        if alphabet.isdisjoint(v[0].lower()): #если v[0] не ru
            if not alphabet.isdisjoint(v[1].lower()): #если v[1] ru
                v.reverse()

        # if v[1].find('/') > -1:
        #     v[1] = v[1][:v[1].find('/')]

# доделать обработку v[1] - разделить еще раз, выбрать английскую часть , остальное выкинуть

        try:
            info['title_ru'] = v[0].strip().capitalize()
            info['title_en'] = v[1].strip().capitalize()
        except: pass
        
        return info
#========================#========================#========================#
    def create_title(self, title, series):
        if series:
            series = u' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
        
        #if self.addon.getSetting('anistar_titles') == '0':
        if '0' in self.addon.getSetting('anistar_titles'):
            label = u'{}{}'.format(title[0], series)
        #if self.addon.getSetting('anistar_titles') == '1':
        if '1' in self.addon.getSetting('anistar_titles'):
            label = u'{}{}'.format(title[1], series)
        #if self.addon.getSetting('anistar_titles') == '2':
        if '2' in self.addon.getSetting('anistar_titles'):
            label = u'{} / {}{}'.format(title[0], title[1], series)
        return label
#========================#========================#========================#
    def create_image(self, anime_id):
        url = '{}uploads/posters/{}/original.jpg'.format(self.site_url, anime_id)

        if self.addon.getSetting('anistar_covers') == '0':
            return url
        else:
            #local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            local_img = '{}_{}{}'.format(self.params['portal'], anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                local_path = os.path.join(self.images_dir, local_img)
                return local_path
            else:
                file_name = os.path.join(self.images_dir, local_img)
                return self.network.get_file(target_name=url, destination_name=file_name)
#========================#========================#========================#
    def create_context(self, anime_id):
        context_menu = []
        
        context_menu.append(('[B][COLOR=darkorange]Обновить Базу Данных[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_database_part&portal=anistar")'))
        context_menu.append(('[B][COLOR=darkorange]Обновить Зеркала[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=mirror_part&portal=anistar")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=red]Очистить историю[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=anistar")'))

        if self.auth_mode and not self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=white]Добавить FAV (сайт)[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=plus&id={}&portal=anistar")'.format(anime_id)))
            context_menu.append(('[B][COLOR=white]Удалить FAV (сайт)[/B][/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=favorites_part&node=minus&id={}&portal=anistar")'.format(anime_id)))

        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append(('[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=anistar")'))
        context_menu.append(('[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=anistar")'))
        context_menu.append(('[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=anistar")'))
        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))

        return context_menu
#========================#========================#========================#
    def create_line(self, title=None, cover=None, params=None, anime_id=None, size=None, folder=True, online=None, metadata=None):
        li = xbmcgui.ListItem(title)

        if anime_id:
            if cover:
                pass
            else:
                cover = self.create_image(anime_id)
            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})
            # 0     1       2           3           4           5       6       7       8       9           10          11      12          13      14      15          16      17      18      19
            #kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios
            anime_info = self.database.get_anime(anime_id)
            
            description = u'{}\n\n[COLOR=steelblue]Озвучивание[/COLOR]: {}'.format(anime_info[10], anime_info[11])
            description = u'{}\n[COLOR=steelblue]Перевод[/COLOR]: {}'.format(description, anime_info[12])
            description = u'{}\n[COLOR=steelblue]Тайминг[/COLOR]: {}'.format(description, anime_info[13])
            description = u'{}\n[COLOR=steelblue]Работа над звуком[/COLOR]: {}'.format(description, anime_info[14])
            description = u'{}\n[COLOR=steelblue]Mastering[/COLOR]: {}'.format(description, anime_info[15])
            description = u'{}\n[COLOR=steelblue]Редактирование[/COLOR]: {}'.format(description, anime_info[16])
            description = u'{}\n[COLOR=steelblue]Другое[/COLOR]: {}'.format(description, anime_info[17])

            info = {
                'genre':anime_info[7], #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                'country':anime_info[18],#string (Germany) or list of strings (["Germany", "Italy", "France"])
                'year':anime_info[3],#	integer (2009)
                'episode':anime_info[2],#	integer (4)
                #'season':'',#	integer (1)
                #'sortepisode':'',#	integer (4)
                #'sortseason':'',#	integer (1)
                #'episodeguide':'',#	string (Episode guide)
                #'showlink':'',#	string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])
                #'top250':'',#	integer (192)
                #'setid':'',#	integer (14)
                #'tracknumber':'',#	integer (3)
                #'rating':'',#	float (6.4) - range is 0..10
                #'userrating':'',#	integer (9) - range is 1..10 (0 to reset)
                #'watched':'',#	deprecated - use playcount instead
                #'playcount':'',#	integer (2) - number of times this item has been played
                #'overlay':'',#	integer (2) - range is 0..7. See Overlay icon types for values
                #'cast':'',#	list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole
                #'castandrole':'',#	list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
                'director':anime_info[9],#	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                'mpaa':anime_info[5],#	string (PG-13)
                'plot':description,#	string (Long Description)
                #'plotoutline':'',#	string (Short Description)
                'title':title,#	string (Big Fan)
                #'originaltitle':'',#	string (Big Fan)
                #'sorttitle':'',#	string (Big Fan)
                'duration':anime_info[6],#	integer (245) - duration in seconds
                'studio':anime_info[19],#	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                #'tagline':'',#	string (An awesome movie) - short description of movie
                'writer':anime_info[8],#	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                'tvshowtitle':title,#	string (Heroes)
                'premiered':anime_info[3],#	string (2005-03-04)
                'status':anime_info[1],#	string (Continuing) - status of a TVshow
                #'set':'',#	string (Batman Collection) - name of the collection
                #'setoverview':'',#	string (All Batman movies) - overview of the collection
                #'tag':'',#	string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
                #'imdbnumber':'',#	string (tt0110293) - IMDb code
                #'code':'',#	string (101) - Production code
                'aired':anime_info[3],#	string (2008-12-07)
                #'credits':'',#	string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
                #'lastplayed':'',#	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #'album':'',#	string (The Joshua Tree)
                #'artist':'',#	list (['U2'])
                #'votes':'',#	string (12345 votes)
                #'path':'',#	string (/home/user/movie.avi)
                #'trailer':'',#	string (/home/user/trailer.avi)
                #'dateadded':'',#	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #'mediatype':anime_info[0],#	string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
                #'dbid':'',#	integer (23) - Only add this for items which are part of the local db. You also need to set the correct 'mediatype'!
            }

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = 'anistar'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        if online: url = online
        #xbmc.log(str(online), xbmc.LOGNOTICE)

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    # def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, online=None): 
    #     li = xbmcgui.ListItem(title)

    #     if anime_id:
    #         cover = self.create_image(anime_id)
    #         art = {'icon': cover, 'thumb': cover, 'poster': cover}
    #         li.setArt(art)

    #         anime_info = self.database.get_anime(anime_id)
    #         info = {'title': title, 'year': anime_info[0], 'genre': anime_info[1], 'director': anime_info[2], 'writer': anime_info[3], 'plot': anime_info[4]}

    #         if size: info['size'] = size

    #         li.setInfo(type='video', infoLabels=info)

    #     li.addContextMenuItems(self.create_context(anime_id))

    #     if folder==False:
    #             li.setProperty('isPlayable', 'true')

    #     params['portal'] = 'anistar'
    #     url = '{}?{}'.format(sys.argv[0], urlencode(params))

    #     if online: url = unquote(online)

    #     xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def create_info(self, anime_id, data, schedule=False, update=False):
        info = dict.fromkeys(['title_ru', 'title_en', 'year', 'genre', 'director', 'author', 'plot'], '')

        if schedule:
            url = '{}index.php?newsid={}'.format(self.site_url, anime_id)
            data = self.network.get_html2(target_name=url)

            try: data = data.decode(encoding='utf-8', errors='replace')
            except: pass

            data = unescape(data)

            title_data = data[data.find('<h1'):data.find('</h1>')]
        else:
            title_data = data[data.find('>')+1:data.find('</a>')]
        
        info.update(self.create_title_info(title_data))

        #xbmc.log(str(type(data)), xbmc.LOGNOTICE)
        genre = data[data.find('<p class="tags">')+16:data.find('</a></p>')]
        genre = genre.replace(u'Новинки(онгоинги)', '').replace(u'Аниме', '')
        genre = genre.replace(u'Категория:', '').replace(u'Хентай', '')
        genre = genre.replace(u'Дорамы', '').replace('></a>,','>')
        info['genre'] = tag_list(genre)

        if u'Новости сайта' in info['genre']:
            if u'<li><b>Жанр: </b>' in data:
                pass
            else:
                return 999

        data_array = data[data.find('news_text">')+11:data.find('<div class="descripts"')]
        data_array = data_array.splitlines()

        for line in data_array:
            if u'Год выпуска:' in line:
                for year in range(1950, 2030, 1):
                    if str(year) in line:
                        info['year'] = year
            if u'Режиссёр:' in line:
                line = line.replace(u'Режиссёр:','')
                info['director'] = tag_list(line)
            if u'Автор оригинала:' in line:
                line = line.replace(u'Автор оригинала:','')
                info['author'] = tag_list(line)

        if schedule:
            plot = data[data.find('description">')+13:data.find('<div class="descripts">')]
        else:
            plot = data[data.find('<div class="descripts">'):data.rfind('<div class="clear"></div>')]

        if '<p class="reason">' in plot:
            plot = plot[:plot.find('<p class="reason">')]

        plot = clean_list(plot)
        #plot = unescape(plot)

        if '<div class="title_spoiler">' in plot:
            spoiler = plot[plot.find('<div class="title_spoiler">'):plot.find('<!--spoiler_text_end-->')]
            spoiler = spoiler.replace('</div>', ' ').replace('"','')
            spoiler = spoiler.replace('#', '\n#')
            spoiler = tag_list(spoiler)

            plot = plot[:plot.find('<!--dle_spoiler')]
            plot = tag_list(plot)
            info['plot'] = u'{}\n\n{}'.format(plot, spoiler)
        else:
            info['plot'] = tag_list(plot)
        
        try:
            self.database.add_anime(
                anime_id=anime_id,
                title_ru = info['title_ru'],
                title_en = info['title_en'],                
                aired_on = info['year'],
                genres = info['genre'],
                director = info['director'],
                writer = info['author'],
                description = info['plot'],
                update = update
            )
        except:
            return 101
        # try:
        #     self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['year'], info['genre'], info['director'], info['author'], info['plot'])
        # except: return 101
        return
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_addon_setting(self):
        self.addon.openSettings()
#========================#========================#========================#
    def exec_update_database_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal'])))
        except: pass

        db_file = os.path.join(self.database_dir, 'ap_{}.db'.format(self.params['portal']))
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/ap_{}.db'.format(self.params['portal'])
        try:                
            data = urlopen(db_url)
            chunk_size = 8192
            bytes_read = 0

            try: file_size = int(data.info().getheaders("Content-Length")[0])
            except: file_size = int(data.getheader('Content-Length'))

            self.progress.create(u'Загрузка Базы Данных')
            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress.update(int(percent), u'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                self.progress.close()
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
                self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
    # def exec_update_database_part(self):
    #     try: self.database.end()
    #     except: pass
        
    #     #try: os.remove(os.path.join(self.database_dir, 'anidub.db'))
    #     try: os.remove(os.path.join(self.database_dir, '{}.db'.format(self.params['portal'])))
    #     except: pass

    #     #db_file = os.path.join(self.database_dir, 'anidub.db')
    #     db_file = os.path.join(self.database_dir, '{}.db'.format(self.params['portal']))
    #     #db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anidub.db'
    #     db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/{}.db'.format(self.params['portal'])
    #     try:                
    #         data = urlopen(db_url)
    #         chunk_size = 8192
    #         bytes_read = 0

    #         try: file_size = int(data.info().getheaders("Content-Length")[0])
    #         except: file_size = int(data.getheader('Content-Length'))

    #         self.progress.create('Загрузка Базы Данных')
    #         with open(db_file, 'wb') as write_file:
    #             while True:
    #                 chunk = data.read(chunk_size)
    #                 bytes_read = bytes_read + len(chunk)
    #                 write_file.write(chunk)
    #                 if len(chunk) < chunk_size:
    #                     break
    #                 percent = bytes_read * 100 / file_size
    #                 self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
    #             self.progress.close()
    #         #label_1 = '{} - База Данных'.format(self.params['portal'].upper())
    #         #label_2 = 'База Данных [COLOR=lime]успешно загружена[/COLOR]'
    #         xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
    #             self.params['portal'].capitalize()), 'База Данных [COLOR=lime]успешно загружена[/COLOR]', 5000, self.icon))
    #         #self.dialog.ok('AniDUB - База Данных','БД успешно загружена')
    #     except:
    #         xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - База Данных'.format(
    #             self.params['portal'].capitalize()), 'База Данных [COLOR=yellow]ERROR: 100[/COLOR]', 5000, self.icon))
    #         #self.dialog.ok('AniDUB - База Данных','Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
    #         pass
#========================#========================#========================#
    # def exec_update_database_part(self):
    #     try: self.database.end()
    #     except: pass
        
    #     try: os.remove(os.path.join(self.database_dir, 'anistar.db'))
    #     except: pass        

    #     db_file = os.path.join(self.database_dir, 'anistar.db')
    #     db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/anistar.db'
    #     try:                
    #         data = urlopen(db_url)
    #         chunk_size = 8192
    #         bytes_read = 0

    #         try: file_size = int(data.info().getheaders("Content-Length")[0])
    #         except: file_size = int(data.getheader('Content-Length'))

    #         self.progress.create('Загрузка Базы Данных')
    #         with open(db_file, 'wb') as write_file:
    #             while True:
    #                 chunk = data.read(chunk_size)
    #                 bytes_read = bytes_read + len(chunk)
    #                 write_file.write(chunk)
    #                 if len(chunk) < chunk_size:
    #                     break
    #                 percent = bytes_read * 100 / file_size
    #                 self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
    #             self.progress.close()
    #         self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
    #     except:
    #         self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
    #         pass
#========================#========================#========================#
    def exec_mirror_part(self):
        from network import WebTools
        self.net = WebTools(auth_usage=False, auth_status=False, proxy_data=self.proxy_data)
        del WebTools

        current_mirror = 'anistar_mirror_{}'.format(self.addon.getSetting('anistar_mirror_mode'))
        site_url = self.addon.getSetting('anistar_mirror_0')

        try:            
            #ht = self.net.get_html2(target_name='https://anistar.org/')
            ht = self.net.get_html2(target_name=site_url)
            actual_url = ht[ht.find('<center><h3><b><u>'):ht.find('</span></a></u></b></h3></center>')]
            actual_url = tag_list(actual_url).lower()
            actual_url = 'https://{}/'.format(actual_url)
            self.addon.setSetting('anistar_unblock', '0')
            
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - [COLOR=lime]Выполнено[/COLOR]'.format(
                self.params['portal'].capitalize()), 'Применяем новый адрес:\n[COLOR=blue]{}[/COLOR], Отключаем разблокировку'.format(actual_url), 5000, self.icon))
            #self.dialog.ok('AniStar', '[COLOR=lime]Выполнено[/COLOR]: Применяем новый адрес:\n[COLOR=blue]{}[/COLOR], Отключаем разблокировку'.format(actual_url))            
        except:
            #actual_url = 'https://anistar.org/'
            actual_url = site_url
            self.addon.setSetting('anistar_unblock', '1')
            
            xbmc.executebuiltin('Notification({},{},{},{})'.format('{} - [COLOR=red]Ошибка[/COLOR]'.format(
                self.params['portal'].capitalize()), 'Применяем базовый адрес:\n[COLOR=blue]{}[/COLOR], Включаем разблокировку'.format(actual_url), 5000, self.icon))
            #self.dialog.ok('AniStar', '[COLOR=red]Ошибка[/COLOR]: Применяем базовый адрес:\n[COLOR=blue]{}[/COLOR], Включаем разблокировку'.format(actual_url))

        self.addon.setSetting(current_mirror, actual_url)
#========================#========================#========================#
    def exec_favorites_part(self):
        url = '{}engine/ajax/favorites.php?fav_id={}&action={}&skin=new36'.format(self.site_url, self.params['id'], self.params['node'])
        label = self.database.get_title(self.params['id'])[0]

        if 'plus' in self.params['node']:
            try:
                self.network.get_html2(target_name=url)
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно добавлено[/COLOR]'.format(label))
            except:
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - 103[/COLOR]'.format(label))

        if 'minus' in self.params['node']:
            try:
                self.network.get_html2(target_name=url)
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Успешно удалено[/COLOR]'.format(label))
            except:
                self.dialog.ok('Избранное','{}\n\n[COLOR=gold]Ошибка - 103[/COLOR]'.format(label))
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            self.addon.setSetting('{}_search'.format(self.params['portal']), '')
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=lime]успешно выполнено[/COLOR]', 5000, self.icon))
        except:
            xbmc.executebuiltin('Notification({},{},{},{})'.format('Поиск', 'Удаление истории [COLOR=yellow]ERROR: 102[/COLOR]', 5000, self.icon))
            pass
#========================#========================#========================#
    def exec_information_part(self):
        from info import animeportal_data as info
            
        start = '[{}]'.format(self.params['param'])
        end = '[/{}]'.format(self.params['param'])
        data = info[info.find(start)+6:info.find(end)].strip()

        self.dialog.textviewer(u'Информация', data)
        return
#========================#========================#========================#
    def exec_main_part(self):
        if self.auth_mode:
            self.create_line(title=u'[B][COLOR=white][ Избранное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'favorites/'})
        self.create_line(title=u'[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title=u'[B][COLOR=lime][ Расписание ][/COLOR][/B]', params={'mode': 'schedule_part'})
        self.create_line(title=u'[B][COLOR=lime][ Категории ][/COLOR][/B]', params={'mode': 'categories_part'})
        self.create_line(title=u'[B][COLOR=lime][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'new/'})
        self.create_line(title=u'[B][COLOR=lime][ RPG ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'rpg/'})
        self.create_line(title=u'[B][COLOR=lime][ Скоро ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'next/'})        
        #if self.addon.getSetting('anistar_adult') == '1':
        if '1' in self.addon.getSetting('anistar_adult'):
            if self.addon.getSetting('anistar_adult_pass') in self.anistar_ignor_list:
                self.create_line(title=u'[B][COLOR=lime][ Хентай ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'hentai/'})
        self.create_line(title=u'[B][COLOR=gold][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'dorams/'})
        self.create_line(title=u'[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'cartoons/'})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title=u'[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по жанрам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'genres'})
            self.create_line(title=u'[B][COLOR=red][ Поиск по году ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'years'})

            data_array = self.addon.getSetting('anistar_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                
                try: self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data.decode('utf8').encode('cp1251'))})
                except: self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data.encode('cp1251'))})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                search_string = skbd.getText()
                
                try: self.params['search_string'] = quote(search_string.decode('utf8').encode('cp1251'))
                except: self.params['search_string'] = quote(search_string.encode('cp1251'))

                data_array = self.addon.getSetting('anistar_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(search_string))
                self.addon.setSetting('anistar_search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        if 'genres' in self.params['param']:
            from info import anistar_genres

            for i in anistar_genres:
                label = '{}'.format(i[1])
                self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&xf={}'.format(quote(i[1]))})

        if 'years' in self.params['param']:
            from info import anistar_years
            for i in anistar_years:
                label = '{}'.format(i)
                self.create_line(title=label, params={'mode': 'common_part', 'param': '&do=xfsearch&type=year&r=anime&xf={}'.format(i)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_categories_part(self):
        from info import anistar_genres

        for data in anistar_genres:
            label = '[B][COLOR=white]{}[/COLOR][/B]'.format(data[1])
            self.create_line(title=label, params={'mode': 'common_part', 'param': '{}'.format(data[0])})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_schedule_part(self):
        self.progress.create("AniStar", "Инициализация")

        #url = '{}{}'.format(self.site_url, 'raspisanie-vyhoda-seriy-ongoingov.html')
        html = self.network.get_html2(
            target_name='{}{}'.format(self.site_url, 'raspisanie-vyhoda-seriy-ongoingov.html'))

        try: html = html.decode(encoding='utf-8', errors='replace')
        except: pass

        html = unescape(html)

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return  

        week_title = []

        today_title = html[html.find('<span>[')+7:html.find(']</span>')]
        today_title = u'{} - {}'.format(u'Сегодня', today_title)

        call_list = html[html.find('<div class=\'cal-list\'>'):html.find('<div id="day1')]
        week_list = u'{}{}'.format(today_title, call_list).replace('<span>',' - ')        
        week_list = tag_list(week_list)
        week_list = week_list.splitlines()

        for day in week_list:
            week_title.append(day)

        data_array = html[html.find('<div class="news-top">'):html.find('function calanime')]
        data_array = data_array.replace(call_list, '')
        data_array = data_array.split('<div id="day')

        w = 0
        i = 0

        for array in data_array:
            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            array = array.split('<div class="top-w" >')
            array.pop(0)

            day_title = u'{}'.format(week_title[w])
            self.create_line(title=u'[B][COLOR=lime]{}[/COLOR][/B]'.format(day_title), params={})
            
            if self.progress.iscanceled():
                break
            self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            for data in array:
                anime_id = data[data.find(self.site_url):data.find('.html">')].replace(self.site_url, '')
                anime_id = anime_id[:anime_id.find('-')]                
                series = ''

                if '<smal>' in data:
                    series = data[data.find('<smal>')+6:data.find('</smal>')]
                else:
                    series = data[data.find('<div class="timer_cal">'):]
                    series = tag_list(series)

                if not self.database.anime_in_db(anime_id):
                    inf = self.create_info(anime_id, data=None, schedule=True)

                label = self.create_title(self.database.get_title(anime_id), series)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

            w = w + 1
        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_common_part(self):
        from info import anistar_ignor_list

        self.progress.create("AniStar", u"Инициализация")
        
        url = '{}{}page/{}/'.format(self.site_url, self.params['param'], self.params['page'])
        post = ''
        
        if 'xfsearch' in self.params['param']:
            url = '{}index.php?cstart={}{}'.format(self.site_url, self.params['page'], self.params['param'])

        if self.params['param'] == 'search_part':
            url = self.site_url
            post = 'do=search&subaction=search&search_start={}&full_search=1&story={}&catlist%5B%5D=39&catlist%5B%5D=113&catlist%5B%5D=76'.format(
                self.params['page'], self.params['search_string'])

        #xbmc.log(str(url), xbmc.LOGNOTICE)
        html = self.network.get_html2(target_name=url, post=post)

        try: html = html.decode(encoding='utf-8', errors='replace')
        except: pass

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return   
        
        data_array = html[html.find('title_left">')+12:html.rfind('<div class="panel-bottom-shor">')]
        data_array = data_array.split('<div class="title_left">')

        if self.params['param'] == 'search_part':
            data_array.pop(0)

        if len(data_array) < 1:
            self.create_line(title=u'[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return   

        i = 0

        for data in data_array:
            data = unescape(data)

            i = i + 1
            p = int((float(i) / len(data_array)) * 100)

            if u'/m/">Манга</a>' in data:
                continue

            if u'/hentai/">Хентай</a>' in data:
                if not self.addon.getSetting('anistar_adult_pass') in self.anistar_ignor_list:
                    continue

            anime_id = data[data.find(self.site_url):data.find('">')].replace(self.site_url, '')
            anime_id = anime_id.replace('index.php?newsid=', '').split('-',1)[0]

            series = ''
            if '<p class="reason">' in data:
                series = data[data.find('<p class="reason">')+18:data.rfind('</p>')]

            if anime_id in anistar_ignor_list:
                continue

            if self.progress.iscanceled():
                break
            self.progress.update(p, u'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

            if not self.database.anime_in_db(anime_id):
                inf = self.create_info(anime_id, data)

                if type(inf) == int:
                    if not inf == 999:
                        self.create_line(title='[B][ [COLOR=red]ERROR: {}[/COLOR] - [COLOR=red]ID:[/COLOR] {} ][/B]'.format(inf, anime_id), params={})
                    continue

            label = self.create_title(self.database.get_title(anime_id), series)
            self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

        self.progress.close()

        if 'button_nav r"><a' in html:
            #if self.params['param'] == 'search_part':
            if 'search_part' in self.params['param']:
                self.create_line(title=u'[B][COLOR=skyblue][ Следующая страница ][/COLOR][/B]', params={
                                 'mode': 'common_part', 'search_string': self.params['search_string'], 'param': 'search_part', 'page': int(self.params['page']) + 1})
            else:
                self.create_line(title=u'[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={
                    'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_select_part(self):
        self.create_line(title=u'[B][ Онлайн просмотр ][/B]', params={'mode': 'online_part', 'id': self.params['id']})
        self.create_line(title=u'[B][ Торрент просмотр ][/B]', params={'mode': 'torrent_part', 'id': self.params['id']})        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_online_part(self):
        if not self.params['param']:
            video_url = '{}test/player2/videoas.php?id={}'.format(self.site_url, self.params['id'])
            html = self.network.get_html2(target_name=video_url)

            try: html = html.decode(encoding='utf-8', errors='replace')
            except: pass

            html = unescape(html)

            data_array = html[html.find('playlst=[')+9:html.find('];')]
            data_array = data_array.split('{')
            data_array.pop(0)

            array = {'480p [multi voice]': [],'720p [multi voice]': [],'480p [single voice]': [],'720p [single voice]': []}

            for data in data_array:
                title = data[data.find('title:"')+7:data.find('",')]
                file_data =  data[data.find('php?360=')+4:data.rfind('",')]

                sd_url = file_data[file_data.find('360=')+4:file_data.find('.m3u8')+5]
                hd_url = sd_url.replace('360', '720')

                if u'Многоголосая озвучка' in title:
                    array['480p [multi voice]'].append(u'{}|{}'.format(title, sd_url))
                    array['720p [multi voice]'].append(u'{}|{}'.format(title, hd_url))
                else:
                    array['480p [single voice]'].append(u'{}|{}'.format(title, sd_url))
                    array['720p [single voice]'].append(u'{}|{}'.format(title, hd_url))
            
            for i in array.keys():
                if array[i]:
                    array_info = '|||'.join(array[i])

                    try: array_info = array_info.encode('utf-8')
                    except: pass

                    label = '[B]Качество: {}[/B]'.format(i)
                    label = label.replace('480p','[COLOR=gold]480p[/COLOR]')
                    label = label.replace('720p','[COLOR=gold]720p[/COLOR]')
                    label = label.replace('[single voice]','[COLOR=blue][single voice][/COLOR]')
                    label = label.replace('[multi voice]','[COLOR=lime][multi voice][/COLOR]')

                    self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': array_info}, anime_id=self.params['id'])
                    #self.create_line(title=label, params={'mode': 'online_part', 'id': self.params['id'], 'param': '|||'.join(array[i])}, anime_id=self.params['id'])

        if self.params['param']:
            #try: data_array = self.params['param'].decode(encoding='utf-8', errors='replace')
            #except: pass
            #except: data_array = self.params['param']
            data_array = unquote(self.params['param']).split('|||')

            #data_array = self.params['param'].split('|||')
            #data_array = data_array.split('|||')

            for data in data_array:
                data = data.split('|')

                #label = data[0].replace('single voice','1111')
                #xbmc.log(str(data[1]), xbmc.LOGNOTICE)

                self.create_line(title=data[0], params={}, anime_id=self.params['id'], online=data[1], folder=False)
                #self.create_line(title=label, params={}, anime_id=self.params['id'], online=data[1], folder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_torrent_part(self):
        if not self.params['param']:
            html = self.network.get_html2('{}index.php?newsid={}'.format(self.site_url, self.params['id']))

            if not '<div class="title">' in html:
                self.create_line(title=u'Контент не обнаружен', params={})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            data_array = html[html.find('<div class="title">')+19:html.rfind('<div class="bord_a1">')]
            data_array = data_array.split('<div class="title">')

            for data in data_array:
                torrent_url = data[data.find('gettorrent.php?id=')+18:data.find('">')]

                data = clean_list(data).replace('<b>','|').replace('&nbsp;','')            
                data = tag_list(data).split('|')

                torrent_title = data[0][:data[0].find('(')].strip()
                torrent_seed = data[1].replace('Раздают:', '').strip()
                torrent_peer = data[2].replace('Качают:', '').strip()
                torrent_size = data[4].replace('Размер:', '').strip()

                label = '{} , [COLOR=yellow]{}[/COLOR], Сидов: [COLOR=green]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                    torrent_title, torrent_size, torrent_seed, torrent_peer)
                    
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'param': torrent_url},  anime_id=self.params['id'])

        if self.params['param']:
            url = '{}engine/gettorrent.php?id={}'.format(self.site_url, self.params['param'])

            file_name = '{}_{}'.format(self.params['portal'], self.params['param'])
            full_name = os.path.join(self.torrents_dir, '{}.torrent'.format(file_name))
            torrent_file = self.network.get_file(target_name=url, destination_name=full_name)

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
                    self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': file_name}, anime_id=self.params['id'], folder=False, size=size[i])
            else:
                self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': file_name}, anime_id=self.params['id'], folder=False, size=info['length'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])
        portal_engine = '{}_engine'.format(self.params['portal'])

        if self.addon.getSetting(portal_engine) == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(self.addon.getSetting('{}_tam'.format(self.params['portal'])))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(quote(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if self.addon.getSetting(portal_engine) == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)