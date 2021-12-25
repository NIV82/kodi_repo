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
            self.cu.execute('CREATE TABLE serials_db (serial_id TEXT NOT NULL PRIMARY KEY, title_ru TEXT, title_en TEXT, aired_on INTEGER, genres TEXT, studios TEXT, country TEXT, description TEXT, image_id INTEGER)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_i ON serials_db (serial_id)')
            self.c.commit()
            
        self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'cast_db\'')
        self.c.commit()
        if self.cu.fetchone()[0] == 0:
            self.cu.execute('CREATE TABLE cast_db (serial_id TEXT NOT NULL PRIMARY KEY, actors TEXT, directors TEXT, producers TEXT, writers TEXT)')
            self.c.commit()
            self.cu.execute('CREATE UNIQUE INDEX i_c ON cast_db (serial_id)')
            self.c.commit()

        # self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'watched_db\'')
        # self.c.commit()
        # if self.cu.fetchone()[0] == 0:
        #     self.cu.execute('CREATE TABLE watched_db(serial_id TEXT NOT NULL PRIMARY KEY, code TEXT)')
        #     self.c.commit()
        #     self.cu.execute('CREATE INDEX w_i ON watched_db (serial_id)')
        #     self.c.commit()

    # def watched_in_db(self, se_code):
    #     serial_id = se_code[:se_code.find('|')]
    #     self.cu.execute('SELECT COUNT(1) FROM watched_db WHERE serial_id=?', (serial_id,))
    #     self.c.commit()
    #     return False if '0' in str(self.cu.fetchone()[0]) else True

    # def add_watched(self, se_code):
    #     serial_code = se_code.split('|')
    #     serial_id = serial_code[0]
    #     code = '{}{}'.format(serial_code[1],serial_code[2])

    #     if self.watched_in_db(se_code):
    #         self.cu.execute('SELECT code FROM watched_db WHERE serial_id=?', (serial_id,))        
    #         self.c.commit()

    #         db_code = self.cu.fetchone()[0]
            
    #         if not code in str(db_code):
    #             new_code = '{}|{}'.format(db_code, code) if db_code else '{}'.format(code)
    #             self.cu.execute('UPDATE watched_db SET code=? WHERE serial_id=?',(new_code, serial_id))
    #             self.c.commit()
    #     else:
    #         self.cu.execute('INSERT INTO watched_db (serial_id, code) VALUES (?,?)',(serial_id, code))
    #         self.c.commit()
    #     return
    
    def add_serial(self, serial_id, title_ru='', title_en='', aired_on='', genres='', studios='', country='', description='', image_id='', update=False):
        if not update:
            self.cu.execute('INSERT INTO serials_db (serial_id, title_ru, title_en, aired_on, genres, studios, country, description, image_id) VALUES (?,?,?,?,?,?,?,?,?)',
                            (serial_id, title_ru, title_en, aired_on, genres, studios, country, description, image_id))
        else:
            self.cu.execute('UPDATE serials_db SET title_ru=?, title_en=?, aired_on=?, genres=?, studios=?, country=?, description=?, image_id=? WHERE serial_id=?',
                            (title_ru, title_en, aired_on, genres, studios, country, description, image_id, serial_id))
        self.c.commit()

    def add_cast(self, serial_id, actors='', directors='', producers='', writers='', update=False):
        if not update:
            self.cu.execute('INSERT INTO cast_db (serial_id, actors, directors, producers, writers) VALUES (?,?,?,?,?)',
                            (serial_id, actors, directors, producers, writers))
        else:
            self.cu.execute('UPDATE cast_db SET actors=?, directors=?, producers=?, writers=? WHERE serial_id=?',
                            (actors, directors, producers, writers, serial_id))
        self.c.commit()

    def serial_in_db(self, serial_id):
        self.cu.execute('SELECT COUNT(1) FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def cast_in_db(self, serial_id):
        self.cu.execute('SELECT COUNT(1) FROM cast_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True
    
    def get_title(self, serial_id):
        self.cu.execute('SELECT title_ru, title_en FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_year(self, serial_id):
        self.cu.execute('SELECT aired_on FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        year = self.cu.fetchone()[0]
        year = year[:year.find('.')]
        return year
    
    def get_serial(self, serial_id):
        self.cu.execute('SELECT aired_on, genres, studios, country, description FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_cast(self, serial_id):
        self.cu.execute('SELECT actors, directors, producers, writers FROM cast_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        
        cast_info = self.cu.fetchone()
        
        cast = {'actors': [], 'directors': [], 'writers': []}
        
        if cast_info[0]:
            role_array = cast_info[0].split('||')
            for role in role_array:
                role = role.split('|')
                if len(role) < 2:
                    role.append('')
                node = {'name':role[0], 'role':role[1]}
                cast['actors'].append(node)

        if cast_info[1]:
            cast['directors'] = cast_info[1]
            if cast_info[2]:
                cast['directors'] = '{},{}'.format(cast_info[1], cast_info[2])
            cast['directors'] = cast['directors'].split(',')
        
        if cast_info[3]:
            cast['writers'] = cast_info[3].split(',')
            
        return cast
    
    def get_image_id(self, serial_id):
        self.cu.execute('SELECT image_id FROM serials_db WHERE serial_id=?', (serial_id,))
        self.c.commit()
        return self.cu.fetchone()[0]
    
    # def get_actors(self, serial_id):
    #     self.cu.execute('SELECT actors FROM cast_db WHERE serial_id=?', (serial_id,))          
    #     self.c.commit()
                
    #     cast_info = self.cu.fetchone()
        
    #     actors = []
        
    #     role_array = cast_info[0].split('||')
    #     for role in role_array:
    #         role = role.split('|')
    #         #while len(role) < 2:
    #         if len(role) < 2:
    #             role.append('')
    #         node = {'name':role[0], 'role':role[1]}
    #         actors.append(node)
        
    #     return actors
    
    # def get_directors(self, serial_id):
    #     self.cu.execute('SELECT directors, producers FROM cast_db WHERE serial_id=?', (serial_id,))
    #     self.c.commit()
        
    #     directors = self.cu.fetchone()
    #     directors = ','.join(directors)
    #     directors = directors.split(',')
        
    #     return directors

    # def get_writers(self, serial_id):
    #     self.cu.execute('SELECT writers FROM cast_db WHERE serial_id=?', (serial_id,))          
    #     self.c.commit()
        
    #     writers = self.cu.fetchone()
    #     writers = writers[0].split(',')        
        
    #     return writers