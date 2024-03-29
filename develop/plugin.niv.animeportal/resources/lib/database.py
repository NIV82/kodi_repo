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

    def anime_in_db(self, anime_id):
        self.cu.execute('SELECT COUNT(1) FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def insert_content(self, info={}):
        self.cu.execute('INSERT INTO anime_db (anime_id, anime_tid, title_ru, title_en, title_jp, kind, status, episodes, aired_on, released_on, rating, duration, genres, writer, director, description, dubbing, translation, timing, sound, mastering, editing, other, country, studios, image) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (info['anime_id'], info['anime_tid'], info['title_ru'], info['title_en'], info['title_jp'], info['kind'], info['status'], info['episodes'], info['aired_on'], info['released_on'], info['rating'], info['duration'], info['genres'], info['writer'], info['director'], info['description'], info['dubbing'], info['translation'], info['timing'], info['sound'], info['mastering'], info['editing'], info['other'], info['country'], info['studios'], info['image']))
        self.c.commit()

    def update_content(self, info={}):
        self.cu.execute('UPDATE anime_db SET anime_tid=?, title_ru=?, title_en=?, title_jp=?, kind=?, status=?, episodes=?, aired_on=?, released_on=?, rating=?, duration=?, genres=?, writer=?, director=?, description=?, dubbing=?, translation=?, timing=?, sound=?, mastering=?, editing=?, other=?, country=?, studios=?, image=? WHERE anime_id=?',
                        (info['anime_tid'], info['title_ru'], info['title_en'], info['title_jp'], info['kind'], info['status'], info['episodes'], info['aired_on'], info['released_on'], info['rating'], info['duration'], info['genres'], info['writer'], info['director'], info['description'], info['dubbing'], info['translation'], info['timing'], info['sound'], info['mastering'], info['editing'], info['other'], info['country'], info['studios'], info['image'], info['anime_id']))
        self.c.commit()
    
    def obtain_content(self, anime_id):
        self.cu.execute('SELECT aired_on, genres, country, director, writer, studios, description FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        s = self.cu.fetchone()

        content = {
            'genre': s[1].split(', '),
            'country': s[2],
            'director': s[3].split(', '),
            'writer': s[4].split(', '),
            'studio': s[5],
            'plot': s[6],
            'year': int(s[0])
            }

        del s
        return content
    
    def extend_content(self, anime_id):
        self.cu.execute('SELECT dubbing, translation, timing FROM anime_db WHERE anime_id=?', (anime_id,))
        self.c.commit()
        ex = self.cu.fetchone()

        content = ''
        if ex[0]:
            content = u'{}\nОзвучивание: {}'.format(content, ex[0])
        if ex[1]:
            content = u'{}\nПеревод: {}'.format(content, ex[1])
        if ex[2]:
            content = u'{}\nТайминг: {}'.format(content, ex[2])
            
        return content
