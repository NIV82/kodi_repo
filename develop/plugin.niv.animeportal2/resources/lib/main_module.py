# -*- coding: utf-8 -*-

def create_main_nodes(portal):
    if 'animeportal' in portal:
        data_array = (
            ('ANIDUB', {'portal': 'anidub'}),
            ('ANILIBRIA', {'portal': 'anilibria'}),
            ('ANIMEDIA', {'portal': 'animedia'}),
            ('ANISTAR', {'portal': 'anistar'}),
            ('SHIZAPROJECT', {'portal': 'shizaproject'})
            )
    
    if 'anidub' in portal:
        data_array = (
            ('Поиск', {'mode': 'search_part', 'portal': 'anidub'}),
            ('Избранное', {'mode': 'favorites_part', 'portal': 'anidub'}),
            ('Аниме', {'mode': 'common_part', 'param': 'anime/', 'portal': 'anidub'}),
            ('Онгоинги', {'mode': 'common_part', 'param': 'anime/anime_ongoing/', 'portal': 'anidub'}),
            ('Вышедшие сериалы', {'mode': 'common_part', 'param': 'anime/full/', 'portal': 'anidub'}),
            ('Аниме фильмы', {'mode': 'common_part', 'param': 'anime_movie/', 'portal': 'anidub'}),
            ('Аниме OVA', {'mode': 'common_part', 'param': 'anime_ova/', 'portal': 'anidub'}),
            ('Дорамы', {'mode': 'common_part', 'param': 'dorama/', 'portal': 'anidub'})
            )

    if 'anilibria' in portal:
        data_array = (
            ('Избранное', {'mode': 'common_part', 'param': 'favorites', 'portal': 'anilibria'}),
            ('Поиск', {'mode': 'search_part', 'portal': 'anilibria'}),
            ('Расписание', {'mode': 'schedule_part', 'portal': 'anilibria'}),
            ('Новое', {'mode': 'common_part', 'param': 'updated', 'portal': 'anilibria'}),
            ('Популярное', {'mode': 'common_part', 'param': 'popular', 'portal': 'anilibria'}),
            ('Каталог', {'mode': 'catalog_part', 'portal': 'anilibria'})
            )

    if 'animedia' in portal:
        data_array = (
            ('Поиск', {'mode': 'search_part', 'portal': 'animedia'}),
            ('Анонсы', {'mode': 'common_part', 'param': 'announcements', 'portal': 'animedia'}),
            ('ТОП-100', {'mode': 'common_part', 'param': 'top-100-anime', 'portal': 'animedia'}),
            ('Популярное', {'mode': 'common_part', 'param': 'populyarnye-anime-nedeli', 'portal': 'animedia'}),
            ('Новинки', {'mode': 'common_part', 'param': 'novinki-anime', 'portal': 'animedia'}),
            ('Завершенные', {'mode': 'common_part', 'param': 'completed', 'portal': 'animedia'}),
            ('Каталог', {'mode': 'catalog_part', 'portal': 'animedia'})
            )

    if 'anistar' in portal:
        data_array = (
            ('Избранное', {'mode': 'common_part', 'param': 'favorites/', 'portal': 'anistar'}),
            ('Поиск', {'mode': 'search_part', 'portal': 'anistar'}),
            ('Расписание', {'mode': 'schedule_part', 'portal': 'anistar'}),
            ('Категории', {'mode': 'categories_part', 'portal': 'anistar'}),
            ('Новинки', {'mode': 'common_part', 'param': 'new/', 'portal': 'anistar'}),
            ('RPG', {'mode': 'common_part', 'param': 'rpg/', 'portal': 'anistar'}),
            ('Скоро', {'mode': 'common_part', 'param': 'next/', 'portal': 'anistar'}),
            ('Хентай', {'mode': 'common_part', 'param': 'hentai/', 'portal': 'anistar'}),
            ('Дорамы', {'mode': 'common_part', 'param': 'dorams/', 'portal': 'anistar'}),
            ('Мультфильмы', {'mode': 'common_part', 'param': 'cartoons/', 'portal': 'anistar'})
            )

    if 'shizaproject' in portal:
        data_array = (
            ('Поиск', {'mode': 'search_part', 'portal': 'shizaproject'}),
            #('Аниме', {'mode': 'anime_part', 'portal': 'shizaproject'}),
            ('Скоро на сайте', {'mode': 'common_part', 'param': 'WISH', 'portal': 'shizaproject'}),
            ('Онгоинги', {'mode': 'common_part', 'param': 'ONGOING', 'portal': 'shizaproject'}),
            ('Завершенные', {'mode': 'common_part', 'param': 'COMPLETED', 'portal': 'shizaproject'}),
            ('Дорамы', {'mode': 'common_part', 'param': 'Дорамы', 'portal': 'shizaproject'}),
            ('Мультфильмы', {'mode': 'common_part', 'param': 'Мультфильмы', 'portal': 'shizaproject'}),
            ('Кино и ТВ', {'mode': 'common_part', 'param': 'Разное', 'portal': 'shizaproject'}),
            ('Каталог', {'mode': 'catalog_part', 'portal': 'shizaproject'})
            )

    return data_array