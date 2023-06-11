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
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from html import unescape
else:
    from urllib import urlopen
    from urllib import urlencode
    from urllib import quote
    from urllib import unquote
    from urlparse import parse_qs
    import HTMLParser
    unescape = HTMLParser.HTMLParser().unescape

shizaproject_season = {'':'','Весна':'SPRING','Лето':'SUMMER','Осень':'FALL','Зима':'WINTER'}
shizaproject_categories = {'':'','Аниме':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzE=','Дорамы':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI=','Мультфильмы':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM=','Разное':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ='}
shizaproject_status = {'':'','Онгоинг':'ONGOING','Выпущено':'RELEASED'}
shizaproject_form = {'':'','ТВ':'TV','ТВ-спешл':'TV_SPECIAL','Фильм':'MOVIE','Короткий Фильм':'SHORT_MOVIE','OVA':'OVA','ONA':'ONA','Музыкальный':'MUSIC','Остальное':'OTHER'}
shizaproject_genre = {'':'','экшен':'R2VucmU6ODM0NDc2MjMxOTY4Njg2MDg=','комедия':'R2VucmU6ODM0NDc4NDQyNDA4ODM3MTI=','драма':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njg=','фантастика':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDE=','сверхъестественное':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTk=','фэнтези':'R2VucmU6ODM0NDgxMzc2MDMwODgzODQ=','романтика':'R2VucmU6ODM0NDc5NTcwNzYwNDk5MjA=','сёнен':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODk=','приключения':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzE=','повседневность':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTY=','сейнен':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMTA=','этти':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzg=','детектив':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDU=','меха':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODQ=','военное':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDQ=','психологическое':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzA=','ужасы':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODI=','исторический':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODE=','сёдзё':'R2VucmU6ODE1OTEzMjc3NTM1MDI3MjA=','спорт':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTA=','музыка':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzI=','триллер':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDA=','игры':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njk=','пародия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODU=','боевые искусства':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDg=','сёдзё-ай':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTc=','дзёсей':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTg='}
shizaproject_direction = {'По убыванию':'DESC','По возрастанию':'ASC'}
shizaproject_sort = {'Дате публикации':'PUBLISHED_AT','Дате обновление':'UPDATED_AT','Просмотрам':'VIEW_COUNT','Названию EN':'ORIGINAL_NAME','Названию RU':'NAME','Рейтингу':'SCORE'}

version = xbmc.getInfoLabel('System.BuildVersion')[:2]
try:
    version = int(version)
except:
    version = 0

try:
    xbmcaddon.Addon('inputstream.adaptive')
except:
    xbmcgui.Dialog().notification(
        heading='Установка Библиотеки - [COLOR=darkorange]inputstream.adaptive[/COLOR]',
        message='inputstream.adaptive',
        icon=None,
        time=3000,
        sound=False
        )
    xbmc.executebuiltin('RunPlugin("plugin://inputstream.adaptive")')

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

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)
    
class Shiza:
    def __init__(self):
        self.progress_bg = xbmcgui.DialogProgressBG()
        self.dialog = xbmcgui.Dialog()

        if not os.path.exists(addon_data_dir):
            os.makedirs(addon_data_dir)

        self.params = {'mode': 'main_part', 'param': '', 'page': '1', 'portal': 'shizaproject'}
        
        args = parse_qs(sys.argv[2][1:])
        for a in args:
            self.params[a] = unquote(args[a][0])

        self.proxy_data = None

        self.site_url = 'https://shiza-project.com/graphql'
        
        self.authorization = False
        
#========================#========================#========================#
        from network import WebTools
        self.network = WebTools(
            proxy_data = self.proxy_data,
            portal='shizaproject')
        del WebTools
