import configparser
import copy
import hashlib
import json
import logging
import random
import time
import requests

import core.common_Util as common_Util
import my_config as cf

# API_URL
TBS_URL = r'http://tieba.baidu.com/dc/common/tbs'
LIKES_URL = r'https://tieba.baidu.com/mo/q/newmoindex'
# LIKES_URL = r'http://c.tieba.baidu.com/c/f/forum/like'
# 客户端签到链接，经验值更高
SIGN_URL = r'http://c.tieba.baidu.com/c/c/forum/sign'

# 用iOS app store 接口获取app最新版本
TIEBA_VERSION = json.loads(requests.get(r'https://itunes.apple.com/lookup?id=477927812').text)['results'][0]['version']

AES_KEY = common_Util.private_crypt.get_aes_key()

HEADERS = {
    'Host': 'tieba.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2012K11AC Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 Mobile Safari/537.36 tieba/12.46.1.1',
}

_session = requests.Session()


def encode_data(data):
    """
    https://blog.csdn.net/qq_42339350/article/details/126386358
    这里的sign生成参考上面文档
    :param data:
    :return: md5后的sign
    """
    s = ''
    keys = data.keys()
    # 这里的sort很关键，必须要
    for i in sorted(keys):
        s += i + '=' + str(data[i])
    sign = hashlib.md5((s + 'tiebaclient!!!').encode('utf-8')).hexdigest().upper()
    data.update({'sign': str(sign)})
    return data


def get_tbs(bduss):
    """
    获取 tbs 参数
    :param bduss:
    :return:
    """
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
    """
    获取用户关注的贴吧
    :param bduss:
    :return:
    """
    headers = copy.copy(HEADERS)
    headers.update({'cookie': f'BDUSS={bduss}'})
    like_response = _session.get(url=LIKES_URL, headers=headers, timeout=5).json()
    like_list = like_response['data']['like_forum']
    return like_list


def client_sign(bduss, tbs, fid, kw):
    """
    客户端贴吧签到接口
    :param bduss: 百度唯一标识，每次都一样，但是都有效
    :param tbs:
    :param fid: 贴吧唯一id
    :param kw: 贴吧名称
    :return:
    """
    # 这里用的是我自己手机RedmiK40抓的包,理论上都可以，服务端应该没做校验
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
    """
    每个用户签到所有贴吧
    :param bduss:
    :return:
    """
    tbs = get_tbs(bduss)

    # 最多循环3轮签到，有些贴吧就是无法签到，可能吧已经被封了
    like_all_num = 0
    not_sign_num = 0
    for i in range(1, 4):
        logging.info(f'第 {i} 轮签到')
        like_list = get_likes(bduss)
        like_all_num = len(like_list)
        had_sign_num = 0

        for x in like_list:
            if x.get('is_sign') == 0:
                client_sign(bduss, tbs, x.get('forum_id'), x.get('forum_name'))
                time.sleep(round(random.uniform(0.2, 0.5)))
            else:
                had_sign_num += 1

        # 先执行签到再执行一遍校验是否全部签到，这里主要是为了防止当天第二次执行脚本
        if had_sign_num == like_all_num:
            logging.info(f'{like_all_num} 个已完全签完')
            break
        # 下面校验大概率只有每天第一次运行才会走到
        else:
            check_list = get_likes(bduss)
            not_sign_num = sum(1 for x in check_list if x.get('is_sign') == 0)
            logging.info(f'还有 {not_sign_num} 个未签')
            if not_sign_num == 0:
                logging.info(f'{like_all_num} 个已完全签完')
                break

    return like_all_num, not_sign_num


def run():
    tieba_config = configparser.ConfigParser()
    tieba_cf_path = cf.com_config.get_tieba_cf_path()
    tieba_config.read(tieba_cf_path, encoding="utf-8")
    sections = tieba_config.sections()
    send_title = '贴吧签到成功'
    send_msg = ''
    for section in sections:
        _bduss = common_Util.private_crypt.decrypt_aes_ebc(tieba_config.get(section, 'encrypt_bduss'), AES_KEY)
        _name = tieba_config.get(section, 'name')
        logging.info(f'开始签到 {_name}')
        like_all_num, not_sign_num = user_signin(_bduss)
        if not_sign_num > 0:
            send_title = '!!!有贴吧签到失败'
        msg = f'{_name}: 贴吧总数：{like_all_num} 已签：{like_all_num - not_sign_num}，未签: {not_sign_num}' + '\n'
        logging.info(msg)
        send_msg += msg
    logging.info(send_msg)
    common_Util.send_message.send_pushplus(cf.com_config.PUSH_TOKEN, send_title, send_msg)


if __name__ == '__main__':
    run()
