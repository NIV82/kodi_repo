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
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

import json

version = xbmc.getInfoLabel('System.BuildVersion')[:2]
try:
    version = int(version)
except:
    version = 0

addon = xbmcaddon.Addon(id='plugin.niv.animeportal')

if sys.version_info.major > 2:
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
    fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))
else:
    from utility import fs_enc
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    icon = fs_enc(xbmc.translatePath(addon.getAddonInfo('icon')))
    fanart = fs_enc(xbmc.translatePath(addon.getAddonInfo('fanart')))

from utility import clean_tags

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class Animedia:
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()
    
        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'portal': 'animedia'}

        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            portal='animedia')
        del WebTools
#========================#========================#========================#
    def create_info(self, data):
        info = {
            'sorttitle': '',
            'cover': '',
            'genre': [],
            'plot': '',
            'torrent_data': []
        }

        if '<img src="' in data:
            cover = data[data.find('<img src="')+10:]
            cover = cover[:cover.find('"')]
            info['cover'] = 'https://animedata.sbin.ru{}'.format(cover)

        title = data[data.find('<a href="'):]
        title = title[title.find('">')+2:title.find('</a>')]
        info['sorttitle'] = u'{}'.format(title)

        if u'Жанры:' in data:
            genres = data[data.find(u'Жанры:')+6:]
            genres = genres[:genres.find('</div>')]
            genres = genres.replace('</b>','').strip()
            info['genre'] = genres.split(', ')

        if '<p>' in data:
            plot = data[data.find('<p>')+3:]
            plot = plot[:plot.rfind('</p>')]
            plot = clean_tags(plot)
            info['plot'] = u'{}'.format(plot)

        torrent_data = []
        if '<a href="torrent' in data:
            torrents = data[data.find('<li>'):]
            torrents = torrents[:torrents.rfind('</li>')]
            torrents = torrents.split('</li>')

            for t in torrents:

                torrent_title = t[t.find('<li>')+4:]
                torrent_title = torrent_title[:torrent_title.find('<a href=')]
                torrent_title = torrent_title.strip()

                torrent_url = t[t.find('<a href="')+9:]
                torrent_url = torrent_url[:torrent_url.find('">')]
                    
                magnets = ''
                if '<a href="magnet' in t:
                    magnets = data[data.find('<a href="magnet')+9:]
                    magnets = magnets[:magnets.find('">')]

                torrent_data.append(
                    {'title': torrent_title, 'torrent_url': torrent_url, 'magnet_url': magnets}
                )

        info.update({'torrent_data':torrent_data})

        return info
#========================#========================#========================#
    def create_pagination(self, data):
        current = data[data.find('<span class="current">')+22:]
        current = current[:current.find('</span>')]
        current = current.replace('.','').replace('Page','')
        current = current.strip()
        current, last = current.split('of')
        pages = [int(current), int(last)]
        return pages
