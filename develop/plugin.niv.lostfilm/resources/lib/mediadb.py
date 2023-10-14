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
    library_path = xbmcvfs.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/')
    mediadb_path = xbmcvfs.translatePath('special://database')
else:
    library_path = utility.fs_enc(xbmc.translatePath('special://userdata/addon_data/plugin.niv.lostfilm/library/'))
    mediadb_path = utility.fs_enc(xbmc.translatePath('special://database'))

class MediaDatabase:
    def __init__(self):
        for node in os.listdir(mediadb_path):
            if 'MyVideos' in node:
                mediadb_name = node
        self.mediadb_path = os.path.join(mediadb_path, mediadb_name)
        
        import sqlite3 as db
        self.c = db.connect(database=self.mediadb_path, detect_types=db.PARSE_DECLTYPES, isolation_level=None)
        del db
        self.cu = self.c.cursor()

    def end(self):
        self.c.close()
    
    def add_dbsource(self, strContent='tvshows', strScraper='metadata.local', scanRecursive=0, useFolderNames=0, strSettings=None, noUpdate=0, exclude=0):
        self.cu.execute("SELECT * FROM path WHERE strPath=?", (library_path,))
        path_exist = bool(self.cu.fetchone())

        if path_exist:
            self.cu.execute("UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, useFolderNames=?, strSettings=?, noUpdate=?, exclude=? WHERE strPath=?",
                (strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, library_path))
        else:
            self.cu.execute(
                "INSERT INTO path (strPath, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))",
                (library_path, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude))
        return