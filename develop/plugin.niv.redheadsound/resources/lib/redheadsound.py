# -*- coding: utf-8 -*-

import os
import sys
#import time
#import json
#import re

from urllib.parse import parse_qs
from urllib.parse import urlencode
# from urllib.parse import quote
from urllib.parse import unquote
# from urllib.request import urlopen
# from html import unescape

from rhs.redheadsound import RHSAPI

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

addon = xbmcaddon.Addon(id='plugin.niv.redheadsound')
handle = int(sys.argv[1])
dialog = xbmcgui.Dialog()

addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
userdata_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
media_path = os.path.join(addon_path, 'resources', 'media')

icon = xbmcvfs.translatePath(addon.getAddonInfo('icon'))
fanart = xbmcvfs.translatePath(addon.getAddonInfo('fanart'))

params = {'path': 'main', 'param': '', 'page': '1', 'section': ''}
args = parse_qs(sys.argv[2][1:])
for key, value in args.items():
    params[key] = unquote(value[0])

# try:
#     xbmcaddon.Addon('inputstream.adaptive')
# except:
#     xbmcgui.Dialog().notification(
#         heading='Установка Библиотеки - [COLOR=darkorange]inputstream.adaptive[/COLOR]',
#         message='inputstream.adaptive',
#         icon=None,
#         time=1000,
#         sound=False
#         )
#     xbmc.executebuiltin('RunPlugin("plugin://inputstream.adaptive")')

class RedHeadSound:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        if not os.path.exists(userdata_path):
            os.makedirs(userdata_path)

        self.rhsapi = RHSAPI()
        self.context_menu = []

        self.site_url = 'https://redheadsound.studio/'
#========================#========================#========================#
    def create_line(self, items, content=True):
        """Модуль для формирования списка в Коди"""

        for item in items:
            listitem = xbmcgui.ListItem(item['label'])

            arts = {}
            if 'arts' in item:
                arts = item.pop('arts')
            listitem.setArt(arts)

            videoinfo = listitem.getVideoInfoTag()
            videoinfo.setMediaType('video')

            if 'info' in item:
                self._videoinfo_assemble(info=item.pop('info'), videoinfo=videoinfo)

            if 'context_menu' in item:
                listitem.addContextMenuItems(item['context_menu'])

            if not item['isFolder']:
                listitem.setProperty('isPlayable', 'true')

            url = f"{sys.argv[0]}?{urlencode(item['params'])}"
            xbmcplugin.addDirectoryItem(
                handle, url=url, listitem=listitem, isFolder=item['isFolder']
                )

        if content:
            xbmcplugin.setContent(handle, 'tvshows')

        xbmcplugin.endOfDirectory(handle, succeeded=True)
#========================#========================#========================#
    def execute(self):
        # getattr(self, 'exec_{}'.format(params['mode']))()
        getattr(self, f"exec_{params['path']}")()
        # try:
        #     self.database.end()
        # except:
        #     pass
# #========================#========================#========================#
#     def exec_clean_part(self):
#         try:
#             addon.setSetting('search', '')
#             self.dialog.notification(heading='RedHeadSound', message='Выполнено',icon=icon,time=1000,sound=False)
#         except:
#             self.dialog.notification(heading='RedHeadSound', message='Ошибка',icon=icon,time=1000,sound=False)
#             pass
#========================#========================#========================#
    def exec_main(self):
        items = []
        main_menu = [
            {
                'label': 'Поиск', 
                'params': {'path': 'search'},
                'arts': {'icon': os.path.join(media_path, 'search.png')}
                },
            {
                'label': 'Каталог',
                'params': {'path': 'catalog'},
                'arts': {'icon': os.path.join(media_path, 'catalog.png')}
                },
            {
                'label': 'Рекомендации',
                'params': {'path': 'content', 'section': 'recommendation'},
                'arts': {'icon': os.path.join(media_path, 'recommendation.png')}
                },
            {
                'label': 'Фильмы',
                'params': {'path': 'content', 'section': 'filmy'},
                'arts': {'icon': os.path.join(media_path, 'filmy.png')}
                },
            {
                'label': 'Сериалы',
                'params': {'path': 'content', 'section': 'serialy'},
                'arts': {'icon': os.path.join(media_path, 'serialy.png')}
                }
        ]

        for node in main_menu:
            main_data = self.rhsapi.menu_assemble(data=node)
            items.append(main_data)

        self.create_line(items=items, content=False)
