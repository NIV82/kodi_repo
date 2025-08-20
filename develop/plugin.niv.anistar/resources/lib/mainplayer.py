import network

net =  network.WebTools()

def _parse_value(value=None):
    value = value[value.find(':')+1:]
    value = value[:value.rfind(',')]
    value = value.replace('"','').replace("'",'')
    value = value.strip()
    return value

def _parse_url(url):
    url = url[url.find('//')+2:]
    url = url.split('/')

    return url

# def _parse_playurl(data):
#     vsd = data[data.find('360=')+4:]
#     vsd = vsd[:vsd.find('&')]

#     vhd = data[data.find('720=')+4:]
#     if '&' in vhd:
#         vhd = vhd[:vhd.find('&')]

#     vhd = f"{vhd}|Referer:{site_url}"

#     return {'SD': vsd, 'HD': vhd, 'type': 'mainplayer'}

def _parse_playlistdata(pldata):
    playlist = dict.fromkeys([
        'title','media_id','image','other_hd','other_2','type_dub',
        'cdn','to_skeep_ad','viewing','file','file_h'
        ], '')

    pldata = pldata.splitlines()
    for pld in pldata:
        if pld.find('title:') > -1:
            playlist['title'] = _parse_value(pld)

        if pld.find('media_id:') > -1:
            playlist['media_id'] = _parse_value(pld)

        if pld.find('image:') > -1:
            playlist['image'] = _parse_value(pld)

        if pld.find('other_hd:') > -1:
            playlist['other_hd'] = _parse_value(pld)

        if pld.find('other_2:') > -1:
            playlist['other_2'] = _parse_value(pld)

        if pld.find('type_dub:') > -1:
            playlist['type_dub'] = _parse_value(pld)

        if pld.find('cdn:') > -1:
            playlist['cdn'] = _parse_value(pld)

        if pld.find('to_skeep_ad:') > -1:
            playlist['to_skeep_ad'] = _parse_value(pld)

        if pld.find('viewing:') > -1:
            playlist['viewing'] = _parse_value(pld)

        if pld.find('file:') > -1:
            playlist['file'] = _parse_value(pld)

        if pld.find('file_h:') > -1:
            playlist['file_h'] = _parse_value(pld)

    return playlist

# def parse_mainplayer(mlink, site_url):
def parse_mainplayer(mlink):
    domain = _parse_url(mlink)
    site_url = domain[0]
    # if not 'https' in site_url:
    #     site_url = f"https://{site_url}"
    #mlink = mlink[mlink.find('/videoas.'):]
    #mlink = f"{site_url}{mlink}"

    html = net.get_bytes(url=mlink)
    if not html['status'] == 200:
        return []
        #return error
    html = html['content']

    player_url = ''
    if html.find(b'src="') > -1:
        player_url = html[html.find(b'src="')+5:]
        player_url = player_url[:player_url.find(b'"')]
        player_url = player_url.decode('utf-8')
        if not player_url.startswith('https'):
            player_url = f"https://{site_url}{player_url}"
        # import xbmc 
        # xbmc.log(str(player_url), xbmc.LOGFATAL)
    player_data = net.get_bytes(url=player_url)
    if not player_data['status'] == 200:
        return []
        #return error
    player_data = player_data['content']

    playlist_array = []

    data_array = player_data[player_data.find(b'playlst=[')+9:]
    data_array = data_array[:data_array.find(b'];')]
    data_array = data_array[:data_array.rfind(b'},')]
    data_array = data_array.decode('utf-8')
    data_array = data_array.split('},')

    for data in data_array:
        pl = _parse_playlistdata(pldata=data)
        playlist_array.append(pl)

    return playlist_array
