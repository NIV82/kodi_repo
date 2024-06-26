# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcplugin
import sys, os

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
        y = (height - h) / 2
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
        ov_image = os.path.join(xbmc.translatePath('special://masterprofile'), 'bg.png')

        ov_image_tmp = ov_image.decode('utf-8') if sys.platform == 'win32' else ov_image

        if not os.path.isfile(ov_image_tmp):
            fl = open(ov_image_tmp, 'wb')
            fl.write(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='))
            fl.close()
        return ov_image

    @staticmethod
    def get_skin_resolution():
        import xml.etree.ElementTree as Et
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

def play_t2h(handle, preload_size, uri, file_id=None, download_path=None):
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

        return 'Загружено [B]{0}[/B] MB[CR]Сиды: [B]{1}[/B][CR]Скорость: [B]{2:6.2f}[/B] Mbit/s'.format(download, seeds, speed)


    download_path = download_path or xbmc.translatePath('special://masterprofile')

    ready = False
    pre_buffer_bytes = preload_size * 1024 * 1024
    
    engine = Engine(uri, download_path=download_path)

    dialog = xbmcgui.DialogProgress()

    with closing(engine):
        engine.start(file_id)
        dialog.create('Torrent2Http', 'Запуск')
        dialog.update(0, 'Torrent2Http', 'Загрузка торрента', '')
        while not xbmc.abortRequested and not ready:
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
                
                dialog.update(100 * file_status.download / pre_buffer_bytes,
                              'Предварительная буферизация: {0} MB'.format(file_status.download / 1024 / 1024),
                              'Сиды: {0}'.format(getSeeds), 'Скорость: {0:6.2f} Mbit/s'.format(getDownloadRate))
                
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
            xbmcplugin.setResolvedUrl(handle, True, item)
            xbmc.sleep(3000)

            while not xbmc.abortRequested and player.isPlaying():
                xbmc.sleep(500)