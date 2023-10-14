# -*- coding: utf-8 -*-

import os
import time
import utility

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

addon = xbmcaddon.Addon(id='plugin.niv.lostfilm')

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

progress_bg = xbmcgui.DialogProgressBG()
#dialog = xbmcgui.Dialog()

try:
    database_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/database/lostfilms.db'))
    library_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/'))
except:
    database_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/database/lostfilms.db')
    library_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/')

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

def create_tvshowdetails(serial_info):
    if not serial_info:
        return False

    tvshowdetails = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<tvshow>\n    <title>{}</title>\n    <plot>{}</plot>\n    <genre>{}</genre>\n    <premiered>{}</premiered>\n    <studio>{}</studio>\n{}\n    <thumb>{}</thumb>\n</tvshow>'.format(
        serial_info['title_ru'],
        serial_info['plot'],
        serial_info['genre'],
        serial_info['premiered'],
        ','.join(serial_info['studio']),
        serial_info['actors'],
        'https://static.lostfilm.top/Images/{}/Posters/shmoster_s1.jpg'.format(serial_info['image_id'])
        )
    
    try:
        tvshowdetails = tvshowdetails.encode('utf-8')
    except:
        pass

    serial_dir = os.path.join(library_path, serial_info['serial_id'])
    if not os.path.exists(serial_dir):
        os.mkdir(serial_dir)

    serial_nfo = os.path.join(serial_dir, 'tvshow.nfo')
    
    with open(serial_nfo, 'wb') as write_file:
        write_file.write(tvshowdetails)

    return

def create_seriesdetails(serial_info):
    if not serial_info:
        return False
    
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
        for i, data in enumerate(data_array):
            try:
                if not 'data-code=' in data:
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
                    
                #p = int((float(i+1) / len(data_array)) * 100)

                #self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                file_name = '{}.{}.{}'.format(serial_info['serial_id'], season_mod, episode_mod)
                nfo_path = os.path.join(serial_dir, '{}.nfo'.format(file_name))

                strm_path = os.path.join(serial_dir, '{}.strm'.format(file_name))                    
                strm_content = 'plugin://plugin.niv.lostfilm/?mode=play_part&id={}&param={}'.format(serial_info['serial_id'], se_code)

                try:
                    strm_content = strm_content.encode('utf-8')
                except:
                    pass

                file_thumb = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(serial_info['image_id'], season)

                episodedetails = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<episodedetails>\n    <title>{}</title>\n    <season>{}</season>\n    <episode>{}</episode>\n    <plot>{}</plot>\n    <thumb>{}</thumb>\n</episodedetails>'.format(
                    episode_title, season, episode, serial_info['plot'], file_thumb)

                try:
                    episodedetails = episodedetails.encode('utf-8')
                except:
                    pass
                
                try:
                    with open(nfo_path, 'wb') as write_file:
                        write_file.write(episodedetails)
                except Exception as e:
                    xbmc.log(e, level=xbmc.LOGFATAL)

                try:
                    with open(strm_path, 'wb') as write_file:
                        write_file.write(strm_content)
                except Exception as e:
                    xbmc.log(e, level=xbmc.LOGFATAL)

            except Exception as e:
                xbmc.log(e, level=xbmc.LOGFATAL)
                
    except Exception as e:
        xbmc.log(e, level=xbmc.LOGFATAL)

    return

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
            
        progress_bg.create('Обновляем медиатеку')

        try:
            for i, item in enumerate(library_items):
                try:
                    p = int((float(i+1) / len(library_items)) * 100)
                    create_tvshows(serial_id=item)
                    progress_bg.update(p, 'Обрабатываем - {} | {} из {}'.format(item, i, len(library_items)))
                except Exception as e:
                    xbmc.log(e, level=xbmc.LOGFATAL)
                    pass
        except Exception as e:
            xbmc.log(e, level=xbmc.LOGFATAL)
            pass

        progress_bg.close()

    xbmc.executebuiltin('UpdateLibrary("video", "", "false")')
    
    return

def create_tvshows(serial_id):
    if not serial_id:
        return

    serial_info = create_serial_info(serial_id)

    create_tvshowdetails(serial_info=serial_info)
    create_seriesdetails(serial_info=serial_info)