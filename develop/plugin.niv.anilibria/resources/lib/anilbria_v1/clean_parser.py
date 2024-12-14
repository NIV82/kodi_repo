# -*- coding: utf-8 -*-

from urllib.parse import urlencode
from urllib.parse import quote
    
BASE_URL = "https://anilibria.top"
API_URL = f"{BASE_URL}/api/v1"
CATALOG_PREURL = f"{API_URL}/anime/catalog"

SEARCH_URL = f"{API_URL}/app/search/releases?query="
SCHEDULE_WEEK_URL = f"{API_URL}/anime/schedule/week"
SCHEDULE_NOW_ULR = f"{API_URL}/anime/schedule/now"
CATALOG_URL = f"{CATALOG_PREURL}/releases?"

GENRES_URL = f"{CATALOG_PREURL}/references/genres"
TYPES_URL = f"{CATALOG_PREURL}/references/types"
STATUTES_URL = f"{CATALOG_PREURL}/references/publish-statuses"
PRODUCTION_URL = f"{CATALOG_PREURL}/references/production-statuses"
SORTING_URL = f"{CATALOG_PREURL}/references/sorting"
SEASONS_URL = f"{CATALOG_PREURL}/references/seasons"
YEARS_URL = f"{CATALOG_PREURL}/references/years"
AGES_URL = f"{CATALOG_PREURL}/references/age-ratings"

RELEASE_URL = f"{API_URL}/anime/releases/"
EPISODE_URL = f"{API_URL}/anime/releases/episodes/"
TORRENT_URL = f"{API_URL}/anime/torrents/release/"

class API:
    def __init__(self, authorization=False):
        from anilbria_v1.webtools import WebTools
        self.network = WebTools(
            auth_usage=authorization
            )
        del WebTools

    def search(self, query=None):
        if query is None:
            return None
        
        query = quote(query)
        complete_url = f"{SEARCH_URL}{query}"

        try:
            search_data = self.network.get_bytes(url=complete_url)
            if not search_data['connection_reason'] == 'OK':
                return None
        except:
            return None

        return search_data

    def schedule(self):
        try:
            schedule_data = self.network.get_bytes(url=SCHEDULE_WEEK_URL)
            if not schedule_data['connection_reason'] == 'OK':
                return None
        except:
            return None
        
        return schedule_data

    def catalog(self, request={}):
        post_data = {
            'page': 1,
            'limit': 15,
            'f[types]': '',
            'f[genres]': '',
            'f[search]': '',
            'f[sorting]': 'FRESH_AT_DESC',
            'f[seasons]': '',
            'f[age_ratings]': '',
            'f[years][to_year]': 2024,
            'f[years][from_year]': 1990,
            'f[publish_statuses]': '',
            'f[production_statuses]': ''
            }

        try:
            post_data.update(request)
        except:
            pass

        post_data = urlencode(post_data)
        complete_url = f"{CATALOG_URL}{post_data}"

        try:
            catalog_data = self.network.get_bytes(url=complete_url)
            if not catalog_data['connection_reason'] == 'OK':
                return None
        except:
            return None

        return catalog_data
    
    def release(self, anime_id=None):
        if anime_id is None:
            return None

        anime_id = quote(anime_id)
        complete_url = f"{RELEASE_URL}{anime_id}"

        try:
            release_data = self.network.get_bytes(url=complete_url)
            if not release_data['connection_reason'] == 'OK':
                return None
        except:
            return None

        return release_data