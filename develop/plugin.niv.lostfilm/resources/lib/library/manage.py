# # -*- coding: utf-8 -*-

import os
import utility

import xbmc
import xbmcaddon
import xbmcvfs

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)
    
addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

try:
    database_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/database/lostfilms.db'))
    library_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/'))
    source_path = utility.fs_enc(xbmc.translatePath('special://userdata/sources.xml'))
    icon = utility.fs_enc(xbmc.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png'))
    mediadb_path = utility.fs_enc(xbmc.translatePath('special://database'))
except:
    database_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/database/lostfilms.db')
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
site_url = addon.getSetting('mirror_0')
current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))
current_url = addon.getSetting(current_mirror)

if not current_url:
    pass
else:
    site_url =  current_url
#========================#========================#========================#
def create_source():
    from library.create_source import Sources
    sources = Sources(media_type='video', source_path=source_path)
    del Sources

    if sources.add_source(label=label, library_path=library_path, icon=icon):
        sources.normalize_xml()

        from library.create_mediadb import MediaDatabase
        media_database = MediaDatabase(mediadb_path=mediadb_path, library_path=library_path)
        del MediaDatabase

        if media_database.add_dbsource():
            media_database.close()
            return True
    
    return False  
#========================#========================#========================#
def create_tvshows(serial_id):
    from library.create_tvshows import TVShows
    tvshows = TVShows()
    del TVShows

    tvshows.serial_info = tvshows.get_serialinfo(serial_id=serial_id)
    if tvshows.create_tvshowdetails():
        if tvshows.create_seriesdetails():
            tvshows.tvshow_update(serial_id=serial_id)
            return True

    return False
#========================#========================#========================#
def update_tvshows():
    from library.create_tvshows import TVShows
    tvshows = TVShows()
    tvshows.update()
    del TVShows
    return