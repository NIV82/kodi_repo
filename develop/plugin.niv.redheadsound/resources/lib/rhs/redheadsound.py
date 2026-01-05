#from typing import Optional
from rhs.constant import *
from rhs.schemes import *
from rhs.network import BaseClient
#from rhs import kinescope
from bs4 import BeautifulSoup

class RHSAPI:
    """
    Класс парсер для извлечения данных с сайта RedHeadSound.
            
    Параметры:
    - base_url (str): url для передачи зеркала сайта в парсер.
    - info_switch (bool): переключатель добавляющий info dict к выдаче
    - art_switch (bool): переключатель добавляющий art dict к выдаче
    """

    def __init__(self, base_url: str = None, info_switch: bool = True, art_switch: bool = True):
        self.site_url = base_url or REDHEADSOUND_BASEURL
        self.info_switch = info_switch
        self.art_switch = art_switch
        self.net = BaseClient()

    def menu_assemble(self, data: dict = None) -> dict:
        """
        Функция для формирования пунктов меню.

        Параметры:
        - data (dict): содержит словарь соответствующий полностью или частично node_scheme из schemes
        """
        if not data:
            error = {'label': 'Ошибка формирования списка', 'params': {'path': 'main'}}
            data = _node_assemble(item=error)

        arts = data.get('arts')
        info = data.get('info')

        row = _node_assemble(data)

        if arts:
            arts = _arts_assemble(item=arts)
            row['arts'] = arts

        if info:
            info = _info_assemble(item=info)
            row['info'] = info

        return row
        
    def search(self, query: str):
        """
        Search section implementation
        """

        user_hash = self._userhash()
        if 'ER' in user_hash:
            return {'Ошибка': user_hash['ER']}

        current_url = f"{self.site_url}/engine/ajax/controller.php?mod=search"
        post_data = {
            'query': query,
            'skin': 'rhs_new',
            'user_hash': user_hash['OK']
        }

        response = self.net.client_post(url=current_url, data=post_data)
        if isinstance(response, dict):
            if 'error' in response:
                return {'Ошибка получения данных': response['error']}

        html = response.content
        soup = BeautifulSoup(html, "html.parser")

        nodes = {'data': [], 'pagination': {}}

        data_array = soup.find_all(class_="move-item")
        for data in data_array:

            cover = data.a.img.get('src').strip()

            rating = data.a.find('span').text.strip()
            rating = _rating_assemble(raw_rating=rating)

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.text
            url = row_content.h4.a.get('href')
            year = row_content.span.text
            mode = data.find(class_='flex').a.text

            row = _node_assemble({
                'label': title,
                'params': {
                    'path': 'select',
                    'src': url,
                    },
            })

            if self.info_switch:
                info = _info_assemble({
                    'title': title,
                    'rating': rating,
                    'mediatype': mode,
                    'genre': [],
                    'year': int(year)
                    })
                row['info'] = info

            if self.art_switch:
                arts = _arts_assemble({
                    'poster': cover,
                })
                row['arts'] = arts

            nodes['data'].append(row)

        return nodes

    def parser(self, section: str = None, page: int = 1) -> dict:
        """
        Основной парсер для всех разделов сайта.
            
        Параметры:
        - section (str): раздел сайта, в том числе и из каталога.
        - page (int, str): номер страницы.
        """

        page_node = ''
        if int(page) > 1:
            page_node = f"/page/{page}/"

        current_url = f"{self.site_url}"
        if section:
            current_url = f"{self.site_url}/{section}{page_node}"

        response = self.net.client_get(url=current_url)
        if isinstance(response, dict):
            if 'error' in response:
                return {'Ошибка получения данных': response['error']}

        html = response.content
            
        soup = BeautifulSoup(html, "html.parser")

        nodes = {'data': [], 'pagination': {}}

        pages = soup.find(class_='navigate-pages flex justify-center align-center gap-12')
        if pages:
            current_page = pages.find('span').get_text(strip=True)
            last_page = pages.find_all('a')
            last_page = [lp.text for lp in last_page][-1]

            nodes['pagination'] = _pages_assemble(cp=current_page, lp=last_page)

        movies = soup.find(class_="movies__list")
        data_array = movies.find_all(class_='move-item')

        data_array = movies.find_all(class_='move-item')
        for data in data_array:

            row_item = data.find(class_='move-item__img')
            image = row_item.img.get('src').strip()
            if not image.startswith('http'):
                image = f"{self.site_url}{image}"

            rating = row_item.find('span').get_text(strip=True)
            rating = _rating_assemble(raw_rating=rating)

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.a.get_text(strip=True)
            url = row_content.h4.a.get('href').strip()

            genre = row_content.find('div', {'class': 'flex change_classes'}).find_all('a')
            genre = [g.text for g in genre]
            year = genre.pop()

            row = _node_assemble({
                'label': title,
                'params': {
                    'path': 'select',
                    'src': url,
                    },
            })

            if self.info_switch:
                info = _info_assemble({
                    'title': title,
                    'rating': rating,
                    'genre': genre,
                    'year': int(year),
                })
                row['info'] = info

            if self.art_switch:
                arts = _arts_assemble({
                    'poster': image,
                })
                row['arts'] = arts

            nodes['data'].append(row)

        return nodes

    def select(self, url):
        """
        Open content page section implementation
        """
        current_url = url

        response = self.net.client_get(url=current_url)
        if isinstance(response, dict):
            if 'error' in response:
                return {'Ошибка получения данных': response['error']}

        html = response.content

        soup = BeautifulSoup(html, "html.parser")

        nodes = []

        genre = soup.find(class_='movie-genere flex wrap').find_all('a')
        genre = [g.get_text(strip=True) for g in genre]

        plot = soup.find('div', {'class': 'modal', 'id': 'description-modal'})
        plot = plot.find_all('p')
        # plot = [desc.p.text for desc in plot if desc.p]
        # if len(plot) > 0:
        #     plot = plot[0].strip()

        description = ''

        for p in plot:
            if not p.text:
                continue
            p = p.text.strip()
            if p not in description:
                description = f'{description}{p}\n'

        plot = description
        
        data_array = soup.find(class_='fullstory-main-page')

        cover = data_array.find(class_='movies-detail__left').img.get('src')
        title = data_array.h1.text

        spans = data_array.find(class_='movie-relize flex gap-32 align-center')
        spans = spans.find_all('span')
        if len(spans) > 3:
            spans.pop(2)
        year, mode, season = [g.text.strip() for g in spans]

        rating = data_array.find(class_='movies-detail__rating').find_all('span')
        rating = _rating_assemble(raw_rating=rating)

        edt = data_array.find(class_='flex direction-column gap-24')
        country = data_array.find(class_='movie_country').get_text(strip=True)
        country = [c.strip() for c in country.split(',')]

        edt = edt.find_all(class_='color-gray-100')
        otitle, mpaa, *other  = [e.text for e in edt]

        contrib = data_array.find(class_='movies-detail__contributors')
        contrib = contrib.find_all(class_='color-gray-100')

        contribution = []
        for c in contrib:
            if c.span in c:
                c = c.span
            contribution.append(c.text)

        studio, quality, dub, *serial_data = contribution

        actor_data = []
        actors = data_array.find(class_='actors-list__grid').find_all(class_='actor-item')
        for actor in actors:
            img = actor.a.img.get('src')
            url = actor.a.get('href')
            name_ru = actor.h4.text
            name_en = actor.span.text
            actor_data.append(
                {
                    'name_ru': name_ru,
                    'name_en': name_en,
                    'cover': f"{self.site_url}{img}",
                    'href': url
                    }
            )

        trailer_url = ''
        if html.find(b'var trailerUrl =') > -1:
            trailer_url = html[html.find(b"var trailerUrl = '")+18:]
            trailer_url = trailer_url[:trailer_url.find(b"'")].decode('utf-8')

        video_url = ''
        if html.find(b'var videoUrl =') > -1:
            video_url = html[html.find(b"var videoUrl = '")+16:]
            video_url = video_url[:video_url.find(b"'")].decode('utf-8')

        seasons = []
        seasons_data = soup.find(class_='swiper seazons-swiper')
        if seasons_data:
            seasons_data = seasons_data.find_all(class_='swiper-slide')

            for data in seasons_data:
                season_url = data.a.get('href')
                season_num = data.a.get_text(strip=True)
                seasons.append({
                    season_num: season_url
                    })

        row = _node_assemble({
            'label': title,
            'params': {
                'path': 'play',
                'src': video_url,
                },
            'isFolder': False,
        })

        content_data = {
                'current_season': season,
                'quality': quality,
                'dubbing': dub,
                'serial_data': serial_data,
            }

        if self.info_switch:
            info = _info_assemble({
                'title': title,
                'originaltitle': otitle,
                #'cover': f"{self.site_url}{cover}",
                'genre': genre,
                'mediatype': mode,
                'year': int(year),
                'rating': rating,
                'country': country,
                'studio': [studio],
                'mpaa': mpaa,
                'plot': plot,
                'path': video_url,
                'trailer': trailer_url,
                'cast': actor_data,
            })
            row['info'] = info

        if self.art_switch:
            arts = _arts_assemble({
                'poster': f"{self.site_url}{cover}",
            })
            row['arts'] = arts

        row['content_data'] = content_data
        row['seasons_data'] = seasons

        nodes.append(row)

        return nodes

    # def play(self, url):
    #     """
    #     Get playlist data for content
    #     """

    #     response = kinescope.parse(url=url)
    #     if isinstance(response, dict):
    #         if 'error' in response:
    #             return {'Ошибка получения данных': response['error']}

    #     playlist_data = response
    #     return playlist_data

    def _userhash(self):
        response = self.net.client_get(url=self.site_url)

        if isinstance(response, dict):
            if 'error' in response:
                return {'ER': response['error']}

        html = response.content

        user_hash = html[html.find(b'dle_login_hash'):]
        user_hash = user_hash[:user_hash.find(b';')]
        user_hash = user_hash[user_hash.find(b"'"):user_hash.rfind(b"'")][1:]
        user_hash = user_hash.decode('utf-8')

        return {'OK': user_hash}

