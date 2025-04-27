import json
import network

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 
    'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7', 
    'Cache-Control': 'no-cache', 
    'Connection': 'Keep-Alive', 
    'Dnt': '1', 
    'Pragma': 'no-cache', 
    'Priority': 'u=0, i', 
    'Referer': 'https://www.google.gp', 
    'Sec-Fetch-Dest': 'document', 
    'Sec-Fetch-Mode': 'navigate', 
    'Sec-Fetch-Site': 'same-origin', 
    'Sec-Fetch-User': '?1', 
    'Sec-Gpc': '1', 
    'Upgrade-Insecure-Requests': '1', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0', 
    'x-requested-with': 'XMLHttpRequest', 
    'Content-Type': 'application/x-www-form-urlencoded'
    }

URL = 'https://vkvideo.ru/al_video.php?act=show'

class ParseVK():
    def __init__(self, vkvideo_url=None, vkreq_url=None):
        self.vk_url = vkvideo_url
        self.req_url = vkreq_url or URL

    def get_playdata(self):
        post_data = {
            "al": "1",
            "autoplay": "1",
            "claim": "",
            "context": "video_other",
            "force_no_repeat": "true",
            "is_video_page": "true",
            "list": "",
            "module": "video_other",
            "show_next": "1",
            "t": "",
            "video": _parse_vkid(self.vk_url),
            }

        net = network.WebTools()

        network.set_headers(headers=HEADERS)

        html = net.get_bytes(url=self.req_url, post=post_data)

        html = html['content'].decode("windows-1251")

        data_array = json.loads(html)
        video_data = data_array['payload']

        playlist = {}
        if video_data[1][4].get("player"):
            data = video_data[1][4]["player"]["params"][0]

            playlist = _parse_vkplaylist(pldata = data)

        return playlist

def _parse_vkplaylist(pldata):
    playlist = {
        'url480': '',
        'url720': '',
        'url1080': '',
        'hls_streams': '',
        'hls': '',
        'type': 'vk'
    }

    if pldata.get("url480"):
        playlist['url480'] = pldata['url480']

    if pldata.get("url720"):
        playlist['url720'] = pldata['url720']

    if pldata.get("url1080"):
        playlist['url1080'] = pldata['url1080']

    if pldata.get("hls_streams"):
        playlist['hls_streams'] = pldata['hls_streams']

    if pldata.get("hls"):
        playlist['hls'] = pldata['hls']

    return playlist

def _parse_vkid(vkurl):
    owner_id = vkurl[vkurl.find('oid=')+4:]
    owner_id = owner_id[:owner_id.find('&')]

    video_id = vkurl[vkurl.find('&id=')+4:]
    video_id = video_id[:video_id.find('&')]

    videos = f"{owner_id}_{video_id}"

    return videos