#========================#========================#========================#
    def create_post(self):
        import json

        if 'select_part' in self.params['mode']:
            post = {
                "operationName": "fetchRelease",
                "query": "query fetchRelease($slug: String!) {\n  release(slug: $slug) {\n    id\n    slug\n    malId\n    name\n    originalName\n    alternativeNames\n    description\n    descriptionSource\n    descriptionExternal\n    descriptionAuthors {\n      id\n      slug\n      username\n      avatar {\n        ...UserAvatarCommon\n        __typename\n      }\n      __typename\n    }\n    cause\n    announcement\n    season\n    seasonYear\n    seasonNumber\n    episodesCount\n    episodesAired\n    episodeDuration\n    type\n    status\n    activity\n    viewCount\n    score\n    rating\n    origins\n    countries\n    airedOn\n    releasedOn\n    nextEpisodeAt\n    cover {\n      ...ReleaseCoverCommon\n      __typename\n    }\n    posters {\n      ...ReleasePosterCommon\n      __typename\n    }\n    screenshots {\n      ...ReleaseScreenshotCommon\n      __typename\n    }\n    studios {\n      id\n      slug\n      name\n      __typename\n    }\n    categories {\n      id\n      slug\n      name\n      __typename\n    }\n    genres {\n      id\n      slug\n      name\n      __typename\n    }\n    tags {\n      id\n      slug\n      name\n      __typename\n    }\n    staff {\n      ...ReleaseStaffCommon\n      __typename\n    }\n    relations {\n      ...ReleaseRelationCommon\n      __typename\n    }\n    torrents {\n      id\n      synopsis\n      downloaded\n      seeders\n      leechers\n      size\n      metadata\n      videoFormat\n      videoQualities\n      magnetUri\n      updatedAt\n      file {\n        id\n        filesize\n        url\n        __typename\n      }\n      __typename\n    }\n    contributors {\n      ...ReleaseContributorCommon\n      __typename\n    }\n    arches {\n      name\n      range\n      __typename\n    }\n    videos {\n      ...ReleaseVideoCommon\n      __typename\n    }\n    episodes {\n      ...ReleaseEpisodeCommon\n      __typename\n    }\n    links {\n      type\n      url\n      __typename\n    }\n    viewerWatchlist {\n      id\n      status\n      score\n      episodes\n      rewatches\n      __typename\n    }\n    viewerFavorite {\n      id\n      __typename\n    }\n    reactionGroups {\n      count\n      content\n      viewerHasReacted\n      __typename\n    }\n    userWatchlistStatusDistributions {\n      count\n      status\n      __typename\n    }\n    userWatchlistScoreDistributions {\n      count\n      score\n      __typename\n    }\n    viewerInBlockedCountry\n    viewerRestrictedByRole\n    __typename\n  }\n}\n\n\
                    fragment ReleaseContributorCommon on ReleaseContributor {\n  id\n  startOn\n  endOn\n  tasks {\n    type\n    ranges\n    __typename\n  }\n  user {\n    id\n    slug\n    username\n    discriminator\n    verified\n    avatar {\n      ...UserAvatarCommon\n      __typename\n    }\n    roles {\n      id\n      name\n      displayColor\n      __typename\n    }\n    __typename\n  }\n  community {\n    id\n    slug\n    name\n    verified\n    avatar {\n      id\n      preview: resize(width: 192, height: 192) {\n        width\n        height\n        url\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseVideoCommon on VideoFile {\n  id\n  embedSource\n  embedUrl\n  __typename\n}\n\n\
                    fragment ReleaseEpisodeCommon on ReleaseEpisode {\n  id\n  name\n  number\n  duration\n  type\n  subtitle {\n    id\n    filename\n    url\n    __typename\n  }\n  videos {\n    ...ReleaseVideoCommon\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleasePosterCommon on ImageFile {\n  id\n  preview: resize(width: 360, height: 500) {\n    width\n    height\n    url\n    __typename\n  }\n  original {\n    width\n    height\n    url\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseCoverCommon on ImageFile {\n  id\n  original {\n    height\n    width\n    url\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseScreenshotCommon on ImageFile {\n  id\n  original {\n    height\n    width\n    url\n    __typename\n  }\n  preview: resize(width: 200, height: 150) {\n    height\n    width\n    url\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseRelationCommon on ReleaseRelation {\n  id\n  type\n  destination {\n    ...ReleaseCard\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseStaffCommon on ReleaseStaff {\n  id\n  roles\n  person {\n    id\n    slug\n    name\n    originalName\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseCard on Release {\n  id\n  slug\n  name\n  originalName\n  airedOn\n  releasedOn\n  publishedAt\n  announcement\n  episodesCount\n  episodesAired\n  episodeDuration\n  season\n  seasonYear\n  seasonNumber\n  status\n  activity\n  type\n  rating\n  viewCount\n  score\n  posters {\n    ...ReleasePosterCommon\n    __typename\n  }\n  genres {\n    id\n    slug\n    name\n    __typename\n  }\n  viewerWatchlist {\n    id\n    status\n    score\n    episodes\n    rewatches\n    __typename\n  }\n  reactionGroups {\n    count\n    content\n    viewerHasReacted\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment UserAvatarCommon on ImageFile {\n  id\n  preview: resize(width: 192, height: 192) {\n    width\n    height\n    url\n    __typename\n  }\n  __typename\n}",
                "variables": {
                    "slug": self.params['slug']
                }
            }
        else:
            post = {
                "operationName":"fetchReleases",
                "variables":{
                    "first":50,
                    "airedOn":None,
                    "query":"",
                    "after": "", 
                    "orderBy":{"field":"PUBLISHED_AT","direction":"DESC"},
                    "type":{"include":[],"exclude":[]},
                    "status":{"include":[],"exclude":["DRAFT"]},
                    "activity":{"include":[],"exclude":["WISH"]},
                    "rating":{"include":[],"exclude":[]},
                    "season":{"include":[],"exclude":[]},
                    "watchlist":{"include":[],"exclude":[]},
                    "genre":{"include":[],"exclude":[]},
                    "category":{"include":[],"exclude":[]},
                    "tag":{"include":[],"exclude":[]},
                    "studio":{"include":[],"exclude":[]},
                    "staff":{"include":[],"exclude":[]},
                    "contributor":{"include":[],"exclude":[]}
                    },
                "query":"query fetchReleases($first: Int, $after: String, $orderBy: ReleaseOrder, $query: String, $tag: ReleaseIDFilter, $category: ReleaseIDFilter, $genre: ReleaseIDFilter, $studio: ReleaseIDFilter, $type: ReleaseTypeFilter, $status: ReleaseStatusFilter, $rating: ReleaseRatingFilter, $airedOn: ReleaseAiredOnRangeFilter, $activity: ReleaseActivityFilter, $season: ReleaseSeasonFilter, $staff: ReleaseIDFilter, $contributor: ReleaseIDFilter, $watchlist: ReleaseWatchlistFilter, $watchlistUserId: ID) {\n  releases(\n    first: $first\n    after: $after\n    orderBy: $orderBy\n    query: $query\n    tag: $tag\n    category: $category\n    genre: $genre\n    studio: $studio\n    type: $type\n    status: $status\n    airedOn: $airedOn\n    rating: $rating\n    activity: $activity\n    season: $season\n    staff: $staff\n    contributor: $contributor\n    watchlist: $watchlist\n    watchlistUserId: $watchlistUserId\n  ) {\n    totalCount\n    edges {\n      node {\n        ...ReleaseCard\n        viewerWatchlist {\n          id\n          status\n          __typename\n        }\n        reactionGroups {\n          count\n          content\n          viewerHasReacted\n          __typename\n        }\n        viewerInBlockedCountry\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      startCursor\n      endCursor\n      __typename\n    }\n    __typename\n  }\n}\n\n\
                    fragment ReleasePosterCommon on ImageFile {\n  id\n  preview: resize(width: 360, height: 500) {\n    width\n    height\n    url\n    __typename\n  }\n  original {\n    width\n    height\n    url\n    __typename\n  }\n  __typename\n}\n\n\
                    fragment ReleaseCard on Release {\n  id\n  slug\n  name\n  originalName\n  description\n airedOn\n  releasedOn\n  publishedAt\n  announcement\n  episodesCount\n  episodesAired\n  episodeDuration\n  season\n  seasonYear\n  seasonNumber\n  status\n  activity\n  type\n  rating\n  viewCount\n  score\n  posters {\n    ...ReleasePosterCommon\n    __typename\n  }\n  genres {\n    id\n    slug\n    name\n    __typename\n  }\n  viewerWatchlist {\n    id\n    status\n    score\n    episodes\n    rewatches\n    __typename\n  }\n  reactionGroups {\n    count\n    content\n    viewerHasReacted\n    __typename\n  }\n  __typename\n}"}
        
            if 'after' in self.params:
                post['variables']['after'] = self.params['after']

            if 'search_string' in self.params:
                post['variables']['query'] = self.params['search_string']

            if self.params['param'] in ('Аниме','Дорамы','Мультфильмы','Разное'):
                post['variables']['category']['include'] = [shizaproject_categories[self.params['param']]]

        if 'catalog' in self.params['param']:
            post['variables']['airedOn'] = {"startYear":int(addon.getSetting('sp_yearstart')),"endYear":int(addon.getSetting('sp_yearend'))}
            
            if addon.getSetting('sp_season'):
                post['variables']['season']['include'] = shizaproject_season[addon.getSetting('sp_season')]
            if addon.getSetting('sp_categories'):
                post['variables']['category']['include'] = shizaproject_categories[addon.getSetting('sp_categories')]
            if addon.getSetting('sp_status'):
                post['variables']['status']['include'] = shizaproject_status[addon.getSetting('sp_status')]
            if addon.getSetting('sp_form'):
                post['variables']['type']['include'] = shizaproject_form[addon.getSetting('sp_form')]
            if addon.getSetting('sp_genre'):
                post['variables']['genre']['include'] = shizaproject_genre[addon.getSetting('sp_genre')]
            
            post['variables']['orderBy'] = {
                "field":shizaproject_sort[addon.getSetting('sp_sort')],
                "direction":shizaproject_direction[addon.getSetting('sp_direction')]}

        post = json.dumps(post)
        #post_data = str(post_data).replace('\'','"').replace('None','null')

        return post
