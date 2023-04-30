# -*- coding: utf-8 -*-
class DataBase:
    def __init__(self, data_file):
        import sqlite3 as db
        self.c = db.connect(database=data_file)
        del db
        self.cu = self.c.cursor()
        self.create_tables()

    def end(self):
        self.c.close()

    def create_tables(self):
        self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'rhs_db\'')
        self.c.commit()
        if self.cu.fetchone()[0] == 0:
            self.cu.execute('CREATE TABLE rhs_db (serial_id INTEGER NOT NULL PRIMARY KEY, title TEXT, year INTEGER, country TEXT, duration INTEGER, director TEXT, actors TEXT, genre TEXT, mpaa TEXT, plot TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON rhs_db (serial_id)')
            self.c.commit()

    def insert_content(self, info={}):
        self.cu.execute('INSERT INTO rhs_db (serial_id, title, year, country, duration, director, actors, genre, mpaa, plot) VALUES (?,?,?,?,?,?,?,?,?,?)',
                        (info['serial_id'], info['title'], info['year'], info['country'], info['duration'], info['director'], info['actors'], info['genre'], info['mpaa'], info['plot']))
        self.c.commit()
        
    def update_content(self, info={}):
        self.cu.execute('UPDATE rhs_db SET title=?, year=?, country=?, duration=?, director=?, actors=?, genre=?, mpaa=?, plot=? WHERE serial_id=?',
                        (info['title'], info['year'], info['country'], info['duration'], info['director'], info['actors'], info['genre'], info['mpaa'], info['plot'], info['serial_id']))
        self.c.commit()
        
    def content_in_db(self, serial_id):
        self.cu.execute('SELECT COUNT(1) FROM rhs_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def obtain_content(self, serial_id):
        self.cu.execute('SELECT title, year, country, duration, director, actors, genre, mpaa, plot FROM rhs_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        s = self.cu.fetchone()
        content = {
            'title': s[0],
            'year': s[1],
            'country': s[2].split(','),
            'duration': int(s[3]),
            'director': s[4].split(','),
            'cast': s[5].split(','),
            'genre': s[6].split(','),
            'mpaa': s[7],
            'plot': s[8],
        }
        del s
        return content