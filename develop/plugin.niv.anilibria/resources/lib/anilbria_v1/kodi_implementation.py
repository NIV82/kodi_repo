# -*- coding: utf-8 -*-
"""A module that provides KODI-adapted functions for accessing the site API"""

import os
import json

from urllib.parse import urlencode
from urllib.parse import quote

from anilbria_v1 import bencode
from anilbria_v1 import webtools
from anilbria_v1 import kodi_schemes

class ALAPI:
    """API IMPLEMENTATION"""
    default_url = "https://anilibria.top"
    def __init__(self, authorization=False, authorization_data=None, base_url=None):
        self.site_url = base_url or ALAPI.default_url
        self.api_url = f"{self.site_url}/api/v1"

        self.network = webtools.WebTools(
            auth_usage=authorization
            )

    def search(self, query=None):
        """SEARCH IMPLEMENTATION"""
        if query is None:
            return _error('Ошибка - Пустой запрос')

        search_url = f"{self.api_url}/app/search/releases?query="
        complete_url = f"{search_url}{quote(query.lower())}"

        data_array = self.network.get_bytes(url=complete_url)
        if not data_array['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        data_array = _json(data_array['content'])

        if data_array == []:
            return _error('Контент не найден')

        if data_array is None:
            return _error('Ошибка обработки JSON')

        processed_info = []
        for content in data_array:
            result = _assemble_info(site_url=self.site_url, data=content)
            processed_info.append(result)

        return processed_info

    def schedule(self):
        """SCHEDULE IMPLEMENTATION"""
        schedule_url = f"{self.api_url}/anime/schedule/week"

        data_array = self.network.get_bytes(url=schedule_url)
        if not data_array['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        data_array = _json(data_array['content'])

        if data_array == []:
            return _error('Контент не найден')

        if data_array is None:
            return _error('Ошибка обработки JSON')

        week = kodi_schemes.week.copy()

        for data in data_array:
            day = data['release']['publish_day']['description']

            release_info = _assemble_info(site_url=self.site_url, data=data['release'])

            if 'new_release_episode_ordinal' in data:
                if data['new_release_episode_ordinal']:
                    release_info['episode'] = int(data['new_release_episode_ordinal'])
                else:
                    release_info['episode'] = 0

            week[day].append(release_info)

        return week

    def latest_release(self):
        """LATEST RELEASE IMPLEMENTATION"""
        latest_url = f"{self.api_url}/anime/releases/latest?limit=42"

        data_array = self.network.get_bytes(url=latest_url)
        if not data_array['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        data_array = _json(data_array['content'])

        if data_array == []:
            return _error('Контент не найден')

        if data_array is None:
            return _error('Ошибка обработки JSON')

        processed_info = []
        for content in data_array:
            result = _assemble_info(site_url=self.site_url, data=content)
            processed_info.append(result)

        return processed_info

    def catalog(self, request=None):
        """CATALOG IMPLEMENTATION"""
        if request is None:
            request = {}

        post_data = kodi_schemes.post_data.copy()
        post_data.update(request)

        post_data = urlencode(post_data)
        post_data = post_data.replace('%27','%22')
        catalog_url = f"{self.api_url}/anime/catalog/releases?"
        complete_url = f"{catalog_url}{post_data}"

        data_array = self.network.get_bytes(url=complete_url)
        if not data_array['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        data_array = _json(data_array['content'])

        if data_array['data'] == []:
            return _error('Контент не найден')

        if data_array is None:
            return _error('Ошибка обработки JSON')

        pagination = _pagination(data=data_array['meta'])

        processed_info = []
        for content in data_array['data']:
            result = _assemble_info(site_url=self.site_url, data=content)
            processed_info.append(result)

        return {'data': processed_info, 'pagination': pagination}

    def release(self, anime_id=None):
        """RELEASE IMPLEMENTATION"""
        if anime_id is None:
            return _error('Отсутствует anime_ID')

        anime_id = quote(f"{anime_id}")

        release_url = f"{self.api_url}/anime/releases/"
        complete_url = f"{release_url}{anime_id}"

        data_array = self.network.get_bytes(url=complete_url)
        if not data_array['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        data_array = _json(data_array['content'])

        if data_array == []:
            return _error('Контент не найден')

        if data_array is None:
            return _error('Ошибка обработки JSON')

        data_array = _assemble_info(site_url=self.site_url, data=data_array)

        return data_array

    def get_genres(self, ready=True):
        """GENRES IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_genres.copy()

        genres_url = f"{self.api_url}/anime/catalog/references/genres"

        genre_dict = self._request_misc(misc_url=genres_url)
        if not genre_dict:
            return {}

        publish_genres = {}
        for genre in genre_dict:
            publish_genres.update({genre['name']: genre['id']})
        publish_genres = dict(sorted(publish_genres.items(), key=lambda item: item[1]))
        return publish_genres

    def get_types(self, ready=True):
        """TYPES IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_types.copy()

        types_url = f"{self.api_url}/anime/catalog/references/types"

        types_dict = self._request_misc(misc_url=types_url)
        if not types_dict:
            return {}

        publish_types = {}
        for t in types_dict:
            publish_types.update({t['description']: t['value']})
        return publish_types

    def get_publish_status(self, ready=True):
        """PUBLISH STATUS IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_status.copy()

        statuses_url = f"{self.api_url}/anime/catalog/references/publish-statuses"

        status_dict = self._request_misc(misc_url=statuses_url)
        if not status_dict:
            return {}

        publish_status = {}
        for status in status_dict:
            publish_status.update({status['description']: status['value']})
        return publish_status

    def get_production_status(self, ready=True):
        """PRODUCTION STATUS IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_production_status.copy()

        production_url = f"{self.api_url}/anime/catalog/references/production-statuses"

        production_dict = self._request_misc(misc_url=production_url)
        if not production_dict:
            return {}

        publish_production_status = {}
        for production in production_dict:
            publish_production_status.update({production['description']: production['value']})
        return publish_production_status

    def get_sorting(self, ready=True):
        """SORTING IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_sorting.copy()

        sorting_url = f"{self.api_url}/anime/catalog/references/sorting"

        sorting_dict = self._request_misc(misc_url=sorting_url)
        if not sorting_dict:
            return {}

        publish_sorting = {}
        for sorting in sorting_dict:
            publish_sorting.update({sorting['label']: sorting['value']})
        return publish_sorting

    def get_seasons(self, ready=True):
        """SEASON IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_seasons.copy()

        season_url = f"{self.api_url}/anime/catalog/references/seasons"

        seasons_dict = self._request_misc(misc_url=season_url)
        if not seasons_dict:
            return {}

        publish_seasons = {}
        for seasons in seasons_dict:
            publish_seasons.update({seasons['description']: seasons['value']})
        return publish_seasons

    def get_years(self, ready=True):
        """YEAR IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_years.copy()

        years_url = f"{self.api_url}/anime/catalog/references/years"

        years_list = self._request_misc(misc_url=years_url)
        if not years_list:
            return []

        publish_years = []
        for years in years_list:
            publish_years.append(years)
        return publish_years

    def get_mpaa(self, ready=True):
        """MPAA IMPLEMENTATION"""
        if ready:
            return kodi_schemes.publish_mpaa.copy()

        mpaa_url = f"{self.api_url}/anime/catalog/references/age-ratings"

        mpaa_dict = self._request_misc(misc_url=mpaa_url)
        if not mpaa_dict:
            return {}

        publish_mpaa = {}
        for ages in mpaa_dict:
            publish_mpaa.update({ages['label']: ages['value']})
        return publish_mpaa

    def get_torrent_file(self, tid=None, thash=None, tpath=None):
        """GET TORRENT FILE"""
        if tpath is None or thash is None:
            return None

        if not os.path.exists(tpath):
            file_id = thash or tid
            #turl = f"{self.api_url}/anime/torrents/{thash}/file"
            turl = f"{self.api_url}/anime/torrents/{file_id}/file"
            torrent_file = self.network.get_file(url=turl, fpath=tpath)
        else:
            torrent_file = tpath

        with open(torrent_file, 'rb') as rf:
            torrent_data = rf.read()

        torrent = bencode.bdecode(torrent_data)
        info = torrent['info']

        torrent_list = []

        if 'files' in info:
            for i, x in enumerate(info['files']):
                node = {
                    'index': i,
                    'label': x['path'][-1],
                    #'size': x['length'],
                    #'hash': thash
                }
                torrent_list.append(node)
        else:
            node = {
                'index': 0,
                'label': info['name'],
                #'size': info['length'],
                #'hash': thash
            }
            torrent_list.append(node)

        torrent_list = sorted(torrent_list, key=lambda item: item['label'])
        return torrent_list

    def _request_misc(self, misc_url=None):
        """GET DATA IMPLEMENTATION"""
        if misc_url is None:
            return None

        html = self.network.get_bytes(url=misc_url)
        if not html['connection_reason'] == 'OK':
            return None

        misc_dict = _json(html['content'])

        return misc_dict

def _assemble_torrents(torrents=None):
    """ASSEMBLE TORRENTS DATA"""
    if not torrents:
        return []

    torrents_info = []

    for tr in torrents:
        item = kodi_schemes.torrent_node.copy()

        item['title'] = tr['label']
        item['id'] = tr['id']
        item['hash'] = tr['hash']
        item['size'] = tr['size']
        item['magnet'] = tr['magnet']

        try:
            item['codec'] = f"{tr['codec']['value']} - {tr['color']['value']}"
            seed = f"[COLOR=lime]S{tr['seeders']:>02}[/COLOR]"
            #leech = f"[COLOR=red]L{tr['leechers']:>02}[/COLOR]"
            # item['seeds'] = f"{seed}|{leech}"
            item['seeds'] = seed
        except: # pylint: disable=W0702
            pass

        torrents_info.append(item)

    return torrents_info

def _assemble_genres(data=None, string=False):
    """ASSEMBLE GENRES DATA"""
    if data is None:
        return []

    try:
        genres = []

        for i in data:
            genres.append(i['name'])

        if string:
            genres = ', '.join(genres)
        return genres
    except: # pylint: disable=W0702
        return []

def _assemble_members(data=None, string=False):
    """ASSEMBLE MEMBERS DATA"""
    if data is None:
        return {}

    try:
        team = {}

        for i in data:
            role = i['role']['description']
            nick = i['nickname']

            if role in team:
                team[role].append(nick)
            else:
                team[role] = [nick]

        if string:
            result = ''
            for k, v in team.items():
                members = ', '.join(v)
                result = f"{result}\n{k}: {members}"
            team = result

        return team
    except: # pylint: disable=W0702
        return {}

def _assemble_episodes(episodes=None):
    """ASSEMBLE EPISODES DATA"""
    if not episodes:
        return []

    episodes_info = []

    for ep in episodes:
        item = kodi_schemes.episode_node.copy()
        vurl = kodi_schemes.vurl_scheme.copy()

        item['title'] = ep['name']
        item['originaltitle'] = ep['name_english']
        item['ordinal'] = ep['ordinal']
        vurl = {
            'SD': ep['hls_480'],
            'HD': ep['hls_720'],
            'FHD': ep['hls_1080']
        }
        item['video_url'] = vurl
        item['duration'] = ep['duration']

        episodes_info.append(item)

    return episodes_info

def _pagination(data=None):
    """PAGINATION IMPLEMENTATION"""
    if data is None:
        return {}

    if 'pagination' in data:
        data = data['pagination']

    pagination = kodi_schemes.pagination_scheme.copy()

    current_page = 0
    if 'current_page' in data and data['current_page']:
        current_page = data['current_page']

    total_pages = 0
    if 'total_pages' in data and data['total_pages']:
        total_pages = data['total_pages']

    next_page = 0
    if current_page < total_pages:
        next_page = current_page + 1

    pagination['current_page'] = current_page
    pagination['next_page'] = next_page
    pagination['total_pages'] = total_pages

    return pagination

def _assemble_info(site_url=None, data=None, genres=False, members=False):
    """REASSIGNMENT DATA"""
    if data is None:
        return _error('Отсутствуют данные')

    main_info = kodi_schemes.main_info.copy()

    main_info['id'] = data['id']
    main_info['title'] = data['name']['main']
    main_info['originaltitle'] = data['name']['english']
    main_info['sorttitle'] = data['name']['main']
    main_info['cover'] = f"{site_url}{data['poster']['src']}"
    main_info['thumb'] = f"{site_url}{data['poster']['src']}"
    main_info['mpaa'] = data['age_rating']['label']
    main_info['plot'] = data['description']

    if 'average_duration_of_episode' in data and data['average_duration_of_episode']:
        main_info['duration'] = int(data['average_duration_of_episode']) * 60

    if 'year' in data and data['year']:
        main_info['year'] = int(data['year'])

    if 'genres' in data:
        main_info['genre'] = _assemble_genres(data=data['genres'], string=genres)

    if 'members' in data:
        main_info['members'] = _assemble_members(data=data['members'], string=members)

    # if 'sponsor' in data:
    #     pass

    if 'episodes' in data:
        main_info['episodes'] = _assemble_episodes(episodes=data['episodes'])

    if 'torrents' in data:
        main_info['torrents'] = _assemble_torrents(torrents=data['torrents'])

    if 'latest_episode' in data:
        if data['episodes_total'] and data['latest_episode']['ordinal']:
            ep_num = f"{data['latest_episode']['ordinal']} из {data['episodes_total']}"
        elif data['latest_episode']['ordinal']:
            ep_num = f"{data['latest_episode']['ordinal']} эпизод"
        else:
            ep_num = ''

        main_info['latest_episode'] = ep_num

    return main_info

def _error(title=None):
    """ERROR IMPLEMENTATION"""
    error = kodi_schemes.error_scheme.copy()
    if title:
        error['label'] = f"{title}"
    return ([error],)

def _json(json_data=None):
    """JSON IMPLEMENTATION"""
    if json_data is None:
        return None

    try:
        json_data = json.loads(json_data)
    except: #pylint: disable=W0702
        return None

    return json_data
