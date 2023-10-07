# -*- coding: utf-8 -*-
import os

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)

class Sources:
    def __init__(self, source_path, mediadb_path):
        self.source_path = source_path
        self.mediadb_path = mediadb_path

        if not os.path.exists(self.source_path):
            with open(self.source_path, 'w') as write_file:
                write_file.write(
                    '<sources>\n    <programs>\n        <default pathversion="1"></default>\n    </programs>\n    <video>\n        <default pathversion="1"></default>\n    </video>\n    <music>\n        <default pathversion="1"></default>\n    </music>\n    <pictures>\n        <default pathversion="1"></default>\n    </pictures>\n    <files>\n        <default pathversion="1"></default>\n    </files>\n    <games>\n        <default pathversion="1"></default>\n    </games>\n</sources>'
                    )

    def add_source(self, library_path, label, icon):
        #xml_data = ''
        with open(self.source_path, 'r') as read_file:
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
            
            with open(self.source_path, 'w') as write_file:
                write_file.write(xml_data)

        from mediadb import MediaDatabase
        self.mdb = MediaDatabase(
            mediadb_path=self.mediadb_path,
            library_path=library_path
            )
        del MediaDatabase

        self.mdb.add_dbsource()

        self.mdb.end()