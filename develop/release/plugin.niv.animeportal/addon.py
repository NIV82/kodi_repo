# -*- coding: utf-8 -*-

import gc
import os
import sys

import xbmcgui
import xbmcplugin
import xbmcaddon

try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.niv.animeportal')

if not addon.getSetting('settings'):
    try:
        addon.setSetting('settings','true')
    except:
        pass

if not sys.argv[2]:
    portal_list = ('anidub', 'anilibria', 'animedia', 'anistar', 'shizaproject')
    active_portal = []

    for portal in portal_list:
        if 'true' in addon.getSetting('use_{}'.format(portal)):
            active_portal.append(portal)

    if len(active_portal) < 1:
        li = xbmcgui.ListItem('[B]Нет Активных Сайтов[/B]')
        xbmcplugin.addDirectoryItem(handle, url=sys.argv[0], listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(handle)

    if len(active_portal) == 1:
        sys.argv[2] = '?portal={}'.format(active_portal[0])

    if len(active_portal) > 1:
        for portal in active_portal:
            li = xbmcgui.ListItem('[B]{}[/B]'.format(portal.upper()))
            info = {'title': portal.upper(), 'tvshowtitle': portal.upper()}
            li.setInfo(type='video', infoLabels=info)
            url = '{}?{}'.format(sys.argv[0], urlencode(
                {'mode': 'main_part', 'portal': portal}))

            xbmcplugin.addDirectoryItem(
                handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(handle)

if 'anidub' in sys.argv[2]:
    if '0' in addon.getSetting('anidub_mode'):
        if 'anidub_t' in sys.argv[2]:
            import adt
            adt.start()
        else:
            import ado
            ado.start()
    if '1' in addon.getSetting('anidub_mode'):
        if 'anidub_o' in sys.argv[2]:
            import ado
            ado.start()
        else:
            import adt
            adt.start()

if 'anilibria' in sys.argv[2]:
    if '0' in addon.getSetting('alv_mode'):
        import alv1
        alv1.start()
    if '1' in addon.getSetting('alv_mode'):
        import alv3
        alv3.start()

if 'anistar' in sys.argv[2]:
    import asv
    asv.start()

if 'animedia' in sys.argv[2]:
    import am
    am.start()

if 'shizaproject' in sys.argv[2]:
    import sp
    sp.start()

gc.collect()