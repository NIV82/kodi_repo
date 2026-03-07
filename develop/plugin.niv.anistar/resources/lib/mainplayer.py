import re
import network

net =  network.WebTools()

def _parse_url(url):
    url = url[url.find('//')+2:]
    url = url.split('/')

    return url

def get_files(data):
    result = {}
    data = data.split('},{')
    for d in data:
        title = re.search('title:"(.*?)"', d)
        file = re.search('file:"(.*?)"', d)

        if title and file:
            result[title.group(1)] = file.group(1)

    return result

def parse_mainplayer(mlink):
    html = net.get_bytes(url=mlink)

    if not html['status'] == 200:
        return []
    html = html['content']
    
    playlist_array = []

    playlist = re.search(
        pattern=b'var playlst=\\[(.+?)\\];',
        string=html,
        flags=re.DOTALL
    )

    playlist = playlist.group(1)
    playlist = re.sub(
        pattern=b'\\t|\\r|\\n|//0',
        repl=b'',
        string=playlist
    )
    playlist = playlist.decode('utf-8')

    playlist = re.findall(
        pattern='{title:(.+?)],},',
        string=playlist
    )


    for node in playlist:
        node = f"title:{node}]"

        title = re.search('title:"(.*?)"', node)
        media_id = re.search('media_id:"(.*?)"', node)
        other_2 = re.search('other_2:"(.*?)"', node)

        files = re.search('files:\\[(.*?)\\],', node)
        if files:
            files = get_files(data=files.group(1))

        files_mp4 = re.search('files_mp4:\\[(.*?)]', node)
        if files_mp4:
            files_mp4 = get_files(data=files_mp4.group(1))

        if title and media_id:
            playlist_array.append(
                {
                    'title': title.group(1),
                    'media_id': media_id.group(1),
                    'other_2': other_2.group(1),
                    'files': files,
                    'files_mp4': files_mp4
                }
            )

    return playlist_array

# def parse_mainplayer(mlink):
#     domain = _parse_url(mlink)
#     site_url = domain[0]

#     if not 'https' in site_url:
#         site_url = f"https://{site_url}"

#     mlink = mlink[mlink.find('/videoas'):]
#     mlink = f"{site_url}{mlink}"

#     html = net.get_bytes(url=mlink)
   
#     if not html['status'] == 200:
#         return []
#         return error
#     html = html['content']

#     player_url = ''
#     result = re.search(pattern=b'as-player" src="(.+?)"', string=html)
#     if result:
#         player_url = result.group(1)
#         player_url = player_url.decode('utf-8')

#         if not player_url.startswith('https'):
#             player_url = f"{site_url}{player_url}"

#     player_data = net.get_bytes(url=player_url)
#     if not player_data['status'] == 200:
#         return []
#         #return error
#     player_data = player_data['content']

#     playlist_array = []

#     playlist = re.search(
#         pattern=b'var playlst=\\[(.+?)\\];',
#         string=player_data,
#         flags=re.DOTALL
#     )

#     playlist = playlist.group(1)
#     playlist = re.sub(
#         pattern=b'\\t|\\r|\\n|//0',
#         repl=b'',
#         string=playlist
#     )
#     playlist = playlist.decode('utf-8')

#     playlist = re.findall(
#         pattern='{title:(.+?)],},',
#         string=playlist
#     )

#     for node in playlist:
#         node = f"title:{node}]"

#         title = re.search('title:"(.*?)"', node)
#         media_id = re.search('media_id:"(.*?)"', node)
#         other_2 = re.search('other_2:"(.*?)"', node)

#         files = re.search('files:\\[(.*?)\\],', node)
#         if files:
#             files = get_files(data=files.group(1))

#         files_mp4 = re.search('files_mp4:\\[(.*?)]', node)
#         if files_mp4:
#             files_mp4 = get_files(data=files_mp4.group(1))

#         if title and media_id:
#             playlist_array.append(
#                 {
#                     'title': title.group(1),
#                     'media_id': media_id.group(1),
#                     'other_2': other_2.group(1),
#                     'files': files,
#                     'files_mp4': files_mp4
#                 }
#             )

#     return playlist_array
