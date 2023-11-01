# -*- coding: utf-8 -*-

from library.manage import library_path
from library.manage import mediadb_path

import sqlite3 as db
c = db.connect(database=mediadb_path, detect_types=db.PARSE_DECLTYPES, isolation_level=None)
del db
cu = c.cursor()

def end():
    c.close()
    
def add_dbsource(strContent='tvshows', strScraper='metadata.local', scanRecursive=0, useFolderNames=0, strSettings=None, noUpdate=0, exclude=0):
    try:
        cu.execute("SELECT * FROM path WHERE strPath=?", (library_path,))
        path_exist = bool(cu.fetchone())

        if path_exist:
            cu.execute("UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, useFolderNames=?, strSettings=?, noUpdate=?, exclude=? WHERE strPath=?",
                (strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, library_path))
        else:
            cu.execute("INSERT INTO path (strPath, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))",
                (library_path, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude))
        
        end()
        return True
    except:
        return False

def remove_source():
    return