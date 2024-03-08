# -*- coding: utf-8 -*-

from . import tmdbweb

TMDB_PARAMS = {'api_key': 'f090bb54758cabf231fb605d3e3e0468'}
BASE_URL = 'https://api.themoviedb.org/3/{}'
IMAGE_URL = {'original': 'https://image.tmdb.org/t/p/original','preview': 'https://image.tmdb.org/t/p/w780'}
#SEARCH_URL = BASE_URL.format('search/movie')
FIND_URL = BASE_URL.format('find/{}')
MOVIE_URL = BASE_URL.format('movie/{}')
SERIES_URL = BASE_URL.format('tv/{}')
#COLLECTION_URL = BASE_URL.format('collection/{}')
#CONFIG_URL = BASE_URL.format('configuration')

class TMDBScraper(object):
    def __init__(self, language, certification_country, search_language, unblock=False):
        self.certification_country = certification_country
        self.language = language
        self.search_language = search_language
        self.unblock = unblock
    
    def get_by_external_id(self, external_ids, return_ids=False):
        if not external_ids.get('imdb'):
            return False

        theurl = FIND_URL.format(external_ids['imdb'])
        params = TMDB_PARAMS.copy()
        if self.search_language is not None:
            params['language'] = self.search_language
        params['external_source'] = 'imdb_id'

        result = tmdbweb.load_info(theurl, params=params, unblock=self.unblock)

        if 'error' in result:
            return False

        movie_results = result.get('movie_results')
        if movie_results:
            result = movie_results[0]
        
        tv_results = result.get('tv_results')
        if tv_results:
            result = tv_results[0]
        
        if return_ids:
            unique_id = {'imdb': '', 'media_type': '', 'kinopoisk': '', 'tmdb': ''}
            unique_id.update(external_ids)
            unique_id['tmdb'] = result['id']
            if result.get('media_type'):
                unique_id['media_type'] = result['media_type'].replace('tv','series')
            return unique_id

        return result

    def get_details(self, uniqueids):
        content = _get_detail(uniqueids=uniqueids, language=self.language, unblock=self.unblock)

        if not content or content.get('error'):
            return None
        
        content_fallback = _get_detail(uniqueids=uniqueids, unblock=self.unblock)

        content['images'] = content_fallback['images']

        if uniqueids['media_type'] == 'series':
            return _assemble_series(
                series=content,
                series_fallback=content_fallback,
                uniqueids=uniqueids,
                language=self.language
                )
        
        if uniqueids['media_type'] == 'movie':
            return _assemble_movie(
                movie=content,
                movie_fallback=content_fallback,
                uniqueids=uniqueids,
                certification_country = self.certification_country,
                language = self.language
                )
        
        return
    
def _assemble_series(series, series_fallback, uniqueids, language):
    info = {
        'title': series['name'],
        'originaltitle': series['original_name'],
        'plot': series.get('overview') or series_fallback.get('overview'),
        'tagline': series.get('tagline') or series_fallback.get('tagline'),
        'studio': _parse_names(series['production_companies']),
        'genre': _parse_names(series['genres']),
        'country': _parse_names(series['production_countries']),
        'credits': _parse_cast(series['credits'], 'crew', 'Writing', ['Comic Book', 'Characters', 'Staff Writer', 'Story Editor']),
        'director': [],
        'premiered': series['first_air_date'],
        'tag': _parse_names(series['keywords']['results'])
    }

    if series.get('created_by'):
        for node in series.get('created_by'):
            info['director'].append(node['name'])

    if series.get('episode_run_time'):
        duration = series.get('episode_run_time')
        if type(duration) == list:
            try:
                duration = duration[0]
            except:
                duration = 0
        info['duration'] = duration * 60

    trailer = _parse_videos(series.get('videos'), series_fallback.get('videos'))
    if trailer:
        info['trailer'] = trailer

    cast = [{
            'name': actor['name'],
            'role': actor['character'],
            'thumbnail': IMAGE_URL['original'] + actor['profile_path']
                if actor['profile_path'] else "",
            'order': actor['order']
        }
        for actor in series['credits'].get('cast', [])
    ]
    available_art = _parse_artwork(series, IMAGE_URL, language)

    return {'info': info, 'uniqueids': uniqueids, 'cast': cast, 'available_art': available_art}
    
