# -*- coding: utf-8 -*-

import sqlite3
from library.manage import os

class MediaDatabaseException(Exception):
    pass

class MediaDatabase:
    def __init__(self, mediadb_path=None, library_path=None):        
        self.mediadb_path = mediadb_path
        if self.mediadb_path is None:
            raise MediaDatabaseException('mediadb_path not exist')
        
        if not os.path.exists(self.mediadb_path):
            raise MediaDatabaseException('database not exist')
        
        self.library_path = library_path
        if self.library_path is None:
            raise MediaDatabaseException('library_path not exist')

        self.connection = sqlite3.connect(self.mediadb_path, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def path_in_db(self, library_path):
        self.cursor.execute("SELECT * FROM path WHERE strPath=?", (library_path,))
        return bool(self.cursor.fetchone())

    def add_dbsource(self, strContent='tvshows', strScraper='metadata.local', scanRecursive=0, useFolderNames=0, strSettings=None, noUpdate=0, exclude=0):
        try:
            if self.path_in_db(library_path=self.library_path):
                self.connection.execute("UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, useFolderNames=?, strSettings=?, noUpdate=?, exclude=? WHERE strPath=?",
                    (strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, self.library_path))
            else:
                self.connection.execute("INSERT INTO path (strPath, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))",
                    (self.library_path, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude))

            return True
        except:
            raise MediaDatabaseException('ERROR')