# -*- coding: utf-8 -*-

from library.manage import os
from library.manage import xbmc

from library.manage import library_path
from library.manage import database_path
from library.manage import addon
from library.manage import site_url

def clean_dir(serial_id=None):
    if not serial_id:
        return
    
    serial_dir = os.path.join(library_path, serial_id)

    if not os.path.isdir(serial_dir):
        return
    
    for item in os.listdir(serial_dir):
        full_path = os.path.join(serial_dir, item)
        os.remove(full_path)

    try:
        os.rmdir(serial_dir)
    except:
        pass

    return

def tvshow_update(serial_id=None):
    if serial_id:
        full_path = os.path.join(library_path, serial_id, '')
    else:
        full_path = library_path

    xbmc.executebuiltin('UpdateLibrary("video", {}, "true")'.format(full_path))
    return

def get_serialinfo(serial_id):
    from database import DataBase
    db = DataBase(database_path)
    del DataBase

    serial_info = db.obtain_nfo(serial_id=serial_id)
    db.end()

    return serial_info

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
            clean_dir(serial_id=serial_info['serial_id'])
        except:
            pass

        if not os.path.exists(serial_dir):
            os.mkdir(serial_dir)

        serial_nfo = os.path.join(serial_dir, 'tvshow.nfo')
        with open(serial_nfo, 'wb') as write_file:
            write_file.write(tvshowdetails)
        return True
    except:
        return False

def create_seriesdetails(serial_info):
    serial_dir = os.path.join(library_path, serial_info['serial_id'])

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
                
                if '0' in addon.getSetting('tvshows_imagemod'):
                    file_thumb = 'https://static.lostfilm.top/Images/{}/Posters/e_{}_{}.jpg'.format(serial_info['image_id'], season, episode)
                elif '1' in addon.getSetting('tvshows_imagemod'):
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

def update():
    if not 'true' in addon.getSetting('update_library'):
        return

    import time

    try:
        library_time = float(addon.getSetting('library_time'))
    except:
        library_time = 0

    try:
        update_time = int(addon.getSetting('update_librarytime')) * 60 * 60
    except:
        update_time = 43200

    if time.time() - library_time > update_time:
        library_items = os.listdir(library_path)

        if len(library_items) < 1:
            return

        for item in library_items:
            try:
                serial_info = get_serialinfo(serial_id=item)

                if create_tvshowdetails(serial_info=serial_info):
                    if create_seriesdetails(serial_info=serial_info):
                        tvshow_update(serial_id=item)

                xbmc.log(str('SUCCESS'), xbmc.LOGFATAL)
            except:
                continue

        addon.setSetting('library_time', str(time.time()))
    return