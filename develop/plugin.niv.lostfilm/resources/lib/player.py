# -*- coding: utf-8 -*-

### За основу взят код и часть функций из ТАМ (xPlayer, play_t2h и вторичные функции под них)
### код частично модифицирован

import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon
import sys, os

from utility import fs_enc, fs_dec

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

if sys.version_info.major > 2:
    from urllib.parse import quote
    addon_data_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    skin_path = xbmcvfs.translatePath('special://skin/')
else:
    from urllib import quote
    addon_data_dir = fs_enc(xbmc.translatePath(addon.getAddonInfo('profile')))
    skin_path = fs_enc(xbmc.translatePath('special://skin/'))

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class xPlayer(xbmc.Player):
    def __init__(self):        
        self.tsserv = None
        self.active = True
        self.started = False
        self.ended = False
        self.paused = False
        self.buffering = False
        
        xbmc.Player.__init__(self)
        width, height = xPlayer.get_skin_resolution()
        w = width
        h = int(0.14 * height)
        x = 0
        y = int((height - h) / 2)
        
        self._ov_window = xbmcgui.Window(12005)
        self._ov_label = xbmcgui.ControlLabel(x, y, w, h, '', alignment=6)        
        self._ov_background = xbmcgui.ControlImage(x, y, w, h, fs_dec(xPlayer.get_ov_image()))        
        self._ov_background.setColorDiffuse('0xD0000000')
        self.ov_visible = False
        self.onPlayBackStarted()
    
    def onPlayBackPaused(self):
        self.ov_show()
        if not xbmc.Player().isPlaying(): xbmc.sleep(2000)
        status = ''
        while xbmc.Player().isPlaying():
            if self.ov_visible == True:
                try:
                    if '2' in addon.getSetting('engine'):
                        status = get_t2h_status()
                except:
                    pass
                self.ov_update(status)
            xbmc.sleep(800)
    
    def onPlayBackStarted(self):
        self.ov_hide()
    
    def onPlayBackResumed(self):
        self.ov_hide()
    
    def onPlayBackStopped(self):
        self.ov_hide()
    
    def __del__(self):
        self.ov_hide()
    
    @staticmethod
    def get_ov_image():
        import base64
        ov_image = os.path.join(addon_data_dir, 'bg.png')
        if not os.path.isfile(ov_image):            
            with open(ov_image, 'wb') as write_file:
                write_file.write(
                    base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')
                    )                
        return ov_image
    
    @staticmethod
    def get_skin_resolution():
        import xml.etree.ElementTree as Et
        tree = Et.parse(os.path.join(skin_path, 'addon.xml'))
        res = tree.findall('./extension/res')[0]
        return int(res.attrib['width']), int(res.attrib['height'])
    
    def ov_show(self):
        if not self.ov_visible:
            self._ov_window.addControls([self._ov_background, self._ov_label])
            self.ov_visible = True
    
    def ov_hide(self):
        if self.ov_visible:
            self._ov_window.removeControls([self._ov_background, self._ov_label])
            self.ov_visible = False
    
    def ov_update(self, txt=" "):
        if self.ov_visible:
            self._ov_label.setLabel(txt)

def play_t2h(uri, file_id, preload_size, download_path):
    from torrent2http import State, Engine, MediaType
    from contextlib import closing
    
    global engine_t2h
    
    if sys.version_info.major > 2:
        monitor = xbmc.Monitor().abortRequested()
    else:
        monitor = xbmc.abortRequested

    try:
        #resume=None
        
        progressBar = xbmcgui.DialogProgress()
        progressBar.create('Torrent2Http', 'Запуск')
        ready = False
        pre_buffer_bytes = preload_size*1024*1024

        engine = Engine(uri, download_path=download_path, enable_dht=True, dht_routers=["router.bittorrent.com:6881","router.utorrent.com:6881"], user_agent = 'uTorrent/2200(24683)')
        engine_t2h = engine
        with closing(engine):
            engine.start(file_id)
            
            try:
                progressBar.update(0, 'Torrent2Http', 'Загрузка торрента', "")
            except:
                progressBar.update(0, 'Загрузка торрента')

            while not monitor and not ready:
                xbmc.sleep(500)
                status = engine.status()
                engine.check_torrent_error(status)
                
                if file_id is None:
                    if monitor:
                        break
                    files = engine.list(media_types=[MediaType.VIDEO])
                    if files is None:
                        continue
                    if not files:
                        break
                        progressBar.close()
                    file_id = files[0].index
                    file_status = files[0]
                else:
                    try:
                        file_status = engine.file_status(file_id)
                    except:
                        file_status = engine.file_status(0)
                    
                    if not file_status:
                        if progressBar.iscanceled():
                            break
                        continue
                    
                if status.state == State.DOWNLOADING:
                    if file_status.download >= pre_buffer_bytes:
                        ready = True
                        break
                    getDownloadRate = status.download_rate / 1024 * 8
                    #getUploadRate = status.upload_rate / 1024 * 8
                    getSeeds = status.num_seeds

                    if sys.version_info.major > 2:
                        progressBar.update(
                            int(100*file_status.download/pre_buffer_bytes),
                            'Предварительная буферизация: {} MB\nСиды: {}\nСкорость: {:.2f} Mbit/s'.format(
                                file_status.download/1024/1024, getSeeds, getDownloadRate))
                    else:
                        progressBar.update(
                            100*file_status.download/pre_buffer_bytes,
                            'Предварительная буферизация: {} MB'.format(file_status.download/1024/1024),
                            'Сиды: {}'.format(getSeeds),
                            'Скорость: {:.2f} Mbit/s'.format(getDownloadRate))

                elif status.state in [State.FINISHED, State.SEEDING]:
                    ready = True
                    break
                
                if progressBar.iscanceled():
                    progressBar.update(0)
                    progressBar.close()
                    break
            
            progressBar.update(0)
            progressBar.close()

            if ready:
                Player=xPlayer()
                item = xbmcgui.ListItem(path=file_status.url)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
                xbmc.sleep(3000)

                while not monitor and xbmc.Player().isPlaying():
                    xbmc.sleep(3000)
    except:
        pass

