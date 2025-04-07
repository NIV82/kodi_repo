# -*- coding: utf-8 -*-
"""MODULE CONTAINS SHEMES"""

info_scheme = {
    'title': '',
    'year': 0,
    'country': '',
    'genre': [],
    'writer': [],
    'director': [],
    'studio': [],
    'dubber': [],
    'translater': [],
    'plot': '',
    'cover': '',
    'originaltitle': '',
    'sorttitle': '',
    'thumb': '',
}

quality_sheme = {
    #'sd': '480p',
    'sd' : '640p',
    #'hd': '720p',
    'fhd': '1080p',
    #'2k': '2K',
    #'2k': '1440p',
    #'4k': '4K'
}

post_scheme = {
    'do': 'search',
    'subaction': 'search',
    'search_start': '',
    'full_search': '0',
    'result_from': '1',
    'story': ''
    }

node_scheme = {
    'label': '',
    'params': {},
    'icon': '',
    'thumb': '',
    'poster': '',
    'context_menu': [],
    'isFolder': True,
    'setContent': False,
    'info': info_scheme.copy()
    }


error_scheme = {
    'label': 'ERROR',
    'params': {
        'path': 'main_part',
        },
    }

title_scheme = {
    'ru': '', 
    'en':'', 
    'ep': ''
    }

paginator_scheme = {
    'cp': 1,
    'np': 0,
    'tp': 0
    }

playlists_scheme = {
    'main': [],
    'sibnet': []
    }

translit_scheme = {
    'ya': 'я',
    'ts': 'ц',
    'ch': 'ч',
    'sh': 'ш',
    'sch': 'щ',
    '@y': 'ъ',
    '@u': 'ы',
    '@i': 'ь',
    '@e': 'э',
    'yu': 'ю',
    'yo': 'ё',
    'zh': 'ж',
    'a': 'а',
    'b': 'б',
    'v': 'в',
    'g': 'г',
    'd': 'д',
    'e': 'е',
    'z': 'з',
    'i': 'и',
    'y': 'й',
    'k': 'к',
    'l': 'л',
    'm': 'м',
    'n': 'н',
    'o': 'о',
    'p': 'п',
    'r': 'р',
    's': 'с',
    't': 'т',
    'u': 'у',
    'f': 'ф',
    'h': 'х'
    }
