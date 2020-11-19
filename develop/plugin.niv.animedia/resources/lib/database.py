# -*- coding: utf-8 -*-

class DBTools:
    def __init__(self, data_file):
        import sqlite3 as db
        self.c = db.connect(database=data_file)
        self.c.text_factory = str
        del db
        self.cu = self.c.cursor()
        self.create_tables()

    def end(self):
        self.c.close()

    def create_tables(self):
        self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'anime_db\'')
        self.c.commit()
        if self.cu.fetchone()[0] == 0:
            self.cu.execute('CREATE TABLE anime_db (anime_id TEXT PRIMARY KEY UNIQUE NOT NULL, title_ru TEXT, title_en TEXT, genre TEXT, year INTEGER (4), studio TEXT, director TEXT, author TEXT, plot TEXT, cover TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX ani_index ON anime_db (anime_id)')
            self.c.commit()

    def is_anime_in_db(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def get_title(self, anime_id):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
    
    def get_cover(self, anime_id):
        self.cu.execute('SELECT cover FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
    
    def get_anime(self, anime_id):
        self.cu.execute('SELECT genre, year, studio, director, author, plot FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
    
    def add_anime(self, anime_id, title_ru, title_en, genre, year, studio, director, author, plot, cover):
        self.cu.execute('INSERT INTO anime_db (anime_id, title_ru, title_en, genre, year, studio, director, author, plot, cover) VALUES (?,?,?,?,?,?,?,?,?,?)',
                        (anime_id, title_ru, title_en, genre, year, studio, director, author, plot, cover))
        self.c.commit()