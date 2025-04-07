# -*- coding: utf-8 -*-
"""MAIN KODI ADDON FILE"""

import os
import sys

from urllib.parse import urlencode
from urllib.parse import parse_qs
from urllib.parse import unquote

from ado import schemes
from ado.scraper import ADOAPI

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

def data_print(data):
    """PRINT LOG IN KODI"""
    xbmc.log(str(data), xbmc.LOGFATAL)

addon = xbmcaddon.Addon(id='plugin.niv.anidub')
handle = int(sys.argv[1])
#
addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
userdata_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
media_path = os.path.join(addon_path, 'resources', 'media')
#
icon = os.path.join(media_path, 'icon.png')
fanart = os.path.join(media_path, 'fanart.jpg')

params = {'path': 'main_part', 'param': '', 'page': '1'}

args = parse_qs(sys.argv[2][1:])

for key, value in args.items():
    params[key] = unquote(value[0])


class ANIDUB:
    """MAIN CLASS"""
    def __init__(self):
        if not os.path.exists(userdata_path):
            os.makedirs(userdata_path)

        self.ado = ADOAPI(base_url=_assemble_siteurl())

    def exec_main_part(self):
        """MAIN MENU"""
        items = [
            {
                'label': '[B]Поиск[/B]',
                'params': {'path': 'search_part'},
                'icon': os.path.join(media_path, 'search.png'),
                },
            {
                'label': '[B]Онгоинги[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_ongoing'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Аниме[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_tv'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Дубляж[/B]',
                'params': {'path': 'partition_part', 'param': 'adubbing'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Дорамы[/B]',
                'params': {'path': 'partition_part', 'param': 'dorama'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Категории[/B]',
                'params': {'path': 'categories_part'},
                'icon': os.path.join(media_path, 'catalog.png')
                }
            ]
        self.create_line(items=items, content=True)

    def exec_categories_part(self):
        """EXTENSION MENU"""
        items = [
            {
                'label': '[B]Аниме TV[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_tv'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Аниме Фильмы[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_movie'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Аниме OVA[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_ova'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Аниме ONA[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_ona'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Аниме Ongoing[/B]',
                'params': {'path': 'partition_part', 'param': 'anime_ongoing'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Японские Сериалы и Фильмы[/B]',
                'params': {'path': 'partition_part', 'param': 'japan_dorama'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Корейские Сериалы и Фильмы[/B]',
                'params': {'path': 'partition_part', 'param': 'korea_dorama'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Китайские Сериалы и Фильмы[/B]',
                'params': {'path': 'partition_part', 'param': 'china_dorama'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Многосерийный сёнэн[/B]',
                'params': {'path': 'partition_part', 'param': 'shonen'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]18+[/B]',
                'params': {'path': 'partition_part', 'param': 'xxx'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Законченные сериалы[/B]',
                'params': {'path': 'partition_part', 'param': 'full'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Незаконченные сериалы[/B]',
                'params': {'path': 'partition_part', 'param': 'unclosed'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Мультфильмы[/B]',
                'params': {'path': 'partition_part', 'param': 'animation'},
                'icon': os.path.join(media_path, 'series.png')
                },
            {
                'label': '[B]Дубляж Анидаба[/B]',
                'params': {'path': 'partition_part', 'param': 'adubbing'},
                'icon': os.path.join(media_path, 'series.png')
                },
            ]
        self.create_line(items=items, content=True)

    def exec_search_part(self):
        """SEARCH IMPLEMENTATION"""
        if not params['param']:
            items = [{
                'label': '[B]Введите название[/B]',
                'params': {
                    'path': 'search_part',
                    'param': 'search_word'
                    },
                'icon': os.path.join(media_path, 'search.png')
                }]

            data_array = addon.getSetting('search_string').split('|')
            data_array.reverse()

            for data in data_array:
                if data == '':
                    continue
                node = {
                    'label': f"[COLOR=gray]{data}[/COLOR]",
                    'params': {
                        'path': 'search_part',
                        'param': 'search_string',
                        'search_string': data
                        },
                    'icon': os.path.join(media_path, 'node.png')
                }
                items.append(node)
            self.create_line(items=items[0:5], content=False)

        if params['param'] == 'search_word':
            search_word = self._input_word()
            if search_word:
                data_array = addon.getSetting('search_string').split('|')
                while len(data_array) >= 3:
                    data_array.pop(0)
                data_array.append(search_word)
                addon.setSetting('search_string', '|'.join(data_array))

        if params['param'] == 'search_string':
            search_data = self.ado.search(query=params['search_string'], page=params['page'])

            items = []
            for data in search_data['info']:
                node = {
                    'label': _assemble_title(title_node=data['title']),
                    'params': {'path': 'release_part', 'id': data['id']},
                    'poster': data['cover']
                    }
                items.append(node)

            if search_data['paginator']['tp'] > search_data['paginator']['cp']:
                page_item = _pagination(pages=search_data['paginator'])
                items.append(page_item)

            self.create_line(items=items, content=True)

    def exec_partition_part(self):
        """PARTITION IMPLEMENTATION"""

        partiton_data = self.ado.partitions(part=params['param'], page=int(params['page']))

        items = []
        for data in partiton_data['info']:
            node = {
                'label': _assemble_title(title_node=data['title']),
                'params': {'path': 'release_part', 'id': data['id']},
                'poster': data['cover']
                }
            items.append(node)

        if partiton_data['paginator']['tp'] > partiton_data['paginator']['cp']:
            page_item = _pagination(pages=partiton_data['paginator'])
            items.append(page_item)

        self.create_line(items=items, content=True)

    def exec_release_part(self):
        """RELEASE IMPLEMENTATION"""
        release_data = self.ado.release(anime_id=params['id'])

        playlist = []
        if addon.getSetting('player_mode') == '0':
            playlist = release_data['playlists'].pop('main')
            if not playlist:
                playlist = release_data['playlists'].pop('sibnet')
        else:
            playlist = release_data['playlists'].pop('sibnet')
            if not playlist:
                playlist = release_data['playlists'].pop('main')

        items = []
        for ep in playlist:
            node = {
                'label': ep['title'],
                'params': {
                    'path': 'play_part',
                    'param': ep['quality_url']
                },
                'info': release_data['info'],
                'isFolder': False
            }
            items.append(node)
        self.create_line(items=items)

    def exec_play_part(self):
        """Модуль для запуска проигрывания Онлайн ссылок"""

        links = self.ado.play_video(videourl=params['param'])
        li = xbmcgui.ListItem(path=links)

        if not 'sibnet' in links:
            try:
                xbmcaddon.Addon('inputstream.adaptive')
            except Exception as e: # pylint: disable=broad-except
                data_print(e)
                self._install_addon(header='inputstream.adaptive')

            if addon.getSetting('inputstream') == '0':
                li.setProperty('inputstream', "inputstream.adaptive")
                li.setProperty('inputstream.adaptive.manifest_type', 'hls')
                if addon.getSetting('quality') == 'AUTO':
                    li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
                else:
                    quality = schemes.quality_sheme.copy()
                    sq = addon.getSetting('quality').lower()
                    rq = quality[sq]
                    li.setProperty('inputstream.adaptive.chooser_resolution_max', rq)
                    li.setProperty('inputstream.adaptive.chooser_resolution_secure_max', rq)
                #li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
                li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')
        else:
            pass

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)

    def create_line(self, items, content=True):
        """Модуль для формирования списка в Коди"""
        for item in items:
            node = _node(item)

            li = xbmcgui.ListItem(node['label'])
            art = {'icon': node['icon']}


            if node['info']:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setMediaType('video')
                #
                videoinfo.setTitle(_clean_title(node['info']['title']))
                videoinfo.setSortTitle(node['info']['sorttitle'])
                videoinfo.setOriginalTitle(node['info']['originaltitle'])
                videoinfo.setPlot(node['info']['plot'])
                #videoinfo.setTagLine(node.get('tagline'))
                videoinfo.setStudios(node['info']['studio']) #list
                #videoinfo.setMediaType(node['info']['mediatype'])
                videoinfo.setGenres(node['info']['genre']) #genre	list - Genres.
                #videoinfo.setCountries(node.get('country')) #countries	list - Countries.
                videoinfo.setWriters(node['info']['writer']) #writers	list - Writers.
                videoinfo.setDirectors(node['info']['director']) #setDirectors(directors)
                videoinfo.setYear(node['info']['year']) #year	integer - Year.
                #videoinfo.setPremiered(node.get('premiered')) #premiered	string - Premiere date
                #videoinfo.setTags(node.get('tag')) #tags	list - Tags
                #videoinfo.setMpaa(node['info']['mpaa']) #mpaa	string - MPAA rating
                #videoinfo.setTrailer(node.get('trailer')) #[string] Trailer path
                #videoinfo.setDuration(node['info']['duration']) #[unsigned int] Duration
                #videoinfo.setTvShowStatus(node['info']['status'])

                art['poster'] = node['info']['cover']
                if node['poster']:
                    art['poster'] = node['poster']

                art['thumb'] = node['info']['thumb']
                if node['thumb']:
                    art['thumb'] = node['thumb']

            li.setArt(art)

            if node['context_menu']:
                li.addContextMenuItems(node['context_menu'])

            if not node['isFolder']:
                li.setProperty('isPlayable', 'true')

            url = f"{sys.argv[0]}?{urlencode(node['params'])}"
            xbmcplugin.addDirectoryItem(handle,url=url,listitem=li,isFolder=node['isFolder'])

        if content:
            xbmcplugin.setContent(handle, 'tvshows')

        xbmcplugin.endOfDirectory(handle, succeeded=True)

    def _input_word(self):
        """Ввод данных для поиска"""
        search_word = xbmcgui.Dialog().input(heading = 'Поиск:', type=xbmcgui.INPUT_ALPHANUM)
        if search_word:
            search_word = search_word.lower()
            if addon.getSetting('search_mode') == '1':
                search_word = _translit_string(search_word)
        return search_word

    def _install_addon(self, header):
        """Функция уведомляет и запускает запрос на установку нужного плагина,
        название передается в формате строки, пример - inputstream.adaptive """

        xbmcgui.Dialog().notification(
            heading=f"Установка Библиотеки: {header}",
            message=header,
            time=1000,
            sound=False
            )
        xbmc.executebuiltin(f'RunPlugin("plugin://{header}")')

    def execute(self):
        """ROUTE"""
        getattr(self, f"exec_{params['path']}")()

def _translit_string(data=None):
    """Модуль транслитерации EN-RU"""
    if data is None:
        return None

    string = data.lower()
    translit_table = schemes.translit_scheme.copy()

    for k, v in translit_table.items():
        if k in string:
            string = string.replace(k, v)

    return string

def _assemble_title(title_node=None):
    if not title_node:
        return ''

    ep = ''
    if title_node['ep']:
        ep = f" | [COLOR=gold]{title_node['ep']}[/COLOR]"

    label = ''
    if addon.getSetting('title_mode') == '0':
        label = title_node['ru']
        if not label:
            label = title_node['en']
    else:
        label = title_node['en']
        if not label:
            label = title_node['ru']

    title = f"{label}{ep}"

    return title

def _node(item=None):
    node_scheme = schemes.node_scheme.copy()

    if item:
        node_scheme.update(item)
    return node_scheme

def _clean_title(node_data=None):
    if not node_data:
        return ''
    title_node = node_data['ru']
    return title_node

def _pagination(pages=None):
    """ASSEMBLE PAGINATION"""
    if pages is None:
        return {}

    node = {}

    if int(pages['cp']) < int(pages['tp']):
        current_page = f"[COLOR=gold]{pages['cp']}[/COLOR]"
        label = f"Страница {current_page} из {pages['tp']}"

        node = {
            'label': label,
            'params': {
                'path': params['path'],
                'param': params['param'],
                'page': int(pages['cp']) + 1,
            },
            'icon': os.path.join(media_path, 'next.png')
        }

        if 'search_string' in params:
            node['params']['search_string'] = params['search_string']

    return node

def _assemble_siteurl():
    """ASSEMBLE SITE_URL"""
    current_mirror = f"mirror_{addon.getSetting('mirrormode')}"

    if not addon.getSetting(current_mirror):
        select_url = addon.getSetting('mirror_0')
    else:
        select_url = addon.getSetting(current_mirror)

    select_url = f"https://{select_url}"

    return select_url
#========================#========================#========================#
def start():
    """START ANIDUB CLASS"""
    ado = ANIDUB()
    ado.execute()
