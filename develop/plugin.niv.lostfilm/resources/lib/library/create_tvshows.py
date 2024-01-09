# -*- coding: utf-8 -*-

from library.manage import os
from library.manage import xbmc
from library.manage import site_url
from library.manage import addon
from library.manage import library_path
from library.manage import database_path
from library.manage import net

import xml.etree.ElementTree as ET

tvshow_info = None

def create_serialdir(serial_id=None):
    if serial_id is None:
        return False
    
    serial_dir = os.path.join(library_path, serial_id)
    if not os.path.exists(serial_dir):
        os.mkdir(serial_dir)
    return

def clean_serialdir(serial_id=None, remove_dir=False):
    if serial_id is None:
        return False

    serial_dir = os.path.join(library_path, serial_id)

    if not os.path.isdir(serial_dir):
        return
        
    for item in os.listdir(serial_dir):
        full_path = os.path.join(serial_dir, item)
        os.remove(full_path)

    if remove_dir:
        os.rmdir(serial_dir)

    return

def normalize_xml(xml_path):
    sources_xml = ET.parse(xml_path)

    elem = sources_xml.getroot()
    tree = ET.ElementTree(elem)

    def indent(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    indent(elem=elem)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    return

def get_serialinfo(serial_id=None):
    if serial_id is None:
        return False

    from database import DataBase
    db = DataBase(database_path)
    del DataBase

    serial_info = db.obtain_nfo(serial_id=serial_id)
    db.end()

    return serial_info

def tvshow_update(serial_id):
    full_path = os.path.join(library_path, serial_id, '')
    xbmc.executebuiltin('UpdateLibrary("video", {}, "true")'.format(full_path))
    return

def tvshow_allupdate():
    xbmc.executebuiltin('UpdateLibrary("video")')
    return

def create_tvshowdetails(serial_id):
    if not serial_id:
        return

    serial_dir = os.path.join(library_path, serial_id)
    if not os.path.exists(serial_dir):
        create_serialdir(serial_id=serial_id)
    else:
        clean_serialdir(serial_id=serial_id)

    if tvshow_info is None:
        serial_info = get_serialinfo(serial_id=serial_id)
    else:
        serial_info = tvshow_info

    tvshow_nfo = os.path.join(serial_dir, 'tvshow.nfo')
    file_thumb = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s1.jpg'.format(serial_info['image_id'])

    tvshow = ET.Element('tvshow')
    ET.SubElement(tvshow, 'title').text = serial_info['title_ru']
    ET.SubElement(tvshow, 'plot').text = serial_info['plot']
    ET.SubElement(tvshow, 'genre').text = serial_info['genre']
    ET.SubElement(tvshow, 'premiered').text = serial_info['premiered']
    ET.SubElement(tvshow, 'studio').text = serial_info['studio']

    for actor_node in serial_info['actors']:
        actor = ET.SubElement(tvshow, 'actor')
        ET.SubElement(actor, 'name').text = actor_node['name']
        ET.SubElement(actor, 'role').text = actor_node['role']
        ET.SubElement(actor, 'thumb').text = actor_node['thumb']

        ET.SubElement(tvshow, 'thumb').text = file_thumb

    etree = ET.ElementTree(tvshow)
    etree.write(tvshow_nfo, encoding='utf-8', xml_declaration=True)
    normalize_xml(tvshow_nfo)

    return

def create_seriesdetails(serial_id):
    if tvshow_info is None:
        serial_info = get_serialinfo(serial_id=serial_id)
    else:
        serial_info = tvshow_info

    serial_dir = os.path.join(library_path, serial_id)
    serial_url = '{}series/{}/seasons/'.format(site_url, serial_id)

    html = net.get_html(url=serial_url)

    if not html:
        return False

    data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
    data_array = data_array.split('<td class="alpha">')
    data_array.reverse()

    for data in data_array:
        try:
            data = data[:data.find('<td class="placeholder">')]

            if not 'PlayEpisode(' in data:
                continue

            se_code = data[data.find('episode="')+9:]
            se_code = se_code[:se_code.find('"')]

            season = int(se_code[len(se_code)-6:len(se_code)-3])
            episode = int(se_code[len(se_code)-3:len(se_code)])

            episode_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
            if '<br>' in episode_title:
                episode_title = episode_title[episode_title.find('">')+2:episode_title.find('<br>')].strip()        
            if '<br />' in episode_title:
                episode_title = episode_title[episode_title.find('<div>')+5:episode_title.find('<br />')].strip()
            if not episode_title:
                continue
                            
            file_name = '{0}.s{1:>02}.e{2:>02}'.format(serial_id, season, episode)
            file_thumb = 'https://static.lostfilm.top/Images/{}/Posters/e_{}_{}.jpg'.format(serial_info['image_id'], season, episode)

            episodedetails = ET.Element('episodedetails')
            ET.SubElement(episodedetails, 'title').text = episode_title
            ET.SubElement(episodedetails, 'season').text = str(season)
            ET.SubElement(episodedetails, 'episode').text = str(episode)
            ET.SubElement(episodedetails, 'plot').text = serial_info['plot']
            ET.SubElement(episodedetails, 'thumb').text = file_thumb

            etree = ET.ElementTree(episodedetails)

            nfo_path = os.path.join(serial_dir, '{}.nfo'.format(file_name))

            etree.write(nfo_path, encoding='utf-8', xml_declaration=True)
            normalize_xml(nfo_path)

            strm_content = 'plugin://plugin.niv.lostfilm/?mode=play_part&id={}&param={}'.format(serial_id, se_code)

            try:
                strm_content = strm_content.encode('utf-8')
            except:
                pass

            strm_path = os.path.join(serial_dir, '{}.strm'.format(file_name))
            with open(strm_path, 'wb') as write_file:
                write_file.write(strm_content)
        except:
            continue
    return

def test():
    xbmc.log(str(tvshow_info), xbmc.LOGFATAL)
    return

def force_update():
    global tvshow_info
    
    library_items = os.listdir(library_path)

    if len(library_items) < 1:
        return

    for item in library_items:
        tvshow_info = get_serialinfo(serial_id=item)

        try:
            create_tvshowdetails(serial_id=item)
            create_seriesdetails(serial_id=item)
        except:
            continue

    tvshow_allupdate()
    
    return

def auto_update():
    global tvshow_info

    if not 'true' in addon.getSetting('update_library'):
        return

    import time

    try:
        library_time = float(addon.getSetting('library_time'))
    except:
        library_time = 0

    update_time = 43200

    if time.time() - library_time > update_time:
        library_items = os.listdir(library_path)

        if len(library_items) < 1:
            return

        for item in library_items:
            tvshow_info = get_serialinfo(serial_id=item)

            try:
                create_tvshowdetails(serial_id=item)
                create_seriesdetails(serial_id=item)
            except:
                continue

        tvshow_allupdate()

        addon.setSetting('library_time', str(time.time()))
    return