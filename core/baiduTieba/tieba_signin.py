import configparser
import copy
import hashlib
import json
import logging
import random
import time
import requests

from common import private_crypt
from my_config import com_config as cf

# API_URL

TBS_URL = r'http://tieba.baidu.com/dc/common/tbs'
LIKES_URL = r'https://tieba.baidu.com/mo/q/newmoindex'
# LIKES_URL = r'http://c.tieba.baidu.com/c/f/forum/like'
SIGN_URL = r'http://c.tieba.baidu.com/c/c/forum/sign'

TIEBA_VERSION = json.loads(requests.get(r'https://itunes.apple.com/lookup?id=477927812').text)['results'][0]['version']

AES_KEY = private_crypt.get_aes_key()

HEADERS = {
    'Host': 'tieba.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2012K11AC Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 Mobile Safari/537.36 tieba/12.46.1.1',
}

_session = requests.Session()


def encode_data(data):
    s = ''
    keys = data.keys()
    for i in sorted(keys):
        s += i + '=' + str(data[i])
    sign = hashlib.md5((s + 'tiebaclient!!!').encode('utf-8')).hexdigest().upper()
    data.update({'sign': str(sign)})
    return data


def get_tbs(bduss):
    logging.info('Getting tbs')
    headers = copy.copy(HEADERS)
    headers.update({'Cookie': f'BDUSS={bduss}'})
    try:
        tbs = _session.get(url=TBS_URL, headers=headers, timeout=5).json()['tbs']
    except Exception as e:
        logging.error(e)
        logging.info('failed get tbs')
    logging.info('get tbs end')
    return tbs


def get_likes(bduss):
    logging.info('Getting likes')
    headers = copy.copy(HEADERS)
    headers.update({'cookie': f'BDUSS={bduss}'})
    like_response = _session.get(url=LIKES_URL, headers=headers, timeout=5).json()
    like_list = like_response['data']['like_forum']
    return like_list


def client_sign(bduss, tbs, fid, kw):
    sign_data = {
        '_client_id': 'wappc_1692700560616_448',
        '_client_type': '2',
        '_client_version': TIEBA_VERSION,
        '_phone_imei': '000000000000000',
        'model': 'M2012K11AC',
        "net_type": "1",
    }
    sign_data.update({'BDUSS': bduss, 'tbs': tbs, 'fid': fid, 'kw': kw, 'timestamp': str(int(time.time()))})
    _data = encode_data(sign_data)
    _session.post(url=SIGN_URL, data=_data, timeout=5).json()


def user_signin(bduss):
    tbs = get_tbs(bduss)
    for i in range(3):
        logging.info(f'第 {i} 轮签到')
        i += 1
        like_list = get_likes(bduss)
        for x in like_list:
            if x.get('is_sign') == 0:
                time.sleep(random.uniform(1, 2))
                client_sign(bduss, tbs, x.get('forum_id'), x.get('forum_name'))


def run():
    tieba_config = configparser.ConfigParser()
    tieba_cf_path = cf.get_tieba_cf_path()
    tieba_config.read(tieba_cf_path, encoding="utf-8")
    sections = tieba_config.sections()
    for section in sections:
        _bduss = private_crypt.decrypt_aes_ebc(tieba_config.get(section, 'encrypt_bduss'), AES_KEY)
        _name = tieba_config.get(section, 'name')
        logging.info(f'开始签到 {_name}')
        user_signin(_bduss)


if __name__ == '__main__':
    run()