#========================#========================#========================#
    def exec_search(self):
        if not params['param']:
            items = []
            search_row = self.rhsapi.menu_assemble({
                'label': '[B]Введите название[/B]',
                'params': {
                    'path': 'search',
                    'param': 'search_word'
                    },
                'arts': {'icon': os.path.join(media_path, 'search.png')}
                })
            items.append(search_row)

            data_array = addon.getSetting('search').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue

                search_node = self.rhsapi.menu_assemble({
                    'label': f"[COLOR=gray]{data}[/COLOR]",
                    'params': {
                        'path': 'search',
                        'param': 'search_string',
                        'search_string': data
                        },
                    'arts': {'icon': os.path.join(media_path, 'node.png')}
                })

                items.append(search_node)
            self.create_line(items=items, content=False)

        if params['param'] == 'search_word':
            search_word = dialog.input(heading = 'Поиск:', type=xbmcgui.INPUT_ALPHANUM)
            if search_word:
                search_word = search_word.lower()
                data_array = addon.getSetting('search').split('|')
                while len(data_array) >= 7:
                    data_array.pop(0)
                data_array.append(search_word)
                addon.setSetting('search', '|'.join(data_array))
                params['param'] = 'search_string'
                params['search_string'] = search_word
            
        if params['param'] == 'search_string':
            search_data = self.rhsapi.search(query=params['search_string'])
            self.create_line(items=search_data['data'])
#========================#========================#========================#
    def exec_catalog(self):
        items = []
        catalog_menu = [
            {
                'label': 'Аниме сериал', 
                'params': {'path': 'content', 'section': 'animeserial'}
                },
            {
                'label': 'Триллер', 
                'params': {'path': 'content', 'section': 'triller'}
                },
            {
                'label': 'Семейные', 
                'params': {'path': 'content', 'section': 'semejnye'}
                },
            {
                'label': 'Ужасы', 
                'params': {'path': 'content', 'section': 'uzhasy'}
                },
            {
                'label': 'Боевик', 
                'params': {'path': 'content', 'section': 'boevik'}
                },
            {
                'label': 'Короткометражка', 
                'params': {'path': 'content', 'section': 'korotkometrazhka'}
                },
            {
                'label': 'Драма', 
                'params': {'path': 'content', 'section': 'drama'}
                },
            {
                'label': 'Преступление', 
                'params': {'path': 'content', 'section': 'prestuplenie'}
                },
            {
                'label': 'Музыка', 
                'params': {'path': 'content', 'section': 'music'}
                },
            {
                'label': 'Мюзикл', 
                'params': {'path': 'content', 'section': 'musical'}
                },
            {
                'label': 'Биография', 
                'params': {'path': 'content', 'section': 'biography'}
                },
            {
                'label': 'Военные', 
                'params': {'path': 'content', 'section': 'military'}
                },
            {
                'label': 'Детективы', 
                'params': {'path': 'content', 'section': 'detectives'}
                },
            {
                'label': 'Фэнтези', 
                'params': {'path': 'content', 'section': 'fantasy'}
                },
            {
                'label': 'Исторические', 
                'params': {'path': 'content', 'section': 'istoricheskie'}
                },
            {
                'label': 'Marvel', 
                'params': {'path': 'content', 'section': 'marvel'}
                },
            {
                'label': 'Приключения', 
                'params': {'path': 'content', 'section': 'prikljuchenija'}
                },
            {
                'label': 'Фантастика', 
                'params': {'path': 'content', 'section': 'fantastika'}
                },
            {
                'label': 'Комедии', 
                'params': {'path': 'content', 'section': 'komedii'}
                },
        ]

        for node in catalog_menu:
            catalog_data = self.rhsapi.menu_assemble(data=node)
            items.append(catalog_data)
        self.create_line(items=items, content=True)
#========================#========================#========================#
    def exec_content(self):
        content_data = self.rhsapi.parser(section=params['section'], page=params['page'])

        if 'next_page' in content_data['pagination']:
            page_node = _pagination(content_data['pagination'])
            content_data['data'].append(page_node)

        self.create_line(items=content_data['data'])
#========================#========================#========================#
    def exec_select(self):
        select_data = self.rhsapi.select(url=params['src'])
        self.create_line(items=select_data)
