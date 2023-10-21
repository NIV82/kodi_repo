# -*- coding: utf-8 -*-

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)

class DataBase:
    def __init__(self, data_file):
        import sqlite3 as db
        self.c = db.connect(database=data_file)
        #self.c.text_factory = str
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

        return content

    def obtain_cast(self, serial_id):
        self.cu.execute('SELECT actors FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def obtain_image_id(self, serial_id):
        self.cu.execute('SELECT image_id FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def obtain_title_ru(self, serial_id):
        self.cu.execute('SELECT title_ru FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()[0]
    
    def obtain_is_movie(self, serial_id):
        self.cu.execute('SELECT title_en FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return True if '1' in self.cu.fetchone()[0] else False
    
    def obtain_serials_id(self):
        self.cu.execute('SELECT title_ru, serial_id, image_id, title_en FROM serials_db')
        self.c.commit()
        return self.cu.fetchall()

    def obtain_nfo(self, serial_id):
        self.cu.execute('SELECT title_ru,aired_on,genres,studios,country,description,image_id,actors FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        serial_info = self.cu.fetchone()

        content = dict.fromkeys(
            ['serial_id', 'title_ru', 'premiered', 'genre', 'studio', 'country', 'plot', 'image_id', 'actors'], '')
        
        content['serial_id'] = serial_id

        if serial_info[0]:
            content['title_ru'] = u'{}'.format(serial_info[0])

        if serial_info[1]:
            content['premiered'] = u'{}'.format(serial_info[1])

        if serial_info[2]:
            content['genre'] = u'{}'.format(serial_info[2].replace('*',','))

        if serial_info[3]:
            content['studio'] = u'{}'.format(serial_info[3].replace('*',','))

        if serial_info[4]:
            content['country'] = u'{}'.format(serial_info[4].replace('*',','))

        if serial_info[5]:
            content['plot'] = u'{}'.format(serial_info[5])

        content['image_id'] = serial_info[6]

        if serial_info[7]:
            actors_array = serial_info[7].split('*')
    
            for node in actors_array:
                node = node.split('|')

                if not node[0]:
                    node[0] = 'uknown'
                if not node[1]:
                    node[1] = 'uknown'
                if node[2]:
                    node[2] = 'https://static.lostfilm.top/Names/{}/{}/{}/{}'.format(
                        node[2][1:2], node[2][2:3], node[2][3:4], node[2].replace('t','m', 1))
                
                result = u'    <actor>\n        <name>{}</name>\n        <role>{}</role>\n        <thumb>{}</thumb>\n    </actor>'.format(node[0], node[1], node[2])

                content['actors'] = u'{}\n{}'.format(content['actors'],result)

        return content