# -*- coding: utf-8 -*-

import os, sys, time
import xbmc, xbmcgui, xbmcplugin

try:
    from urllib import urlencode, urlopen, quote, unquote
except:
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import urlopen

from utility import tag_list, clean_list, unescape

class Animedia:
    def __init__(self, images_dir, torrents_dir, database_dir, cookie_dir, params, addon, dialog, progress):
        self.progress = progress
        self.dialog = dialog
        self.addon = addon
        self.images_dir = images_dir
        self.torrents_dir = torrents_dir
        self.database_dir = database_dir
        self.cookie_dir = cookie_dir
        self.params = params

        self.proxy_data = self.create_proxy_data()
        self.site_url = self.create_site_url()
        self.auth_mode = bool(self.addon.getSetting('animedia_auth_mode') == '1')
#================================================
        try: animedia_session = float(self.addon.getSetting('animedia_session'))
        except: animedia_session = 0

        if time.time() - animedia_session > 28800:
            self.addon.setSetting('animedia_session', str(time.time()))
            try: os.remove(os.path.join(self.cookie_dir, 'animedia.sid'))
            except: pass
            self.addon.setSetting('animedia_auth', 'false')
#================================================
        from network import WebTools
        self.network = WebTools(auth_usage=self.auth_mode,
                                auth_status=bool(self.addon.getSetting('animedia_auth') == 'true'),
                                proxy_data=self.proxy_data,
                                portal='animedia')
        self.network.sid_file = os.path.join(self.cookie_dir, 'animedia.sid' )
        self.auth_post_data = {
            'ACT': '14', 'RET': '/', 'site_id': '4',
            'username': self.addon.getSetting('animedia_username'),
            'password': self.addon.getSetting('animedia_password')}
        self.network.auth_post_data = urlencode(self.auth_post_data)
        self.network.auth_url = self.site_url
        del WebTools
