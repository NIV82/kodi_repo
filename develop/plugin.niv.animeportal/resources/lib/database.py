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
        self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'anime_db\'')
        self.c.commit()
        if self.cu.fetchone()[0] == 0:
            self.cu.execute('CREATE TABLE anime_db (anime_id TEXT NOT NULL PRIMARY KEY, anime_tid TEXT, title_ru TEXT, title_en TEXT, title_jp TEXT, kind TEXT, status TEXT, episodes INTEGER, aired_on INTEGER, released_on INTEGER, rating TEXT, duration INTEGER, genres TEXT, writer TEXT, director TEXT, description TEXT, dubbing TEXT, translation TEXT, timing TEXT, sound TEXT, mastering TEXT, editing TEXT, other TEXT, country TEXT, studios TEXT, image TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON anime_db (anime_id)')
            self.c.commit()

    # def add_anime(self, anime_id, anime_tid='', title_ru='', title_en='', title_jp='', kind='', status='', episodes='', aired_on='', released_on='', rating='', duration='', genres='', writer='', director='', description='', dubbing='', translation='', timing='', sound='', mastering='', editing='', other='', country='', studios='', image=''):
    #     self.cu.execute('INSERT INTO anime_db (anime_id, anime_tid, title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
    #                     (anime_id, anime_tid, title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image))
    #     self.c.commit()

    # def update_anime(self, anime_id, title_ru='', title_en='', title_jp='', kind='', status='', episodes='', aired_on='', released_on='', rating='', duration='', genres='', writer='', director='', description='', dubbing='', translation='', timing='', sound='', mastering='', editing='', other='', country='', studios='', image=''):
    #     self.cu.execute('UPDATE anime_db SET title_ru=?, title_en=?, title_jp=?, kind=?, status=?, episodes=?, aired_on=?, released_on=?, rating=?, duration=?, genres=?, writer=?, director=?, description=?, dubbing=?, translation=?, timing=?, sound=?, mastering=?, editing=?, other=?, country=?, studios=?, image=? WHERE anime_id=?',
    #                     (title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image, anime_id))
    #     self.c.commit()

    def add_anime(self, anime_id, anime_tid='', title_ru='', title_en='', title_jp='', kind='', status='', episodes='', aired_on='', released_on='', rating='', duration='', genres='', writer='', director='', description='', dubbing='', translation='', timing='', sound='', mastering='', editing='', other='', country='', studios='', image='', update=False):
        if not update:
            self.cu.execute('INSERT INTO anime_db (anime_id, anime_tid, title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                            (anime_id, anime_tid, title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image))
        else:
            self.cu.execute('UPDATE anime_db SET title_ru=?, title_en=?, title_jp=?, kind=?, status=?, episodes=?, aired_on=?, released_on=?, rating=?, duration=?, genres=?, writer=?, director=?, description=?, dubbing=?, translation=?, timing=?, sound=?, mastering=?, editing=?, other=?, country=?, studios=?, image=? WHERE anime_id=?',
                            (title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image, anime_id))
        self.c.commit()
    
    def anime_in_db(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def get_tid(self, anime_id):
        self.cu.execute('SELECT anime_tid FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def get_title(self, anime_id):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_cover(self, anime_id):
        self.cu.execute('SELECT image FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def get_anime(self, anime_id):
        self.cu.execute('SELECT kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios FROM anime_db WHERE anime_id=?', (anime_id,))            #'SELECT genres, director, writer, description, dubbing, translation, timing, country, studios, aired_on FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
#========================#========================#========================#========================#========================#     
class Anilibria_DB:
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
            self.cu.execute('CREATE TABLE anime_db(anime_id INTEGER NOT NULL PRIMARY KEY, title_ru TEXT, title_en TEXT, genres TEXT, voices TEXT, year INTEGER (4), description TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON anime_db (anime_id)')
            self.c.commit()

    def add_anime(self, anime_id, title_ru, title_en, genres, voices, year, description):
        self.cu.execute('INSERT INTO anime_db (anime_id, title_ru, title_en, genres, voices, year, description) VALUES (?,?,?,?,?,?,?)',
                        (anime_id, title_ru, title_en, genres, voices, year, description))
        self.c.commit()

    def is_anime_in_db(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True
    
    def get_title(self, anime_id):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_anime(self, anime_id):
        self.cu.execute('SELECT genres, voices, year, description FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
#========================#========================#========================#========================#========================#
class Anistar_DB:
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
            self.cu.execute('CREATE TABLE anime_db(anime_id INTEGER NOT NULL PRIMARY KEY, title_ru TEXT, title_en TEXT, year INTEGER (4), genre TEXT, director TEXT, author TEXT, plot TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON anime_db (anime_id)')
            self.c.commit()

    def add_anime(self, anime_id, title_ru, title_en, year, genre, director, author, plot):
        self.cu.execute('INSERT INTO anime_db (anime_id, title_ru, title_en, year, genre, director, author, plot) VALUES (?,?,?,?,?,?,?,?)',
                        (anime_id, title_ru, title_en, year, genre, director, author, plot))
        self.c.commit()

    def is_anime_in_db(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True
    
    def get_anime(self, anime_id):
        self.cu.execute('SELECT year, genre, director, author, plot FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()
    
    def get_title(self, anime_id):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()

#========================#========================#========================#========================#========================#
class Animedia_DB:
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
        
#========================#========================#========================#========================#========================#

class ShizaProject_DB:
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
            self.cu.execute('CREATE TABLE anime_db(anime_id TEXT PRIMARY KEY UNIQUE NOT NULL, shiki_id INTEGER, title_ru TEXT, title_en TEXT, plot TEXT, countries TEXT, aired TEXT, studios TEXT, genres TEXT, authors TEXT, dubbing TEXT, mastering TEXT, timing TEXT, other TEXT, translation TEXT, editing TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON anime_db (anime_id)')
            self.c.commit()

    def add_anime(self, anime_id, shiki_id, title_ru, title_en, plot, countries, aired, studios, genres, authors, dubbing, mastering, timing, other, translation, editing):
        self.cu.execute('INSERT INTO anime_db (anime_id, shiki_id, title_ru, title_en, plot, countries, aired, studios, genres, authors, dubbing, mastering, timing, other, translation, editing) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (anime_id, shiki_id, title_ru, title_en, plot, countries, aired, studios, genres, authors, dubbing, mastering, timing, other, translation, editing))
        self.c.commit()

    def is_anime_in_db(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def get_title(self, anime_id):
        self.cu.execute('SELECT title_ru, title_en FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_anime(self, anime_id):
        self.cu.execute('SELECT plot, countries, aired, studios, genres, authors, dubbing, mastering, timing, other, translation, editing FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return self.cu.fetchone()