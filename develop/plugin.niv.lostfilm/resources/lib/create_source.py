# -*- coding: utf-8 -*-

import os
import utility

import xbmc
import xbmcvfs

try:
    library_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/'))
    source_path = utility.fs_enc(xbmc.translatePath('special://userdata/sources.xml'))
    icon = utility.fs_enc(xbmc.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png'))
    mediadb_path = utility.fs_enc(xbmc.translatePath('special://database'))
except:
    library_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/')
    source_path = xbmcvfs.translatePath('special://userdata/sources.xml')
    icon = xbmcvfs.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png')
    mediadb_path = xbmcvfs.translatePath('special://database')

def create_xmlsource():
    label='LostFilm - NIV'
    try:
        if not os.path.exists(source_path):
            with open(source_path, 'w') as write_file:
                write_file.write(
                    '<sources>\n    <programs>\n        <default pathversion="1"></default>\n    </programs>\n    <video>\n        <default pathversion="1"></default>\n    </video>\n    <music>\n        <default pathversion="1"></default>\n    </music>\n    <pictures>\n        <default pathversion="1"></default>\n    </pictures>\n    <files>\n        <default pathversion="1"></default>\n    </files>\n    <games>\n        <default pathversion="1"></default>\n    </games>\n</sources>'
                    )
                
        with open(source_path, 'r') as read_file:
            xml_data = read_file.read()
        
        if not label in xml_data:
            node_original = xml_data[xml_data.find('<video>'):xml_data.find('</video>')+8]
                    
            if '<default pathversion="1"></default>' in node_original:
                vid_modified = node_original.replace(
                '<default pathversion="1"></default>', '<default pathversion="1"></default>\n        <source>\n            <name>{}</name>\n            <path pathversion="1">{}</path>\n            <thumbnail pathversion="1">{}</thumbnail>\n            <allowsharing>true</allowsharing>\n        </source>'.format(label, library_path , icon)
                )

            if '<default pathversion="1" />' in node_original:
                vid_modified = node_original.replace(
                '<default pathversion="1" />', '<default pathversion="1" />\n        <source>\n            <name>{}</name>\n            <path pathversion="1">{}</path>\n            <thumbnail pathversion="1">{}</thumbnail>\n            <allowsharing>true</allowsharing>\n        </source>'.format(label, library_path , icon)
                )

            xml_data = xml_data.replace(node_original, vid_modified)

            with open(source_path, 'w') as write_file:
                write_file.write(xml_data)
    except:
        return False

    return True

def create_dbsource():
    try:
        import media_database
        media_database.add_dbsource()
        media_database.end()
    except:
        return False

    return True

def create_sources():
    if create_xmlsource():
        if create_dbsource():
            return True