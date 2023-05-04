# -*- coding: utf-8 -*-

import gc
import os
import sys

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

addon = xbmcaddon.Addon(id='plugin.niv.animeportal')
xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

if not addon.getSetting('settings'):
    try:
        addon.setSetting('settings','true')
    except:
        pass

def data_print(data):
    xbmc.log(str(data), xbmc.LOGFATAL)

# =======================================================================================
# try:
#     xbmcaddon.Addon('script.module.requests')
# except:
#     xbmcgui.Dialog().notification(
#         heading='Установка Библиотеки',
#         message='script.module.requests',
#         icon=None,time=3000,sound=False
#         )
#     xbmc.executebuiltin('RunPlugin("plugin://script.module.requests")')
# =======================================================================================
if not sys.argv[2]:
    portal_list = ('anidub', 'anilibria', 'animedia', 'anistar', 'shizaproject')
    active_portal = []

    for portal in portal_list:
        if 'true' in addon.getSetting('use_{}'.format(portal)):
            if 'anidub' in portal:
                anidub_mode = ['anidub_o', 'anidub_t']
                portal = anidub_mode[int(addon.getSetting('anidub_mode'))]
            active_portal.append(portal)

    if len(active_portal) < 1:
        li = xbmcgui.ListItem(
            '[B][COLOR=white]Нет Активных Сайтов[/COLOR][/B]')
        xbmcplugin.addDirectoryItem(
            int(sys.argv[1]), url=sys.argv[0], listitem=li, isFolder=True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    if len(active_portal) == 1:
        sys.argv[2] = '?portal={}'.format(active_portal[0])

    if len(active_portal) > 1:
        for portal in active_portal:
            label = portal.replace('_t', ' torrent').replace('_o', ' online')
            li = xbmcgui.ListItem('[B][COLOR=white]{}[/COLOR][/B]'.format(label.upper()))
            info = {'title': portal.upper(), 'tvshowtitle': portal.upper()}
            li.setInfo(type='video', infoLabels=info)
            url = '{}?{}'.format(sys.argv[0], urlencode(
                {'mode': 'main_part', 'portal': portal}))

            if 'animedia' in portal:
                li.addContextMenuItems(
                    [('[COLOR=white]Обновить Зеркало[/COLOR]',
                      'Container.Update("plugin://plugin.niv.animeportal/?node=actual_url&portal=animedia")')]
                )

            xbmcplugin.addDirectoryItem(
                int(sys.argv[1]), url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

if 'anidub_o' in sys.argv[2]:
    from anidub_o import Anidub
    anidub = Anidub()
    anidub.execute()
    del Anidub

if 'anidub_t' in sys.argv[2]:
    from anidub_t import Anidub
    anidub = Anidub()
    anidub.execute()
    del Anidub

if 'anilibria' in sys.argv[2]:
    from anilibria import Anilibria
    anilibria = Anilibria()
    anilibria.execute()
    del Anilibria

if 'anistar' in sys.argv[2]:
    from anistar import Anistar
    anistar = Anistar()
    anistar.execute()
    del Anistar

if 'animedia' in sys.argv[2]:
    # if 'actual_url' in params['node']:
    #     addon.setSetting('animedia_auth', 'false')
    #     addon.setSetting('animedia_mirror_1', '')

    from animedia import Animedia
    animedia = Animedia()
    animedia.execute()
    del Animedia

if 'shizaproject' in sys.argv[2]:
    from shizaproject import Shiza
    shiza = Shiza()
    shiza.execute()
    del Shiza

gc.collect()
