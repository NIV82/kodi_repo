# import sys
# import os

from bs4 import BeautifulSoup
from redheadsound_api.network import BaseClient

class RHSAPI:
    default_url = "https://redheadsound.studio"

    def __init__(self, base_url=None):
        self.site_url = base_url or RHSAPI.default_url
        self.net = BaseClient()

    def search(self, query=None, page=None):
        user_hash = self._get_userhash()
        if 'ER' in user_hash:
            return {'Ошибка': user_hash['ER']}

        current_url = f"{self.site_url}/engine/ajax/controller.php?mod=search"
        post_data = {
            'query': query,
            'skin': 'rhs_new',
            'user_hash': user_hash['OK']
        }

        response = self.net.client_post(url=current_url, data=post_data)

        if not 'OK' in response['reason']:
            return {'Ошибка получения данных': 'error'}

        soup = BeautifulSoup(response['response'].content, "html.parser")

        rows = {'data': [], 'pagination': {}}

        data_array = soup.find_all(class_="move-item")
        for data in data_array:

            cover = data.a.img.get('src').strip()
            rating = data.a.find('span').text.strip()

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.text
            url = row_content.h4.a.get('href')
            year = row_content.span.text
            mode = data.find(class_='flex').a.text


            rows['data'].append({
                'title': title,
                'section': '',
                'info': {
                    'cover': cover,
                    'rating': rating,
                    'type': mode,
                    'url': url,
                    'genre': '',
                    'year': year
                }})

        return rows

    # def main(self):
    #     response = self.net.client_get(url=self.site_url)

    #     if not 'OK' in response['reason']:
    #         return {'Ошибка получения данных': 'error'}

    #     soup = BeautifulSoup(response['response'], "html.parser")

    #     main_menu = {'Поиск': 'search'}
    #     menu_data = soup.find(class_='menu flex align-center justify-end')
    #     for row in menu_data.find_all("a"):
    #         row_path = row.get('href').replace('/','')
    #         row_text = row.text

    #         if 'Обучение' in row_text:
    #             continue

    #         main_menu.update(
    #             {row_text: row_path}
    #         )

    #     return main_menu

    def main(self):
        rows = {'data': [], 'pagination': {}}

        data = {
            'Поиск': 'search',
            'Каталог': 'catalog',
            'Рекомендации': 'recommendation',
            'Фильмы': 'filmy',
            'Сериалы': 'serialy'
            }

        for title, section in data.items():
            rows['data'].append(
                {
                    'title': title,
                    'section': section,
                    'info': {}
                }
            )

        return rows

    def catalog(self):
        rows = {'data': [], 'pagination': {}}

        data = {
            'Аниме сериал': 'animeserial',
            'Триллер': 'triller',
            'Семейные': 'semejnye',
            'Ужасы': 'uzhasy',
            'Боевик': 'boevik',
            'Короткометражка': 'korotkometrazhka',
            'Драма': 'drama',
            'Преступление': 'prestuplenie',
            'Музыка': 'music',
            'Мюзикл': 'musical',
            'Биография': 'biography',
            'Военные': 'military',
            'Детективы': 'detectives',
            'Фэнтези': 'fantasy',
            'Исторические': 'istoricheskie',
            'Marvel': 'marvel',
            'Приключения': 'prikljuchenija',
            'Фантастика': 'fantastika',
            'Комедии': 'komedii'
            }

        for title, section in data.items():
            rows['data'].append(
                {
                    'title': title,
                    'section': section,
                    'info': {}
                }
            )

        return rows

    def recommendation(self):
        current_url = f"{self.site_url}/recommendation"
        response = self.net.client_get(url=current_url)

        if not 'OK' in response['reason']:
            return {'Ошибка получения данных': 'error'}

        soup = BeautifulSoup(response['response'].content, "html.parser")

        rows = {'data': [], 'pagination': {}}

        recomendation = soup.find(class_="movies__list")
        data_array = recomendation.find_all(class_='move-item')
        for data in data_array:
            row_item = data.find(class_='move-item__img')
            image = row_item.img.get('src')

            spans = row_item.find_all('span')
            rating, mode = [x.text for x in spans]

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.a.text
            url = row_content.h4.a.get('href')
            if url.startswith('/'):
                url = url[1:]

            row_data = row_content.find('div', {'class': 'flex change_classes'}).find_all('a')
            row_data = [g.text for g in row_data]
            year = row_data[-1:]
            genre = row_data[:-1]

            rows['data'].append({
                'title': title,
                'section': '',
                'info': {
                    'cover': image,
                    'rating': rating,
                    'type': mode,
                    'url': url,
                    'genre': genre,
                    'year': year
                }})

        return rows

    # def education(self):
    #     return

    def filmy(self, page):
        current_url = f"{self.site_url}/filmy"
        if page:
            current_url = f"{self.site_url}/filmy/page{page}"

        response = self.net.client_get(url=current_url)

        if not 'OK' in response['reason']:
            return {'Ошибка получения данных': 'error'}

        soup = BeautifulSoup(response['response'].content, "html.parser")

        rows = {'data': [], 'pagination': {}}

        pages = soup.find(class_='navigate-pages flex justify-center align-center gap-12')
        if pages:
            current_page = pages.find('span').get_text(strip=True)
            last_page = pages.find_all('a')
            last_page = [lp.text for lp in last_page][-1]
            rows['pagination'] = {'fp': 1, 'cp': current_page, 'lp': last_page}

        movies = soup.find(class_="movies__list")
        data_array = movies.find_all(class_='move-item')

        data_array = movies.find_all(class_='move-item')
        for data in data_array:

            row_item = data.find(class_='move-item__img')
            image = row_item.img.get('src').strip()

            rating = row_item.find('span').get_text(strip=True)

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.a.get_text(strip=True)
            url = row_content.h4.a.get('href').strip()

            genre = row_content.find('div', {'class': 'flex change_classes'}).find_all('a')
            genre = [g.text for g in genre]
            year = genre.pop()

            rows['data'].append({
                'title': title,
                'section': '',
                'info': {
                    'cover': image,
                    'rating': rating,
                    'type': '',
                    'url': url,
                    'genre': genre,
                    'year': year
                }})

        return rows

    def serialy(self, page=None):
        current_url = f"{self.site_url}/serialy"
        if page:
            current_url = f"{self.site_url}/serialy/page/{page}"

        response = self.net.client_get(url=current_url)

        if not 'OK' in response['reason']:
            return {'Ошибка получения данных': 'error'}

        soup = BeautifulSoup(response['response'].content, "html.parser")

        rows = {'data': [], 'pagination': {}}

        pages = soup.find(class_='navigate-pages flex justify-center align-center gap-12')
        if pages:
            current_page = pages.find('span').get_text(strip=True)
            last_page = pages.find_all('a')
            last_page = [lp.text for lp in last_page][-1]
            rows['pagination'] = {'fp': 1, 'cp': current_page, 'lp': last_page}

        series = soup.find(class_="movies__list")
        data_array = series.find_all(class_='move-item')

        data_array = series.find_all(class_='move-item')
        for data in data_array:
            row_item = data.find(class_='move-item__img')
            image = row_item.img.get('src').strip()

            rating = row_item.find('span').get_text(strip=True)

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.a.get_text(strip=True)
            url = row_content.h4.a.get('href').strip()

            genre = row_content.find('div', {'class': 'flex change_classes'}).find_all('a')
            genre = [g.text for g in genre]
            year = genre.pop()

            rows['data'].append({
                'title': title,
                'section': '',
                'info': {
                    'cover': image,
                    'rating': rating,
                    'type': '',
                    'url': url,
                    'genre': genre,
                    'year': year
                }})

        return rows

    def content(self, section, page=None):
        current_url = f"{self.site_url}/{section}"
        if page:
            current_url = f"{self.site_url}/{section}/page/{page}"
        response = self.net.client_get(url=current_url)

        if not 'OK' in response['reason']:
            return {'Ошибка получения данных': 'error'}
        html = response['response'].content

        soup = BeautifulSoup(html, "html.parser")

        rows = {'data': [], 'pagination': {}}

        pages = soup.find(class_='navigate-pages flex justify-center align-center gap-12')
        if pages:
            current_page = pages.find('span').get_text(strip=True)
            last_page = pages.find_all('a')
            last_page = [lp.text for lp in last_page][-1]
            rows['pagination'] = {'fp': 1, 'cp': current_page, 'lp': last_page}

        content = soup.find(class_="movies__list")
        data_array = content.find_all(class_='move-item')

        data_array = content.find_all(class_='move-item')
        for data in data_array:
            row_item = data.find(class_='move-item__img')
            image = row_item.img.get('src').strip()

            rating = row_item.find('span').get_text(strip=True)

            row_content = data.find(class_='move-item__content')
            title = row_content.h4.a.get_text(strip=True)
            url = row_content.h4.a.get('href').strip()

            genre = row_content.find('div', {'class': 'flex change_classes'}).find_all('a')
            genre = [g.text for g in genre]
            year = genre.pop()

            rows['data'].append({
                        'title': title,
                        'section': '',
                        'info': {
                            'cover': image,
                            'rating': rating,
                            'type': '',
                            'url': url,
                            'genre': genre,
                            'year': year
                        }})

        return rows

    def select(self, url):
        current_url = url
        response = self.net.client_get(url=current_url)

        if not 'OK' in response['reason']:
            return {'Ошибка получения данных': 'error'}

        html = response['response'].content

        soup = BeautifulSoup(html, "html.parser")
        plot = soup.find('div', {'class': 'modal', 'id': 'description-modal'})
        plot = plot.find_all('p')
        plot = [desc.p.text for desc in plot if desc.p]
        if len(plot) > 0:
            plot = plot[0].strip()

        data_array = soup.find(class_='fullstory-main-page')

        cover = data_array.find(class_='movies-detail__left').img.get('src')
        title = data_array.h1.text

        spans = data_array.find(class_='movie-relize flex gap-32 align-center')
        spans = spans.find_all('span')
        if len(spans) > 3:
            spans.pop(2)
        year, mode, season = [g.text.strip() for g in spans]

        rating = data_array.find(class_='movies-detail__rating').find_all('span')
        rating = [r.text.strip() for r in rating]
        rating = {'this': rating[0], 'kinopoisk': rating[1], 'imdb': rating[2]}

        edt = data_array.find(class_='flex direction-column gap-24')
        country = data_array.find(class_='movie_country').get_text(strip=True)

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
                {'name_ru': name_ru, 'name_en': name_en, 'cover': img, 'href': url}
            )

        trailer_url = None
        if html.find(b'var trailerUrl =') > -1:
            trailer_url = html[html.find(b"var trailerUrl = '")+18:]
            trailer_url = trailer_url[:trailer_url.find(b"'")].decode('utf-8')

        video_url = None
        if html.find(b'var videoUrl =') > -1:
            video_url = html[html.find(b"var videoUrl = '")+16:]
            video_url = video_url[:video_url.find(b"'")].decode('utf-8')

        content_data = {
            'ru_title': title,
            'en_title': otitle,
            'cover': f"{self.site_url}{cover}",
            'mode': mode,
            'year': year,
            'seson': season,
            'rating': rating,
            'description': plot,
            'country': country,
            'studio': studio,
            'quality': quality,
            'dubbing': dub,
            'mpaa': mpaa,
            'serial_data': serial_data,
            'actor_data': actor_data,
            'trailer_url': trailer_url,
            'video_url': video_url
        }

        return content_data

    def _get_userhash(self):
        response = self.net.client_get(url=self.site_url)

        if not 'OK' in response['reason']:
            return {'ER': response['error']}

        response = response['response'].content

        user_hash = response[response.find(b'dle_login_hash'):]
        user_hash = user_hash[:user_hash.find(b';')]
        user_hash = user_hash[user_hash.find(b"'"):user_hash.rfind(b"'")][1:]
        user_hash = user_hash.decode('utf-8')

        return {'OK': user_hash}
