# # -*- coding: utf-8 -*-

import os
import utility
import time

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
    
addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')
dialog = xbmcgui.Dialog()

try:
    database_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/lostfilms.db'))
    library_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/'))
    source_path = utility.fs_enc(xbmc.translatePath('special://userdata/sources.xml'))
    icon = utility.fs_enc(xbmc.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png'))
    mediadb_path = utility.fs_enc(xbmc.translatePath('special://database'))
except:
    database_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/lostfilms.db')
    library_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/')
    source_path = xbmcvfs.translatePath('special://userdata/sources.xml')
    icon = xbmcvfs.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png')
    mediadb_path = xbmcvfs.translatePath('special://database')
#========================#========================#========================#
mediadb_name = ''
for node in os.listdir(mediadb_path):    
    if 'MyVideos' in node:
        mediadb_name = node

mediadb_path = os.path.join(mediadb_path, mediadb_name)
#========================#========================#========================#
library_mode = addon.getSetting('userpath')

if not '0' in library_mode:
    if addon.getSetting('userpath_{}'.format(library_mode)):
        library_path = addon.getSetting('userpath_{}'.format(library_mode))

try:
    if not os.path.exists(library_path):
        os.makedirs(library_path)
except:
    pass
#========================#========================#========================#
label = addon.getSetting('library_label')
#========================#========================#========================#
media_type = 'video'
#========================#========================#========================#
site_url = addon.getSetting('mirror_0')
current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))
current_url = addon.getSetting(current_mirror)

if not current_url:
    pass
else:
    site_url =  current_url
#========================#========================#========================#
if '0' in addon.getSetting('unblock'):
    proxy_data = None
elif '1' in addon.getSetting('unblock'):
    if addon.getSetting('proxy'):
        proxy_data = {'https': addon.getSetting('proxy')}
    else:
        proxy_data = {'https': 'http://185.85.121.12:1088'}
else:
    proxy_data = {'https': 'http://185.85.121.12:1088'}
#========================#========================#========================#
from network import WebTools
net = WebTools(proxy_data=proxy_data)
del WebTools
#========================#========================#========================#
def create_source():
    import library.create_source as create_source
    import library.create_mediadb as create_mediadb

    if create_source.bool_path_exist():
        dialog.notification(heading='Медиатека',message='Источник уже существует',icon=icon,time=1000,sound=False)
    else:
        create_source.add_source()

    create_mediadb.add_librarysource()
    create_mediadb.close()
    return
#========================#========================#========================#
def create_tvshows(serial_id):
    import library.create_tvshows as create_tvshows
    
    serial_dir = os.path.join(library_path, serial_id)
    if not os.path.exists(serial_dir):
        create_tvshows.create_serialdir(serial_id=serial_id)
    else:
        create_tvshows.clean_serialdir(serial_id=serial_id)

    create_tvshows.tvshow_info = create_tvshows.get_serialinfo(serial_id=serial_id)

    create_tvshows.create_tvshowdetails(serial_id=serial_id)
    create_tvshows.create_seriesdetails(serial_id=serial_id)
    create_tvshows.tvshow_allupdate()
    del create_tvshows
    
    return
#========================#========================#========================#
def update_tvshows():
    import library.create_tvshows as create_tvshows
    create_tvshows.force_update()
    return
#========================#========================#========================#
def auto_update():
    import library.create_tvshows as create_tvshows
    create_tvshows.auto_update()
    return