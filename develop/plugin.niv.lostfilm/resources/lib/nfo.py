# -*- coding: utf-8 -*-

import os

def data_print(data):
    import xbmc
    xbmc.log(str(data), xbmc.LOGFATAL)
    
class CreateNFO:
    def __init__(self, library_path, site_url, **nfo_data):
    # def __init__(self, library_path):
        self.library_path = library_path
        self.nfo_data = nfo_data
        self.site_url = site_url
        self.serial_url = '{}series/{}/seasons/'.format(site_url, self.nfo_data['serial_id'])
        
        self.serial_dir = os.path.join(self.library_path, self.nfo_data['serial_id'])
    #https://www.lostfilm.today/v_search.php?c=779&s=1&e=2
    def create_tvshows(self):
        tvshowdetails = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<tvshow>\n    <title>{}</title>\n    <plot>{}</plot>\n    <genre>{}</genre>\n    <premiered>{}</premiered>\n    <studio>{}</studio>\n{}\n    <thumb>{}</thumb>\n</tvshow>'.format(
            self.nfo_data['title_ru'],
            self.nfo_data['plot'],
            self.nfo_data['genre'],
            self.nfo_data['premiered'],
            ','.join(self.nfo_data['studio']),
            self.nfo_data['actors'],
            'https://static.lostfilm.top/Images/{}/Posters/shmoster_s1.jpg'.format(self.nfo_data['image_id'])
            )

        try:
            tvshowdetails = tvshowdetails.encode('utf-8')
        except:
            pass

        #serial_dir = os.path.join(self.library_path, self.nfo_data['serial_id'])
        if not os.path.exists(self.serial_dir):
            os.mkdir(self.serial_dir)
        
        serial_nfo = os.path.join(self.serial_dir, 'tvshow.nfo')
        try:
            with open(serial_nfo, 'wb') as write_file:
                write_file.write(tvshowdetails)
        except Exception as e:
            data_print(e)
        return


    # def create_movies(self):
    #     return
    
    def create_episodedetails(self):
        from network import get_web
        html = get_web(url=self.serial_url)

        data_array = html[html.find('<div class="have'):html.rfind('holder"></td>')]
        data_array = data_array.split('<td class="alpha">')
        data_array.reverse()

        try:
            for i, data in enumerate(data_array):
                try:
                    if not 'data-code=' in data:
                        continue

                    se_code = data[data.find('episode="')+9:]
                    se_code = se_code[:se_code.find('"')]

                    season = int(se_code[len(se_code)-6:len(se_code)-3])
                    season_mod = 's{:>02}'.format(season)

                    episode = int(se_code[len(se_code)-3:len(se_code)])
                    episode_mod = 'e{:>02}'.format(episode)

                    episode_title = data[data.find('<td class="gamma'):data.find('<td class="delta"')]
                    if '<br>' in episode_title:
                        episode_title = episode_title[episode_title.find('">')+2:episode_title.find('<br>')].strip()        
                    if '<br />' in episode_title:
                        episode_title = episode_title[episode_title.find('<div>')+5:episode_title.find('<br />')].strip()
                    if not episode_title:
                        continue
                    
                    p = int((float(i+1) / len(data_array)) * 100)

                    #self.progress_bg.update(p, 'Обработано - {} из {}'.format(i, len(data_array)))

                    # file_name = '{}.{}.{}.nfo'.format(self.nfo_data['serial_id'], season_mod, episode_mod)
                    file_name = '{}.{}.{}'.format(self.nfo_data['serial_id'], season_mod, episode_mod)
                    nfo_path = os.path.join(self.serial_dir, '{}.nfo'.format(file_name))

                    #plugin://plugin.video.tam/?url=http%3A%2F%2F127.0.0.1%3A8095%2Fproxy%2Fhttp%3A%2F%2Frutor.is%2Fdownload%2F941749&ind=0&ad=0&mode=play&title=One+Piece.s01.e01
                    #mode=play_part&id=Gen_V&param=779001001
                    #['plugin://plugin.niv.lostfilm/', '47', '?mode=play_part&id=Gen_V&param=779001001', 'resume:false']
                    strm_path = os.path.join(self.serial_dir, '{}.strm'.format(file_name))                    
                    #strm_content = '{}v_search.php?c={}&s={}&e={}'.format(self.site_url, self.nfo_data['image_id'], season, episode)
                    strm_content = 'plugin://plugin.niv.lostfilm/?mode=play_part&id={}&param={}'.format(self.nfo_data['serial_id'], se_code)
                    try:
                        strm_content = strm_content.encode('utf-8')
                    except:
                        pass


                    file_thumb = 'https://static.lostfilm.top/Images/{}/Posters/shmoster_s{}.jpg'.format(self.nfo_data['image_id'], season)

                    episodedetails = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<episodedetails>\n    <title>{}</title>\n    <season>{}</season>\n    <episode>{}</episode>\n    <plot>{}</plot>\n    <thumb>{}</thumb>\n</episodedetails>'.format(
                        episode_title, season, episode, self.nfo_data['plot'], file_thumb)

                    try:
                        episodedetails = episodedetails.encode('utf-8')
                    except:
                        pass

                    with open(nfo_path, 'wb') as write_file:
                        write_file.write(episodedetails)
                    
                    try:
                        with open(strm_path, 'wb') as write_file:
                            write_file.write(strm_content)
                    except Exception as e:
                        data_print(e)

                except:
                    data_print('ERROR-1')
        except:
            data_print('ERROR-2')

        return