#========================#========================#========================#
    def exec_play(self):
        """
        Не осилил DRM ClearKey в mpd на данный момент
        
        """
        pass
        # video_url = params['src']
        # playlist_data = self.rhsapi.play(url=video_url)
        # playlist_url = playlist_data['src']

        #playlist_url = 'https://kinescope.io/new-manifest/686767d8-c0f5-4a17-aaf0-1ea7d951d276/master.mpd'
        # if not playlist_url:
        #     return

        #listitem = xbmcgui.ListItem(path=playlist_url)

        # listitem = xbmcgui.ListItem(path=playlist_url, offscreen=True)
        #listitem = xbmcgui.ListItem(path=playlist_url, offscreen=True)


        # These two lines are needed to prevent the HTTP HEAD request from Kodi core, used to determine the mimetype
        # listitem.setProperty('inputstream', "inputstream.adaptive")
        # listitem.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        # if '0' in addon.getSetting('inputstream_adaptive'):
        #     li.setProperty('inputstream', "inputstream.adaptive")
        #     #li.setProperty('inputstream.adaptive.manifest_type', 'hls')

        #     if addon.getSetting('quality') == 'AUTO':
        #         li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
        #     elif addon.getSetting('quality') == 'SELECT':
        #         li.setProperty('inputstream.adaptive.stream_selection_type', 'ask-quality')
        #     else:
        #         q = addon.getSetting('quality').lower()
        #         li.setProperty('inputstream.adaptive.chooser_resolution_max', q)
        #         li.setProperty('inputstream.adaptive.chooser_resolution_secure_max', q)

        #     li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        #xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=listitem)

    def _videoinfo_assemble(self, info, videoinfo):
        #rating = _rating(info.get('rating'))

        videoinfo.setGenres(info['genre'])
        videoinfo.setCountries(info['country'])
        videoinfo.setYear(info['year'])
        videoinfo.setEpisode(info['episode'])
        videoinfo.setSeason(info['season'])
        videoinfo.setSortEpisode(info['sortepisode'])
        videoinfo.setSortSeason(info['sortseason'])
        videoinfo.setEpisodeGuide(info['episodeguide'])
        videoinfo.setShowLinks(info['showlink'])
        videoinfo.setTop250(info['top250'])
        videoinfo.setSetId(info['setid'])
        videoinfo.setTrackNumber(info['tracknumber'])
        videoinfo.setRating(_rating(info.get('rating')))
        #videoinfo.setRatings(info['rating'])
        #videoinfo.setUserRating(info['userrating'])
        videoinfo.setPlaycount(info['playcount'])
        #videoinfo.setCast(info['cast'])
        videoinfo.setCast(_cast_assemble(info['cast']))
        videoinfo.setDirectors(info['director'])
        videoinfo.setMpaa(info['mpaa'])
        videoinfo.setPlot(info['plot'])
        videoinfo.setPlotOutline(info['plotoutline'])
        videoinfo.setTitle(info['title'])
        videoinfo.setOriginalTitle(info['originaltitle'])
        videoinfo.setSortTitle(info['sorttitle'])
        videoinfo.setDuration(info['duration'])
        videoinfo.setStudios(info['studio'])
        videoinfo.setTagLine(info['tagline'])
        videoinfo.setWriters(info['writer'])
        videoinfo.setTvShowTitle(info['tvshowtitle'])
        videoinfo.setPremiered(info['premiered'])
        videoinfo.setTvShowStatus(info['status'])
        videoinfo.setSet(info['set'])
        videoinfo.setSetOverview(info['setoverview'])
        videoinfo.setTags(info['tag'])
        videoinfo.setIMDBNumber(info['imdbnumber'])
        videoinfo.setProductionCode(info['code'])
        videoinfo.setFirstAired(info['aired'])
        videoinfo.setLastPlayed(info['lastplayed'])
        videoinfo.setAlbum(info['album'])
        videoinfo.setArtists(info['artist'])
        videoinfo.setVotes(info['votes'])
        videoinfo.setPath(info['path'])
        videoinfo.setTrailer(info['trailer'])
        videoinfo.setDateAdded(info['dateadded'])
        videoinfo.setMediaType(info['mediatype'])
        videoinfo.setDbId(info['dbid'])

def _rating(rating):
    if rating['rhs']:
        value = rating['rhs']
    elif rating['kinopoisk']:
        value = rating['kinopoisk']
    elif rating['imdb']:
        value = rating['imdb']
    else:
        value = 0

    return value

def _pagination(pages):
    """Assemble Pages"""

    node = {}
    if pages['next_page'] != 0:
        current_page = f"[COLOR=gold]{pages['current_page']}[/COLOR]"
        label = f"Страница {current_page} из {pages['total_pages']}"

        node = {
            'label': label,
            'params': {
                'path': params['path'],
                'page': pages['next_page'],
                'section': params['section']
                },
            'context_menu': [],
            'isFolder': True,
            'setContent': False,
            }

    return node

def _cast_assemble(cast_info):
    actors = []
    for cast in cast_info:
    #     if '0' in addon.getSetting('tmdb_unblock'):
    #         #url=url.replace('api.themoviedb.org','api-themoviedb-org.translate.goog')
    #         cast['thumbnail'] = cast['thumbnail'].replace('image.tmdb.org', 'image-tmdb-org.translate.goog')

        actors.append(xbmc.Actor(
            name=cast['name_ru'] or cast['name_en'],
            # role=cast['role'],
            # order=cast['order'],
            thumbnail=cast['cover']) #thumbnail=cast['thumbnail'])
            )

    return actors
    
def start():
    redheadsound = RedHeadSound()
    redheadsound.execute()
    del redheadsound
