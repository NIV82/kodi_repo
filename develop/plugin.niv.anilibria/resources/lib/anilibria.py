# -*- coding: utf-8 -*-
"""MAIN KODI ADDON FILE"""

import os
import sys

from urllib.parse import urlencode
#from urllib.parse import quote
#from urllib.parse import quote_plus
from urllib.parse import parse_qs
from urllib.parse import unquote
from urllib.parse import quote

from anilbria_v1 import kodi_schemes
from anilbria_v1.kodi_implementation import ALAPI

#del ALAPI

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

def data_print(data):
    """PRINT LOG IN KODI"""
    xbmc.log(str(data), xbmc.LOGFATAL)

addon = xbmcaddon.Addon(id='plugin.niv.anilibria')
handle = int(sys.argv[1])
#
addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
userdata_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
media_path = os.path.join(addon_path, 'resources', 'media')
#
icon = os.path.join(media_path, 'icon.png')
fanart = os.path.join(media_path, 'fanart.jpg')
#
progress_bg = xbmcgui.DialogProgressBG()
dialog = xbmcgui.Dialog()

params = {'path': 'main_part', 'param': '', 'page': '1'}

args = parse_qs(sys.argv[2][1:])

for key, value in args.items():
    params[key] = unquote(value[0])

class Anilibria:
    """MAIN CLASS"""
    def __init__(self):
        if not os.path.exists(userdata_path):
            os.makedirs(userdata_path)

        self.torrents_dir = os.path.join(userdata_path, 'torrents')
        if not os.path.exists(self.torrents_dir):
            os.mkdir(self.torrents_dir)

        self.alapi = ALAPI(
            base_url=_assemble_siteurl()
            )

    def exec_main_part(self):
        """MAIN MENU"""
        items = [
            {
                'label': '[B]Поиск[/B]',
                'params': {'path': 'search_part'},
                'icon': os.path.join(media_path, 'search.png'),
                },
            {
                'label': '[B]Расписание[/B]',
                'params': {'path': 'schedule_part'},
                'icon': os.path.join(media_path, 'schedule.png')
                },
            {
                'label': '[B]Новое[/B]',
                'params': {'path': 'latest_part'},
                'icon': os.path.join(media_path, 'new.png')
                },
            {
                'label': '[B]Популярное[/B]',
                'params': {'path': 'popular_part','mode': 'RATING_DESC'},
                'icon': os.path.join(media_path, 'favorites.png')
                },
            {
                'label': '[B]Каталог[/B]',
                'params': {'path': 'catalog_part'},
                'icon': os.path.join(media_path, 'catalog.png')
                }
            ]
        self.create_line(items=items, content=False)

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
            search_data = self.alapi.search(query=params['search_string'])

            if isinstance(search_data, tuple):
                self.create_line(search_data[0])
                return

            items = []
            for sn in search_data:
                node = {
                    'label': sn['title'],
                    'params': {
                        'path': 'select_part',
                        'id': sn['id']
                        },
                    'info': sn
                    }
                items.append(node)
            self.create_line(items=items)

    def exec_schedule_part(self):
        """SCHEDULE IMPLEMENTATION"""
        schedule_data = self.alapi.schedule()

        if isinstance(schedule_data, tuple):
            self.create_line(schedule_data[0])
            return

        items = []
        for day in schedule_data:
            node = {
                'label': f"[B]{day}[/B]",
                'icon': os.path.join(media_path, 'schedule.png'),
                'isFolder': False
            }
            items.append(node)

            for sd in schedule_data[day]:
                sd['thumb'] = ''
                title = f"[COLOR=blue]EP{sd['episode']:>03}[/COLOR] | {sd['title']}"

                node = {
                    'label': title,
                    'params': {
                        'path': 'select_part',
                        'id': sd['id']
                        },
                    'icon': os.path.join(media_path, 'empty.png'),
                    'info': sd,
                    }
                items.append(node)

        self.create_line(items=items, content=False)
        return

    def exec_latest_part(self):
        """LATEST RELEASE IMPLEMENTATION"""
        latest_data = self.alapi.latest_release()

        if isinstance(latest_data, tuple):
            self.create_line(latest_data[0])
            return

        items = []

        for ld in latest_data:
            node = {
                'label': f"{ld['title']} | [COLOR=gold]{ld['latest_episode']}[/COLOR]",
                'params': {
                    'path': 'select_part',
                    'id': ld['id'],
                    },
                'info': ld
                }
            items.append(node)

        self.create_line(items=items)
        return

    def exec_popular_part(self):
        """POPULAR IMPLEMENTATION"""
        popular_data = self.alapi.catalog({'page': params['page'],'f[sorting]': params['mode']})

        if isinstance(popular_data, tuple):
            self.create_line(popular_data[0])
            return

        items = []
        for pd in  popular_data['data']:
            node = {
                'label': pd['title'],
                'params': {
                    'path': 'select_part',
                    'id': pd['id']
                    },
                'info': pd,
                }
            items.append(node)

        if popular_data['pagination']:
            pages = _pagination(pages=popular_data['pagination'])
            if pages:
                items.append(pages)

        self.create_line(items=items)
        return

    def exec_catalog_part(self):
        """CATALOG IMPLEMENTATION"""
        items = [
            {
                'label': f"Жанр: [COLOR=gold]{addon.getSetting('genres')}[/COLOR]",
                'params': {'path': 'catalog_select', 'param': 'genres'}
            },
            {
                'label': f"Тип: [COLOR=gold]{addon.getSetting('types')}[/COLOR]",
                'params': {'path': 'catalog_select', 'param': 'types'}
            },
            {
                'label': f"Статус выхода: [COLOR=gold]{addon.getSetting('publish')}[/COLOR]",
                'params': {'path': 'catalog_select', 'param': 'publish'}
            },
            {
                'label': f"Статус озвучки: [COLOR=gold]{addon.getSetting('production')}[/COLOR]",
                'params': {'path': 'catalog_select', 'param': 'production'}
            },
            {
                'label': f"Сортировка: [COLOR=gold]{addon.getSetting('sorting')}[/COLOR]",
                'params': {'path': 'catalog_select', 'param': 'sorting'}
            },
            {
                'label': f"Сезоны: [COLOR=gold]{addon.getSetting('seasons')}[/COLOR]",
                'params': {'path': 'catalog_select', 'param': 'seasons'}
            },
            {
                'label': f"Период выхода - От: [COLOR=gold]{addon.getSetting('from_year')}[/COLOR]",
                'params': {'path': 'catalog_select2', 'param': 'from_year'}
            },
            {
                'label': f"Период выхода - До: [COLOR=gold]{addon.getSetting('to_year')}[/COLOR]",
                'params': {'path': 'catalog_select2', 'param': 'to_year'}
            },
            {
                'label': f"Возрастной рейтинг: [COLOR=gold]{addon.getSetting('mpaa')}[/COLOR]",
                'params': {'path': 'catalog_select2', 'param': 'mpaa'}
            },
            {
                'label': f"По Названию: [COLOR=gold]{addon.getSetting('search')}[/COLOR]",
                'params': {'path': 'catalog_select2', 'param': 'search_word'}
            },
            {
                'label': "[COLOR=gold][ Сбросить Все ][/COLOR]",
                'params': {'path': 'catalog_select2', 'param': 'clean_catalog'}
            },
            {
                'label': "[COLOR=gold][ Поиск ][/COLOR]",
                'params': {'path': 'catalog_search','param': ''}
            },
            ]
        self.create_line(items=items)

    def exec_catalog_select(self):
        """CATALOG NODES IMPLEMENTATION - PART1"""
        if params['param'] == 'genres':
            genres = self.alapi.get_genres()
            list_genres = list(genres.keys())
            result = dialog.select('Жанр:', list_genres)
            if result >= 0:
                addon.setSetting(id='genres', value=list_genres[result])

        if params['param'] == 'types':
            types = self.alapi.get_types()
            list_types = list(types.keys())
            result = dialog.select('Тип:', list_types)
            if result >= 0:
                addon.setSetting(id='types', value=list_types[result])

        if params['param'] == 'publish':
            publish = self.alapi.get_publish_status()
            list_publish = list(publish.keys())
            result = dialog.select('Статус выхода:', list_publish)
            if result >= 0:
                addon.setSetting(id='publish', value=list_publish[result])

        if params['param'] == 'production':
            production = self.alapi.get_production_status()
            list_production = list(production.keys())
            result = dialog.select('Статус озвучки:', list_production)
            if result >= 0:
                addon.setSetting(id='production', value=list_production[result])

        if params['param'] == 'sorting':
            sorting = self.alapi.get_sorting()
            list_sorting = list(sorting.keys())
            result = dialog.select('Сортировка:', list_sorting)
            if result >= 0:
                addon.setSetting(id='sorting', value=list_sorting[result])

        if params['param'] == 'seasons':
            seasons = self.alapi.get_seasons()
            list_seasons = list(seasons.keys())
            result = dialog.select('Сезон выхода:', list_seasons)
            if result >= 0:
                addon.setSetting(id='seasons', value=list_seasons[result])

    def exec_catalog_select2(self):
        """CATALOG NODES IMPLEMENTATION - PART2"""
        if params['param'] == 'from_year':
            from_year = self.alapi.get_years()
            result = dialog.select('Начальная дата:', from_year)
            if result >= 0:
                addon.setSetting(id='from_year', value=from_year[result])

        if params['param'] == 'to_year':
            to_year = self.alapi.get_years()
            result = dialog.select('Конечная дата:', to_year)
            if result >= 0:
                addon.setSetting(id='to_year', value=to_year[result])

        if params['param'] == 'mpaa':
            mpaa = self.alapi.get_mpaa()
            list_mpaa = list(mpaa.keys())
            result = dialog.select('Возрастной рейтинг:', list_mpaa)
            if result >= 0:
                addon.setSetting(id='mpaa', value=list_mpaa[result])

        if params['param'] == 'search_word':
            search_word = self._input_word()
            if search_word:
                addon.setSetting('search', search_word)

        if params['param'] == 'clean_catalog':
            try:
                addon.setSetting('genres', '')
                addon.setSetting('types', '')
                addon.setSetting('publish', '')
                addon.setSetting('production', '')
                addon.setSetting('sorting', 'Обновлены недавно')
                addon.setSetting('seasons', '')
                addon.setSetting('from_year', '1990')
                addon.setSetting('to_year', '2025')
                addon.setSetting('mpaa', '')
                addon.setSetting('search', '')

                dialog.notification(heading='Поиск', message='Выполнено', time=1000, sound=False)
            except Exception as e: # pylint: disable=broad-except
                data_print(e)
                dialog.notification(heading='Поиск', message='Ошибка', time=1000, sound=False)

    def exec_catalog_search(self):
        """Формирует запрос и список найденного в каталоге"""
        genres = self.alapi.get_genres()
        types = self.alapi.get_types()
        sorting = self.alapi.get_sorting()
        season = self.alapi.get_seasons()
        age_rating = self.alapi.get_mpaa()
        publish = self.alapi.get_publish_status()
        production = self.alapi.get_production_status()

        request = {
            'page': params['page'],
            'limit': 15,
            'f[types]': types[addon.getSetting('types')],
            'f[genres]': genres[addon.getSetting('genres')],
            'f[search]': addon.getSetting('search'),
            'f[sorting]': sorting[addon.getSetting('sorting')],
            'f[seasons]': season[addon.getSetting('seasons')],
            'f[age_ratings]': age_rating[addon.getSetting('mpaa')],
            'f[years][to_year]': addon.getSetting('to_year'),
            'f[years][from_year]': addon.getSetting('from_year'),
            'f[publish_statuses]': publish[addon.getSetting('publish')],
            'f[production_statuses]': production[addon.getSetting('production')]
            }

        catalog_data = self.alapi.catalog(request=request)

        if isinstance(catalog_data, tuple):
            self.create_line(catalog_data[0])
            return

        items = []
        for cd in  catalog_data['data']:
            node = {
                'label': cd['title'],
                'params': {
                    'path': 'select_part',
                    'id': cd['id']
                    },
                'info': cd,
                }
            items.append(node)

        pages = _pagination(catalog_data['pagination'])
        if pages:
            items.append(pages)

        self.create_line(items=items)
        return

    def exec_select_part(self):
        """Формирует список онлайн и торрент"""
        release_data = self.alapi.release(anime_id=params['id'])

        if isinstance(release_data, tuple):
            self.create_line(release_data[0])
            return

        episodes = release_data.pop('episodes')
        torrents = release_data.pop('torrents')

        items = []
        if addon.getSetting('playmode') == '0':
            for ep in episodes:
                release_data['duration'] = ep['duration']
                vd = _hls_url(quality=addon.getSetting('quality'), episode=ep)
                node = {
                    'label': vd['title'],
                    'params': {
                        'path': 'online_play',
                        'param': vd['url']
                    },
                    'info': release_data,
                    'isFolder': False
                }
                items.append(node)
            self.create_line(items)

        if addon.getSetting('playmode') == '1':
            for tf in torrents:
                node = {
                    'label': f"{tf['seeds']}|{tf['title']}",
                    'params': {
                        'path': 'torrent_part',
                        'id': tf['id'],
                        'magnet': tf['magnet'],
                        'hash': tf['hash'],
                        },
                    'info': release_data,
                    }
                items.append(node)
            self.create_line(items=items)

        return

    def exec_torrent_part(self):
        """Формирует список серий из торрента"""
        #tid = params['id']
        thash = params['hash']
        #torrent_magnet = params['magnet']

        tpath = os.path.join(self.torrents_dir, f"{thash}.torrent")
        torrent_data = self.alapi.get_torrent_file(thash=thash, tpath=tpath)

        items = []
        for td in torrent_data:
            node = {
                'label': td['label'],
                'params': {
                    'path': 'torrent_play',
                    'index': td['index'],
                    'torrent_id': thash,
                    #'magnet': torrent_magnet
                },
                'isFolder': False
            }
            items.append(node)
        self.create_line(items=items)

    def exec_torrent_play(self):
        """Модуль выбора движка для проигрывания Торрента"""
        turl = os.path.join(self.torrents_dir, f"{params['torrent_id']}.torrent")
        index = int(params['index'])
        torrent_engine = addon.getSetting('engine')

        if torrent_engine == '0':
            try:
                purl =f"plugin://plugin.video.tam/?mode=play&url={quote(turl)}&ind={index}"
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(handle, True, item)
            except Exception as e: # pylint: disable=broad-except
                data_print(e)
                dialog.notification(heading='T2HTTP', message='Ошибка', time=1000, sound=False)

        if torrent_engine == '1':
            try:
                purl = f"plugin://plugin.video.elementum/play?uri={quote(turl)}&oindex={index}"
                item = xbmcgui.ListItem(path=purl)
                xbmcplugin.setResolvedUrl(handle, True, item)
            except Exception as e: # pylint: disable=broad-except
                data_print(e)
                dialog.notification(heading='ELEMENTUM', message='Ошибка', time=1000, sound=False)

    def exec_online_play(self):
        """Модуль для запуска проигрывания Онлайн ссылок"""
        try:
            xbmcaddon.Addon('inputstream.adaptive')
        except Exception as e: # pylint: disable=broad-except
            data_print(e)
            self.install_addon(header='inputstream.adaptive')

        li = xbmcgui.ListItem(path=params['param'])

        if addon.getSetting('inputstream') == '0':
            li.setProperty('inputstream', "inputstream.adaptive")
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
            li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)
