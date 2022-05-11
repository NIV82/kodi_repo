# coding: utf-8

from sys import version_info
import requests
import json
import time

if version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse   # type: ignore
class V2toV1Adapter(object):

    key_equivalents = {
        'TorrentStatusString': 'stat_string',
        'TorrentStatus': 'stat',
        'Length': 'torrent_size',
        'Files': 'file_stats',
        'FileStats': 'file_stats',
    }

    deprecated = {
        'UploadSpeed':  0,
    }

    def __init__(self, v2):
        self.v2 = v2

    def __str__(self):
        return self.v2.__str__()

    def get(self, key, def_val=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return def_val

    def _get_v2_key(self, key):
        v2key = key[0].lower()
        for ch in key[1:]:
            if ch.isupper():
                v2key += '_' + ch.lower()
            else:
                v2key += ch
        return v2key

    def __contains__(self, item):
        if item in self.v2:
            return True

        ke = self.key_equivalents
        if item in ke and ke[item] in self.v2:
            return True

        return self._get_v2_key(item) in self.v2

    def __getitem__(self, key):
        if key in self.v2:
            return self.v2[key]

        if key in self.deprecated:
            return self.deprecated[key]

        def get_element(value):
            if isinstance(value, dict):
                return self.__class__(value)
            elif isinstance(value, list):
                return [ get_element(item) for item in value ]
            return value

        def get_value(v2key):
            if v2key in self.v2:
                value = self.v2[v2key] 
                return get_element(value)
            else:
                raise KeyError

        ke = self.key_equivalents
        if key in ke:
            try:
                return get_value(ke[key])
            except KeyError:
                pass

        v2key = self._get_v2_key(key)

        return get_value(v2key)

class V2toV1ListAdapter(V2toV1Adapter):
    key_equivalents = {
        #'TorrentStatusString': 'stat_string',
        #'TorrentStatus': 'stat',
        'Length': 'torrent_size',
        'Files': 'file_stats',
        'FileStats': 'file_stats',
        #'Name': 'title',
    }

def _u(s):
    if version_info >= (3, 0):
        return s
    return unicode(s)   # type: ignore

def no_log(s):
    pass

def url2path(url):
    import urllib
    return urllib.url2pathname(urlparse(url).path)

def encode_url(s):
    import urllib

    if version_info >= (3, 0):
        return urllib.parse.quote(s.encode('utf8'))
    else:
        return urllib.quote(s.encode('utf8'))

class BaseEngine(object):

    def make_url(self, path):
        return 'http://' + self.host + ':' + str(self.port) + path

    @property
    def is_v2(self):
        if 'version' not in self.__dict__:
            self.version = self.echo()

        return self.version >= (1, 2)

    def request(self, name, method='POST', data=None, files=None):

        if self.is_v2 and name == 'upload':
            url = self.make_url('/torrent/upload')
            data = {'save': True}
            r = requests.post(url, data=data, files=files)
            return r

        url = self.make_url('/torrents' if self.is_v2 else '/torrent/' + name)

        self.log(_u(url))

        if self.is_v2:
            if not data:
                data = {}
            data['action'] = name

        if data:
            data = json.dumps(data)

        if method=='POST':
            r = requests.post(url, data=data, files=files)
        else:
            r = requests.get(url, data=data, files=files)

        if r.ok:
            pass
        else:
            self.log('!!! Wrong request !!!')
            self.log('Error code {}'.format(r.status_code))

        return r

    def echo(self):
        url = self.make_url('/echo')
        try:
            r = requests.get(url)
        except requests.ConnectionError as e:
            self.log(_u(e))
            return False

        if r.status_code == requests.codes.ok:
            self.log(r.text)
            ver = r.text

            if ver.startswith('MatriX'):
                ver = ver.replace('MatriX', '2.0')

            ver = ver.replace('_', '.')
            ver = [int(n) for n in ver.split('.')[:3]]
            return tuple(ver)

        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            self.log(_u(e))
        except:
            pass

        return False

    def stat(self):
        if self.is_v2:
            return V2toV1Adapter(self.request('get', data={'Hash': self.hash}).json())
        else:
            return self.request('stat', data={'Hash': self.hash}).json()

    def get(self):
        if self.is_v2:
            return V2toV1Adapter(self.request('get', data={'Hash': self.hash}).json())
        else:
            return self.request('get', data={'Hash': self.hash}).json()
        
    def list(self):
        if self.is_v2:
            return [V2toV1ListAdapter(item) for item in self.request('list').json()]
        else:
            return self.request('list').json()

    def restart(self):
        self.request('restart', method='GET')

    def rem(self):
        self.request('rem', data={'Hash': self.hash})

    def drop(self):
        self.request('drop', data={'Hash': self.hash})

    def upload_file(self, filename):
        files = {'file': open(filename, 'rb')}
        return self.request('upload', files=files)

    def add(self, uri, title=None, poster=None, data=None):
        params = {'Link': uri}
        if self.is_v2:
            params['save_to_db'] = True
            if title:
                params['title'] = title
            if poster:
                params['poster'] = poster
        else:
            params['DontSave'] = False
            info = {}
            if title:
                info['title'] = title
            if poster:
                info['poster_path'] = poster
            if info:
                params['Info'] = json.dumps(info, ensure_ascii=False)

        r = self.request('add', data=params)

        if self.is_v2:
            info = json.loads(r.content)
            self.hash = info['hash']
        else:
            self.hash = r.content

        if isinstance(self.hash, bytes):
            self.hash = self.hash.decode("utf-8")

        self.log('Engine add')
        self.log(self.hash)
        self.log(_u(r.headers))
        self.log(r.text)

        return r.status_code == requests.codes.ok

    def upload(self, name, data):
        files = {'file': (name, data)}

        r = self.request('upload', files=files)

        try:
            res = r.json()[0]
        except KeyError:
            res = r.json()

        self.hash = res['hash'] if self.is_v2 else res

        self.log('Engine upload')
        self.log(self.hash)
        self.log(_u(r.headers))
        self.log(r.text)

        return r.status_code == requests.codes.ok


class Engine(BaseEngine):
    def _wait_for_data(self, timeout=10):
        self.log('_wait_for_data')
        #files = self.list()
        for n in range(timeout*2):
            st = self.stat()
            try:
                self.log(st['TorrentStatusString'])

                if st['TorrentStatusString'] != 'Torrent working':
                    time.sleep(0.5)
                else:
                    break
            except KeyError:
                self.log('"TorrentStatusString" not in stat')
                time.sleep(0.5)

    def __init__(self, uri=None, path=None, data=None, host='127.0.0.1', port=8090, log=no_log, hash=None, title=None, poster=None):
        self.uri = uri
        self.host = host
        self.port = port
        self.hash = hash
        self.log = log
        self.success = True
        self._playable_items = []
        self.data = None
        
        self.version = self.echo()
        if not self.version:
            self.success = False
            return

        if uri:
            if uri.startswith('magnet:') or uri.startswith('http:') or uri.startswith('https:'):
                self.add(uri, title, poster)
                self._wait_for_data()
                return

            if uri.startswith('file:'):
                path = url2path(uri)

        if path and not data:
            with open(path, 'rb') as f:
                data = f.read()

        if data:
            name = path or 'Torrserver engine'
            self.upload(name, data)
            self._wait_for_data()

    @property
    def playable_items(self):
        return self._get_playable_items()

    def _get_playable_items(self):

        if self._playable_items:
            return self._playable_items

        if not self.data:
            st = self.stat()
            if 'RealIdFileStats' not in st:
                raise NotImplementedError('magnet links not supported for torrent indexes, use sorted_index or name')
            if st.get('RealIdFileStats') is None:
                raise NotImplementedError('RealIdFileStats is disabled in TorrServer 1.1.77_6, please enable it')
            for i in st['RealIdFileStats']: #it only torrserver 1.1.77_6 with RealIdFileStats and &ind=
                self._playable_items.append({'index': i['Id'], 'name': i['Path'], 'size': i['Length']})
            return self._playable_items

            # import bencode
            
            # with open(torrent_file, 'rb') as read_file:
            #     torrent_data = read_file.read()

            # torrent = bencode.bdecode(torrent_data)
            
        import os
        #from bencode import bdecode
        import bencode
        #decoded = bdecode(self.data)
        decoded = bencode.bdecode(self.data)

        info = decoded['info']

        def info_name():
            if 'name.utf-8' in info:
                return info['name.utf-8']
            else:
                return info['name']

        def f_path(f):
            if 'path.utf-8' in f:
                return f['path.utf-8']
            else:
                return f['path']

        def _name(name):
            import sys
            try:
                if sys.version_info < (3, 0) and isinstance(name, str):
                    return name.decode('utf-8')
            except UnicodeDecodeError:
                import chardet
                enc = chardet.detect(name)
                if enc['confidence'] > 0.5:
                    try:
                        name = name.decode(enc['encoding'])
                    except UnicodeDecodeError:
                        pass
            return name

        info_name = _name(info_name())
        try:
            if 'files' in info:
                for i, f in enumerate(info['files']):
                    name = _name('/'.join(f_path(f)))
                    name = u'/'.join([info_name, name])
                    size = f['length']

                    self._playable_items.append({'index': i, 'name': name, 'size': size})
            else:
                self._playable_items = [ {'index': 0, 'name': info_name, 'size': info['length'] } ]
        except UnicodeDecodeError:
            return None

        return self._playable_items

    def _magnet2data(self, magnet):
        self.log('-'*100)
        self.log('_magnet2data')

        '''
        try:
            from python_libtorrent import get_libtorrent
            lt = get_libtorrent()			
            
        except ImportError:
            self.log('_magnet2data: import error')
            return None
            
        except:
            self.log('_magnet2data: other error')
            return None
            

        import tempfile, sys, shutil
        from time import sleep

        tempdir = tempfile.mkdtemp()
        ses = lt.session()
        params = {
            'save_path': tempdir,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        handle = lt.add_magnet_uri(ses, magnet, params)

        self.log("Downloading Metadata (this may take a while)")
        while (not handle.has_metadata()):
            try:
                sleep(1)
                self.log('Wait for data')
            except KeyboardInterrupt:
                self.log("Aborting...")
                ses.pause()
                self.log("Cleanup dir " + tempdir)
                shutil.rmtree(tempdir)
                return None
        ses.pause()
        self.log("Done")

        torinfo = handle.get_torrent_info()
        torfile = lt.create_torrent(torinfo)

        torcontent = lt.bencode(torfile.generate())
        return torcontent
        '''

    def upload(self, name, data):
        self.data = data
        return BaseEngine.upload(self, name, data)

    def add(self, uri, title=None, poster=None, data=None):
        if uri.startswith('magnet:'):
            pass  # self.data = self._magnet2data(uri)
        else:
            r = requests.get(uri)
            if r.status_code == requests.codes.ok:
                self.data = r.content

        return BaseEngine.add(self, uri, title=title, poster=poster)

    def start_preload(self, url):
        def download_stream():
            req = requests.get(url, stream=True, allow_redirects=False)
            for chunk in req.iter_content(chunk_size=128):
                self.log('dowload chunk: 128')

        import threading
        t = threading.Thread(target=download_stream)
        t.start()

    def id_to_files_index(self, file_id):
        ts = self.torrent_stat()

        try:
            pi = self._get_playable_items()[file_id]
        except:
            return file_id

        files_index = 0
        for fl in ts['Files']:
            self.log(_u(fl['Name']))
            if pi['name'] == fl['Name']:
                return files_index
            files_index += 1

        return file_id

    def _start_v2(self, start_index=None):
        preload_url = self.make_url("/stream?link={}&index={}&preload".format(
            self.hash, start_index+1
        ))

        self.start_preload(preload_url)

    def _start_v1(self, start_index=None):
        for n in range(5):
            self.log('Try # {0}'.format(n))
            try:
                files = self.list()
                self.log(_u(files))

                for torrent in files:
                    if self.hash == torrent['Hash']:
                        file = torrent['Files'][start_index]
                        preload = file['Preload']

                        self.start_preload(self.make_url(preload))
                        return
                break
            except BaseException as e:
                self.log(e)
                time.sleep(0.5)
                continue

        self.log('Preload not started')

    def start(self, start_index=None):
        self.log('Engine start')

        if start_index is None:
            start_index = 0

        if self.is_v2:
            self._start_v2(start_index)
        else:
            self._start_v1(start_index)

    def _torrent_stat_v1(self):
        lst = self.list()

        for torr in lst:
            if self.hash == torr['Hash']:
                return torr

    def torrent_stat(self):
        if self.is_v2:
            return self.stat()
        else:
            return self._torrent_stat_v1()

    def file_stat(self, index):
        ts = self.torrent_stat()
        return ts['Files'][index]

    def files(self):
        ts = self.torrent_stat()
        id = 0
        for f in ts['Files']:
            yield { 'file_id': id, 
                    'path': f['path'] if self.is_v2 else f['Name'],
                    'size': f['length'] if self.is_v2 else f['Size'],
                    #'viewed': f['viewed'] if self.is_v2 else f['Viewed']
            }
            id += 1

    def get_ts_index(self, name):
        ts = self.torrent_stat()
        index = 0
        for f in ts['Files']:
            if f['Name'] == name:
                return index
            index += 0

    def play_url(self, index):
        fs = self.file_stat(index)

        if self.is_v2:
            r = requests.get(self.make_url("/stream/?link={}&m3u".format(self.hash)))
            if r.status_code == requests.codes.ok:
                for line in r.text.splitlines():
                    if line.startswith('http://'):
                        find_str = "&index={}&".format( fs['id'] )
                        if find_str in line:
                            return line
            else:
                quoted_path = encode_url(fs['path'])
                return self.make_url("/stream/{}?link={}&index={}&play".format(
                                                quoted_path, self.hash, index+1))

        return self.make_url(fs['Link'])

    def progress(self):
        info = self.stat()
        percent = float(info['downloaded']) * 100 / info['size']

    def buffer_progress(self):
        st = self.stat()

        self.log(_u(st))

        preloadedBytes = st.get('PreloadedBytes', 0)
        preloadSize = st.get('PreloadSize', 0)
        if preloadSize > 0 and preloadedBytes > 0:
            prc = preloadedBytes * 100 / preloadSize
            if prc >= 100:
                prc = 100

            stat_id = st.get('TorrentStatus')
            if prc > 0 and stat_id != 2: # 2 - 'Torrent preload'
                prc = 100
            return prc

        return 0

    @property
    def title(self):
        if self.is_v2:
            return self.stat().get('title')
        else:
            ts = self.torrent_stat()
            info = ts.get('Info')
            if info:
                info = json.loads(info)
                if info:
                    return info.get('title')

    @property
    def poster(self):
        if self.is_v2:
            return self.stat().get('poster')
        else:
            ts = self.torrent_stat()
            info = ts.get('Info')
            if info:
                info = json.loads(info)
                if info:
                    return info.get('poster_path')

    @property
    def fanart(self):
        if self.is_v2:
            return None # self.stat().get('fanart')
        else:
            ts = self.torrent_stat()
            info = ts.get('Info')
            if info:
                info = json.loads(info)
                if info:
                    return info.get('backdrop_path')

    @staticmethod
    def extract_hash_from_magnet(magnet):
        # 'magnet:?xt=urn:btih:3b68e98ec4522d7a2c3dae1614bb32d3e8a41155&dn=rutor.info&tr=udp%3A%2F%2Fopentor.org%3A2710&tr=udp%3A%2F%2Fopentor.org%3A2710&tr=http%3A%2F%2Fretracker.local%2Fannounce'
        result = magnet.replace('magnet:?xt=urn:btih:', '')
        result = result.split('&')[0]
        return result

    @staticmethod
    def extract_hash_from_play_url(url):
        prefixes = ['torrent/view/', 'link=', 'xt=urn:btih:']

        import re
        for prefix in prefixes:
            m = re.search(prefix + r'(\w{40})', url) 
            if m:
                return m.group(1)

    def get_art(self):
        """ returns art """
        art = {}

        poster = self.poster
        if poster:
            art = {
                'thumb': poster,
                'poster': poster,
            }

        fanart = self.fanart
        if fanart:
            art['fanart'] = fanart

        return art

    def _get_video_info_v1(self):
        ts = self.torrent_stat()
        info = ts.get('Info')
        if info:
            info = json.loads(info)
            if info:
                return self._get_video_info_from_data(info)
        return {}

    def _get_video_info_v2(self):
        info = None
        ts = self.stat()
        data = ts.get('data', {})
        if data:
            info = json.loads(data)
        if info:
            return self._get_video_info_from_data(info)
        else:
            return {'title': self.title}

    def _get_video_info_from_data(self, info):
        video_info = {}
        if 'title' in info:
            video_info = {'title': info['title']}
        if 'overview' in info:
            video_info['plot'] = info.get('overview', '')
        if 'year' in info:
            video_info['year'] = int(info.get('year'))
        if 'genres' in info:
            genres = []
            for g in info['genres']:
                genres.append(g['name'])
            if genres: 
                video_info['genre'] = genres
        if 'original_title' in info:
            video_info['originaltitle'] = info.get('original_title')
        if 'vote_average' in info:
            video_info['rating'] = info.get('vote_average', 0.0)
        if 'origin_country' in info:
            country = ''
            for g in info.get('origin_country'):
                country += g + ', '
            if country: video_info['studio'] = country.strip(' ,')
        if 'runtime' in info:
            video_info['duration'] = info.get('runtime', 0) / 1000
        return video_info

    def get_video_info(self):
        """ returns video info """
        if self.is_v2:
            return self._get_video_info_v2()
        else:
            return self._get_video_info_v1()

# if __name__ == '__main__':
#     path = 'D:\\test.torrent'
#     file_id = 2

#     def log(s):
#         with open('engine.log', 'a') as f:
#             try:
#                 f.write(s.encode('utf-8'))
#             except:
#                 f.write(s)
#             f.write('\n')

#     # host='192.168.1.5'
#     #e = Engine(path=path, log=log)
#     #e = Engine(uri='http://rutor.is/download/657889', log=log)
#     #e = Engine(uri='magnet:?xt=urn:btih:a60f1bf7abf47af05ff8bd2b5f33fff65e7d7159&dn=rutor.info_%D0%9C%D0%B0%D0%BD%D0%B8%D1%84%D0%B5%D1%81%D1%82+%2F+%D0%94%D0%B5%D0%BA%D0%BB%D0%B0%D1%80%D0%B0%D1%86%D0%B8%D1%8F+%2F+Manifest+%5B01%D1%8501-11+%D0%B8%D0%B7+18%5D+%282018%29+WEB-DL+720p+%7C+LostFilm&tr=udp://opentor.org:2710&tr=udp://opentor.org:2710&tr=http://retracker.local/announce', log=log)

#     e = Engine(path='/Users/vd/.kodi/temp/lazyf1.torrent')

#     e.start()

#     g = e.get()
#     s = e.stat()

#     while 'FileStats' not in s:
#         time.sleep(0.5)
#         s = e.stat()

#     while True:
#         try:
#             st = e.stat()
#             downloaded = int(st['LoadedSize'] / 1024 / 1024)
#             print(downloaded)
#             size = int(st['FileStats'][0]['Length'] / 1024 / 1024)
#             print(size)
#             dl_speed = int(st['DownloadSpeed'] / 1024)
#             print(dl_speed)
#             ul_speed = int(st['UploadSpeed'] / 1024)
#             print(ul_speed)
#             num_seeds =	st['ConnectedSeeders']
#             print(num_seeds)
#             num_peers =	st['ActivePeers']
#             print(num_peers)

#             if downloaded > size:
#                 break
#         except:
#             pass

#     fstats = s['FileStats']
#     item = fstats[0]
#     size = int(item['Length'])

#     for file_id in range(0, 8):
#         play_url = e.play_url(file_id)
#         log(play_url)