#========================#========================#========================#
    def create_sibnet(self, url): #Общий функционал заимствован у автора Eviloid - SHIZA Project, переписан под нужды
        from network import get_web

        html = get_web(url, bytes=False)

        #result = {'url':'Видео недоступно', 'thumb':''}
        episode_url = ''
        try:
            #s = re.search(r'<div class=videostatus><p>(.*?)</p>', html)
            if '<div class=videostatus><p>' in html:
                s = html[html.find('<div class=videostatus><p>')+26:]
                s = s[:s.find('</p>')]


            # if s:
            #     result['url'] = s.group(1).decode('cp1251')

            elif '{src: "' in html:
                s = html[html.find('{src: "')+7:]
                s = s[:s.find('"')]

                episode_url = u'https://video.sibnet.ru{}|referer={}'.format(s,url)

                # thumb = ''
                # if 'meta property="og:image" content="' in html:
                #     thumb = html[html.find('meta property="og:image" content="')+34:]
                #     thumb = thumb[:thumb.find('"')]
                #     thumb = u'https:{}'.format(thumb)

        except:
            pass

        return episode_url
#========================#========================#========================#
    def create_kodik(self, url): #Общий функционал заимствован у автора Eviloid - SHIZA Project, переписан под нужды
        from network import get_web
        import json

        def decode_kodik(url):
            keys   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            result = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789'

            from base64 import standard_b64decode

            return standard_b64decode(''.join(result[keys.index(k)] for k in url) + '===').decode('utf-8')

        result = {'360':'', '480':'', '720':''}

        try:
            html = get_web(url=url, bytes=False)

            url = html[html.find("data-code='//")+13:]
            url = url[:url.find("'")].split('/')

            new_url = 'https://{}/gvi'.format(url[0])
            payload = {'type': url[1], 'id': url[2], 'hash': url[3]}
            payload = urlencode(payload)

            html = get_web(url=new_url, post=payload)

            data = json.loads(html)

            links = data['links']
            
            for r in list(result.keys()):
                result[r] = u'https:{}'.format(decode_kodik(links[r][0]['src']))

        except:
            pass

        return result
