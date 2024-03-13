# -*- coding: utf-8 -*-

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)

db_content = {'uniqueid':"""CREATE TABLE uniqueid (
    uniqueid_id INTEGER PRIMARY KEY,
    media_type  TEXT,
    tmdb       TEXT,
    imdb        TEXT,
    kinopoisk TEXT)""",

    'movie': """CREATE TABLE movie (
    idMedia INTEGER Primary Key,
    title TEXT,
    originaltitle TEXT,
    plot TEXT,
    tagline TEXT,
    studio TEXT,
    genre TEXT,
    country TEXT,
    credits TEXT,
    director TEXT,
    premiered TEXT,
    tag TEXT,
    mpaa TEXT,
    trailer TEXT,
    duration TEXT)""",

    'series': """CREATE TABLE series (
    idMedia INTEGER Primary Key,
    title TEXT,
    originaltitle TEXT,
    plot TEXT,
    tagline TEXT,
    studio TEXT,
    genre TEXT,
    country TEXT,
    credits TEXT,
    director TEXT,
    premiered TEXT,
    tag TEXT,
    mpaa TEXT,
    trailer TEXT,
    duration TEXT)""",

    'actor': """CREATE TABLE actor (
    actor_id INTEGER PRIMARY KEY,
    name     TEXT,
    art_urls TEXT)""",

    'actor_link':"""CREATE TABLE actor_link (
    actor_id   INTEGER,
    media_id   INTEGER,
    role       TEXT,
    cast_order INTEGER)""",

    'arts':"""CREATE TABLE arts (
    idMedia INTEGER PRIMARY KEY,
    poster_url TEXT,
    poster_preview TEXT,
    landscape_url TEXT,
    landscape_preview TEXT,
    fanart_url TEXT,
    fanart_preview TEXT,
    clearlogo_url TEXT,
    clearlogo_preview TEXT)""",
    }


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
        # self.cu.execute('SELECT COUNT(1) FROM sqlite_master WHERE type=\'table\' AND name=\'movie\'')
        # self.c.commit()

        # if self.cu.fetchone()[0] == 0:

        #     self.cu.execute(db_movie)
        #     self.c.commit()
        #     self.cu.execute('CREATE UNIQUE INDEX i_i ON movie (title)')
        #     self.c.commit()

        for i in db_content:
            self.cu.execute("SELECT COUNT(1) FROM sqlite_master WHERE type='table' AND name='{}'".format(i))
            self.c.commit()

            if self.cu.fetchone()[0] == 0:
                self.cu.execute(db_content[i])
                self.c.commit()

    def get_idSet(self, unique_imdb):
        self.cu.execute('SELECT uniqueid_id, media_type, tmdb, imdb, kinopoisk FROM uniqueid WHERE imdb=?', (unique_imdb,))
        self.c.commit()
        res = self.cu.fetchone()
        ids = {'uniqueid_id': res[0], 'media_type': res[1], 'tmdb': res[2], 'imdb':res[3], 'kinopoisk': res[4]}
        return ids
    
    def imdb_in_db(self, unique_imdb):
        self.cu.execute('SELECT COUNT(1) FROM uniqueid WHERE imdb=?', (unique_imdb,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def actor_in_db(self, unique_name):
        self.cu.execute('SELECT COUNT(1) FROM actor WHERE name=?', (unique_name,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def get_actorId(self, unique_name):
        self.cu.execute('SELECT actor_id FROM actor WHERE name=?', (unique_name,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def get_mediaId(self, imdb_id):
        self.cu.execute('SELECT uniqueid_id FROM uniqueid WHERE imdb=?', (imdb_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def get_arts(self, unique_set):
        self.cu.execute('SELECT poster_url, poster_preview, landscape_url, landscape_preview, fanart_url, fanart_preview, clearlogo_url, clearlogo_preview FROM arts WHERE idMedia=?', (unique_set['uniqueid_id'],))
        self.c.commit()
        res = self.cu.fetchone()

        arts = {
            'original': {
                'poster': res[0],
                'landscape': res[2],
                'fanart': res[4],
                'clearlogo': res[6],
                'thumb': res[0]
            },
            'preview': {
                'poster': res[1],
                'landscape': res[3],
                'fanart': res[5],
                'clearlogo': res[7],
                'thumb': res[1]
            }
        }

        return arts

    def get_content(self, unique_set):
        request_string = 'SELECT title, originaltitle, plot, tagline, studio, genre, country, credits, director, premiered, tag, mpaa, trailer, duration FROM {} WHERE idMedia=?'.format(
            unique_set['media_type'])

        self.cu.execute(request_string, (unique_set['uniqueid_id'],))
        self.c.commit()
        res = self.cu.fetchone()

        info = {
            'title': res[0],
            'originaltitle': res[1],
            'plot': res[2],
            'tagline': res[3],
            'studio': res[4].split(' / '),
            'genre': res[5].split(' / '),
            'country': res[6].split(' / '),
            'credits': res[7].split(' / '),
            'director': res[8].split(' / '),
            'premiered': res[9],
            'tag': res[10].split(' / '),
            'mpaa': res[11],
            'trailer': res[12],
            'duration': int(res[13])
            }

        return info

    def get_actors(self, actor_id):
        self.cu.execute('SELECT name, art_urls FROM actor WHERE actor_id=?', (actor_id,))
        self.c.commit()
        return self.cu.fetchone()

    def get_cast(self, unique_set):
        self.cu.execute('SELECT actor_id, role, cast_order FROM actor_link WHERE media_id=?', (unique_set['uniqueid_id'],))
        self.c.commit()
        result = self.cu.fetchall()

        cast = []
        for node in result:
            actor = self.get_actors(actor_id=node[0])
            cast.append({'name': actor[0],'role': node[1], 'thumbnail': actor[1],'order':node[2]})            

        return cast

    def get_metainfo(self, unique_imdb):
        unique_set = self.get_idSet(unique_imdb=unique_imdb)

        info = self.get_content(unique_set=unique_set)
        arts = self.get_arts(unique_set=unique_set)
        cast = self.get_cast(unique_set=unique_set)

        meta_info = {
            'uniqueid': unique_set,
            'info': info,
            'arts': arts,
            'cast': cast
        }

        return meta_info   
############################################################################################################################################
    def insert_uniqueid(self, unique_id):
        ids = {'media_type':'', 'tmdb':'','imdb':'','kinopoisk':''}
        ids.update(unique_id)
        
        self.cu.execute('INSERT INTO uniqueid (media_type, tmdb, imdb, kinopoisk) VALUES (?,?,?,?)', (
            ids['media_type'], ids['tmdb'], ids['imdb'], ids['kinopoisk']))
        self.c.commit()
        return

    def insert_media(self, meta_info, media_id, uniqueids):
        info = {
            'title':'',
            'originaltitle':'',
            'plot':'',
            'tagline':'',
            'studio':'',
            'genre':'',
            'country':'',
            'credits':'',
            'director':'',
            'premiered':'',
            'tag':'',
            'mpaa':'',
            'trailer':'',
            'duration': 0,
            }
        info.update(meta_info)

        for i in info:
            if info[i] == None:
                info[i] = ''
            if type(info[i]) == list:
                info[i] = ' / '.join(info[i])

        req_string = 'INSERT INTO {} (idMedia, title, originaltitle, plot, tagline, studio, genre, country, credits, director, premiered, tag, mpaa, trailer, duration) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'.format(
            uniqueids['media_type'])
        self.cu.execute(req_string, (media_id, info['title'],info['originaltitle'],info['plot'],info['tagline'],info['studio'],info['genre'],info['country'],info['credits'],info['director'],info['premiered'],info['tag'],info['mpaa'],info['trailer'],info['duration']))
        self.c.commit()

        return

    def insert_arts(self, media_id, arts, update=False):
        info_arts = {
            'poster_url': '',
            'poster_preview': '',
            'landscape_url': '',
            'landscape_preview': '',
            'fanart_url': '',
            'fanart_preview': '',
            'clearlogo_url':'',
            'clearlogo_preview':''
            }
        
        for i in arts:
            if len(arts[i]) > 0:
                for a in arts[i][0]:
                    x = '{}_{}'.format(i,a)
                    if x in info_arts:
                        info_arts[x] = arts[i][0][a]
        if update:
            self.cu.execute('UPDATE arts SET poster_url=?, poster_preview=?, landscape_url=?, landscape_preview=?, fanart_url=?, fanart_preview=?, clearlogo_url=?, clearlogo_preview=? WHERE idMedia=?',
                            (info_arts['poster_url'],info_arts['poster_preview'],info_arts['landscape_url'],info_arts['landscape_preview'],info_arts['fanart_url'],info_arts['fanart_preview'],info_arts['clearlogo_url'],info_arts['clearlogo_preview'], media_id))
        else:
            self.cu.execute('INSERT INTO arts (idMedia, poster_url, poster_preview, landscape_url, landscape_preview, fanart_url, fanart_preview, clearlogo_url, clearlogo_preview) VALUES (?,?,?,?,?,?,?,?,?)', 
                                (media_id,info_arts['poster_url'],info_arts['poster_preview'],info_arts['landscape_url'],info_arts['landscape_preview'],info_arts['fanart_url'],info_arts['fanart_preview'],info_arts['clearlogo_url'],info_arts['clearlogo_preview']))
        self.c.commit()

        return

    def insert_cast(self, media_id, cast):
        for node in cast:
            if not self.actor_in_db(unique_name=node['name']):
                self.cu.execute('INSERT INTO actor (name, art_urls) VALUES (?,?)',
                                (node['name'], node['thumbnail']))
                self.c.commit()

            actor_id = self.get_actorId(node['name'])

            self.cu.execute('INSERT INTO actor_link (actor_id, media_id, role, cast_order) VALUES (?,?,?,?)', 
                            (actor_id, media_id, node['role'], node['order']))
            self.c.commit()

        return
############################################################################################################################################
    def update_uniqueid(self, unique_id):
        ids = {'media_type': '', 'tmdb': '', 'imdb': '', 'kinopoisk': ''}
        ids.update(unique_id)
        
        self.cu.execute('UPDATE uniqueid SET media_type=?,tmdb=?,kinopoisk=?  WHERE imdb=?', (
            ids['media_type'], ids['tmdb'], ids['kinopoisk'], ids['imdb']))
        
        self.c.commit()
        return
    
    def update_media(self, meta_info, media_id, uniqueids):
        info = {
            'title':'',
            'originaltitle':'',
            'plot':'',
            'tagline':'',
            'studio':'',
            'genre':'',
            'country':'',
            'credits':'',
            'director':'',
            'premiered':'',
            'tag':'',
            'mpaa':'',
            'trailer':'',
            'duration': 0,
            }
        info.update(meta_info)

        for i in info:
            if info[i] == None:
                info[i] = ''
            if type(info[i]) == list:
                info[i] = ' / '.join(info[i])

        req_string = 'UPDATE {} SET title = ?, originaltitle = ?, plot = ?, tagline = ?, studio = ?, genre = ?, country = ?, credits = ?, director = ?, premiered = ?, tag = ?, mpaa = ?, trailer = ?, duration = ? WHERE idMedia = ?'.format(
            uniqueids['media_type'])
        self.cu.execute(req_string, (info['title'],info['originaltitle'],info['plot'],info['tagline'],info['studio'],info['genre'],info['country'],info['credits'],info['director'],info['premiered'],info['tag'],info['mpaa'],info['trailer'],info['duration'], media_id))
        self.c.commit()

        return
    
    def update_arts(self, media_id, arts):
        info_arts = {
            'poster_url': '',
            'poster_preview': '',
            'landscape_url': '',
            'landscape_preview': '',
            'fanart_url': '',
            'fanart_preview': '',
            'clearlogo_url':'',
            'clearlogo_preview':''
            }
        
        for i in arts:
            if len(arts[i]) > 0:
                for a in arts[i][0]:
                    x = '{}_{}'.format(i,a)
                    if x in info_arts:
                        info_arts[x] = arts[i][0][a]

        self.cu.execute('UPDATE arts SET poster_url=?, poster_preview=?, landscape_url=?, landscape_preview=?, fanart_url=?, fanart_preview=?, clearlogo_url=?, clearlogo_preview=? WHERE idMedia=?',
                        (info_arts['poster_url'],info_arts['poster_preview'],info_arts['landscape_url'],info_arts['landscape_preview'],info_arts['fanart_url'],info_arts['fanart_preview'],info_arts['clearlogo_url'],info_arts['clearlogo_preview'], media_id))
        self.c.commit()

        return


    def update_cast(self, media_id, cast):
        for node in cast:
            if self.actor_in_db(unique_name=node['name']):
                self.cu.execute('UPDATE actor SET art_urls=? WHERE name=?', (node['thumbnail'], node['name']))
                self.c.commit()

                actor_id = self.get_actorId(node['name'])

                self.cu.execute('UPDATE actor_link SET role=?, cast_order=? WHERE actor_id=? AND media_id=?', (node['role'], node['order'], actor_id, media_id))
                self.c.commit()
            else:
                self.cu.execute('INSERT INTO actor (name, art_urls) VALUES (?,?)',(node['name'], node['thumbnail']))
                self.c.commit()

                actor_id = self.get_actorId(node['name'])

                self.cu.execute('INSERT INTO actor_link (actor_id, media_id, role, cast_order) VALUES (?,?,?,?)',(actor_id, media_id, node['role'], node['order']))
                self.c.commit()

        return

    # def get_actor_link(self, actor_id, media_id):
    #     self.cu.execute('SELECT actor_id, media_id, role, cast_order FROM actor_link WHERE actor_id=? AND media_id=?', (actor_id, media_id,))
    #     self.c.commit()

    #     res = self.cu.fetchall()
    #     result = []
                
    #     for i in res:
    #         actor_link = {
    #             'actor_id': i[0],
    #             'media_id': i[1],
    #             'role': i[2],
    #             'cast_order': i[3]
    #             }
    #         result.append(actor_link)
        
    #     return result
############################################################################################################################################
    def insert_content(self, meta_info):
        uniqueids = meta_info['uniqueids']
        info = meta_info['info']
        cast = meta_info['cast']
        arts = meta_info['available_art']

        self.insert_uniqueid(unique_id=uniqueids)
        media_id = self.get_mediaId(imdb_id=uniqueids['imdb'])

        self.insert_media(meta_info=info, media_id=media_id, uniqueids=uniqueids)
        self.insert_arts(media_id=media_id, arts=arts)
        self.insert_cast(media_id=media_id, cast=cast)
                
        return

    def update_content(self, meta_info):
        uniqueids = meta_info['uniqueids']
        media_id = self.get_mediaId(imdb_id=uniqueids['imdb'])

        info = meta_info['info']
        cast = meta_info['cast']
        arts = meta_info['available_art']

        self.update_media(meta_info=info, media_id=media_id, uniqueids=uniqueids)
        self.update_arts(media_id=media_id, arts=arts)
        self.update_cast(media_id=media_id, cast=cast)

        return