#================================================
        if self.auth_mode:
            if not self.addon.getSetting("animedia_username") or not self.addon.getSetting("animedia_password"):
                self.params['mode'] = 'addon_setting'
                self.dialog.ok('Авторизация','Ошибка - укажите [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                return

            if not self.network.auth_status:
                if not self.network.auth_check():
                    self.params['mode'] = 'addon_setting'
                    self.dialog.ok('Авторизация','Ошибка - проверьте [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR]')
                    return
                else:
                    self.addon.setSetting("animedia_auth", str(self.network.auth_status).lower())
#================================================
        if not os.path.isfile(os.path.join(self.database_dir, 'animedia.db')):
            self.exec_update_part()
#================================================
        from database import Animedia_DB
        self.database = Animedia_DB(os.path.join(self.database_dir, 'animedia.db'))
        del Animedia_DB
#================================================
        self.animedia_genre = {"":"","Комедия":"1","Этти":"2","Школа":"3","Мистика":"4","Приключения":"5","Фантастика":"6","Боевые искусства":"7","Война":"9","Детектив":"11","Дзёсэй":"12","Драма":"13","Исторический":"14","Киберпанк":"15","Криминал":"17","Махо-сёдзё":"18","Медицина":"19","Меха":"21","Музыка":"23","Пародия":"25","По игре":"26","Повседневность":"27","Постапокалиптика":"29","Психология":"30","Романтика":"31","Самурайский боевик":"32","Сёдзе":"33","Сёнэн":"34","Сёнэн-ай":"35","Спорт":"37","Сэйнэн":"38","Триллер":"39","Трэш":"40","Ужасы":"41","Фэнтези":"42","Вампиры":"43","Подкасты":"47","Дорамы":"48","История":"49","Лайв-экшн":"50","Сёдзё-ай":"51","Экшен":"52","Сверхъестественное":"53","Гарем":"98"}
        self.animedia_year = {"":"","2020":"2020","2019":"2019","2018":"2018","2017":"2017","2016":"2016","2015":"2015","2014":"2014","2013":"2013","2012":"2012","2011":"2011","2010":"2010","2009":"2009","2008":"2008","2007":"2007","2006":"2006","2005":"2005","2004":"2004","2003":"2003","2002":"2002","2001":"2001","2000":"2000","1990-e":"199","1980-e":"198"}
        self.animedia_form = {"":"","ТВ-сериал":"ТВ","Фильмы":"Полнометражный","OVA, ONA, Special":"OVA","Дорама":"Дорама"}
        self.animedia_status = {"":"","Сейчас выходит":"0","Вышедшие":"1"}
        self.animedia_sort = {"Популярности":"view_count_one|desc","Дате добавления":"entry_date|desc"}
        self.animedia_studio = ("","8bit","A-1 Pictures","A.C.G.T","ACTAS"," Inc.","AIC","AIC A.S.T.A.","AIC PLUS","Ajia-do","AKOM","Animac","ANIMATE","Aniplex","ARMS","Artland","ARTMIC Studios","Asahi Production","asread","Ashi Productions","Aubeck","Bandai Visual","Barnum Studio","Bee Train","BeSTACK","Bones","Brain's Base","EMT²","Chaos Project","Cherry Lips","CLAMP","CoMix Wave Inc.","CJ Entertainment","Cinema Citrus","Daume","David Production","Dax International","Digital Frontier","Digital Works","Diomedea","DLE","Dogakobo","Dong Woo Animation","Doumu","DR Movie","Easyfilm","Eiken","EMation","Feel","Five Ways","Foursome","Fuji TV / KTV","FUNimation Entertainment","Frontier Works","G&G Entertainment","Gainax","Gallop","GANSIS","Gathering","Geneon Universal Entertainment","GoHands","Gonzino","Gonzo Digimation","Green Bunny","Group TAC","Hal Film Maker","Hangar-18","Hoods Entertainment","Idea Factory","Imagin","J.C.Staff","Jinni`s Animation Studios","Kaname Production","Khara","Kitty Films","Knack","Kokusai Eigasha","KSS","Kids Station","Kyoto Animation","Lemon Heart","Madhouse","Manpuku Jinja","Magic Bus","Magic Capsule","Manglobe","Mappa","Media Factory","MediaNet","Milky","Minamimachi Bugyosho","Mook Animation","Moonrock","MOVIC","Mystery","Nickelodeon","Mushi Production","Nippon Animation","Nippon Animedia","Nippon Columbia","Nomad","NAZ","NUT","Lantis","Lerche","Liden Films","OB Planning","Office AO","Oh! Production","OLM"," Inc.","Ordet","Oriental Light and Magic","P Production","P.A. Works","Palm Studio","Pastel","Phoenix Entertainment","Picture Magic","Pink Pineapple","Planet","Plum","Production I.G","Production Reed","Project No.9","Primastea","Pony Canyon","Polygon Pictures","Rising Force","Radix","Rikuentai","Robot","Rooster Teeth","FUNimation Entertainment","Satelight","Sanzigen","Seven Arcs","SHAFT","Shirogumi Inc.","Shin-Ei Animation","Shogakukan Music & Digital Entertainment","Soft Garage","Soft on Demand","Starchild Records","Studio 4°C","Studio Rikka","Studio APPP","Studio Blanc","Studio Comet","Studio DEEN","Studio Fantasia","Studio Flag","Studio Gallop","Studio Ghibli","Studio Guts","Studio Hibari","Studio Junio","Studio Live","Studio Pierrot","Studio Gokumi","Studio Barcelona","Sunrise","Silver Link","SynergySP","Tatsunoko Productions","Telecom Animation Film","Tezuka Productions","TMS Entertainment","TNK","The Answer Studio","The Klock Worx","Toei Animation","TV Tokyo","Tokyo Kids","Tokyo Broadcasting System","Tokyo Movie Shinsha","Top Craft","Transarts","Triangle Staff","Trinet Entertainment","Trigger","TYO Animations","UFO Table","Victor Entertainment","Viewworks","White Fox","Wonder Farm","Wit Studio","Xebec","XEBEC-M2","Zexcs","Zuiyo","Hoods Drifters Studio")
        self.animedia_voice = ("","Amails","Agzy","4a4i","Matorian","aZon","ArtLight","BlackVlastelin","Demetra","Derenn","DEMIKS","Rikku","ABSURD95","AMELIA","ANGEL","ANIMAN","Andry B","AriannaFray","AXLt","BLACK_VLASTELIN","ELADIEL","ENEMY","ENILOU","ERINANT","EneerGy","Egoist","Eugene","FaSt","FREYA","FRUKT","FUEGOALMA","FUUROU","GFT","GKONKOV","GOMER","GREH","HHANZO","HUNTER26","ITLM","JAM","JEPT","JULIABLACK","KovarnyBober","KIARA_LAINE","Kleo Rin","KUCLIA","KASHI","Kansai","Kobayashi","Kona-chan","LISEK","LINOKK","L'Roy","LUNIFERA","LUPIN","LeXar","Lyxor","MACHAON","MEISEI","MIRIKU","MisterX","MIRONA","MOONY","MULYA","MUNYA","MUSTADIO","MyDuck","MezIdA","NAZEL","NASTR","NEAR","N_O_I_R","NIKIRI","Nuriko","Neonoir","Kabrok","Komuro","LolAlice","ORIKO","OZIRIST","PERSONA99","Phoenix","RYC99","RUBY","REZAN","Riddle","Reewayvs","Railgun","Revi_Kim","Rizz_Fisher","SAHAWK","SAJURI","SANDEL","SAY","SCREAM","SHACHIBURI","SHALU","SILV","STEFAN","Soer","TDUBOVIC","TINDA","TicTac","TRAY","TRINAD","TROUBLE","Televizor","TSUMI","VIKI","VINS","YUKIO","ZACK_FAIR","ZART","ZENDOS","VULPES VUPLES","Wicked_Wayfarer","Григорий Коньков","NRG Film Distribution","Tina","ВИКТОР БОЛГОВ","Mega Anime","Пифагор","Реанимедия","Ruscico","MC Entertainment","Симбад","Ruri","Odissey","Акварелька","Garison","zaShunina","Sad_Kit","Milirina","Leo Tail","Satsuki","SilverTatsu","Sabadaher","Morin","KingMaster","Каркас")
#================================================
    def create_proxy_data(self):
        if self.addon.getSetting('animedia_unblock') == '0':
            return None

        try: proxy_time = float(self.addon.getSetting('animeportal_proxy_time'))
        except: proxy_time = 0

        if time.time() - proxy_time > 86400:
            self.addon.setSetting('animeportal_proxy_time', str(time.time()))
            proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                
            try: proxy_pac = str(proxy_pac, encoding='utf-8')
            except: pass
                
            proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
            self.addon.setSetting('animeportal_proxy', proxy)
            proxy_data = {'https': proxy}
        else:
            if self.addon.getSetting('animeportal_proxy'):
                proxy_data = {'https': self.addon.getSetting('animeportal_proxy')}
            else:
                proxy_pac = urlopen("http://antizapret.prostovpn.org/proxy.pac").read()

                try: proxy_pac = str(proxy_pac, encoding='utf-8')
                except: pass

                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                self.addon.setSetting('animeportal_proxy', proxy)
                proxy_data = {'https': proxy}

        return proxy_data
#================================================
    def create_site_url(self):
        site_url = self.addon.getSetting('animedia_mirror_0')
        #current_mirror = 'animedia_mirror_{}'.format(self.addon.getSetting('animedia_mirror_mode'))

        # if not self.addon.getSetting(current_mirror):
        #     pass
        # else:
        #     site_url = self.addon.getSetting(current_mirror)

        return site_url

    def create_url(self):
        url = '{}P{}'.format(self.site_url, int(self.params['page'])-1)

        if self.params['param'] == 'search_part':
            url = '{}ajax/search_result/P0?limit=100&keywords={}&orderby_sort=entry_date|desc'.format(self.site_url, self.params['search_string'])

        if self.params['param'] == 'popular':
            url = '{}ajax/search_result/P0?limit=100&orderby_sort=view_count_one|desc'.format(self.site_url)

        if self.params['param'] == 'catalog':
            genre = '&category={}'.format(self.animedia_genre[self.addon.getSetting('animedia_genre')]) if self.animedia_genre[self.addon.getSetting('animedia_genre')] else ''
            voice = '&search:voiced={}'.format(quote(self.addon.getSetting('animedia_voice'))) if self.addon.getSetting('animedia_voice') else ''
            studio = '&search:studies={}'.format(quote(self.addon.getSetting('animedia_studio'))) if self.addon.getSetting('animedia_studio') else ''
            sort = '&orderby_sort={}'.format(self.animedia_sort[self.addon.getSetting('animedia_sort')]) if self.animedia_sort[self.addon.getSetting('animedia_sort')] else ''
            year = '&search:datetime={}'.format(self.animedia_year[self.addon.getSetting('animedia_year')]) if self.animedia_year[self.addon.getSetting('animedia_year')] else ''
            form = '&search:type={}'.format(quote(self.animedia_form[self.addon.getSetting('animedia_form')])) if self.animedia_form[self.addon.getSetting('animedia_form')] else ''
            ongoing = '&search:ongoing={}'.format(self.animedia_status[self.addon.getSetting('animedia_status')]) if self.animedia_status[self.addon.getSetting('animedia_status')] else ''

            url = '{}ajax/search_result/P0?limit=100{}{}{}{}{}{}{}'.format(self.site_url, genre, voice, studio, year, form, ongoing, sort)
        return url
#================================================
    def create_title(self, anime_id, series):
        title = self.database.get_title(anime_id)

        if series:
            #series = series.replace('Серия','').replace('Серии','')
            series = series.strip()
            series = ' - [COLOR=gold][ {} ][/COLOR]'.format(series)
        else:
            series = ''
       
        if self.addon.getSetting('animedia_titles') == '0':
            label = '{}{}'.format(title[0], series)
        if self.addon.getSetting('animedia_titles') == '1':
            label = '{}{}'.format(title[1], series)
        if self.addon.getSetting('animedia_titles') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)

        return label

    def create_image(self, anime_id):        
        cover = self.database.get_cover(anime_id)