#========================#========================#========================#
    def create_info(self, data):
        from utility import clean_tags
        info = {
            'slug': '',
            'sorttitle': '',
            'title': '',
            'plot': '',
            'premiered': '',
            'mpaa': '',
            'rating': 0,
            'cover': '',
            'genre': [],
            'country': [],
            'director': [],
            'studio': []
            }
        
        info['slug'] = u'{}'.format(data['slug'])
        info['sorttitle'] = u'{}'.format(data['name'])

        episodes = ''
        if 'episodesAired' in list(data.keys()):
            if data['episodesAired']:
                episodes = u' | [COLOR=gold]{}[/COLOR]'.format(data['episodesAired'])

                if 'episodesCount' in list(data.keys()):
                    if episodes and data['episodesCount']:
                        episodes = u'{} [COLOR=gold]из {}[/COLOR]'.format(episodes, data['episodesCount'])

        info['title'] = u'{}{}'.format(data['name'], episodes)

        if 'posters' in list(data.keys()):
            if data['posters']:
                poster = []
                for p in data['posters']:
                    poster.append(p['original']['url'])
                info['cover'] = poster[0]

        if 'description' in list(data.keys()):
            if data['description']:
                plot = clean_tags(data['description'])
                plot = clean_tags(data['description'], tag_start='[', tag_end=']')
                info['plot'] = u'{}\n'.format(plot)

        if 'airedOn' in list(data.keys()):
            if data['airedOn']:
                info['premiered'] = u'{}'.format(data['airedOn'])
        
        if 'rating' in list(data.keys()):
            if data['rating']:
                info['mpaa'] = u'{}'.format(data['rating'])

        if 'score' in list(data.keys()):
            if data['score']:
                info['rating'] = float(data['score'])

        if 'countries' in list(data.keys()):
            if data['countries']:
                info['country'] = data['countries']

        if 'genres' in list(data.keys()):
            if data['genres']:
                genre = []
                for gen in data['genres']:
                    genre.append(u'{}'.format(gen['name']))
                info['genre'] = genre

        if 'studios' in list(data.keys()):
            if data['studios']:
                studios = []
                for s in data['studios']:
                    studios.append(s['name'])
                info['studio'] = studios

        if 'staff' in list(data.keys()):            
            if data['staff']:
                directors = []
                for d in data['staff']:
                    directors.append(d['person']['name'])
                info['director'] = directors

        if 'contributors' in list(data.keys()):
            if data['contributors']:
                contributors = {
                    'MALE_VOICE_ACTING': [],
                    'FEMALE_VOICE_ACTING': [],
                    'EDITING': [],
                    'MASTERING': [],
                    'TIMING': [],
                    'TRANSLATION': [],
                    'OTHER': []
                    }
                
                for con in data['contributors']:
                    username = con['user']['username']
                    for t in con['tasks']:
                        task_type = t['type']                                                
                        if task_type in list(contributors.keys()):
                            contributors[task_type].append(username)
                        else:
                            contributors['OTHER'].append(username)

                con_name = {
                    'MALE_VOICE_ACTING': 'Озвучивание мужских ролей: ',
                    'FEMALE_VOICE_ACTING': 'Озвучивание женских ролей: ',
                    'EDITING': 'Редактура: ',
                    'MASTERING': 'Работа со звуком: ',
                    'TIMING': 'Работа над таймингом: ',
                    'TRANSLATION': 'Перевод: ',
                    'OTHER': 'Другое: '
                    }
                
                if info['plot']:
                    for cont in contributors:
                        if contributors[cont]:
                            normal_name = con_name[cont]
                            node = u'\n{}{}'.format(normal_name, ', '.join(contributors[cont]))
                            info['plot'] = u'{}{}'.format(info['plot'], node)

        return info
