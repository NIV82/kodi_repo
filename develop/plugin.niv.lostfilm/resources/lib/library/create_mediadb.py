# -*- coding: utf-8 -*-

import sqlite3
from library.manage import os
from library.manage import mediadb_path
from library.manage import library_path

connection = sqlite3.connect(mediadb_path, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
cursor = connection.cursor()

def close():
    connection.close()

def path_in_db(path):
    cursor.execute("SELECT * FROM path WHERE strPath=?", (path,))
    connection.commit()
    return bool(cursor.fetchone())

def obtain_idparent(strPath):
    cursor.execute('SELECT idPath FROM path WHERE strPath=?', (strPath,))
    connection.commit()
    return cursor.fetchone()[0]
    
def add_librarysource(strContent='tvshows', strScraper='metadata.local', scanRecursive=0, useFolderNames=0, strSettings=None, noUpdate=0, exclude=0):
    if path_in_db(path=library_path):
        connection.execute("UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, useFolderNames=?, strSettings=?, noUpdate=?, exclude=? WHERE strPath=?",
            (strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, library_path))
        connection.commit()
    else:
        connection.execute("INSERT INTO path (strPath, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))",
            (library_path, strContent, strScraper, scanRecursive, useFolderNames, strSettings, noUpdate, exclude))
        connection.commit()
    return

def add_tvshowsource(serial_id):
    strPath = os.path.join(library_path, serial_id, '')
        
    if not path_in_db(path=strPath):
        idParentPath = obtain_idparent(library_path)
        connection.execute("INSERT INTO path (strPath, dateAdded, idParentPath) VALUES (?, DATETIME('now'), ?)",
            (strPath, idParentPath))
        connection.commit()
    return