#========================#========================#========================#
    def create_context(self):
        context_menu = []
        
        if 'search_part' in self.params['mode'] and self.params['param'] == '':
            context_menu.append(('Очистить историю поиска', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=animedia")'))

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
            else:
                li.setInfo(type='video', infoLabels=info)

        li.addContextMenuItems(self.create_context())

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']

        if 'tam' in params:
            if version <= 18:
                try:
                    label = info['sorttitle'].encode('utf-8')
                except:
                    label = info['sorttitle']
            else:
                label = info['sorttitle']

            info_data = repr({'title':label})
            url='plugin://plugin.video.tam/?mode=open&info={}&url={}'.format(quote_plus(info_data), quote(params['tam']))
        else:
            url = '{}?{}'.format(sys.argv[0], urlencode(params))

        #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()        
        try: self.database.end()
        except: pass
#========================#========================#========================#
    def exec_addon_setting(self):
        addon.openSettings()
#========================#========================#========================#
    def exec_update_anime_part(self):
        self.create_info(anime_id=self.params['id'], update=True)
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('am_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=1000,sound=False)
            pass
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B]Поиск[/B]', params={'mode': 'search_part'})
        self.create_line(title='[B]Архив Торрентов[/B]', params={'mode': 'common_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if self.params['param'] == '':
            self.create_line(title='[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = addon.getSetting('am_search').split('|')
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
                data_array = addon.getSetting('am_search').split('|')                    
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array.append(self.params['search_string'])
                addon.setSetting('am_search', '|'.join(data_array))
                self.params['param'] = 'search_string'
            else:
                return False
        
        if 'search_string' in self.params['param']:
            if self.params['search_string'] == '':
                return False

            url = 'https://animedata.sbin.ru/animedia/trackersearch?page={}&q={}'.format(
                self.params['page'], quote(self.params['search_string'])
            )

            html = self.network.get_html(url=url)

            data_array = html[html.find('<div class="release-info">')+26:]
            data_array = data_array[:data_array.rfind('<hr/>')]
            data_array = data_array.split('<div class="release-info">')

            for data in data_array:
                info = self.create_info(data)

                torrent_data = info.pop('torrent_data')

                if torrent_data:
                    label = u'{}'.format(info['sorttitle'])

                    info_data = json.dumps(info)
                    torrent_data = json.dumps(torrent_data)

                    self.create_line(title=label, params={'mode': 'select_part', 'param': info_data,'torrent_data':torrent_data}, **info)
                else:
                    label = '[COLOR=gray]{}[/COLOR]'.format(info['sorttitle'])
                    self.create_line(title=label, folder=False)

            if '<div class="pagination">' in html:
                pagination = html[html.find('<div class="pagination">')+24:]
                pages = self.create_pagination(data=pagination)
                    
                if pages[0] < pages[1]:
                    label = '[COLOR=gold]{}[/COLOR] из {} | Следующая страница - [COLOR=gold]{}[/COLOR]'.format(int(self.params['page']), pages[1], int(self.params['page'])+1)
                    self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'search_string': self.params['search_string'], 'page': int(self.params['page']) + 1})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self, url=None):
        url = 'https://animedata.sbin.ru/animedia/?page={}'.format(
            self.params['page']
        )

        html = self.network.get_html(url=url)

        data_array = html[html.find('<div class="release-info">')+26:]
        data_array = data_array[:data_array.rfind('<hr/>')]
        data_array = data_array.split('<div class="release-info">')

        for data in data_array:
            info = self.create_info(data)

            torrent_data = info.pop('torrent_data')

            if torrent_data:
                label = u'{}'.format(info['sorttitle'])

                info_data = json.dumps(info)
                torrent_data = json.dumps(torrent_data)

                self.create_line(title=label, params={'mode': 'select_part', 'param': info_data,'torrent_data':torrent_data}, **info)
            else:
                label = u'[COLOR=gray]{}[/COLOR]'.format(info['sorttitle'])
                self.create_line(title=label, folder=False)

        if '<div class="pagination">' in html:
            pagination = html[html.find('<div class="pagination">')+24:]
            pages = self.create_pagination(data=pagination)
                
            if pages[0] < pages[1]:
                label = u'[COLOR=gold]{}[/COLOR] из {} | Следующая страница - [COLOR=gold]{}[/COLOR]'.format(int(self.params['page']), pages[1], int(self.params['page'])+1)            
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        info = json.loads(self.params['param'])

        torrent_data = json.loads(self.params['torrent_data'])

        for torrent in torrent_data:
            torrent_label = torrent['title']

            torrent_url = torrent['torrent_url']
            torrent_url = 'https://animedata.sbin.ru/animedia/{}'.format(torrent_url)
            torrent_url = torrent_url.replace(' ','%20')

            magnet_url = torrent['magnet_url']
            magnet_url = magnet_url.replace(' ','%20')

            label = torrent_label
            self.create_line(title=label, params={'mode': 'select_part', 'tam': torrent_url}, **info)

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
def start():
    animedia = Animedia()
    animedia.execute()