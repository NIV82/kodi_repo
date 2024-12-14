# -*- coding: utf-8 -*-
"""MODULE CONTAINS SHEMES"""

main_info = {
    'id': '',
    'mediatype': '',
    'year': 0,
    'title': '',
    'originaltitle': '',
    'sorttitle': '',
    'cover': '',
    'thumb': '',
    'status': '',
    'mpaa': '',
    'plot': '',
    'duration': 0,
    'genre': [],
    'tag': '',
    'members': '',
    'sponsor': '',
    'episodes': [],
    'torrents': [],
    'latest_episode': {}
}

week = {
    'Понедельник': [],
    'Вторник': [],
    'Среда': [],
    'Четверг': [],
    'Пятница': [],
    'Суббота': [],
    'Воскресенье': []
    }

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

publish_genres = {
    '':'', 'Комедия': 1, 'Меха': 2, 'Психологическое': 3, 'Сёнен': 4, 'Сейнен': 5, 
    'Триллер': 6, 'Школа': 7, 'Драма': 8, 'Мистика': 9, 'Повседневность': 10, 
    'Романтика': 11, 'Спорт': 12, 'Ужасы': 13, 'Экшен': 14, 'Боевые искусства': 15, 
    'Демоны': 16, 'Игры': 17, 'Магия': 18, 'Музыка': 19, 'Сёдзе': 20, 
    'Супер сила': 21, 'Фантастика': 22, 'Этти': 23, 'Вампиры': 24, 'Детектив': 25, 
    'Исторический': 26, 'Приключения': 27, 'Сверхъестественное': 28, 
    'Фэнтези': 29, 'Киберпанк': 30, 'Сёдзе-ай': 31, 'Гарем': 32, 'Дзёсей': 33, 
    'Исекай': 34, 'Пародия': 36
    }

publish_types = {
    '':'', 'ТВ': 'TV', 'ОNA': 'ONA', 'WEB': 'WEB', 'OVA': 'OVA',
    'OAD': 'OAD', 'Фильм': 'MOVIE', 'Дорама': 'DORAMA', 'Спешл': 'SPECIAL'
    }

publish_status = {
    '':'', 'Онгоинг': 'IS_ONGOING', 'Неонгоинг': 'IS_NOT_ONGOING'
    }

publish_production_status = {
    '':'', 'Сейчас в озвучке': 'IS_IN_PRODUCTION',
    'Озвучка завершена': 'IS_NOT_IN_PRODUCTION'
    }

publish_sorting = {
    'Обновлены недавно': 'FRESH_AT_DESC', 'Обновлены давно': 'FRESH_AT_ASC', 
    'Самый высокий рейтинг': 'RATING_DESC', 'Самый низкий рейтинг': 'RATING_ASC', 
    'Самые новые': 'YEAR_DESC', 'Самые старые': 'YEAR_ASC'
    }

publish_seasons = {
    '':'', 'Зима': 'winter', 'Весна': 'spring', 'Лето': 'summer', 'Осень': 'autumn'
    }

publish_years = [
    '1990','1996','1998','1999','2001','2003','2004','2005','2006','2007',
    '2008','2009','2010','2011','2012','2013','2014','2015','2016','2017',
    '2018','2019','2020','2021','2022','2023','2024','2025'
    ]

publish_mpaa = {
    '':'', '0+': 'R0_PLUS', '6+': 'R6_PLUS', '12+': 'R12_PLUS', 
    '16+': 'R16_PLUS', '18+': 'R18_PLUS'
    }

torrent_node = {
    'title': '',
    'id':'',
    'hash': '',
    'size': '',
    'magnet': '',
    'codec': '',
    'seeds': ''
    }

episode_node = {
    'title': '',
    'originaltitle': '',
    'ordinal': '',
    'video_url': {'SD': '', 'HD': '', 'FHD': ''},
    'duration': 0
    }

pagination_scheme = {
    'current_page': '', 
    'next_page': '', 
    'total_pages': ''
    }

error_scheme = {
    'label': 'ERROR',
    'params': {
        'path': 'main_part',
        },
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
    'info': main_info.copy()
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
