# -*- coding: utf-8 -*-

import os
import shutil
import hashlib

from os.path import dirname

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

def packages_rebuild():
    full_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n\n'

    plugins = []

    for dp in develop_plugins:
        node = os.path.join(develop_dir, dp)
        if not 'script.module' in node:
            continue
        plugins.append(node)

    for plugin in plugins:
        module_path = os.path.join(develop_dir, plugin)
        module_xml = os.path.join(module_path, 'addon.xml')

        if os.path.isfile(module_xml):
            with open(module_xml, 'r', encoding="utf-8") as read_file:
                xml_data = read_file.read()

            xml_data = xml_data.splitlines()

            for line in xml_data:
                if '<?xml' in line:
                    continue
                if 'resources/media/' in line:
                    line = line.replace('resources/media/', '')

                full_xml = f"{full_xml}{line}\n"

        full_xml = f"{full_xml}\n"

    full_xml = f"{full_xml}{'</addons>'}"
    full_xml = full_xml.replace('\n\n\n','\n\n')

    with open(os.path.join(packages_dir, 'addons.xml'), 'w', encoding="utf-8") as write_file:
        write_file.write(full_xml)

    md5_generator(os.path.join(packages_dir, 'addons.xml'))

    return

def plugin_rebuild():
    full_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n\n'

    plugins = []

    for dp in develop_plugins:
        node = os.path.join(develop_dir, dp)
        if 'script.module' in node:
            continue
        plugins.append(node)

    for plugin in plugins:
        addon_path = os.path.join(develop_dir, plugin)
        addon_xml = os.path.join(addon_path, 'addon.xml')

        if os.path.isfile(addon_xml):
            with open(addon_xml, 'r', encoding='utf-8') as read_file:
                xml_data = read_file.read()

            xml_data = xml_data.splitlines()

            for line in xml_data:
                if '<?xml' in line:
                    continue
                if 'resources/media/' in line:
                    line = line.replace('resources/media/', '')

                full_xml = f"{full_xml}{line}\n"

        full_xml = f"{full_xml}\n"

    full_xml = f"{full_xml}{'</addons>'}"
    full_xml = full_xml.replace('\n\n\n','\n\n')

    with open(os.path.join(release_dir, 'addons.xml'), 'w', encoding='utf-8') as write_file:
        write_file.write(full_xml)

    md5_generator(os.path.join(release_dir, 'addons.xml'))

    return


root_dir = dirname(dirname(__file__))
develop_dir = dirname(__file__)
release_dir = os.path.join(root_dir, 'release')
packages_dir = os.path.join(root_dir, 'packages')
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

    release_path = os.path.join(release_dir, develop_plugin)
    if 'script.module' in plugin_path:
        release_path = os.path.join(packages_dir, develop_plugin)

    version = data[data.find('" version="')+11:data.find('" provider')]
    package_name = f"{develop_plugin}-{version}"
    destination = os.path.join(release_path, package_name)

    if not os.path.isfile(f"{destination}.zip"):
        packing(base_name=destination, root_dir=develop_dir, base_dir=develop_plugin)

packages_rebuild()
plugin_rebuild()
