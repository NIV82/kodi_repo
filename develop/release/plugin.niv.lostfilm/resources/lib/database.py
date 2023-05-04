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
        self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'serials_db\'')
        self.c.commit()

        if self.cu.fetchone()[0] == 0:
            self.cu.execute('CREATE TABLE serials_db (serial_id TEXT NOT NULL PRIMARY KEY, title_ru TEXT, title_en TEXT, aired_on TEXT, genres TEXT, directors TEXT, producers TEXT, writers TEXT, studios TEXT, country TEXT, description TEXT, image_id INTEGER, actors TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON serials_db (serial_id)')
            self.c.commit()

    def insert_content(self, serial_id, content):
        self.cu.execute('INSERT INTO serials_db (serial_id, title_ru, title_en, aired_on, genres, directors, producers, writers, studios, country, description, image_id, actors) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (serial_id, content['title_ru'], content['title_en'], content['aired_on'], content['genres'], content['directors'], content['producers'], content['writers'], content['studios'], content['country'], content['description'], content['image_id'], content['actors']))
        self.c.commit()

    def update_content(self, serial_id, content):
        self.cu.execute('UPDATE serials_db SET title_ru=?, title_en=?, aired_on=?, genres=?, directors=?, producers=?, writers=?, studios=?, country=?, description=?, image_id=?, actors=? WHERE serial_id=?', (
            content['title_ru'], 
            content['title_en'], 
            content['aired_on'], 
            content['genres'], 
            content['directors'], 
            content['producers'], 
            content['writers'], 
            content['studios'], 
            content['country'],
            content['description'], 
            content['image_id'], 
            content['actors'], 
            serial_id)
            )
        self.c.commit()

    def content_in_db(self, serial_id):
        self.cu.execute('SELECT COUNT(1) FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def obtain_content(self, serial_id):
        self.cu.execute('SELECT aired_on, genres, directors, producers, writers, studios, country, description FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()

        serial_info = self.cu.fetchone()

        director = ''
        if serial_info[2]:
            director = serial_info[2]

            if serial_info[3]:
                director = u'{}*{}'.format(director, serial_info[3])

        content = {
            'premiered': serial_info[0],
            'genre': serial_info[1].split('*'),
            'director': director.split('*'),
            'writer': serial_info[4].split('*'),
            'studio': serial_info[5].split('*'),
            'country': serial_info[6].split(','),
            'plot': serial_info[7]
            }

        del serial_info
        return content

    def obtain_cast(self, serial_id):
        self.cu.execute('SELECT actors FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def obtain_image_id(self, serial_id):
        self.cu.execute('SELECT image_id FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def obtain_serials_id(self):
        self.cu.execute('SELECT title_ru, serial_id, image_id, title_en FROM serials_db')
        self.c.commit()
        return self.cu.fetchall()