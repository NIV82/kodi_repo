"""MAIN SCRAPER FILE"""

from html import unescape
from ado import webtools
from ado import schemes

DEFAULT_URL = "https://anidub.world"

class ADOAPI:
    """API IMPLEMENTATION"""

    def __init__(self, authorization=False, authorization_data=None, base_url=None):
        self.site_url = base_url or DEFAULT_URL

        self.network = webtools.WebTools(
            auth_usage=authorization,
            )

    def search(self, query=None, page=1):
        """SEARCH IMPLEMENTATION"""
        if query is None:
            return _error('Ошибка - Пустой запрос')

        post_data = schemes.post_scheme.copy()
        post_data['search_start'] = page
        post_data['result_from'] = ((int(page)-1) * 32) + 1
        post_data['story'] = query.lower()

        html = self.network.get_bytes(url = self.site_url, post = post_data)
        if not html['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        if html['content'].find(b'<div class="th-item">') < 0:
            return _error('Контент не найден')

        result = _parse_list(html['content'], self.site_url)
        if not result:
            return _error('Контент не найден')

        result['paginator']['cp'] = int(page)
        return result

    def partitions(self, part=None, page=1):
        """SITE PARTITIONS IMPLEMENTATION"""
        section_url = self.site_url
        if part:
            section_url = f"{self.site_url}/{part}/"

        if int(page) > 1:
            section_url = f"{section_url}page/{page}/"

        html = self.network.get_bytes(url = section_url)
        if not html['connection_reason'] == 'OK':
            return _error('Ошибка запроса')

        if html['content'].find(b'<div class="th-item">') < 0:
            return _error('Контент не найден')

        result = _parse_list(html['content'], self.site_url)

        if not result:
            return _error('Контент не найден')

        result['paginator']['cp'] = int(page)
        return result

    def release(self, anime_id=None):
        """ANIME INFO IMPLEMENTATION"""
        if anime_id is None:
            return _error('Ошибка - Отсутствует ID')

        release_url = f"{self.site_url}/index.php?newsid={anime_id}"

        html = self.network.get_bytes(url = release_url)
        if not html['connection_reason'] == 'OK':
            return _error('Ошибка запроса')
        html = html['content'].decode('utf-8')

        info = schemes.info_scheme.copy()
        playlists = schemes.playlists_scheme.copy()

        if html.find('<div class="fposter img-box img-fit">') > -1:
            anime_cover = html[html.find('<div class="fposter img-box img-fit">')+37:]
            anime_cover = anime_cover[anime_cover.find('<img src="')+10:]
            anime_cover = anime_cover[:anime_cover.find('"')]
            if not '://' in anime_cover:
                anime_cover = f"{self.site_url}{anime_cover}"
            info['cover'] = unescape(anime_cover)

        if html.find('<div class="fheader fx-row fx-middle">') > -1:
            data_array = html[html.find('<div class="fheader fx-row fx-middle">'):]
            data_array = data_array[:data_array.find('<iframe allowf')]

            title_block = data_array[:data_array.find('<div class="fmeta fx-row fx-start">')]
            title_block = title_block[title_block.find('<h'):].strip()
            info['title'] = _parse_titleblock(title=title_block)

            meta_block = data_array[data_array.find('<div class="fmeta fx-row fx-start">'):]
            meta_block = data_array[:data_array.find('<div class="fright-title">')]
            info.update(_parse_info(meta_block))

            plot_block = data_array[data_array.find('<div class="fright-title">'):]
            plot_block = plot_block[:plot_block.find('<div class="frates anidbrating">')]
            info['plot'] = _parse_description(description=plot_block)

            player_block = data_array[data_array.find('<div class="tabs-b video-box">')+30:]
            playlists.update(_parse_players(block=player_block))

        return {'info': info, 'playlists': playlists}

    def play_video(self, videourl=None):
        """PARSE LINK FROM URL"""
        if not videourl:
            return None

        vurl = ''
        if 'player.' in videourl:
            vurl = videourl

        if 'sibnet' in videourl:
            vurl = _parse_sibnet(url=videourl)

        return vurl

def _parse_sibnet(url=None):
    if not url:
        return None

    req = webtools.WebTools().get_bytes(url=url)
    if not req['connection_reason'] == 'OK':
        return _error('Ошибка запроса')
    req = req['content']

    play_url = ''
    if req.find(b'player.src([{src: "') > -1:
        video_src = req[req.find(b'player.src([{src: "')+19:]
        video_src = video_src[:video_src.find(b'"')]
        video_src = video_src.decode('utf-8')
        play_url = f"https://video.sibnet.ru{video_src}|referer={url}"

    return play_url

# def _parse_mainplayerurl(url=None):
#     if not url:
#         return {}

#     req = webtools.WebTools().get_bytes(url=url)
#     if not req['connection_reason'] == 'OK':
#         return _error('Ошибка запроса')
#     req = req['content'].decode('utf-8')

#     req = req.splitlines()

#     links = {}
#     for node in req:
#         if '/fhd' in node:
#             links['fhd'] = node
#         if '/sd.' in node:
#             links['sd'] = node

#     return links

def _error(title=None):
    """ERROR IMPLEMENTATION"""
    error = schemes.error_scheme.copy()
    if title:
        error['label'] = f"{title}"
    return ([error],)

def _parse_title(title=None):
    """PARSE TITLE"""
    if title is None:
        return []

    title_node = schemes.title_scheme.copy()

    if '[' in title:
        anime_series = title[title.rfind('[')+1:]
        if ']' in anime_series:
            anime_series = anime_series[:anime_series.find(']')]
        title_node['ep'] = anime_series
        title = title[:title.rfind('[')].strip()
    else:
        title_node['ep'] = ''

    title = title.split(' /')
    title_node['ru'] = title[0].strip()
    if len(title) > 1:
        title_node['en'] = title[1].strip()

    return title_node

def _parse_titleblock(title=None):
    if title is None:
        return []

    result = {}
    if '<h1>' in title:
        result['ru'] = title[title.find('<h1>')+4:title.find('</h1>')]
    elif '<h2>' in title:
        result['ru'] = title[title.find('<h2>')+4:title.find('</h2>')]
    if '<h3>' in title:
        result['en'] = title[title.find('<h3>')+4:title.find('</h3>')]
    if '<h4>' in title:
        result['ep'] = title[title.find('<h4>')+4:title.find('</h4>')]

    if len(result) < 2:
        result = _parse_title(title=result['ru'])

    return result

def _parse_values(node=None):
    if node is None:
        return []
    result = []
    node = node.split(',')
    for n in node:
        n = n[n.find('">')+2:]
        n = n[:n.find('<')]
        result.append(n.strip())
    return result

def _parse_description(description=None):
    if description is None:
        return []

    plot = ''
    if description.find('fdesc clr full-text clearfix">') > -1:
        plot = description[description.find('fdesc clr full-text clearfix">')+30:]
        plot = plot[:plot.find('</div>')]

        if '<!--dle_spoiler' in plot:
            plot = plot[:plot.find('<!--dle_spoiler')]
        plot = plot.replace('<p>', '').replace('</p>','\n').replace('<br>','')
        if '<' in plot and '</' in plot:
            fix = plot[plot.find('<'):plot.find('</')+5]
            plot = plot.replace(fix,'')
        plot = unescape(plot).strip()

    return plot

def _parse_mainplayer(main_block=None):
    if main_block is None:
        return []

    url = main_block[:main_block.find('">')]
    url = unescape(url)
    url = url.replace('<span data="', '')

    domain = url[:url.find('/index')]

    req = webtools.WebTools().get_bytes(url=url)

    if not req['connection_reason'] == 'OK':
        return _error('Ошибка запроса')

    req = req['content'].decode('utf-8')

    player_array = []

    play_list = req[req.find('<span data='):]
    play_list = play_list[:play_list.rfind('</span>')]
    play_list = play_list.split('</span>')
    for node in play_list:
        span_data = node[node.find('<span data="')+12:]
        span_data = span_data[:span_data.find('"')]

        span_title = node[node.rfind('>')+1:]
        span_title = span_title.strip()
        player_array.append(
            {'title': span_title, 'quality_url': f"{domain}/vid.php?v=/{span_data}"}
        )

    return player_array

def _parse_sibneturls(sibnet_block=None):
    if sibnet_block is None:
        return []

    player_array = []
    sibnet_block = sibnet_block.split('</span>')
    for node in sibnet_block:
        span_data = node[node.find('<span data="')+12:]
        span_data = span_data[:span_data.find('"')]

        span_title = node[node.rfind('>')+1:]
        span_title = span_title.strip()

        player_array.append(
            {'title': span_title, 'quality_url': span_data}
            )

    return player_array

def _parse_players(block=None):
    if block is None:
        return []

    block = block.split('<div class="tabs-b video-box">')

    playlist = {}
    for player in block:
        if not '<span data="' in player:
            continue

        node = player[player.find('<span data="'):]
        node = node[:node.rfind('</span>')]

        if '://player.' in node:
            playlist['main'] = _parse_mainplayer(main_block=node)

        if 'sibnet.' in node:
            playlist['sibnet'] = _parse_sibneturls(sibnet_block=node)

    return playlist

def _parse_info(info_data=None):
    if not info_data:
        return {}

    meta = {}

    if info_data.find('/year/') > -1:
        year = info_data[info_data.find('/year/'):]
        year = year[year.find('">')+2:]
        year = year[:year.find('<')]
        meta['year'] = int(year)

    if info_data.find('/country/') > -1:
        country = info_data[info_data.find('/country/'):]
        country = country[country.find('">')+2:]
        country = country[:country.find('<')]
        meta['country'] = country

    if info_data.find('/genre/') > -1:
        genre = info_data[info_data.find('/genre/'):]
        genre = genre[:genre.find('</li>')]
        meta['genre'] = _parse_values(genre)

    if info_data.find('/autor/') > -1:
        autor = info_data[info_data.find('/autor/'):]
        autor = autor[:autor.find('</li>')]
        meta['writer'] = _parse_values(node=autor)

    if info_data.find('/director/') > -1:
        director = info_data[info_data.find('/director/'):]
        director = director[:director.find('</li>')]
        meta['director'] = _parse_values(node=director)

    if info_data.find('/studio/') > -1:
        studio = info_data[info_data.find('/studio/'):]
        studio = studio[:studio.find('</li>')]
        meta['studio'] = _parse_values(node=studio)

    if info_data.find('/dubber/') > -1:
        dubber = info_data[info_data.find('/dubber/'):]
        dubber = dubber[:dubber.find('</li>')]
        meta['dubber'] = _parse_values(node=dubber)

    if info_data.find('/translater/') > -1:
        translater = info_data[info_data.find('/translater/'):]
        translater = translater[:translater.find('</li>')]
        meta['translater'] = _parse_values(node=translater)

    return meta

def _parse_list(data=None, site_url=None):
    """PARSE ANIME LIST IMPLEMENTATION"""
    if data is None or site_url is None:
        return []

    result = []

    try:
        data = data.decode('utf-8')
    except: # pylint: disable=W0702
        pass

    data_array = data[data.find('<div class="th-item">')+21:data.rfind('<!-- END CONTENT -->')]
    data_array = data_array.split('<div class="th-item">')

    for node in data_array:
        anime_id = node[node.find('th-in" href="')+13:node.find('.html">')]
        anime_id = anime_id[anime_id.rfind('/')+1:anime_id.find('-')]

        anime_cover = node[node.find('<img src="')+10:]
        anime_cover = anime_cover[:anime_cover.find('"')]
        anime_cover = unescape(anime_cover)

        if not '://' in anime_cover:
            anime_cover = f"{site_url}{anime_cover}"

        anime_title = node[node.find('<div class="th-title">')+22:]
        anime_title = anime_title[:anime_title.find('</div>')]
        anime_title = _parse_title(title=anime_title)

        result.append(
            {'id': anime_id, 'title': anime_title, 'cover': anime_cover}
        )

    pages = schemes.paginator_scheme.copy()
    if data.find('navigation">') > -1:
        total_page = data[data.find('navigation">')+12:]
        total_page = total_page[:total_page.find('</div>')]
        total_page = total_page[total_page.rfind('">')+2:]
        total_page = total_page[:total_page.find('<')]
        total_page = int(total_page.strip())

        pages['tp'] = int(total_page)

    return {'info': result, 'paginator': pages}
