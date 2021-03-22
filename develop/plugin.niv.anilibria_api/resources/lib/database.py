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
            self.cu.execute('CREATE TABLE anime_db(anime_id INTEGER NOT NULL PRIMARY KEY, title_ru TEXT, title_en TEXT, genres TEXT, voice TEXT, translator TEXT, editing TEXT, decor TEXT, timing TEXT, year INTEGER (4), description TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON anime_db (anime_id)')
            self.c.commit()

    def add_anime(self, anime_id, title_ru, title_en, genres, voice, translator, editing, decor, timing, year, description):
        self.cu.execute('INSERT INTO anime_db (anime_id, title_ru, title_en, genres, voice, translator, editing, decor, timing, year, description) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                        (anime_id, title_ru, title_en, genres, voice, translator, editing, decor, timing, year, description))
        self.c.commit()

    # def create_tables(self):
    #     self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'anime_db\'')
    #     self.c.commit()
    #     if self.cu.fetchone()[0] == 0:
    #         self.cu.execute('CREATE TABLE anime_db(anime_id INTEGER NOT NULL PRIMARY KEY, title_ru TEXT, title_en TEXT, year INTEGER (4), genre TEXT, dubbing TEXT, timing TEXT, subs TEXT, plot TEXT, anime_url TEXT)')
    #         self.c.commit()
    #         self.cu.execute('CREATE UNIQUE INDEX i_i ON anime_db (anime_id)')
    #         self.c.commit()

    # def add_anime(self, anime_id, title_ru, title_en, year, genre, dubbing, timing, subs, plot, anime_url):
    #     self.cu.execute('INSERT INTO anime_db (anime_id, title_ru, title_en, year, genre, dubbing, timing, subs, plot, anime_url) VALUES (?,?,?,?,?,?,?,?,?,?)',
    #                     (anime_id, title_ru, title_en, year, genre, dubbing, timing, subs, plot, anime_url))
    #     self.c.commit()

    def is_anime_in_db(self, anime_url):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_url=?', (anime_url,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def get_cover(self, anime_url):
        self.cu.execute('SELECT anime_id FROM anime_db WHERE anime_url=?', (anime_url,))
        self.c.commit()
        data = self.cu.fetchone()
        return data[0]
    
    def get_anime(self, anime_url):
        self.cu.execute('SELECT year, genre, dubbing, timing, subs, plot FROM anime_db WHERE anime_url=?', (anime_url,))
        self.c.commit()
        return self.cu.fetchone()

    def get_title(self, anime_url):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_url=?', (anime_url,))
        self.c.commit()
        return self.cu.fetchone()

### ========================================================================================================
###    api.anilibria   =====================================================================================
### ========================================================================================================

    def get_title_api(self, anime_id):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_anime_api(self, anime_id):
        self.cu.execute('SELECT genres, voice, translator, editing, decor, timing, year, description FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
    
    def is_anime_in_db_api(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True