#========================#========================#========================#
    # def create_context(self, anime_id):
    #     context_menu = []
    #     if 'search_part' in self.params['mode'] and self.params['param'] == '':
    #         context_menu.append(('[COLOR=red]Очистить историю[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=clean_part&portal=shizaproject")'))

    #     if 'common_part' in self.params['mode'] or 'favorites_part' in self.params['mode'] or 'search_part' in self.params['mode'] and not self.params['param'] == '':
    #         context_menu.append((u'[COLOR=white]Обновить аниме[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_anime_part&id={}&portal=shizaproject")'.format(anime_id)))
            
    #     context_menu.append(('[COLOR=lime]Новости обновлений[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=information_part&param=news&portal=shizaproject")'))
    #     context_menu.append(('[COLOR=darkorange]Обновить Базу Данных[/COLOR]', 'Container.Update("plugin://plugin.niv.animeportal/?mode=update_file_part&portal=shizaproject")'))

    #     return context_menu
#========================#========================#========================#
    def create_line(self, title, anime_id=None, params={}, folder=True, **info):
        li = xbmcgui.ListItem(title)

        if info:
            try:
                cover = info.pop('cover')
            except:
                cover = None

            try:
                info['title'] = info['sorttitle']
            except:
                pass

            li.setArt({'icon': cover, 'thumb': cover, 'poster': cover})

            if version == 20:
                videoinfo = li.getVideoInfoTag()
                videoinfo.setTitle(info['title'])
                videoinfo.setSortTitle(info['sorttitle'])
                videoinfo.setPremiered(info['premiered'])
                videoinfo.setGenres(info['genre'])
                videoinfo.setMpaa(info['mpaa'])
                videoinfo.setRating(info['rating'])
                videoinfo.setPlot(info['plot'])

                videoinfo.setCountries(info['country'])
                videoinfo.setDirectors(info['director'])
                videoinfo.setStudios(info['studio'])
            else:
                li.setInfo(type='video', infoLabels=info)
            #li.setInfo(type='video', infoLabels=info)
        #li.addContextMenuItems(self.create_context(anime_id))

        if folder==False:
            li.setProperty('isPlayable', 'true')

        params['portal'] = self.params['portal']
        
        if 'tam' in params:
            from urllib.parse import quote_plus
            info = quote_plus(repr(info))
            url='plugin://plugin.video.tam/?mode=open&info={}&url={}'.format(info, quote(params['tam']))
            #url='plugin://plugin.video.tam/?mode=open&url={}'.format(quote(params['tam']))
        else:
            url = '{}?{}'.format(sys.argv[0], urlencode(params))

        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