#========================#========================#========================#
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
                videoinfo.setTitle(node['info']['title'])
                videoinfo.setSortTitle(node['info']['sorttitle'])
                videoinfo.setOriginalTitle(node['info']['originaltitle'])
                videoinfo.setPlot(node['info']['plot'])
                #videoinfo.setTagLine(node.get('tagline'))
                #videoinfo.setStudios(node.get('studio')) #list
                #videoinfo.setMediaType(node['info']['mediatype'])
                videoinfo.setGenres(node['info']['genre']) #genre	list - Genres.
                #videoinfo.setCountries(node.get('country')) #countries	list - Countries.
                #videoinfo.setWriters(node.get('credits')) #writers	list - Writers.
                #videoinfo.setDirectors(node.get('director')) #setDirectors(directors)
                videoinfo.setYear(node['info']['year']) #year	integer - Year.
                #videoinfo.setPremiered(node.get('premiered')) #premiered	string - Premiere date
                #videoinfo.setTags(node.get('tag')) #tags	list - Tags
                videoinfo.setMpaa(node['info']['mpaa']) #mpaa	string - MPAA rating
                #videoinfo.setTrailer(node.get('trailer')) #[string] Trailer path
                videoinfo.setDuration(node['info']['duration']) #[unsigned int] Duration
                #videoinfo.setTvShowStatus(node['info']['status'])

                art['poster'] = node['info']['cover']
                art['thumb'] = node['info']['thumb']

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

    def execute(self):
        """Модуль Роутинга"""
        getattr(self, f"exec_{params['path']}")()

    def _input_word(self):
        """Ввод данных для поиска"""
        search_word = dialog.input(heading = 'Поиск:', type=xbmcgui.INPUT_ALPHANUM)
        if search_word:
            search_word = search_word.lower()
            if addon.getSetting('search_mode') == '1':
                search_word = _translit_string(search_word)
        return search_word

    def install_addon(self, header):
        """Функция уведомляет и запускает запрос на установку нужного плагина,
        название передается в формате строки, пример - inputstream.adaptive """

        xbmcgui.Dialog().notification(
            heading=f"Установка Библиотеки: {header}",
            message=header,
            time=1000,
            sound=False
            )
        xbmc.executebuiltin(f'RunPlugin("plugin://{header}")')

    def _create_context(self, label, path):
        """Создание пункта контекстного меню"""
        req = (
            label, f'Container.Update("plugin://plugin.niv.anilibria/?path={path}")')
        return req

