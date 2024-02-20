# -*- coding: utf-8 -*-

db_content = {'media': """CREATE TABLE media (
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

    'uniqueid':"""CREATE TABLE uniqueid (
    uniqueid_id INTEGER PRIMARY KEY,
    media_type  TEXT,
    tmdb       TEXT,
    imdb        TEXT)""",

    # 'actor': """CREATE TABLE actor (
    # actor_id INTEGER PRIMARY KEY,
    # name     TEXT,
    # art_urls TEXT)""",

    # 'actor_link':"""CREATE TABLE actor_link (
    # actor_id   INTEGER,
    # media_id   INTEGER,
    # role       TEXT,
    # cast_order INTEGER)""",

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

    def imdb_in_db(self, unique_imdb):
        self.cu.execute('SELECT COUNT(1) FROM uniqueid WHERE imdb=?', (unique_imdb,))
        self.c.commit()
        return False if self.cu.fetchone()[0] == 0 else True

    def get_mediaId(self, imdb_id):
        self.cu.execute('SELECT uniqueid_id FROM uniqueid WHERE imdb=?', (imdb_id,))
        self.c.commit()
        return self.cu.fetchone()[0]

    def get_media(self, media_id):
        self.cu.execute('SELECT title, originaltitle, plot, tagline, studio, genre, country, credits, director, premiered, tag, mpaa, trailer, duration FROM media WHERE idMedia=?', (media_id,))
        self.c.commit()
        res = self.cu.fetchone()

        info = {
            'title': res[0],
            'originaltitle': res[1],
            'plot': res[2],
            'tagline': res[3],
            'studio': res[4].split(' / '), #string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
            'genre': res[5].split(' / '), #string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
            'country': res[6].split(' / '), #string (Germany) or list of strings (["Germany", "Italy", "France"])
            'credits': res[7].split(' / '), #string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
            'director': res[8].split(' / '), #string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
            'premiered': res[9], #string (2005-03-04)
            'tag': res[10].split(' / '), #string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
            'mpaa': res[11],
            'trailer': res[12],
            'duration': res[13], #integer (245) - duration in seconds
        }

        return info

    def get_arts(self, media_id):
        self.cu.execute('SELECT poster_url, poster_preview, landscape_url, landscape_preview, fanart_url, fanart_preview, clearlogo_url, clearlogo_preview FROM arts WHERE idMedia=?', (media_id,))
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
    
    def get_metainfo(self, unique_imdb):
        self.cu.execute('SELECT uniqueid_id, media_type FROM uniqueid WHERE imdb=?', (unique_imdb,))
        self.c.commit()

        media_id = self.get_mediaId(imdb_id=unique_imdb)
        #result = self.cu.fetchone()

        # ids = {'uniqueid_id': result[0], 'media_type': result[1]}
        #info = self.get_media(media_id=ids['uniqueid_id'])
        #arts = self.get_arts(media_id=ids['uniqueid_id'])

        info = self.get_media(media_id=media_id)
        arts = self.get_arts(media_id=media_id)

        assemble = {
            # 'ids': ids,
            'info': info,
            'arts': arts
        }

        return assemble
        #return res

    def insert_media(self, media_id, media):
        for i in media:
            if media[i] == None:
                media[i] = ''

        meta = {
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
            'duration':'',
            }
        meta.update(media)

        if meta.get('genre'):
            meta['genre'] = ' / '.join(meta['genre'])
        if meta.get('tag'):
            meta['tag'] = ' / '.join(meta['tag'])
        if meta.get('studio'):
            meta['studio'] = ' / '.join(meta['studio'])
        if meta.get('country'):
            meta['country'] = ' / '.join(meta['country'])
        if meta.get('director'):
            meta['director'] = ' / '.join(meta['director'])
        if meta.get('credits'):
            meta['credits'] = ' / '.join(meta['credits'])

        self.cu.execute('INSERT INTO media (idMedia, title, originaltitle, plot, tagline, studio, genre, country, credits, director, premiered, tag, mpaa, trailer, duration) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (media_id, meta['title'],meta['originaltitle'],meta['plot'],meta['tagline'],meta['studio'],meta['genre'],meta['country'],meta['credits'],meta['director'],meta['premiered'],meta['tag'],meta['mpaa'],meta['trailer'],meta['duration']))
        self.c.commit()

        return

    def insert_uniqueid(self, unique_id):
        self.cu.execute('INSERT INTO uniqueid (media_type, tmdb, imdb) VALUES (?,?,?)', (
            unique_id['media_type'], unique_id['tmdb'], unique_id['imdb']))
        self.c.commit()

        return
    
    def insert_arts(self, media_id, arts):

        self.cu.execute('INSERT INTO arts (idMedia, poster_url, poster_preview, landscape_url, landscape_preview, fanart_url, fanart_preview, clearlogo_url, clearlogo_preview) VALUES (?,?,?,?,?,?,?,?,?)', 
                            (media_id, arts['poster_url'],arts['poster_preview'],arts['landscape_url'],arts['landscape_preview'],arts['fanart_url'],arts['fanart_preview'],arts['clearlogo_url'],arts['clearlogo_preview']))
        self.c.commit()

        return

    def insert_content(self, meta_info):
        unique_id = meta_info.pop('unique_id')
        self.insert_uniqueid(unique_id=unique_id)

        media_id = self.get_mediaId(imdb_id=unique_id['imdb'])
        media_id = int(media_id)

        media = meta_info.pop('media')
        self.insert_media(media_id, media)

        available_art = meta_info.pop('available_arts')
        self.insert_arts(media_id=media_id, arts=available_art)

        return