###========================================================  quote(cover[0])
        url = 'https://static.animedia.tv/uploads/{}'.format(quote(cover[0]))

        if self.addon.getSetting('animedia_covers') == '0':
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

    def create_context(self, anime_id):
        context_menu = []

        context_menu.append(('[B][COLOR=darkorange]Обновить Базу Данных[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_part&portal=animedia")'))

        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
            context_menu.append(('[B][COLOR=red]Очистить историю[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=animedia")'))

        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))
        context_menu.append(('[B][COLOR=lime]Новости обновлений[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=animedia")'))
        context_menu.append(('[B][COLOR=lime]Настройки воспроизведения[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=play&portal=animedia")'))
        context_menu.append(('[B][COLOR=lime]Описание ошибок плагина[/COLOR][/B]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=bugs&portal=animedia")'))
        context_menu.append(('[B][COLOR=white]- - - - - - - - - - - - - - - - [/COLOR][/B]', ''))

        return context_menu

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True, ex_info=None): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)

            anime_info = self.database.get_anime(anime_id)
            info = {'title': title, 'genre': anime_info[0], 'year': anime_info[1], 'studio': anime_info[2], 'director': anime_info[3], 'writer': anime_info[4], 'plot': anime_info[5]}

            if ex_info:
                info['plot'] += '\n\nСерии: {}\nКачество: {}\nРазмер: {}\nКонтейнер: {}\nВидео: {}\nАудио: {}\nПеревод: {}\nТайминг: {}'.format(
                    ex_info['series'], ex_info['quality'], ex_info['size'], ex_info['container'], ex_info['video'], ex_info['audio'], ex_info['translate'], ex_info['timing'])

            if size: info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
                li.setProperty('isPlayable', 'true')

        params['portal'] = 'animedia'
        url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def create_info(self, anime_id):
        url = '{}anime/{}'.format(self.site_url, anime_id)

        html = self.network.get_html(target_name=url)

        if type(html) == int: return html

        info = dict.fromkeys(['title_ru', 'title_en', 'genre', 'year', 'studio', 'director', 'author', 'plot', 'cover'], '')

        info['cover'] = html[html.rfind('<a href="https://static.animedia.tv/uploads/')+44:html.rfind('" class="zoomLink">')]

        #data_array = html[html.find('post__header">')+14:html.find('<!--Media post End-->')]
        data_array = html[html.find('post__header">')+14:html.find('</article>')]

        info['plot'] = data_array[data_array.find('<p>'):data_array.rfind('</p>')]
        info['plot'] = tag_list(info['plot'])
        info['plot'] = clean_list(info['plot'])
        info['plot'] = unescape(info['plot'])
        
        data_array = data_array.splitlines()

        for data in data_array:
            if '<h1 class="media' in data:
                info['title_ru'] = data[data.find('title">')+7:data.find('</h1>')].strip()
            if 'Жанр:' in data:
                data = data.replace('Жанр: ','').replace('</a>', ', ')
                info['genre'] = tag_list(data)[:-1]
            if 'Английское название:' in data:
                info['title_en'] = data[data.find('<span>')+6:data.find('</span>')].strip()
            if 'Дата выпуска:' in data:
                data = tag_list(data)
                for year in range(1975, 2030, 1):
                    if str(year) in data:
                        info['year'] = year
            if 'Студия:' in data:
                info['studio'] = data[data.find('<span>')+6:data.find('</span>')]
                info['studio'] = unescape(info['studio'])
            if 'Режисер:' in data:
                info['director'] = data[data.find('<span>')+6:data.find('</span>')]
            if 'Автор оригинала:' in data:
                info['author'] = data[data.find('<span>')+6:data.find('</span>')]

        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['genre'], info['year'],
                          info['studio'], info['director'], info['author'], info['plot'], info['cover'])
        except: return 101
        return

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try: self.database.end()
        except: pass

    def exec_addon_setting(self):
        self.addon.openSettings()

    def exec_update_part(self):
        try: self.database.end()
        except: pass
        
        try: os.remove(os.path.join(self.database_dir, 'animedia.db'))
        except: pass        

        db_file = os.path.join(self.database_dir, 'animedia.db')
        db_url = 'https://github.com/NIV82/kodi_repo/raw/main/resources/animedia.db'        
        try:                
            data = urlopen(db_url)
            chunk_size = 8192
            bytes_read = 0

            try: file_size = int(data.info().getheaders("Content-Length")[0])
            except: file_size = int(data.getheader('Content-Length'))

            self.progress.create('Загрузка Базы Данных')
            with open(db_file, 'wb') as write_file:
                while True:
                    chunk = data.read(chunk_size)
                    bytes_read = bytes_read + len(chunk)
                    write_file.write(chunk)
                    if len(chunk) < chunk_size:
                        break
                    percent = bytes_read * 100 / file_size
                    self.progress.update(int(percent), 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                self.progress.close()
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Успешно загружена[/COLOR]')
        except:
            self.dialog.ok('База Данных','База Данных - [COLOR=yellow]Ошибка загрузки: 100[/COLOR])')
            pass

    def exec_clean_part(self):
        try:
            self.addon.setSetting('animedia_search', '')
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]Успешно выполнено[/COLOR]')
        except:
            self.dialog.ok('Поиск','Удаление истории - [COLOR=gold]ERROR: 102[/COLOR]')
            pass

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=blue][ Популярное ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'popular'})
        self.create_line(title='[B][COLOR=yellow][ Новинки ][/COLOR][/B]', params={'mode': 'common_part'})      
        self.create_line(title='[B][COLOR=lime][ Каталог ][/COLOR][/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'search'})

            data_array = self.addon.getSetting('animedia_search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'search_part', 'search_string': quote(data)})

        if self.params['param'] == 'search':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = quote(skbd.getText())
                data_array = self.addon.getSetting('animedia_search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), unquote(self.params['search_string']))
                self.addon.setSetting('animedia_search', data_array)
                self.params['param'] = 'search_part'
                self.exec_common_part()
            else:
                return False

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_common_part(self, url=None):
        self.progress.create("Animedia", "Инициализация")

        url = self.create_url()
        html = self.network.get_html(target_name=url)
        
        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        if '<div class="ads-list__item">' in html:
            data_array = html[html.find('<div class="ads-list__item">')+28:html.find('<!-- Pagination End-->')]            
            data_array = data_array.split('<div class="ads-list__item">')

            i = 0

            for data in data_array:
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                series = data[data.find('font">')+6:data.find('</div></div></div>')]

                try: series = series.encode('cp1251').decode('utf-8')
                except: pass

                anime_id = data[data.find('primary"><a href="')+47:data.find('" title=')]

                if '></div></div>' in anime_id: continue

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id)

                    if type(inf) == int:
                        self.create_line(title='[B][[COLOR=red]ERROR: {}[/COLOR] - [COLOR=lime]ID: {} ][/COLOR][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(anime_id, series)
                self.create_line(title=label,anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})
        
        self.progress.close()

        if '">Вперёд</a></li>' in html:
            self.create_line(title='[COLOR=F020F0F0][ Следующая страница ][/COLOR]', params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 16)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_catalog_part(self):
        if self.params['param'] == '':
            self.create_line(title='Форма выпуска: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_form')), params={'mode': 'catalog_part', 'param': 'form'})
            self.create_line(title='Жанр аниме: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_genre')), params={'mode': 'catalog_part', 'param': 'genre'})
            self.create_line(title='Озвучивал: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_voice')), params={'mode': 'catalog_part', 'param': 'voice'})
            self.create_line(title='Студия: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_studio')), params={'mode': 'catalog_part', 'param': 'studio'})
            self.create_line(title='Год выпуска: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_year')), params={'mode': 'catalog_part', 'param': 'year'})
            self.create_line(title='Статус раздачи: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_status')), params={'mode': 'catalog_part', 'param': 'status'})
            self.create_line(title='Сортировка по: [COLOR=yellow]{}[/COLOR]'.format(self.addon.getSetting('animedia_sort')), params={'mode': 'catalog_part', 'param': 'sort'})
            self.create_line(title='[COLOR=yellow][ Поиск ][/COLOR]', params={'mode': 'common_part', 'param':'catalog'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        
        if self.params['param'] == 'form':
            result = self.dialog.select('Выберите Тип:', tuple(self.animedia_form.keys()))
            self.addon.setSetting(id='animedia_form', value=tuple(self.animedia_form.keys())[result])
        
        if self.params['param'] == 'genre':
            result = self.dialog.select('Выберите Жанр:', tuple(self.animedia_genre.keys()))
            self.addon.setSetting(id='animedia_genre', value=tuple(self.animedia_genre.keys())[result])

        if self.params['param'] == 'voice':
            result = self.dialog.select('Выберите Войсера:', self.animedia_voice)
            self.addon.setSetting(id='animedia_voice', value=self.animedia_voice[result])

        if self.params['param'] == 'studio':
            result = self.dialog.select('Выберите Студию:', self.animedia_studio)
            self.addon.setSetting(id='animedia_studio', value=self.animedia_studio[result])

        if self.params['param'] == 'year':
            result = self.dialog.select('Выберите Год:', tuple(self.animedia_year.keys()))
            self.addon.setSetting(id='animedia_year', value=tuple(self.animedia_year.keys())[result])
        
        if self.params['param'] == 'status':
            result = self.dialog.select('Выберите статус:', tuple(self.animedia_status.keys()))
            self.addon.setSetting(id='animedia_status', value=tuple(self.animedia_status.keys())[result])
        
        if self.params['param'] == 'sort':
            result = self.dialog.select('Сортировать по:', tuple(self.animedia_sort.keys()))
            self.addon.setSetting(id='animedia_sort', value=tuple(self.animedia_sort.keys())[result])

    def exec_select_part(self):
        html = self.network.get_html(target_name='{}anime/{}'.format(self.site_url, self.params['id']))

        ex_info = dict.fromkeys(['series', 'quality', 'size', 'container', 'video', 'audio', 'translate', 'timing'], '')

        tab = []

        if html.find('<div class="media__tabs" id="down_load">') > -1:
            tabs_nav = html[html.find('data-toggle="tab">')+18:html.find('<!-- tabs navigation end-->')]
            tabs_nav = tabs_nav.split('data-toggle="tab">')

            for tabs in tabs_nav:
                nav = tabs[:tabs.find('</a></li>')]
                tab.append(nav)

            tabs_content = html[html.find('<div class="tracker_info">')+26:html.find('<!-- tabs content end-->')]
            tabs_content = tabs_content.split('<div class="tracker_info">')
            
            for x, content in enumerate(tabs_content):
                title = tab[x].strip()

                seed = content[content.find('green_text_top">')+16:content.find('</div></div></div>')]
                peer = content[content.find('red_text_top">')+14:content.find('</div></div></div></div>')]

                torrent_url = content[content.find('<a href="')+9:content.find('" class')]
                #magnet_url = content[content.rfind('<a href="')+9:content.rfind('" class')]

                content = content.splitlines()

                for line in content:
                    if '<h3 class=' in line:
                        if title in line:
                            ex_info['series'] = ''
                        else:
                            series = line[line.find('">')+2:line.find('</h3>')].replace('из XXX','')
                            series = series.replace('Серии','').replace('Серия','').strip()
                            ex_info['series'] = ' - [ {} ]'.format(series)

                        ex_info['quality'] = line[line.find('</h3>')+5:]
                        ex_info['quality'] = ex_info['quality'].replace('Качество','').strip()
                    if '>Размер:' in line:
                        ex_info['size'] = tag_list(line[line.find('<span>'):])
                    if 'Контейнер:' in line:
                        ex_info['container'] = line[line.find('<span>')+6:line.find('</span>')]
                    if 'Видео:' in line:
                        ex_info['video'] = line[line.find('<span>')+6:line.find('</span>')]
                    if 'Аудио:' in line:                        
                        ex_info['audio'] = line[line.find('<span>')+6:line.find('</span>')].strip()
                    if 'Перевод:' in line:                        
                        ex_info['translate'] = line[line.find('<span>')+6:line.find('</span>')]
                    if 'Тайминг и сведение звука:' in line:
                        ex_info['timing'] = line[line.find('<span>')+6:line.find('</span>')]
                    
                label = '{}{} , [COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сиды: [COLOR=lime]{}[/COLOR] , Пиры: [COLOR=red]{}[/COLOR]'.format(
                    title, ex_info['series'], ex_info['size'], ex_info['quality'], seed, peer)                    
                
                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'], ex_info=ex_info)
        else:
            tabs_content = html[html.find('<li class="tracker_info_pop_left">')+34:html.find('<!-- Media series tabs End-->')]
            tabs_content = tabs_content.split('<li class="tracker_info_pop_left">')

            for content in tabs_content:
                content = clean_list(content)
                title = content[content.find('left_top">')+10:content.find('</span>')]
                title = title.replace('Серии ','').replace('Серия ','').strip()
                
                quality = content[content.find(')')+1:content.find('</span><p>')]
                quality = quality.replace('р', 'p').strip()

                torr_inf = content[content.find('left_op">')+9:content.rfind(';</span></span></p>')]
                torr_inf = tag_list(torr_inf)
                torr_inf = torr_inf.replace('Размер: ','').replace('Сидов: ','').replace('Пиров: ','')
                torr_inf = torr_inf.split(';')

                # magnet_url = content[content.find('href="')+6:content.find('" class=')]
                torrent_url = content[content.rfind('href="')+6:content.rfind('" class=')]

                label = 'Серии: {} , [COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(
                    title, torr_inf[0], quality, torr_inf[2], torr_inf[3])

                self.create_line(title=label, params={'mode': 'torrent_part', 'id': self.params['id'], 'torrent_url': torrent_url},  anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):
        url = self.params['torrent_url']

        file_name = '{}_{}'.format(self.params['portal'], self.params['id'])
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
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))