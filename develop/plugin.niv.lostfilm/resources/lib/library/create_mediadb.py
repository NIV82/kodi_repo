# -*- coding: utf-8 -*-

import sqlite3
from library.manage import os
from library.manage import mediadb_path
from library.manage import library_path

class MediaDatabase:
    def __init__(self):
        if not os.path.exists(mediadb_path):
            return False

        self.connection = sqlite3.connect(mediadb_path, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def path_in_db(self, library_path):
        self.cursor.execute("SELECT * FROM path WHERE strPath=?", (library_path,))
        return bool(self.cursor.fetchone())

    def add_dbsource(self, strContent='tvshows', strScraper='metadata.local', scanRecursive=0, useFolderNames=0, strSettings=None, noUpdate=0, exclude=0):
        try:
            if self.path_in_db(library_path=library_path):
                self.connection.execute("UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, useFolderNames=?, strSettings=?, noUpdate=?, exclude=? WHERE strPath=?",
                    (strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, library_path))
            else:
                self.connection.execute("INSERT INTO path (strPath, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))",
                    (library_path, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude))

            return True
        except:
            return False