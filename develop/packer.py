# -*- coding: utf-8 -*-

import os
import shutil
import hashlib
import gc

def md5_generator(file_path):
    with open(file_path, 'rb') as open_file:
        data = hashlib.md5(open_file.read())
        data = data.hexdigest()
        
    with open('{}.md5'.format(file_path), 'wb') as open_file:
        open_file.write(data.encode('utf-8'))

def packing(base_name, root_dir, base_dir):
    shutil.make_archive(base_name = destination,
                        format = 'zip',
                        root_dir = develop_dir,
                        base_dir = develop_plugin)
    md5_generator('{}.zip'.format(destination))
    return

def xml_rebuild():
    full_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n\n'

    plugins = [
        os.path.join(develop_dir, 'plugin.niv.animeportal'),
        os.path.join(develop_dir, 'plugin.niv.lostfilm')
        ]

    repo_dir = [release_dir, matrix_dir]
    
    for plugin in plugins:
        plugin_path = os.path.join(develop_dir, plugin)
                
        develop_xml = os.path.join(plugin_path, 'addon.xml')
                
        if os.path.isfile(develop_xml):
            with open(develop_xml, 'r') as open_file:
                xml_data = open_file.read()
                
            xml_data = xml_data.splitlines()

            for line in xml_data:
                if '<?xml' in line:
                    continue
                if '<icon>' in line:
                    line = line.replace('resources/media/', '')
                if '<fanart>' in line:
                    line = line.replace('resources/media/', '')
                full_xml = '{}{}\n'.format(full_xml, line)
                
        full_xml = '{}\n'.format(full_xml)
        
    full_xml = '{}{}'.format(full_xml, '</addons>')
    
    release_xml = full_xml.replace('<!-- <requires> -->', '<requires>\n    <import addon="xbmc.python" version="2.26.0" />\n  </requires>')
    matrix_xml = full_xml.replace('<!-- <requires> -->', '<requires>\n    <import addon="xbmc.python" version="3.0.0" />\n  </requires>')

    with open(os.path.join(release_dir, 'addons.xml'), 'w') as open_file:
            open_file.write(release_xml)
    md5_generator(os.path.join(release_dir, 'addons.xml'))
    
    with open(os.path.join(matrix_dir, 'addons.xml'), 'w') as open_file:
        open_file.write(matrix_xml)
    md5_generator(os.path.join(matrix_dir, 'addons.xml'))
    
    return

def release_path(develop_name):
    result = []
    
    repos = [release_dir, matrix_dir]

    for repo in repos:
        plug_path = os.path.join(repo, develop_name)
        result.append(plug_path)
        
    return result

develop_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.split(develop_dir)[0]
release_dir = os.path.join(root_dir, 'release')
matrix_dir = os.path.join(root_dir, 'matrix')

develop_plugins = ['plugin.niv.animeportal','plugin.niv.lostfilm']

for develop_plugin in develop_plugins:
    plugin_path = os.path.join(develop_dir, develop_plugin)

    if not os.path.isdir(plugin_path):
        continue

    xml_path = os.path.join(plugin_path, 'addon.xml')
    
    if not os.path.isfile(xml_path):
        continue

    with open(xml_path, 'r') as open_file:
        data = open_file.read()
    
    version = data[data.find('" version="')+11:data.find('" provider')]
    package_name = '{}-{}'.format(develop_plugin, version)
    rel_path = release_path(develop_plugin)

    for act_path in rel_path:
        destination = os.path.join(act_path, package_name)
        
        if not os.path.isfile('{}.zip'.format(destination)):
            packing(base_name=destination, root_dir=develop_dir, base_dir=develop_plugin)

xml_rebuild()