def _assemble_movie(movie, movie_fallback, uniqueids, certification_country, language):
    info = {
        'title': movie['title'],
        'originaltitle': movie['original_title'],
        'plot': movie.get('overview') or movie_fallback.get('overview'),
        'tagline': movie.get('tagline') or movie_fallback.get('tagline'),
        'studio': _parse_names(movie['production_companies']),
        'genre': _parse_names(movie['genres']),
        'country': _parse_names(movie['production_countries']),
        'credits': _parse_cast(movie['casts'], 'crew', 'Writing', ['Screenplay', 'Writer', 'Author']),
        'director': _parse_cast(movie['casts'], 'crew', 'Directing', ['Director']),
        'premiered': movie['release_date'],
        'tag': _parse_names(movie['keywords']['keywords'])
    }

    if 'countries' in movie['releases']:
        certcountry = certification_country.upper()
        for country in movie['releases']['countries']:
            if country['iso_3166_1'] == certcountry and country['certification']:
                info['mpaa'] = country['certification']
                break

    trailer = _parse_trailer(movie.get('trailers', {}), movie_fallback.get('trailers', {}))
    if trailer:
        info['trailer'] = trailer
    if movie.get('runtime'):
        info['duration'] = movie['runtime'] * 60

    cast = [{
            'name': actor['name'],
            'role': actor['character'],
            'thumbnail': IMAGE_URL['original'] + actor['profile_path']
                if actor['profile_path'] else "",
            'order': actor['order']
        }
        for actor in movie['casts'].get('cast', [])
    ]
    available_art = _parse_artwork(movie, IMAGE_URL, language)

    return {'info': info, 'uniqueids': uniqueids, 'cast': cast, 'available_art': available_art}
    
def _get_detail(uniqueids, language=None, unblock=False):
        if language:
            if uniqueids['media_type'] == 'series':
                details = 'images,videos,credits,keywords'
            if uniqueids['media_type'] == 'movie':
                details = 'trailers,images,releases,casts,keywords'
        else:
            if uniqueids['media_type'] == 'series':
                details = 'images,videos'
            if uniqueids['media_type'] == 'movie':
                details = 'trailers,images'
        return _get_movie(uniqueids, language=language, append_to_response=details, unblock=unblock)
    
def _parse_artwork(movie, urlbases, language):
    if language:
        language = language.split('-')[0]
    posters = []
    landscape = []
    logos = []
    fanart = []

    if 'images' in movie:
        posters = _parse_images_fallback(movie['images']['posters'], urlbases, language)
        landscape = _parse_images_fallback(movie['images']['backdrops'], urlbases, language)
        logos = _parse_images_fallback(movie['images']['logos'], urlbases, language)
        fanart = _parse_images(movie['images']['backdrops'], urlbases, None)

    return {'poster': posters, 'landscape': landscape, 'fanart': fanart, 'clearlogo': logos}
    
def _parse_images(imagelist, urlbases, language='_any'):
    result = []
    for img in imagelist:
        if language != '_any' and img['iso_639_1'] != language:
            continue
        if img['file_path'].endswith('.svg'):
            continue
        result.append({
            'url': urlbases['original'] + img['file_path'],
            'preview': urlbases['preview'] + img['file_path'],
            'lang': img['iso_639_1']
        })
    return result

def _parse_images_fallback(imagelist, urlbases, language, language_fallback='en'):
    images = _parse_images(imagelist, urlbases, language)

    if language != language_fallback:
        images.extend(_parse_images(imagelist, urlbases, language_fallback))

    if not images:
        images = _parse_images(imagelist, urlbases)

    return images

def _parse_trailer(trailers, fallback):
    if trailers.get('youtube'):
        return 'plugin://plugin.video.youtube/?action=play_video&videoid='+trailers['youtube'][0]['source']
    if fallback.get('youtube'):
        return 'plugin://plugin.video.youtube/?action=play_video&videoid='+fallback['youtube'][0]['source']
    return None
    
def _parse_videos(videos, videos_fallback):
    if videos.get('results'):
        results = videos.get('results')
        for res in results:
            if res['site'] == 'YouTube':
                trailer_url = 'plugin://plugin.video.youtube/?action=play_video&videoid={}'.format(res['key'])
                return trailer_url
                
    if videos_fallback.get('results'):
        results = videos_fallback.get('results')
        for res in results:
            if res['site'] == 'YouTube':
                trailer_url = 'plugin://plugin.video.youtube/?action=play_video&videoid={}'.format(res['key'])
                return trailer_url
    return None

def _parse_cast(casts, casttype, department, jobs):
    result = []
    if casttype in casts:
        for cast in casts[casttype]:
            if cast['department'] == department and cast['job'] in jobs and cast['name'] not in result:
                result.append(cast['name'])
    return result
    
def _parse_names(items):
    return [item['name'] for item in items] if items else []

def _get_movie(uniqueids, language=None, append_to_response=None, unblock=False):
        tmdb_id = uniqueids.get('tmdb')

        if uniqueids['media_type'] == 'movie':
            theurl = MOVIE_URL.format(tmdb_id)
        elif uniqueids['media_type'] == 'series':
            theurl = SERIES_URL.format(tmdb_id)
        else:
            return False

        params = TMDB_PARAMS.copy()
        if language is not None:
            params['language'] = language
        if append_to_response is not None:
            params['append_to_response'] = append_to_response

        return tmdbweb.load_info(theurl, params=params, unblock=unblock)