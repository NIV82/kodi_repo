import network
import json
import base64

net =  network.WebTools()

def get_translate_box(url=None):
    if not url:
        return None

    html = net.get_bytes(url=url)
    # if not html['connection_reason'] == 'OK':
    #     return _error('Ошибка запроса')
    html = html['content']

    if not html.find(b'<div class="serial-translations-box">') > -1:
        return None

    translate_box = html[html.find(b'<div class="serial-translations-box">')+37:]
    translate_box = translate_box[:translate_box.rfind(b'</option>')]
    translate_box = translate_box.decode('utf-8')
    translate_box = translate_box.split('</option>')

    options = []
    for translate in translate_box:
        translate_data = {
            'id': '',
            'translation_type': '',
            'media_id': '',
            'media_hash': '',
            'media_type': '',
            'title': '',
            'episode_count': '',
            'selected': False
            }

        if translate.find('data-id=') > -1:
            dataid = translate[translate.find('data-id="')+9:]
            translate_data['id'] = dataid[:dataid.find('"')]

        if translate.find('data-translation-type=') > -1:
            datatype = translate[translate.find('data-translation-type="')+23:]
            translate_data['translation_type'] = datatype[:datatype.find('"')]

        if translate.find('data-media-id=') > -1:
            datamediaid = translate[translate.find('data-media-id="')+15:]
            translate_data['media_id'] = datamediaid[:datamediaid.find('"')]

        if translate.find('data-media-hash=') > -1:
            datamediahash = translate[translate.find('data-media-hash="')+17:]
            translate_data['media_hash'] = datamediahash[:datamediahash.find('"')]

        if translate.find('data-media-type=') > -1:
            datamediatype = translate[translate.find('data-media-type="')+17:]
            translate_data['media_type'] = datamediatype[:datamediatype.find('"')]

        if translate.find('data-title=') > -1:
            datatitle = translate[translate.find('data-title="')+12:]
            translate_data['title'] = datatitle[:datatitle.find('"')]

        if translate.find('data-episode-count=') > -1:
            dataepcount = translate[translate.find('data-episode-count="')+20:]
            translate_data['episode_count'] = dataepcount[:dataepcount.find('"')]

        if translate.find('selected="') > -1:
            translate_data['selected'] = True

        options.append(translate_data)

    return options

def get_playlist_box(url=None):
    domain = _parse_url(url=url)

    html = net.get_bytes(url=url)
    html = html['content']

    if not html.find(b'<div class="serial-series-box">') > -1:
        return None

    serial_data = html[html.find(b'<div class="serial-series-box">')+31:]
    serial_data = serial_data[:serial_data.find(b'</select>')]
    serial_data = serial_data.decode('utf-8').strip()
    if serial_data.endswith('</option>'):
        serial_data = serial_data[0:len(serial_data)-9]
    serial_data = serial_data.split('</option>')

    options = []
    for sd in serial_data:
        pl = {
            'title': '',
            'media_id': '',
            'image': '',
            'other_hd': '',
            'other_2': '',
            'type_dub': '',
            'cdn': '',
            'to_skeep_ad': '',
            'viewing': 'false',
            'file': '',
            'file_h': ''
            }

        if sd.find('data-id=') > -1:
            dataid = sd[sd.find('data-id="')+9:]
            pl['media_id'] = dataid[:dataid.find('"')]

        if sd.find('data-hash=') > -1:
            datahash = sd[sd.find('data-hash="')+11:]
            datahash = datahash[:datahash.find('"')]

        if sd.find('data-title=') > -1:
            datatitle = sd[sd.find('data-title="')+12:]
            pl['title'] = datatitle[:datatitle.find('"')]

        if datahash and pl['media_id']:
            pl['file'] = f"https://{domain[0]}/seria/{pl['media_id']}/{datahash}/720p"

        options.append(pl)

    return options

def get_playurl(url):
    try:
        result = {'360':'', '480':'', '720':''}
        domain = _parse_url(url)

        new_url = f"https://{domain[0]}/ftor"

        payload = {'type': domain[1], 'id': domain[2], 'hash': domain[3]}

        html = net.get_bytes(url=new_url, post=payload)

        html = html['content'].decode('utf-8')

        data = json.loads(html)

        links = data['links']

        for r in list(result.keys()):
            decode_url = _decode_kodik(links[r][0]['src'])

            if not 'http' in decode_url:
                result[r] = f"https:{decode_url}"
            else:
                result[r] = decode_url

        result['type'] = 'kodik'
    except:
        result = ''

    return result

def _decode_kodik(url):
    keys   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    result = 'STUVWXYZABCDEFGHIJKLMNOPQRstuvwxyzabcdefghijklmnopqr0123456789'

    decode_result = ''
    for k in url:
        keys_index = keys.index(k)
        keys_result = result[keys_index]
        decode_result = f"{decode_result}{keys_result}"

    if decode_result:
        decode_result = f"{decode_result}==="

    decode_result = base64.standard_b64decode(decode_result)
    decode_result = decode_result.decode('utf-8')

    return decode_result

def _parse_url(url):
    if url.startswith('https://'):
        url = url[8:]

    url = url.split('/')
    return url
