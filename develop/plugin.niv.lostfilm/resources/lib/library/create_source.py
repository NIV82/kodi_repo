# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from library.manage import os
from library.manage import source_path
from library.manage import label
from library.manage import library_path
from library.manage import icon
from library.manage import media_type

if not os.path.exists(source_path):
    sources = ET.Element('sources')
    programs = ET.SubElement(sources, 'programs')
    default_node = ET.SubElement(programs, 'default', {'pathversion': '1'})
    video = ET.SubElement(sources, 'video')
    default_node = ET.SubElement(video, 'default', {'pathversion': '1'})
    music = ET.SubElement(sources, 'music')
    default_node = ET.SubElement(music, 'default', {'pathversion': '1'})
    pictures = ET.SubElement(sources, 'pictures')
    default_node = ET.SubElement(pictures, 'default', {'pathversion': '1'})
    files = ET.SubElement(sources, 'files')
    default_node = ET.SubElement(files, 'default', {'pathversion': '1'})
    games = ET.SubElement(sources, 'games')
    default_node = ET.SubElement(games, 'default', {'pathversion': '1'})
    etree = ET.ElementTree(sources)
    etree.write(source_path, encoding='utf-8', xml_declaration=True)

sources_xml = ET.parse(source_path)
sources_elem = sources_xml.getroot()
sources_tree = ET.ElementTree(sources_elem)

def get_sources():
    sources = {}
    select_source = sources_tree.find(media_type)

    for node in select_source.findall('source'):
        name = ''
        if node.find('name') is not None:
            name = node.find('name').text

        path = ''
        if node.find('path') is not None:
            path = node.find('path').text

        thumb = ''
        if node.find('thumbnail') is not None:
            thumb = node.find('thumbnail').text

        if name in sources.keys():
            name = '{} - copy'.format(name)
                
        sources[name] = [name,path,thumb]
    return sources

def bool_path_exist():
    sources = get_sources()

    for source in sources.items():
        sc_path = source[1][1]
        if library_path == sc_path:
            return True
        return False

def dict_path_exist():
    sources = get_sources()
    exist_sources = {}

    for source in sources.values():
        sc_name = source[0]
        sc_path = source[1]

        if library_path == sc_path:
            exist_sources[sc_name] = source

    del sources                
    return exist_sources

def normalize_xml():
    def indent(sources_elem, level=0):
        i = "\n" + level*"  "
        if len(sources_elem):
            if not sources_elem.text or not sources_elem.text.strip():
                sources_elem.text = i + "  "
            if not sources_elem.tail or not sources_elem.tail.strip():
                sources_elem.tail = i
            for sources_elem in sources_elem:
                indent(sources_elem, level+1)
            if not sources_elem.tail or not sources_elem.tail.strip():
                sources_elem.tail = i
        else:
            if level and (not sources_elem.tail or not sources_elem.tail.strip()):
                sources_elem.tail = i

    indent(sources_elem=sources_elem)
    sources_tree.write(source_path, encoding="utf-8", xml_declaration=True)
    return

def add_source():
    select_source = sources_xml.find(media_type)

    source = ET.SubElement(select_source, 'source')
    ET.SubElement(source, 'name').text = label
    ET.SubElement(source, 'path', {'pathversion': '1'}).text = library_path
    ET.SubElement(source, 'thumbnail', {'pathversion': '1'}).text = icon
    ET.SubElement(source, 'allowsharing').text = 'true'
    sources_xml.write(source_path, 'utf-8', xml_declaration=True)

    normalize_xml()
    return