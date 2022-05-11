# -*- coding: utf-8 -*-

### Данный файл извлечен из плагина plugin.video.evld.shiza-project.com , частично модифицирован 
### и приспособлен, вероятно временно, под необходимые задачи (проигрывание через T2HTTP)

import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon
import sys, os

if sys.version_info.major > 2:
    #from urllib.parse import urlencode
    from urllib.parse import quote
    #from urllib.parse import unquote
    #from urllib.parse import parse_qs
    #from urllib.request import urlopen
    #from html import unescape
else:
    #from urllib import urlencode
    #from urllib import urlopen
    from urllib import quote
    #from urllib import unquote
    #from urlparse import parse_qs
    #import HTMLParser
    #unescape = HTMLParser.HTMLParser().unescape
    
addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

data = {
    'torrent_index':'',
    'torrent_url':'',
    'download_dir':''
    }

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

class myPlayer(xbmc.Player):

    def __init__(self):
        self.engine = None
        self.started = False
        self.paused = False

        self.update_proc = None

        xbmc.Player.__init__(self)
        width, height = myPlayer.get_skin_resolution()
        w = width
        h = int(0.14 * height)
        x = 0
        y = (height - h) // 2
        #y = int((height - h) / 2)
        self._ov_window = xbmcgui.Window(12005)
        self._ov_label = xbmcgui.ControlLabel(x, y, w, h, '', alignment=6)
        self._ov_background = xbmcgui.ControlImage(x, y, w, h, myPlayer.get_ov_image())
        self._ov_background.setColorDiffuse('0xD0000000')

        self.ov_visible = False
        self.onPlayBackStarted()

    def onPlayBackPaused(self):
        self.ov_show()

    def onPlayBackStarted(self):
        self.ov_hide()

        if not xbmc.Player().isPlaying():
            xbmc.sleep(2000)

        status = ''
        while xbmc.Player().isPlaying():
            if self.ov_visible == True:
                status = self.get_status()
                self.ov_update(status)
            xbmc.sleep(800)

    def onPlayBackResumed(self):
        self.ov_hide()
        
    def onPlayBackStopped(self):
        self.ov_hide()

    def __del__(self):
        self.ov_hide()

    def get_status(self):
        try:
            status = self.update_proc(self.engine)
        except:
            status = ''

        return status

    @staticmethod
    def get_ov_image():
        import base64
        ov_image = os.path.join(data['download_dir'], 'bg.png')

        if not os.path.isfile(ov_image):
            fl = open(ov_image, 'wb')
            fl.write(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='))
            fl.close()
        return ov_image

    @staticmethod
    def get_skin_resolution():
        import xml.etree.ElementTree as Et
        
        if sys.version_info.major > 2:
            skin_path = xbmcvfs.translatePath('special://skin')
        else:
            skin_path = xbmc.translatePath('special://skin')
            
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

    def ov_update(self, txt=' '):
        if self.ov_visible:
            self._ov_label.setLabel(txt)

def abortRequested():
    if sys.version_info.major > 2:
        return xbmc.Monitor().abortRequested()
    else:
        return xbmc.abortRequested
 
def play_t2h(uri, preload_size, file_id, download_path):
    from torrent2http import State, Engine, MediaType, Error
    from contextlib import closing

    def update_proc(engine):
        try:
            status   = engine.status()
            speed    = status.download_rate / 1024 * 8
            seeds    = status.num_seeds
        except:
            speed    = '?????'
            seeds    = '?'
        
        try:    tdownload = status.total_download / 1024 / 1024
        except: tdownload = '???'
        
        try:
            files = engine.list(media_types=[MediaType.VIDEO])
            #file_id = files[0].index
            file_status = engine.file_status(engine.file_id)
            download = file_status.download / 1024 / 1024
        except:
            download = tdownload

        return 'Загружено [B]{0:.0f}[/B] MB[CR]Сиды: [B]{1}[/B][CR]Скорость: [B]{2:6.2f}[/B] Mbit/s'.format(download, seeds, speed)

    ready = False
    pre_buffer_bytes = preload_size * 1024 * 1024
    engine = Engine(uri, download_path=download_path)

    # if sys.version_info.major > 2:
    #     monitor = xbmc.Monitor()
    # else:
    #     monitor = xbmc.abortRequested
        
    #monitor = xbmc.Monitor()
    dialog = xbmcgui.DialogProgress()

    with closing(engine):
        engine.start(file_id)
        dialog.create('Torrent2Http', 'Запуск')
        dialog.update(0, 'Загрузка торрента')
        #while not monitor.abortRequested() and not ready:
        while not abortRequested() and not ready:
            xbmc.sleep(500)

            if dialog.iscanceled():
                ready = False
                break

            status = engine.status()
            try:
                engine.check_torrent_error(status)
            except Error as e:
                xbmcgui.Dialog().notification('Torrent2Http', e.message, time=8000, sound=True)
                break

            if file_id is None:
                files = engine.list(media_types=[MediaType.VIDEO])
                if files is None:
                    continue
                if not files:
                    dialog.close()
                    break
                file_id = files[0].index
                file_status = files[0]
            else:
                file_status = engine.file_status(file_id)
                if not file_status:
                    continue
            if status.state == State.DOWNLOADING:
                if file_status.download >= pre_buffer_bytes:
                    ready = True
                    break
                getDownloadRate = status.download_rate / 1024 * 8
                getSeeds = status.num_seeds
                
                dialog.update(int(100 * file_status.download / pre_buffer_bytes), 'Предварительная буферизация: {0:.0f} MB\nСиды: {1}\nСкорость: {2:6.2f} Mbit/s'.format(file_status.download / 1024 / 1024, getSeeds, getDownloadRate))
                
            elif status.state in [State.FINISHED, State.SEEDING]:
                ready = True
                break
            
        dialog.update(0)
        dialog.close()

        if ready:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()

            player = myPlayer()
            engine.file_id = file_id
            player.engine = engine
            player.update_proc = update_proc

            item = xbmcgui.ListItem(path=file_status.url)
            #xbmcplugin.setResolvedUrl(handle, True, item)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            xbmc.sleep(3000)

            #while not monitor.abortRequested() and player.isPlaying():
            while not abortRequested() and player.isPlaying():
                xbmc.sleep(500)

def get_index(torrent_file, index):
    with open(torrent_file, 'rb') as read_file:
        torrent_data = read_file.read()
    
    import bencode
    torrent = bencode.bdecode(torrent_data)

    series_current = []
    series_sorted = []
#lostfix index start ===============================================
    if 'files' in torrent['info']:
        if int(index) > 0:
            index = int(index) - 1
#lostfix index end ===============================================
        for i in torrent['info']['files']:
            series_current.append(i['path'][-1])
            series_sorted.append(i['path'][-1])

        series_sorted.sort()
        current_file = series_current[index]
            
        new_index = 0

        for i in series_sorted:
            if current_file in i:
                return new_index
            new_index = new_index + 1
    else:
        return 0

def rt(node):
    try:
        node = node.decode('utf-8')
    except:
        pass
    
    if os.path.isfile('/etc/os-release'):
        with open('/etc/os-release', 'r') as read_file:
            data = read_file.read()
        if not 'LibreELEC' in data and 'Generic' in data:
            try:
                node=node.decode('windows-1251')
            except:
                pass
    
    # if not is_libreelec():
    #     try:
    #         node=node.decode('windows-1251')
    #     except:
    #         pass

    try:
        node=node.encode('utf-8')
    except:
        pass
    
    return node

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

def selector(**kwargs):
    data.update(kwargs)
    
    if '0' in addon.getSetting('engine'):
        try:
            tam_engine = ('','ace', 't2http', 'yatp', 'torrenter', 'elementum', 'xbmctorrent', 'ace_proxy', 'quasar', 'torrserver', 'torrserver_tam', 'lt2http')
            engine = tam_engine[int(addon.getSetting('tam'))]
            purl ="plugin://plugin.video.tam/?mode=play&url={}&ind={}&engine={}".format(
                quote(data['torrent_url']), data['torrent_index'], engine)
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            return True
        except:
            return False

    if '1' in addon.getSetting('engine'):
        try:
### проверить индекс и выбор серии
            purl ="plugin://plugin.video.elementum/play?uri={}&oindex={}".format(quote(data['torrent_url']), data['torrent_index'])
            item = xbmcgui.ListItem(path=purl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            return True
        except:
            return False

    if '2' in addon.getSetting('engine'):
        try:
            url = 'file:///{}'.format(data['torrent_url'].replace('\\','/'))
            index = get_index(data['torrent_url'], data['torrent_index'])
            ddir = addon.getSetting('t2h_ddir') or data['download_dir']
            buffer = int(addon.getSetting('t2h_preload'))
            play_t2h(uri=url,file_id=index,preload_size=buffer,download_path=ddir)
            return True
        except:
            return False

    if '3' in addon.getSetting('engine'):
        try:
            url = torrent2magnet(data['torrent_url'])
            index = get_index(data['torrent_url'], data['torrent_index'])
            import torrserver_player
            torrserver_player.Player(
                torrent=url,
                sort_index=index,
                host=addon.getSetting('ts_host'),
                port=addon.getSetting('ts_port'))            
            return True
        except:
            return False