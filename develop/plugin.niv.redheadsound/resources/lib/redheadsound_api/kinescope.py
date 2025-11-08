
"""The API Parser for the Kinescope service receives 
a url and returns a response in the form of a dictionary
"""

import re
from redheadsound_api.network import BaseClient

class KinescopeParser:
    def __init__(self, url=None):
        self.url = url
        self.net = BaseClient()

    def parse_playlist(self):
        html = self.net.client_get(url=self.url)
        if 'OK' in html['reason']:
            html = html['response'].text
        else:
            return {}

        pattern = re.compile(r"sources:(.*?)ad:", re.MULTILINE | re.DOTALL)
        data_array = re.findall(pattern=pattern, string=html)

        for data in data_array:
            video_url = re.search(r'src":"(.*?)"', data)
            video_url = video_url.group(1).strip()
            video_url = video_url.replace(r'\u0026', '&')

            video_title = re.search(r'title: "(.*?)"', data)
            video_title = video_title.group(1).strip()

            video_poster = re.search(r'src: "(.*?)"', data)
            video_poster = video_poster.group(1).strip()

            srcset = re.search(r'srcset: \[(.+?)\],', data, re.MULTILINE | re.DOTALL)
            srcset = self._parse_imgset(srcset)

            result = {
                'src': video_url, 'title': video_title, 'cover': video_poster, 'images': srcset
            }

            return result

    def _parse_imgset(self, imgset):
        if imgset:
            imgset = imgset.group(1)
        else:
            return {}

        images = {'webp':{}, 'jpeg':{}}

        imgset = imgset.split('},')
        for node in imgset:
            if not 'src:' in node:
                continue

            node = node.strip()

            imgsrc = re.search(r'src: "(.*?)",', node).group(1)
            imgtype = re.search(r'image/(.+?)\'', node).group(1)
            imgsize_mode = re.search(r'(\w{3})-height', node).group(1)
            imgsize = re.search(r'height:(.*?)px', node).group(1)
            imgsize = imgsize.replace('.1','+').strip()

            images[imgtype][imgsize] = {
                'src': imgsrc, 'mode': imgsize_mode
            }

        return images

def parse(url):
    kinescope = KinescopeParser(url=url)
    kinescope_data = kinescope.parse_playlist()
    return kinescope_data
