# -*- coding: utf-8 -*-

from library.manage import os
from library.manage import library_path
from library.manage import source_path
from library.manage import icon
from library.manage import label

def add_source():
    try:
        if not os.path.exists(source_path):
            with open(source_path, 'w') as write_file:
                write_file.write(
                    '<sources>\n    <programs>\n        <default pathversion="1"></default>\n    </programs>\n    <video>\n        <default pathversion="1"></default>\n    </video>\n    <music>\n        <default pathversion="1"></default>\n    </music>\n    <pictures>\n        <default pathversion="1"></default>\n    </pictures>\n    <files>\n        <default pathversion="1"></default>\n    </files>\n    <games>\n        <default pathversion="1"></default>\n    </games>\n</sources>'
                    )

        with open(source_path, 'r') as read_file:
            xml_data = read_file.read()
        
        if not library_path in xml_data:
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
            # try:
            #     xml_data = xml_data.encode('utf-8')
            # except:
            #     pass

            # with open(self.source_path, 'wb') as write_file:
            #     write_file.write(xml_data)

            with open(source_path, 'w') as write_file:
                write_file.write(xml_data)
            
            return True
        else:
            return False
    except:
        return False
    
def delete_source():
    return

def edit_source():
    return

def fix_source():
    return