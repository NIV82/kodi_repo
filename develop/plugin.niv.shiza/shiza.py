# -*- coding: utf-8 -*-

import gc
import os
import sys
import urllib
import time

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import utility
import info

class Main:
    addon = xbmcaddon.Addon(id='plugin.niv.shiza')
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')    

    def __init__(self):
        self.progress = xbmcgui.DialogProgress()
        self.dialog = xbmcgui.Dialog()

        self.addon_data_dir = utility.fs_enc(xbmc.translatePath(Main.addon.getAddonInfo('profile')))
        if not os.path.exists(self.addon_data_dir):
            os.makedirs(self.addon_data_dir)

        self.images_dir = os.path.join(self.addon_data_dir, 'images')
        if not os.path.exists(self.images_dir):
            os.mkdir(self.images_dir)

        self.torrents_dir = os.path.join(self.addon_data_dir, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': 1}

        args = utility.get_params()
        for a in args:
            self.params[a] = urllib.unquote_plus(args[a])

        if Main.addon.getSetting('unblock') == '1':
            try:
                proxy_time = float(Main.addon.getSetting('proxy_time'))
            except:
                proxy_time = 0
            
            if time.time() - proxy_time > 36000:
                Main.addon.setSetting('proxy_time', str(time.time()))
                proxy_pac = urllib.urlopen("http://antizapret.prostovpn.org/proxy.pac").read()
                proxy = proxy_pac[proxy_pac.find('PROXY ')+6:proxy_pac.find('; DIRECT')].strip()
                Main.addon.setSetting('proxy', proxy)
                proxy_data = {'https': proxy}
            else:
                proxy_data = {'https': Main.addon.getSetting('proxy')}                
        else:
            proxy_data = None

        from network import WebTools
        self.network = WebTools(use_auth=True, auth_state=bool(Main.addon.getSetting("auth").lower() == 'true'), proxy_data=proxy_data)
        del WebTools

        self.network.auth_post_data = {
            'field-email': Main.addon.getSetting('login'),
            'field-password': Main.addon.getSetting('password')}
        self.network.sid_file = utility.fs_enc(os.path.join(self.addon_data_dir, 'shiza.sid' ))
        self.network.download_dir = self.addon_data_dir
        
        if self.params['mode'] == 'main_part' and self.params['param'] == '':
            try: os.remove(self.network.sid_file)
            except: pass

        if not Main.addon.getSetting("login") or not Main.addon.getSetting("password"):
            self.params['mode'] = 'addon_setting'
            xbmc.executebuiltin('XBMC.Notification(Авторизация, Укажите логин и пароль)')            
            return

        if not self.network.auth_state:
            if not self.network.authorization():
                self.params['mode'] = 'addon_setting'
                xbmc.executebuiltin('XBMC.Notification(Ошибка, Проверьте логин и пароль)')
                return
            else:
                Main.addon.setSetting("auth", str(self.network.auth_state).lower())

        if not os.path.isfile(os.path.join(self.addon_data_dir, 'shiza.db')):
            try:
                data = urllib.urlopen('https://github.com/NIV82/kodi_repo/raw/main/release/plugin.niv.shiza/shiza.db')
                chunk_size = 8192
                bytes_read = 0
                file_size = int(data.info().getheaders("Content-Length")[0])
                self.progress.create('Загрузка Базы Данных')
                with open(os.path.join(self.addon_data_dir, 'shiza.db'), 'wb') as f:
                    while True:
                        chunk = data.read(chunk_size)
                        bytes_read = bytes_read + len(chunk)
                        f.write(chunk)
                        if len(chunk) < chunk_size:
                            break
                        p = bytes_read * 100 / file_size
                        if p > 100:
                            p = 100
                        self.progress.update(p, 'Загружено: {} из {} Mb'.format('{:.2f}'.format(bytes_read/1024/1024.0), '{:.2f}'.format(file_size/1024/1024.0)))
                    self.progress.close()
                xbmc.executebuiltin('XBMC.Notification(База Данных, [B]БД успешно загружена[/B])')
            except:
                xbmc.executebuiltin('XBMC.Notification(База Данных, Ошибка загрузки - [COLOR=yellow]ERROR: 100[/COLOR])')
                pass

        from database import DBTools
        self.database = DBTools(utility.fs_dec(os.path.join(self.addon_data_dir, 'shiza.db')))
        del DBTools

    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try:
            self.database.end()
        except:
            pass

    def create_info(self, anime_id):
        html = self.network.get_html('http://shiza-project.com/releases/view/{}'.format(anime_id))

        if type(html) == int:
            return html

        info = dict.fromkeys(['title_ru', 'title_en', 'country', 'form', 'series', 'plot', 'studio', 'year', 'genre', 'authors', 'cover'], '')

        html = utility.clean_list(html)

        title = html[html.find('"alt="')+6:html.find('"title=')]
        
        info['title_ru'] = utility.rep_list(html[html.rfind('<h3>')+4:html.rfind('</h3>')])        
        info['title_en'] = utility.rep_list(title[:title.find(',')])        

        country = ('Китай','США','Франция','Южная Корея','Япония')
        for value in country:
            if value in title:
                info['country'] = value

        info['plot'] = html[html.find('<div class="desc">')+18:html.find('<article class="card-content">')]
        info['plot'] = utility.rep_list(info['plot'])
        info['plot'] = utility.tag_list(info['plot']).strip()

        info_ex = html[html.find('<div class="media-post media-role">')+35:html.find('<div class="card-header color-warning">Источник</div>')]     
        info_ex = info_ex.split('<div class="media-post media-role">')

        info['dubbing'] = []
        info['sound'] = []
        info['translation'] = []

        for inf in info_ex:            
            if 'озвучивание' in inf or 'Озвучивание' in inf:
                dubb = inf[inf.find('?t=')+3:inf.find('"><img src')]
                info['dubbing'].append(dubb)
            if 'тайминг' in inf:
                sounds = inf[inf.find('?t=')+3:inf.find('"><img src')]
                info['sound'].append(sounds)
            if 'перевод' in inf:
                translate = inf[inf.find('?t=')+3:inf.find('"><img src')]
                info['translation'].append(translate)
    
        info['dubbing'] = urllib.unquote_plus(', '.join(info['dubbing']))
        info['sound'] = urllib.unquote_plus(', '.join(info['sound']))
        info['translation'] = urllib.unquote_plus(', '.join(info['translation']))

        data_array = html[html.find('<ul class="params">')+19:html.find('<div class="desc">')]
        data_array = data_array.split('</li>')

        for data in data_array:
            if 'Жанры:' in data:
                info['genre'] = utility.tag_list(data).replace('Жанры:', '').strip()
            if 'Выпуск' in data:
                for i in range(1970, 2026, 1):
                    if str(i) in data:
                        info['year'] = i
            if 'Cоздатели' in data:
                info['authors'] = utility.tag_list(data).replace('Cоздатели:', '').strip()
            if 'Студия' in data:
                info['studio'] = utility.tag_list(data).replace('Студия:', '').strip()
            if 'Метки' in data:
                if info['genre'] == '':
                    info['genre'] = utility.tag_list(data).replace('Метки:', '').strip()

        if info['year'] == '':
            for i in range(1970, 2026, 1):
                if str(i) in title:
                    info['year'] = i
        try:
            self.database.add_anime(anime_id, info['title_ru'], info['title_en'], info['genre'], info['authors'], info['plot'],
                          info['dubbing'], info['translation'], info['sound'], info['country'], info['studio'], info['year'])
        except:
            xbmc.executebuiltin("XBMC.Notification(Ошибка парсера, ERROR: 101)")
            return 101
        return

    def create_exinfo(self, torr_id, ex_info):
        ex_info = utility.clean_list(ex_info)
        ex_info = ex_info.split('href="javascript:void(0)" ')

        for ex in ex_info:
            if torr_id in ex:
                size = ex[ex.find('>')+1:ex.find('<')]
                
                seed_peer = ex[ex.find('<div class="torrent-counter">')+29:ex.find('качающих')]
                seed_peer = seed_peer.replace('раздающих', ',')
                seed_peer = utility.tag_list(seed_peer).split(',')

                seed = seed_peer[0].strip()
                peer = seed_peer[1].strip()

                if '<b>Раздел:</b>' in ex:
                    ts = 'Series: {}'.format(ex[ex.find('<b>Раздел:</b>')+20:ex.find('<br>')].strip())
                    ex_info = '{}|{}|{}|{}'.format(size, seed, peer, ts)
                else:
                    ex_info = '{}|{}|{}'.format(size, seed, peer)
        return ex_info

    def create_title(self, title, series):
        if series:
            series = ' - [ {} ]'.format(series)
        else:
            series = ''
        
        if Main.addon.getSetting('title_mode') == '0':
            label = '{}{}'.format(title[0], series)
        if Main.addon.getSetting('title_mode') == '1':
            label = '{}{}'.format(title[1], series)
        if Main.addon.getSetting('title_mode') == '2':
            label = '{} / {}{}'.format(title[0], title[1], series)
        return label

    def create_image(self, anime_id):
        url = 'http://shiza-project.com/upload/covers/{}/latest.jpg'.format(anime_id)

        if Main.addon.getSetting('cover_mode') == 'false':
            return url
        else:
            local_img = '{}{}'.format(anime_id, url[url.rfind('.'):])
            if local_img in os.listdir(self.images_dir):
                return utility.fs_dec(os.path.join(self.images_dir, local_img))
            else:
                self.network.download_dir = self.images_dir
                return self.network.get_file(target=url, dest_name=local_img)

    def create_line(self, title=None, params=None, anime_id=None, size=None, folder=True): 
        li = xbmcgui.ListItem(title)

        if anime_id:
            cover = self.create_image(anime_id)
            art = {'icon': cover, 'thumb': cover, 'poster': cover}
            li.setArt(art)
            
            anime_info = self.database.get_anime(anime_id)
            
            info = {'title': title, 'year': anime_info[8], 'genre': anime_info[0], 'plot': anime_info[2],
                    'director': anime_info[1], 'country': anime_info[6], 'studio': anime_info[7]}
            
            info['plot'] = '{}\n\nОзвучивание: {}\nПеревод: {}\nРабота со звуком: {}'.format(
                info['plot'], anime_info[3], anime_info[4], anime_info[5])

            if size:
                info['size'] = size

            li.setInfo(type='video', infoLabels=info)

        if self.params['mode'] == 'search_part' and self.params['param'] == '':
            li.addContextMenuItems([('[B]Очистить историю[/B]', 'Container.Update("plugin://plugin.niv.shiza/?mode=clean_part")')])

        if folder==False:
                li.setProperty('isPlayable', 'true')

        url = '{}?{}'.format(sys.argv[0], urllib.urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

    def exec_addon_setting(self):
        Main.addon.openSettings()

    def exec_clean_part(self):
        try:
            Main.addon.setSetting('search', '')
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, Успешно выполнено)")
        except:
            xbmc.executebuiltin("XBMC.Notification(Удаление истории, [COLOR=yellow]ERROR: 102[/COLOR])")
            pass
        xbmc.executebuiltin('Container.Refresh')

    def exec_main_part(self):
        self.create_line(title='[B][COLOR=red][ Поиск ][/COLOR][/B]', params={'mode': 'search_part'})
        self.create_line(title='[B][COLOR=yellow][ Новинки ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/novelty'})
        self.create_line(title='[B][COLOR=lime][ Все ][/COLOR][/B]', params={'mode': 'common_part', 'param': ''})
        self.create_line(title='[B][COLOR=lime][ Онгоинги ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/ongoing'})
        self.create_line(title='[B][COLOR=lime][ Завершенные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/completed'})
        self.create_line(title='[B][COLOR=lime][ Приостановленные ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/suspended'})
        self.create_line(title='[B][COLOR=lime][ Рекомендуемые ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'releases/top'})
        self.create_line(title='[B][COLOR=blue][ Дорамы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/completed/category/dorama'})
        self.create_line(title='[B][COLOR=blue][ Кино и ТВ ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/completed/category/film-and-tv'})
        self.create_line(title='[B][COLOR=blue][ Мультфильмы ][/COLOR][/B]', params={'mode': 'common_part', 'param': 'status/completed/category/cartoon'})
        self.create_line(title='[B][COLOR=white][ Информация ][/COLOR][/B]', params={'mode': 'information_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_common_part(self, url=None, post=None):
        self.progress.create("SHIZA Project", "Инициализация")

        url = 'http://shiza-project.com/{}?page={}'.format(self.params['param'], self.params['page'])

        if 'releases/search' in self.params['param']:
            url = 'http://shiza-project.com/{}{}&page={}'.format(self.params['param'], self.params['search_string'], self.params['page'])

        html = self.network.get_html(target=url)
        
        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return
        
        if html.find('class="card-box"') > -1:
            data_array = html[html.find('class="card-box"'):html.rfind('</figure>')]
            data_array = data_array.split('</figure>')

            i = 0

            for data in data_array:
                i = i + 1
                p = int((float(i) / len(data_array)) * 100)

                data = utility.clean_list(data)

                anime_id = data[data.find('/view/')+6:data.find('title=')]
                anime_id = anime_id.replace('"', '').strip()

                series = data[data.find('<p>')+3:data.find('</p>')].split(',')
                series = series[len(series)-1].replace(' эп.', '').replace('эп, +', '+')

                if self.progress.iscanceled():
                    break
                self.progress.update(p, 'Обработано: {}% - [ {} из {} ]'.format(p, i, len(data_array)))

                if not self.database.is_anime_in_db(anime_id):
                    inf = self.create_info(anime_id)
                
                    if type(inf) == int:
                        self.create_line(title='[B][COLOR=red][ ERROR: {} - ID: {} ][/COLOR][/B]'.format(inf, anime_id), params={})
                        continue

                label = self.create_title(self.database.get_title(anime_id), series)
                self.create_line(title=label, anime_id=anime_id, params={'mode': 'select_part', 'id': anime_id})

            if len(data_array) >= 20:
                if not 'releases/top' in self.params['param'] and not 'status/novelty' in self.params['param']:
                    if not 'search_string' in self.params:
                        self.create_line(title='[B][COLOR=blue][ Следующая страница ][/COLOR][/B]', params={
                            'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})
                    else:
                        self.create_line(title='[B][COLOR=blue][ Следующая страница ][/COLOR][/B]', params={
                            'mode': self.params['mode'], 'param': self.params['param'], 'search_string': self.params['search_string'], 'page': (int(self.params['page']) + 1)})
        else:
            self.create_line(title='[COLOR=yellow][ Ничего не найдено ][/COLOR]', params={'mode': 'main_part'})

        self.progress.close()
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
    
    def exec_information_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=white][ Настройки плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'sett'})
            self.create_line(title='[B][COLOR=white][ Настройки воспроизведения ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'play'})
            self.create_line(title='[B][COLOR=white][ Совместимость с движками ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'comp'})
            self.create_line(title='[B][COLOR=white][ Новости обновлений ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'news'})
            self.create_line(title='[B][COLOR=white][ Описание ошибок плагина ][/COLOR][/B]', params={'mode': 'information_part', 'param': 'bugs'})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            txt = info.data
            start = '[{}]'.format(self.params['param'])
            end = '[/{}]'.format(self.params['param'])
            data = txt[txt.find(start)+6:txt.find(end)].strip()

            self.dialog.textviewer('Плагин для просмотра аниме с ресурса [COLOR orange]shiza-project.com[/COLOR]', data)
        return

    def exec_search_part(self):
        if not Main.addon.getSetting('search'):
            Main.addon.setSetting('search', '')

        if self.params['param'] == '':
            self.create_line(title='[B][COLOR=red][ Поиск по названию ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'releases/search?q='})
            self.create_line(title='[B][COLOR=red][ Поиск по меткам ][/COLOR][/B]', params={'mode': 'search_part', 'param': 'releases/search?t='})

            data_array = Main.addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                self.create_line(title='{}'.format(data), params={'mode': 'common_part', 'param':'releases/search?q=', 'search_string': data})

        if 'releases/search?q' in self.params['param']:
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск:')
            skbd.doModal()
            if skbd.isConfirmed():
                self.params['search_string'] = urllib.quote(skbd.getText())
                data_array = Main.addon.getSetting('search').split('|')                    
                while len(data_array) >= 10:
                    data_array.pop(0)
                data_array = '{}|{}'.format('|'.join(data_array), urllib.unquote(self.params['search_string']))
                Main.addon.setSetting('search', data_array)
                self.exec_common_part()
            else:
                return False
        
        if 'releases/search?t=' in self.params['param']:
            for tag in info.tags:
                label = '{}'.format(tag)
                self.create_line(title=label, params={'mode': 'common_part', 'param': 'releases/search?t=', 'search_string': urllib.quote(tag)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_select_part(self):
        html = self.network.get_html('http://shiza-project.com/releases/view/{}'.format(self.params['id']))

        if type(html) == int:
            self.create_line(title='[B][COLOR=red]ERROR: {}[/COLOR][/B]'.format(html), params={})
            return

        ex_info = html[html.find('href="javascript:void(0)" ')+26:html.rfind('Размер')]

        info = html[html.find('<article class="card card-torrent">')+35:html.rfind('Размер')]
        info = utility.clean_list(info)

        data_array = info[info.find('<nav>')+5:info.find('</nav>')]
        data_array = data_array.split('<a class="btn btn-primary')
        data_array.pop(0)

        data_torr=[]

        for v in data_array:
            quality = v[v.find('>')+1:v.find('<')]

            data = v.split('torrent_')
            data.pop(0)

            for d in data:
                torr_id = d[:d.find('"')]                        
                torr_info = self.create_exinfo(torr_id, ex_info)
                data_torr.append('{}|{}|{}'.format(torr_id, quality, torr_info))

        dte = {}
        torrent_title = {}
        torrent_quality = {}
        
        for i, dt in enumerate(data_torr):
            dt = dt.split('|')
            torrent_quality[i] = '{}'.format(dt[1])            

            if 'Series' in dt[len(dt)-1]:
                torrent_title[i] = 'Серии: {} , '.format(dt[len(dt)-1].replace('Series: ', ''))
            else:
                torrent_title[i] = ''               
            dte[i] = '|'.join(dt)


        for i in sorted(torrent_title, key=torrent_title.get):
            torr_title = torrent_title[i]
            torr_quality = torrent_quality[i]
            dt = dte[i].replace('МБ', 'MB').replace('ГБ', 'GB')
            dt = dt.split('|')
            
            label = '{}[COLOR=yellow]{}[/COLOR] , [COLOR=blue]{}[/COLOR] , Сидов: [COLOR=lime]{}[/COLOR] , Пиров: [COLOR=red]{}[/COLOR]'.format(torr_title, dt[2], torr_quality, dt[3], dt[4])

            self.create_line(title=label, params={'mode': 'torrent_part', 'torrent_id': dt[0], 'id': self.params['id']},  anime_id=self.params['id'])

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def exec_torrent_part(self):        
        self.network.download_dir = self.torrents_dir

        url = 'http://shiza-project.com/download/torrents/{}/{}'.format(self.params['id'], self.params['torrent_id'])
        file_name = self.network.get_file(target=url, dest_name='{}.torrent'.format(self.params['torrent_id']))

        import bencode
        torrent_data = open(utility.fs_dec(file_name), 'rb').read()
        torrent = bencode.bdecode(torrent_data)

        info = torrent['info']
        series = {}
        size = {}
        
        if 'files' in info:
            for i, x in enumerate(info['files']):
                size[i] = x['length']
                series[i] = x['path'][-1]
            for i in sorted(series, key=series.get):
                self.create_line(title=series[i], params={'mode': 'play_part', 'index': i, 'id': self.params['torrent_id']}, anime_id=self.params['id'], folder=False, size=size[i])
        else:
            self.create_line(title=info['name'], params={'mode': 'play_part', 'index': 0, 'id': self.params['torrent_id']}, anime_id=self.params['id'], folder=False, size=info['length'])
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def exec_play_part(self):
        url = os.path.join(self.torrents_dir, '{}.torrent'.format(self.params['id']))
        index = int(self.params['index'])

        if Main.addon.getSetting("Engine") == '0':
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver')
            engine = tam_engine[int(Main.addon.getSetting("TAMengine"))]            
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(urllib.quote_plus(url), index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        if Main.addon.getSetting("Engine") == '1':
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(urllib.quote_plus(url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        xbmc.executebuiltin("Container.Refresh")

if __name__ == "__main__":    
    shiza = Main()
    shiza.execute()
    del shiza
    
gc.collect()