#========================#========================#========================#
    def execute(self):
        getattr(self, 'exec_{}'.format(self.params['mode']))()
#========================#========================#========================#
    def exec_clean_part(self):
        try:
            addon.setSetting('sp_search', '')
            self.dialog.notification(heading='Поиск',message='Выполнено',icon=icon,time=1000,sound=False)
        except:
            self.dialog.notification(heading='Поиск',message='Ошибка',icon=icon,time=1000,sound=False)
            pass
#========================#========================#========================#
    # def exec_information_part(self):
    #     data = u'[B][COLOR=darkorange]V-1.0.1[/COLOR][/B]\n\
    # - Исправлены метки просмотренного в торрента файлах'
    #     self.dialog.textviewer('Информация', data)
    #     return
#========================#========================#========================#
    def exec_main_part(self):
        self.create_line(title='[B]Поиск[/B]', params={'mode': 'search_part'})
        self.create_line(title='[B]Все Релизы[/B]', params={'mode': 'common_part'})
        self.create_line(title='[B]Аниме[/B]', params={'mode': 'common_part', 'param': 'Аниме'})
        self.create_line(title='[B]Дорамы[/B]', params={'mode': 'common_part', 'param': 'Дорамы'})
        self.create_line(title='[B]Мультфильмы[/B]', params={'mode': 'common_part', 'param': 'Мультфильмы'})
        self.create_line(title='[B]Кино и ТВ[/B]', params={'mode': 'common_part', 'param': 'Разное'})
        self.create_line(title='[B]Каталог[/B]', params={'mode': 'catalog_part'})
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
#========================#========================#========================#
    def exec_search_part(self):
        if not self.params['param']:
            self.create_line(title=u'[B]Поиск по названию[/B]', params={'mode': 'search_part', 'param': 'search_word'})

            data_array = addon.getSetting('sp_search').split('|')
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
                data_array = addon.getSetting('sp_search').split('|')
                while len(data_array) >= 6:
                    data_array.pop(0)
                data_array.append(self.params['search_string'])
                addon.setSetting('sp_search', '|'.join(data_array))
                self.params['param'] = 'search_string'
            else:
                return False
            
        if 'search_string' in self.params['param']:
            if not self.params['search_string']:
                return False

            post_data = self.create_post()
            html = self.network.get_bytes(url = self.site_url, post=post_data)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            import json
            anime_data = json.loads(html)

            if not anime_data['data']['releases']['edges']:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            array = anime_data['data']['releases']['edges']

            if len(array) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            try:
                for data in array:
                    data = data['node']

                    try:
                        info = self.create_info(data)
                        label = info.pop('title')
                        slug = info.pop('slug')

                        self.create_line(title=label, params={'mode': 'select_part', 'slug': slug}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

            if anime_data['data']['releases']['pageInfo']['hasNextPage']:
                after = anime_data['data']['releases']['pageInfo']['endCursor']

                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)            
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'after': after, 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_common_part(self):
        post_data = self.create_post()
        html = self.network.get_bytes(url = self.site_url, post=post_data)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        import json
        anime_data = json.loads(html)

        if not anime_data['data']['releases']['edges']:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        array = anime_data['data']['releases']['edges']

        if len(array) < 1:
            self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        try:
            for data in array:
                data = data['node']

                try:
                    info = self.create_info(data)
                    label = info.pop('title')
                    slug = info.pop('slug')

                    self.create_line(title=label, params={'mode': 'select_part', 'slug': slug}, **info)
                except:
                    self.create_line(title='Ошибка строки - сообщите автору')
        except:
            self.create_line(title='Ошибка блока - сообщите автору')

        if anime_data['data']['releases']['pageInfo']['hasNextPage']:
            after = anime_data['data']['releases']['pageInfo']['endCursor']

            label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)            
            self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'after': after, 'page': (int(self.params['page']) + 1)})

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_select_part(self):
        post_data = self.create_post()
        html = self.network.get_bytes(url = self.site_url, post=post_data)

        if not html:
            self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
            return
        
        import json
        anime_data = json.loads(html)

        data = anime_data['data']['release']

        torrents = data.pop('torrents')
        episodes = data.pop('episodes')

        info = self.create_info(data)
        info.pop('title')
        info.pop('slug')

        if '0' in addon.getSetting('sp_playmode'):
            if len(episodes) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            for ep in episodes:
                if ep['name']:
                    label = u'{} - {}'.format(ep['number'], ep['name'])
                else:
                    label = u'{} - Серия {}'.format(ep['number'], ep['number'])
                
                episodes = {'KODIK': '', 'SIBNET': ''}

                if ep['videos']:
                    for e in ep['videos']:
                        source = e['embedSource']
                        source_url = e['embedUrl']

                        episodes[source] = source_url

                current_select = addon.getSetting('sp_playerselect')

                if episodes[current_select]:
                    episode_url = episodes[current_select]
                elif episodes['KODIK']:
                    episode_url = episodes['KODIK']
                    label = u'{} | KODIK'.format(label)
                elif episodes['SIBNET']:
                    episode_url = episodes['SIBNET']
                    label = u'{} | SIBNET'.format(label)
                else:
                    continue

                self.create_line(title=label, params={'mode': 'play_part', 'param': episode_url}, folder=False, **info)

        if '1' in addon.getSetting('sp_playmode'):
            if len(torrents) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return

            try:
                for t in torrents:
                    try:
                        seeders = t['seeders']
                        leechers = t['leechers']
                        videoformat = t['videoFormat']

                        torrent_size = t['size']
                        torrent_quality = t['videoQualities'][0]

                        torrent_url = t['file']['url']
                        if '?filename=' in torrent_url:
                            torrent_url = torrent_url[:torrent_url.find('?filename=')]
                        #magnet_url = t['magnetUri']

                        label = u'{} - {} | S{} - L{}'.format(torrent_quality, videoformat, seeders, leechers)
                        
                        self.create_line(title=label, params={'tam': torrent_url}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        return
#========================#========================#========================#
    def exec_play_part(self):
        url = self.params['param']

        if 'sibnet.ru' in url:
            data = self.create_sibnet(url)
        elif 'vk.com' in url:
            data_print('*** NODE - VK URL')
            #data = ''#_parse_vk(url)
        elif 'myvi.ru' in url:
            data_print('*** NODE - MUVI URL')
            #data = ''#_parse_myvi(url)
        elif 'aniqit' or 'kodik' or 'anivod' in url:
            data = self.create_kodik(url)

        if 'KODIK' in addon.getSetting('sp_playerselect'):
            if data['720']:
                episode_hls = data['720']
            elif data['480']:
                episode_hls = data['480']
            elif data['360']:
                episode_hls = data['360']
            else:
                self.dialog.notification(heading='Получение Адреса', message='Ошибка получения ссылки', icon=icon, time=1000, sound=False)
                return

            li = xbmcgui.ListItem(path=episode_hls)
        else:
            li = xbmcgui.ListItem(path=data)

        # if '0' in addon.getSetting('sp_inputstream'):
        #     li.setProperty('inputstream', "inputstream.adaptive")
        #     li.setProperty('inputstream.adaptive.manifest_type', 'hls')
        #     li.setProperty('inputstream.adaptive.stream_selection_type', 'adaptive')
        #     li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
        #     li.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
        return
#========================#========================#========================#
    def exec_catalog_part(self):
        shizaproject_year = ['{}'.format(year) for year in range(1970,2024)]

        if not self.params['param']:
            self.create_line(title='Год (начало отрезка): [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_yearstart')), params={'mode': 'catalog_part', 'param': 'sp_yearstart'})
            self.create_line(title='Год (конец отрезка): [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_yearend')), params={'mode': 'catalog_part', 'param': 'sp_yearend'})  
            self.create_line(title='Сезон: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_season')), params={'mode': 'catalog_part', 'param': 'sp_season'})            
            self.create_line(title='Категория: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_categories')), params={'mode': 'catalog_part', 'param': 'sp_categories'})
            self.create_line(title='Статус тайтла: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_status')), params={'mode': 'catalog_part', 'param': 'sp_status'})
            self.create_line(title='Тип: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_form')), params={'mode': 'catalog_part', 'param': 'sp_form'})
            self.create_line(title='Жанр: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_genre')), params={'mode': 'catalog_part', 'param': 'sp_genre'})
            self.create_line(title='Сортировка по: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_sort')), params={'mode': 'catalog_part', 'param': 'sp_sort'})
            self.create_line(title='Направление сортировки: [COLOR=gold]{}[/COLOR]'.format(
                addon.getSetting('sp_direction')), params={'mode': 'catalog_part', 'param': 'sp_direction'})

            self.create_line(title='[COLOR=gold][ Поиск ][/COLOR]', params={'mode': 'catalog_part', 'param':'catalog'})
            
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)  
            return          
        
        if 'sp_yearstart' in self.params['param']:
            result = self.dialog.select('Начало отрезка:', tuple(shizaproject_year))
            addon.setSetting(id='sp_yearstart', value=tuple(shizaproject_year)[result])        
        if 'sp_yearend' in self.params['param']:
            result = self.dialog.select('Конец отрезка:', tuple(shizaproject_year))
            addon.setSetting(id='sp_yearend', value=tuple(shizaproject_year)[result])
        if 'sp_season' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_season.keys()))
            addon.setSetting(id='sp_season', value=tuple(shizaproject_season.keys())[result])
        if 'sp_categories' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_categories.keys()))
            addon.setSetting(id='sp_categories', value=tuple(shizaproject_categories.keys())[result])
        if 'sp_status' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_status.keys()))
            addon.setSetting(id='sp_status', value=tuple(shizaproject_status.keys())[result])
        if 'sp_form' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_form.keys()))
            addon.setSetting(id='sp_form', value=tuple(shizaproject_form.keys())[result])
        if 'sp_genre' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_genre.keys()))
            addon.setSetting(id='sp_genre', value=tuple(shizaproject_genre.keys())[result])
        if 'sp_sort' in self.params['param']:
            result = self.dialog.select('Сортировка по:', tuple(shizaproject_sort.keys()))
            addon.setSetting(id='sp_sort', value=tuple(shizaproject_sort.keys())[result])        
        if 'sp_direction' in self.params['param']:
            result = self.dialog.select('Направление сортировки:', tuple(shizaproject_direction.keys()))
            addon.setSetting(id='sp_direction', value=tuple(shizaproject_direction.keys())[result])
        
        if 'catalog' in self.params['param']:
            post_data = self.create_post()
            html = self.network.get_bytes(url = self.site_url, post=post_data)

            if not html:
                self.create_line(title='Ошибка получения данных', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            import json
            anime_data = json.loads(html)

            if not anime_data['data']['releases']['edges']:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            array = anime_data['data']['releases']['edges']

            if len(array) < 1:
                self.create_line(title='Контент отсутствует', params={'mode': 'main_part'})
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
                return
            
            try:
                for data in array:
                    data = data['node']

                    try:
                        info = self.create_info(data)
                        label = info.pop('title')
                        slug = info.pop('slug')

                        self.create_line(title=label, params={'mode': 'select_part', 'slug': slug}, **info)
                    except:
                        self.create_line(title='Ошибка строки - сообщите автору')
            except:
                self.create_line(title='Ошибка блока - сообщите автору')

            if anime_data['data']['releases']['pageInfo']['hasNextPage']:
                after = anime_data['data']['releases']['pageInfo']['endCursor']

                label = '[COLOR=gold]{:>02}[/COLOR] | Следующая страница - [COLOR=gold]{:>02}[/COLOR]'.format(int(self.params['page']), int(self.params['page'])+1)            
                self.create_line(title=label, params={'mode': self.params['mode'], 'param': self.params['param'], 'after': after, 'page': (int(self.params['page']) + 1)})

            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)            
            return
    
def start():
    shiza = Shiza()
    shiza.execute()
    del shiza