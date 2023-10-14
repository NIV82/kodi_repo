# -*- coding: utf-8 -*-

import os
import utility

import xbmc
import xbmcvfs

version = xbmc.getInfoLabel('System.BuildVersion')[:2]
try:
    version = int(version)
except:
    version = 0

if version >= 19:
    icon = xbmcvfs.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png')
    library_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/')
    source_path = xbmcvfs.translatePath('special://userdata/sources.xml')
else:
    icon = utility.fs_enc(xbmc.translatePath('special://home/addons/plugin.niv.lostfilm/resources/media/icon.png'))
    library_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/'))
    source_path = utility.fs_enc(xbmc.translatePath('special://userdata/sources.xml'))

label='LostFilm - NIV'

class Sources:
    def __init__(self):
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

        try:
            from mediadb import MediaDatabase
            mdb = MediaDatabase()
            mdb.add_dbsource()
            mdb.end()
            del MediaDatabase
        except Exception as e:
            xbmc.log("Lostfilm Sources Error Start ======================", level=xbmc.LOGFATAL)
            xbmc.log(e.encode('utf-8'), level=xbmc.LOGFATAL)
            xbmc.log("Lostfilm Sources Error End ======================", level=xbmc.LOGFATAL)