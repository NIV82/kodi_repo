# -*- coding: utf-8 -*-

import os
import shutil
import hashlib

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

    plugins = []

    for dp in develop_plugins:
        node = os.path.join(develop_dir, dp)
        plugins.append(node)

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
                if 'resources/media/' in line:
                    line = line.replace('resources/media/', '')

                full_xml = '{}{}\n'.format(full_xml, line)

        full_xml = '{}\n'.format(full_xml)

    full_xml = '{}{}'.format(full_xml, '</addons>')

    try:
        full_xml = full_xml.replace('\n\n\n','\n\n')
    except:
        pass

    with open(os.path.join(release_dir, 'addons.xml'), 'w') as open_file:
            open_file.write(full_xml)

    md5_generator(os.path.join(release_dir, 'addons.xml'))

    return

develop_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = develop_dir[:develop_dir.find(r'\develop')]
release_dir = os.path.join(root_dir, 'release')
develop_plugins = os.listdir(develop_dir)

for develop_plugin in develop_plugins:
    plugin_path = os.path.join(develop_dir, develop_plugin)

    if not os.path.isdir(plugin_path):
        continue

    if '_old' in plugin_path:
        continue

    xml_path = os.path.join(plugin_path, 'addon.xml')

    if not os.path.isfile(xml_path):
        continue

    with open(xml_path, 'r') as open_file:
        data = open_file.read()

    version = data[data.find('" version="')+11:data.find('" provider')]
    package_name = f"{develop_plugin}-{version}"
    release_path = os.path.join(release_dir, develop_plugin)
    destination = os.path.join(release_path, package_name)

    if not os.path.isfile(f"{destination}.zip"):
        packing(base_name=destination, root_dir=develop_dir, base_dir=develop_plugin)

xml_rebuild()
