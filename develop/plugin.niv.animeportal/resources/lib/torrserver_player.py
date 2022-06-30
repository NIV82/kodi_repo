# coding: utf-8

from __future__ import absolute_import

#from . import engine
import torrserver_engine as engine
import xbmc, xbmcgui, xbmcplugin, time, sys

class OurDialogProgress(xbmcgui.DialogProgress):
    def create(self, heading, line1="", line2="", line3=""):
        try:
            xbmcgui.DialogProgress.create(self, heading, line1, line2, line3)
        except TypeError:
            message = line1
            if line2:
                message += '\n' + line2
            if line3:
                message += '\n' + line3
            xbmcgui.DialogProgress.create(self, heading, message)

    def update(self, percent, line1="", line2="", line3=""):
        try:
            xbmcgui.DialogProgress.update(self, int(percent), line1, line2, line3)
        except TypeError:
            message = line1
            if line2:
                message += '\n' + line2
            if line3:
                message += '\n' + line3
            xbmcgui.DialogProgress.update(self, int(percent), message)


def humanizeSize(size):
    B = u"б"
    KB = u"Кб"
    MB = u"Мб"
    GB = u"Гб"
    TB = u"Тб"
    UNITS = [B, KB, MB, GB, TB]
    HUMANFMT = "%.2f %s"
    HUMANRADIX = 1024.

    for u in UNITS[:-1]:
        if size < HUMANRADIX : return HUMANFMT % (size, u)
        size /= HUMANRADIX

    return HUMANFMT % (size,  UNITS[-1])

def _log(s):
    import sys
    def make_message(_s):
        if sys.version_info < (3, 0):
            return u'Torrserver: {0}'.format(unicode(_s)).encode('utf8')
        else:
            return 'Torrserver: {0}'.format(str(_s))

    if isinstance(s, BaseException):
        exc_type, exc_val, exc_tb = sys.exc_info()
        import traceback
        lines = traceback.format_exception(exc_type, exc_val, exc_tb, limit=10)
        for line in lines:
            xbmc.log (make_message(line))
    else:
        xbmc.log (make_message(s))


class Player(xbmc.Player):

    #def __init__(self, uri=None, path=None, data=None, index=None, sort_index=None, name=None, host=None, port=None):
    def __init__(self, torrent=None, path=None, data=None, index=None, sort_index=None, name=None, host=None, port=None):

        try:
            xbmc.Player.__init__(self)
            self.show_overlay = False

            self.fs_video = xbmcgui.Window(12005)

            x = 20
            y = 180
            w = self.fs_video.getWidth()
            h = 100

            self.info_label = xbmcgui.ControlLabel(x, y, w, h, '', textColor='0xFF00EE00', font='font16')
            self.info_label_bg = xbmcgui.ControlLabel(x+2, y+2, w, h, '', textColor='0xAA000000', font='font16')

#            from .settings import Settings
#            s = Settings()

            self.engine = engine.Engine(uri=torrent, path=path, data=data, log=_log, host=host, port=port)

            if not self.engine.success:
                dialog = xbmcgui.Dialog()
                dialog.notification('TorrServer', 'Server not started. Please start server or reconfigure settings',
                                    xbmcgui.NOTIFICATION_INFO, 5000)
                return

            ts = self.engine.torrent_stat()
            
            if len(ts['Files']) == 1:
                sort_index = 0
                index = 0
            else:
                if sort_index is None:
                    if name is not None:
                        sort_index = self.engine.get_ts_index(name)
                    elif index is not None:
                        sort_index = self.engine.id_to_files_index(index)

            self.file_id = sort_index
            self.engine.start(sort_index)

            if self.prebuffer():
                _log('Prebuffer success')

                playable_url = self.engine.play_url(sort_index)
                handle = int(sys.argv[1])
                list_item = xbmcgui.ListItem(path=playable_url)

                xbmcplugin.setResolvedUrl(handle, True, list_item)

                self.loop()

#            if not s.save_in_database:
#                _log("Remove from DB")
#                self.engine.rem()

        except BaseException as e:
            _log('************************ ERROR ***********************')
            _log(e)

    def prebuffer(self):
        pDialog = OurDialogProgress()
        pDialog.create("TorrServer", "Wait for info....")
        success = False
        counter = 0
        while True:
            if counter > 60:
                return False

            if pDialog.iscanceled() :
                pDialog.close()
                self.engine.drop()
                break

            time.sleep(0.5)
            st = self.engine.stat()
            #_log(st)

            if 'message' in st:
                counter += 1
                continue

            downSpeed = humanizeSize(st.get('DownloadSpeed', 0))
            preloadedBytes = st.get('PreloadedBytes', 0)
            preloadSize = st.get('PreloadSize', 0)
            line2 = u'S:{0} A:{1} T:{2}'.format(
                st.get('ConnectedSeeders', 0),
                st.get('ActivePeers', 0),
                st.get('TotalPeers', 0))

            line3 = u"D: {0}/сек [{1}/{2}]".format(
                downSpeed, 
                humanizeSize(preloadedBytes), 
                humanizeSize(preloadSize))

            if preloadSize > 0 and preloadedBytes > 0:
                prc = preloadedBytes * 100 / preloadSize
                if prc > 100:
                    prc = 100
                pDialog.update(prc, line2, line3)

                stat_s = st.get('TorrentStatusString')
                _log(stat_s)

                stat_id = st.get('TorrentStatus')
                if  (preloadedBytes >= preloadSize) or \
                    (prc > 0 and stat_id != 2): # 2 - 'Torrent preload'
                    success = True
                    pDialog.close()
                    break

        return success


    def _show_progress(self):
        if not self.show_overlay:
            self.fs_video.addControls([self.info_label_bg, self.info_label])
            self.show_overlay = True

    def _hide_progress(self):
        if self.show_overlay:
            self.fs_video.removeControls([self.info_label_bg, self.info_label])
            self.show_overlay = False

    def UpdateProgress(self):
        if self.show_overlay:
            info = self.engine.stat()
            try:
                fstats = info['FileStats']
                item = fstats[self.file_id]
                _log(item)
                size		= int(item['Length'])
                downloaded	= int(info['LoadedSize'])
                dl_speed	= int(info['DownloadSpeed'])
                percent = float(downloaded) * 100 / size
                if percent >= 0:
                    heading = u"{0} МB из {1} МB - {2}".format(downloaded/1024/1024, size/1024/1024, int(percent)) + r'%' + '\n'
                    if percent < 100:
                        heading += u"Скорость загрузки: {0} KB/сек\n".format(dl_speed/1024)
                        heading += u"Сиды: {0}    Пиры: {1}".format(info['ConnectedSeeders'], info['ActivePeers'])

                    self.info_label.setLabel(heading)
                    self.info_label_bg.setLabel(heading)
            except BaseException as e:
                _log('************************ ERROR ***********************')
                _log(e)
                
    def loop(self):
        while not xbmc.abortRequested and not self.isPlaying():
            xbmc.sleep(100)

        _log('************************ START Playing ***********************')
            
        while not xbmc.abortRequested and self.isPlaying():
            xbmc.sleep(1000)
            self.UpdateProgress()

        _log('************************ FINISH Playing ***********************')
            
    def __del__(self):				self._hide_progress()
    def onPlayBackPaused(self):		self._show_progress()
    def onPlayBackResumed(self):	self._hide_progress()
    def onPlayBackEnded(self):		self._hide_progress()
    def onPlayBackStopped(self):	self._hide_progress()
    
    
