# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from library.manage import os
from library.manage import source_path
from library.manage import label
from library.manage import library_path
from library.manage import icon

class Sources(object):
    def __init__(self, media_type=None):
        self.media_type = media_type
        if self.media_type == None:
            return False

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
        
        self.sources_xml = ET.parse(source_path)
        self.sources = None

    def normalize_xml(self):
        elem = self.sources_xml.getroot()
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
        tree.write(source_path, encoding="utf-8", xml_declaration=True)
        return

    def get_sources(self):
        elem = self.sources_xml.getroot()
        self.xml_tree = ET.ElementTree(elem)

        sources = {}
        select_source = self.xml_tree.find(self.media_type)

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

    def bool_path_exist(self):
        if library_path is None:
            return None
        
        sources = self.get_sources()

        for source in sources.items():
            sc_path = source[1][1]
            
            if library_path == sc_path:
                return True

        return False

    def dict_path_exist(self):
        if library_path is None:
            return None
        
        sources = self.get_sources()
        exist_sources = {}

        for source in sources.values():
            sc_name = source[0]
            sc_path = source[1]

            if library_path == sc_path:
                exist_sources[sc_name] = source

        del sources                
        return exist_sources

    def add_source(self):
        try:
            select_source = self.sources_xml.find(self.media_type)

            source = ET.SubElement(select_source, 'source')
            ET.SubElement(source, 'name').text = label
            ET.SubElement(source, 'path', {'pathversion': '1'}).text = library_path
            ET.SubElement(source, 'thumbnail', {'pathversion': '1'}).text = icon
            ET.SubElement(source, 'allowsharing').text = 'true'
            self.sources_xml.write(source_path, 'utf-8', xml_declaration=True)

            return True
        except:
            return False