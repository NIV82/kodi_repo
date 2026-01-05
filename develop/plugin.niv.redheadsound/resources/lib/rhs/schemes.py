# -*- coding: utf-8 -*-
"""MODULE CONTAINS SHEMES"""

info_scheme = {
    'genre': [],#Comedy or ["Comedy", "Animation", "Drama"]
    'country': [],#Germany or ["Germany", "Italy", "France"]
    'year': 0,#2025
    'episode': 0,#4
    'season': 0,#2
    'sortepisode': 0,#4
    'sortseason': 0,#2
    'episodeguide': '',#Episode guide
    'showlink': [],#Caprica or ["Battlestar Galactica", "Caprica"]
    'top250': 0,#249
    'setid': 0,#14
    'tracknumber': 0,#3
    'rating': 0.0,#6.3
    'userrating': 0,#6
    'playcount': 0,#3
    'cast': [],#["Michal C. Hall","Jennifer Carpenter"]
    'castandrole': [],#list of tuples [("Michael C. Hall","Dexter"),]
    'director': [],#Dagur Kari or ["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]
    'mpaa': '',#PG-13
    'plot': '',#Long Description
    'plotoutline': '',#Short Description
    'title': '',#Big Fan
    'originaltitle': '',#Big Fan
    'sorttitle': '',#Big Fan
    'duration': 0,#256 in seconds
    'studio': [],#Warner Bros. or ["Warner Bros.", "Disney", "Paramount"]
    'tagline': '',#An awesome movie - short description of movie
    'writer': [],#Robert D. Siegel or ["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"]
    'tvshowtitle': '',#Heroes
    'premiered': '',#2005-03-04
    'status': '',#Continuing - status of a TVshow
    'set': '',#Batman Collection - name of the collection
    'setoverview': '',#All Batman movies - overview of the collection
    'tag': [],#cult or ["cult", "documentary", "best movies"] - movie tag
    'imdbnumber': '',#tt0110293 - IMDb code
    'code': '',#101 - Production code
    'aired': '',#2008-12-07
    'credits': [],#Andy Kaufman or ["Dagur Kari", "Quentin Tarantino",] - writing credits
    'lastplayed': '',#Y-m-d h:m:s = 2009-04-05 23:16:04
    'album': '',#The Joshua Tree
    'artist': [],#['U2', 'U3']
    'votes': 0,#12345 votes
    'path': '',#/home/user/movie.avi
    'trailer': '',#/home/user/trailer.avi
    'dateadded': '',#Y-m-d h:m:s = 2009-04-05 23:16:04
    'mediatype': 'video',#"video", "movie", "tvshow", "season", "episode" or "musicvideo"
    'dbid': 0,#23
}

# week = {
#     'Понедельник': [],
#     'Вторник': [],
#     'Среда': [],
#     'Четверг': [],
#     'Пятница': [],
#     'Суббота': [],
#     'Воскресенье': []
#     }

# torrent_node = {
#     'title': '',
#     'id':'',
#     'hash': '',
#     'size': '',
#     'magnet': '',
#     'codec': '',
#     'seeds': ''
#     }

# vurl_scheme = {
#     'SD': '',
#     'HD': '',
#     'FHD': ''
#     }

# episode_node = {
#     'title': '',
#     'originaltitle': '',
#     'ordinal': '',
#     'video_url': {},
#     'duration': 0
#     }

# pagination_scheme = {
#     'current_page': '',
#     'next_page': '',
#     'total_pages': ''
#     }

# error_scheme = {
#     'label': 'ERROR',
#     'params': {
#         'path': 'main_part',
#         },
#     }

pagination_scheme = {
    'first_page': 1,
    'current_page': 0,
    'next_page': 0,
    'total_pages': 0
    }

art_scheme = {
    'icon': '',
    'thumb': '',
    'poster': '',
    'banner': '',
    'fanart': '',
    'clearart': '',
    'clearlogo': '',
    'landscape': ''
}

node_scheme = {
    'label': '',
    'params': {},
    'context_menu': [],
    'isFolder': True,
    'setContent': False,
    }