def get_t2h_status():
    try:
        from torrent2http import MediaType
        try:
            status   = engine_t2h.status()
            speed    = status.download_rate / 1024 * 8
            seeds    = status.num_seeds
        except:
            speed    = '?????'
            seeds    = '?'
        
        try:
            tdownload = status.total_download / 1024 / 1024
        except:
            tdownload = '???'
        
        try:
            files = engine_t2h.list(media_types=[MediaType.VIDEO])
            file_id = files[0].index
            file_status = engine_t2h.file_status(file_id)
            download = file_status.download / 1024 / 1024
        except:
            download = tdownload
            
        return 'Загружено {} MB\nСиды: {}\nСкорость: {:.2f} Mbit/s'.format(download, seeds, speed)
    except:
        return 'err'

def is_libreelec():
    try:
        if os.path.isfile('/etc/os-release'):
            f = open('/etc/os-release', 'r')
            str = f.read()
            f.close()
            if "LibreELEC" in str and "Generic" in str:
                return True
    except: pass
    return False

def rt(s):
    try:
        s=s.decode('utf-8')
    except:
        pass
    
    if not is_libreelec():
        try:
            s=s.decode('windows-1251')
        except:
            pass

    try:
        s=s.encode('utf-8')
    except:
        pass
    
    return s


def media(t):
    L = ['.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts']
    for i in L:
        if i in t.lower():
            return True
    return False

def clean_series(series_list):
    valid_series = []
    
    for series in series_list:
        if media(series[0]):
            valid_series.append(series)

    return valid_series

def get_index(torrent_file, index):
    with open(torrent_file, 'rb') as read_file:
        torrent_data = read_file.read()
    
    import bencode
    torrent = bencode.bdecode(torrent_data)

    series_sorted = []

    if 'files' in torrent['info']:
        x = 0

        for i in torrent['info']['files']:
            series_sorted.append([i['path'][-1],x])
            x = x + 1

        series_sorted.sort()
        series_sorted = clean_series(series_sorted)

        new_index = series_sorted[index][1]
        
        return new_index
    else:
        return 0
    
def torrent2magnet(torrent_file):
    import hashlib, bencode
        
    with open(torrent_file, 'rb') as read_file:
        torrent_data = read_file.read()

    metainfo = bencode.bdecode(torrent_data)

    announce=''
    if 'announce' in metainfo.keys():
        announce = '&tr={}'.format(quote(metainfo['announce']))
    if 'announce-list' in metainfo.keys():
        try:
            for data in metainfo['announce-list']:
                announce = '{}&tr={}'.format(announce, quote(data[0]))
        except:
            pass
    infohash = hashlib.sha1(bencode.bencode(metainfo['info'])).hexdigest()
    magneturi = 'magnet:?xt=urn:btih:{}&dn={}{}'.format(infohash, quote(rt(metainfo['info']['name'])),announce)
    
    return magneturi

def selector(torrent_index, torrent_url, download_dir):
    if int(torrent_index) > 0:
        torrent_index = int(torrent_index) - 1

    index = get_index(torrent_url, torrent_index)

    if '0' in addon.getSetting('engine'):
        try:
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver', 'torrserver_tam', 'lt2http')
            engine = tam_engine[int(addon.getSetting('tam'))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(torrent_url, index, engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            return True
        except:
            return False

    if '1' in addon.getSetting('engine'):
        try:
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(torrent_url), index)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            return True
        except:
            return False

    if '2' in addon.getSetting('engine'):
        try:
            url = 'file:///{}'.format(torrent_url.replace('\\','/'))
            ddir = addon.getSetting('t2h_ddir') or download_dir
            buffer = int(addon.getSetting('t2h_preload'))
            play_t2h(uri=url, file_id=index, preload_size=buffer, download_path=ddir)
            return True
        except:
            return False

    if '3' in addon.getSetting('engine'):
        try:
            url = torrent2magnet(torrent_url)
            import torrserver_player
            torrserver_player.Player(
                torrent=url,
                sort_index=index,
                host=addon.getSetting('ts_host'),
                port=addon.getSetting('ts_port'))            
            return True
        except:
            return False