def _rating_assemble(raw_rating):
    if isinstance(raw_rating, list):
        raw_rating = [r.text.strip() for r in raw_rating]
    else:
        raw_rating = [raw_rating.strip()]

    if 'Без рейтинга' in raw_rating:
        raw_rating[raw_rating.index('Без рейтинга')] = '0'

    while len(raw_rating) < 3:
        raw_rating.insert(len(raw_rating), 0)

    rating_complete = {
        'rhs': float(raw_rating[0]),
        'kinopoisk': float(raw_rating[1]),
        'imdb': float(raw_rating[2])
        }

    return rating_complete

def _node_assemble(item=None):
    node_sample = node_scheme.copy()
    if item:
        node_sample.update(item)
    return node_sample

def _info_assemble(item=None):
    info_sample = info_scheme.copy()
    if item:
        info_sample.update(item)
    return info_sample

def _arts_assemble(item=None):
    art_sample = art_scheme.copy()
    if item:
        art_sample.update(item)
    return art_sample

def _pages_assemble(cp=None, lp=None):
    page_sample = pagination_scheme.copy()

    if cp:
        cp = int(cp)
        page_sample['current_page'] = cp

    if lp:
        lp = int(lp)
        page_sample['total_pages'] = lp

    if cp < lp:
        page_sample['next_page'] = cp + 1

    if page_sample['next_page'] != 0:
        node_sample = node_scheme.copy()
        info_sample = info_scheme.copy()
        art_sample = art_scheme.copy()


    return page_sample
