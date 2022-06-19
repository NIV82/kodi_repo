# -*- coding: utf-8 -*-

### основа некоторых фукнций была взята из ТАМ

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

def get_index(torrent_file, index):    
    valid_media = ('.avi', '.mov', '.mp4', '.mpg', '.mpeg', '.m4v', '.mkv', '.ts', '.vob', '.wmv', '.m2ts')
    
    with open(torrent_file, 'rb') as read_file:
        torrent_data = read_file.read()
    
    import bencode
    torrent = bencode.bdecode(torrent_data)

    series = []

    if 'files' in torrent['info']:
        for i, x in enumerate(torrent['info']['files']):            
            extension = x['path'][-1][x['path'][-1].rfind('.'):]

            if extension in valid_media:
                if 'Ghostfacers.Promo' in x['path'][-1]:
                    continue                
                series.append([x['path'][-1], i])
                
        series.sort()

        real_index = series[index][1]
    else:
        real_index = 0
    
    return real_index

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
 
def selector(torrent_url, series_index='', torrent_index=''):
    if series_index:
        try:
            index = int(series_index)
        except:
            index = series_index

        if index > 0:
            index = index - 1

        index = get_index(torrent_url, index)
    
    if torrent_index:
        try:
            index = int(torrent_index)
        except:
            index = torrent_index

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