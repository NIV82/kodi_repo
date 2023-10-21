# -*- coding: utf-8 -*-

import os
import time
import utility

import xbmc
import xbmcaddon
import xbmcvfs

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

def create_site_url():
    site_url = addon.getSetting('mirror_0')
    current_mirror = 'mirror_{}'.format(addon.getSetting('mirror_mode'))
    current_url = addon.getSetting(current_mirror)

    if not current_url:
        return site_url
    else:
        return current_url

def create_serial_info(serial_id):
    from database import DataBase
    db = DataBase(database_path)
    del DataBase

    serial_info = db.obtain_nfo(serial_id=serial_id)
    db.end()

    return serial_info

def clean_dir(path=None):
    if not path:
        return
    
    if not os.path.isdir(path):
        return
    
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        os.remove(full_path)

    try:
        os.rmdir(path)
    except:
        pass

    return

def update(serial_id=None):
    if serial_id:
        full_path = os.path.join(library_path, serial_id, '')
    else:
        full_path = library_path

    xbmc.executebuiltin('UpdateLibrary("video", {}, "true")'.format(full_path))
    return

# def update():
#     xbmc.executebuiltin('UpdateLibrary("video", {}, "true")'.format(library_path))
#     return

def create_tvshowdetails(serial_info):
    try:
        tvshowdetails = u'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<tvshow>\n    <title>{}</title>\n    <plot>{}</plot>\n    <genre>{}</genre>\n    <premiered>{}</premiered>\n    <studio>{}</studio>\n{}\n    <thumb>{}</thumb>\n</tvshow>'.format(
            serial_info['title_ru'],
            serial_info['plot'],
            serial_info['genre'],
            serial_info['premiered'],
            serial_info['studio'],
            serial_info['actors'],
            'https://static.lostfilm.top/Images/{}/Posters/shmoster_s1.jpg'.format(serial_info['image_id'])
            )
        
        try:
            tvshowdetails = tvshowdetails.encode('utf-8')
        except:
            pass

        serial_dir = os.path.join(library_path, serial_info['serial_id'])

        try:
            clean_dir(path=serial_dir)
        except:
            pass
        
        if not os.path.exists(serial_dir):
            os.mkdir(serial_dir)

        serial_nfo = os.path.join(serial_dir, 'tvshow.nfo')
        with open(serial_nfo, 'wb') as write_file:
            write_file.write(tvshowdetails)
    except:
        return False
    
    return True

def create_seriesdetails(serial_info):    
    serial_dir = os.path.join(library_path, serial_info['serial_id'])

    site_url = create_site_url()
    serial_url = '{}series/{}/seasons/'.format(site_url, serial_info['serial_id'])

    from network import get_web
    html = get_web(url=serial_url)

    if not html:
        return False

    data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
    data_array = data_array.split('<td class="alpha">')
    data_array.reverse()

    try:
        for data in data_array:
            try:
                if not 'PlayEpisode(' in data:
                    continue

                se_code = data[data.find('episode="')+9:]
                se_code = se_code[:se_code.find('"')]

                season = int(se_code[len(se_code)-6:len(se_code)-3])
                season_mod = 's{:>02}'.format(season)

                episode = int(se_code[len(se_code)-3:len(se_code)])
                episode_mod = 'e{:>02}'.format(episode)

                episode_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
                if '<br>' in episode_title:
                    episode_title = episode_title[episode_title.find('">')+2:episode_title.find('<br>')].strip()        
                if '<br />' in episode_title:
                    episode_title = episode_title[episode_title.find('<div>')+5:episode_title.find('<br />')].strip()
                if not episode_title:
                    continue
                    
                file_name = '{}.{}.{}'.format(serial_info['serial_id'], season_mod, episode_mod)
                strm_content = 'plugin://plugin.niv.lostfilm/?mode=play_part&id={}&param={}'.format(serial_info['serial_id'], se_code)

                try:
                    strm_content = strm_content.encode('utf-8')
                except:
                    pass

                file_thumb = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_info['image_id'], season)

                episodedetails = u'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<episodedetails>\n    <title>{}</title>\n    <season>{}</season>\n    <episode>{}</episode>\n    <plot>{}</plot>\n    <thumb>{}</thumb>\n</episodedetails>'.format(
                    episode_title, season, episode, serial_info['plot'], file_thumb)

                try:
                    episodedetails = episodedetails.encode('utf-8')
                except:
                    pass
                
                nfo_path = os.path.join(serial_dir, '{}.nfo'.format(file_name))
                with open(nfo_path, 'wb') as write_file:
                    write_file.write(episodedetails)

                strm_path = os.path.join(serial_dir, '{}.strm'.format(file_name))
                with open(strm_path, 'wb') as write_file:
                    write_file.write(strm_content)

            except:
                continue
    except:
        return False

    return True

def create_update_library():
    if 'true' in addon.getSetting('update_library'):
        pass
    else:
        return

    try:
        library_time = float(addon.getSetting('library_time'))
    except:
        library_time = 0

    try:
        update_time = int(addon.getSetting('update_librarytime')) * 60 * 60
    except:
        update_time = 43200

    if time.time() - library_time > update_time:
        addon.setSetting('library_time', str(time.time()))

        library_items = os.listdir(library_path)

        if len(library_items) < 1:
            return

        for item in library_items:
            try:
                create_tvshows(serial_id=item)
            except:
                continue

        xbmc.executebuiltin('UpdateLibrary("video", {}, "true")'.format(library_path))
    return

def create_tvshows(serial_id):
    if not serial_id:
        return False

    try:
        serial_info = create_serial_info(serial_id)
    except:
        return False

    if create_tvshowdetails(serial_info=serial_info):
        if create_seriesdetails(serial_info=serial_info):
            return True
    
    return False