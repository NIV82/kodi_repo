# -*- coding: utf-8 -*-

import os

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)

class MediaDatabase:
    def __init__(self, mediadb_path, library_path):
        for node in os.listdir(mediadb_path):
            if 'MyVideos' in node:
                mediadb_name = node
        self.mediadb_path = os.path.join(mediadb_path, mediadb_name)
        
        import sqlite3 as db
        self.c = db.connect(database=self.mediadb_path, detect_types=db.PARSE_DECLTYPES, isolation_level=None)
        del db
        self.cu = self.c.cursor()

        self.library_path = library_path

    def end(self):
        self.c.close()

    def path_exist(self, check_path):
        self.cu.execute("SELECT * FROM path WHERE strPath=?", (check_path,))
        path_exist = bool(self.cu.fetchone())
        return path_exist
    
    def add_dbsource(self, strContent='tvshows', strScraper='metadata.local', scanRecursive=0, useFolderNames=0, strSettings=None, noUpdate=0, exclude=0):
        path_exist = self.path_exist(self.library_path)

        if path_exist:
            self.cu.execute("UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, useFolderNames=?, strSettings=?, noUpdate=?, exclude=? WHERE strPath=?",
                (strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, self.library_path))
        else:
            self.cu.execute(
                "INSERT INTO path (strPath, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))",
                (self.library_path, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude))
        return