def _translit_string(data=None):
    """Модуль транслитерации EN-RU"""
    if data is None:
        return None

    string = data.lower()
    translit_table = kodi_schemes.translit_scheme.copy()

    for k, v in translit_table.items():
        if k in string:
            string = string.replace(k, v)

    return string

def _hls_url(quality=None, episode=None):
    """Обработка ссылки онлайн-видео"""
    if quality is None or episode is None:
        return None

    #data_print(epi)
    if episode['title'] and episode['ordinal']:
        title = f"{episode['ordinal']} - {episode['title']}"
    else:
        title = episode['title'] or episode['originaltitle'] or episode['ordinal']

    if episode['video_url'][quality]:
        episode_hls = episode['video_url'][quality]
        title = f"{title}"
    elif episode['video_url']['FHD']:
        episode_hls = episode['video_url']['FHD']
        title = f"{title} | FHD"
    elif episode['video_url']['HD']:
        episode_hls = episode['video_url']['HD']
        title = f"{title} | HD"
    elif episode['video_url']['SD']:
        episode_hls = episode['video_url']['SD']
        title = f"{title} | SD"
    else:
        return None

    return {'title': title, 'url': episode_hls}

def _pagination(pages=None):
    """ASSEMBLE PAGINATION"""
    if pages is None:
        return None
    node = {}

    if pages['next_page'] != 0:
        current_page = f"[COLOR=gold]{pages['current_page']}[/COLOR]"
        label = f"Страница {current_page} из {pages['total_pages']}"

        node = {
            'label': label,
            'params': {
                'path': 'catalog_search',
                'page': pages['next_page'],
            },
            'icon': os.path.join(media_path, 'next.png')
        }

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

def _node(item=None):
    node_scheme = kodi_schemes.node_scheme.copy()

    if item:
        node_scheme.update(item)
    return node_scheme

def start():
    """Модуль запуска"""
    al = Anilibria()
    al.execute()
