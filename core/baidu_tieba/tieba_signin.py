import configparser
import copy
import hashlib
import json
import logging
import os
import random
import sys
import time
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core import common_util
import my_config as cf

tieba_cf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tieba_config'))

logging.basicConfig(level=cf.com_config.LOG_LEVEL, format='%(asctime)s-%(levelname)s: %(message)s')

logging.info(cf.com_config.get_author_info('百度贴吧自动签到'))

TBS_URL = r'http://tieba.baidu.com/dc/common/tbs'  # 获取tbs
LIKES_URL_WEB = r'https://tieba.baidu.com/mo/q/newmoindex'  # 网页版获取关注的吧，但是一次最多返回200个
LIKES_URL_CLIENT = r'http://c.tieba.baidu.com/c/f/forum/like'  # 客户端获取关注的吧
SIGN_URL = r'http://c.tieba.baidu.com/c/c/forum/sign'  # 客户端签到链接，经验值更高

# 用iOS app store 接口获取app最新版本
TIEBA_VERSION = json.loads(requests.get(r'https://itunes.apple.com/lookup?id=477927812').text)['results'][0]['version']

AES_KEY = common_util.private_crypt.get_aes_key()

HEADERS = {
    'Host': 'tieba.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2012K11AC Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 Mobile Safari/537.36 tieba/12.46.1.1',
}

# 这里用的是我自己手机RedmiK40抓的包,理论上都可以，服务端应该没做校验
SIGN_DATA = {
    '_client_id': 'wappc_1692700560616_448',
    '_client_type': '2',
    '_client_version': TIEBA_VERSION,
    '_phone_imei': '000000000000000',
    'model': 'M2012K11AC',
    "net_type": "1",
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
        return tbs
    except Exception as e:
        logging.error(e)
        logging.info('failed get tbs')
    logging.info('get tbs end')


def add_to_like_list(forum_key, forum_list, like_list):
    """
    增加关注的贴吧
    :param forum_key:
    :param forum_list:
    :param like_list:
    :return:
    """
    if forum_key in forum_list and len(forum_list[forum_key]) > 0:
        for x in forum_list[forum_key]:
            tmp_dict = {
                'forum_id': x['id'],
                'forum_name': x['name'],
            }
            like_list.append(tmp_dict)


def get_likes_client(bduss):
    """
    客户端接口获取用户关注的贴吧
    :param bduss:
    :return:
    """
    NON_GCONFORUM = 'non-gconforum'  # 没有“百度贴吧企业平台认证”,大部分吧都是
    GCONFORUM = 'gconforum'  # “百度贴吧企业平台认证”，只有少部分吧才有

    headers = copy.copy(HEADERS)
    headers.update({'cookie': f'BDUSS={bduss}'})

    like_list = []
    # 是否还有下一页
    has_more = '1'
    i = 1
    while has_more == '1':
        sign_data = copy.copy(SIGN_DATA)
        sign_data.update({'page_no': str(i), 'page_size': '100'})
        _data = encode_data(sign_data)

        like_response = _session.post(url=LIKES_URL_CLIENT, headers=headers, data=_data, timeout=5).json()
        has_more = like_response['has_more']
        tmp_forum_l = like_response['forum_list']

        add_to_like_list(NON_GCONFORUM, tmp_forum_l, like_list)
        add_to_like_list(GCONFORUM, tmp_forum_l, like_list)

        i += 1

    return like_list


def get_likes_web(bduss):
    """
    通过web接口获取用户关注的贴吧
    :param bduss:
    :return: 关注的贴吧列表
    """
    headers = copy.copy(HEADERS)
    headers.update({'cookie': f'BDUSS={bduss}'})
    like_response = _session.get(url=LIKES_URL_WEB, headers=headers, timeout=5).json()
    like_list = like_response['data']['like_forum']
    return like_list


def client_sign(bduss, tbs, fid, kw):
    """
    客户端贴吧签到接口
    :param bduss: 百度唯一标识，每次都不一样，但是都有效
    :param tbs:
    :param fid: 贴吧唯一id
    :param kw: 贴吧名称
    :return:
    """
    sign_data = copy.copy(SIGN_DATA)
    sign_data.update({'BDUSS': bduss, 'tbs': tbs, 'fid': fid, 'kw': kw, 'timestamp': str(int(time.time()))})
    _data = encode_data(sign_data)
    rsp = _session.post(url=SIGN_URL, data=_data, timeout=5).json()
    if 'user_info' in rsp and rsp['user_info']['is_sign_in'] == '1':
        logging.info(f'{kw}: 签到成功')
        return True

    if rsp['error_code'] == '160002':
        logging.info(f'{kw}: {rsp["error_msg"]}')
        return True

    logging.error(f'{kw}: {rsp["error_code"]}:{rsp["error_msg"]}')
    return False


def user_signin(bduss):
    """
    每个用户签到所有贴吧
    :param bduss:
    :return:
    """
    tbs = get_tbs(bduss)
    had_sign_num = 0
    like_list = get_likes_client(bduss)
    like_all_num = len(like_list)
    # 最多循环3轮签到，有些贴吧就是无法签到，可能吧已经被封了
    for i in range(1, 4):
        logging.info(f'第 {i} 轮签到')
        had_sign_num = 0

        for x in like_list.copy():
            is_sign_flag = client_sign(bduss, tbs, x.get('forum_id'), x.get('forum_name'))
            if is_sign_flag:
                had_sign_num += 1
                like_list.remove(x)
                time.sleep(round(random.uniform(0.1, 0.4), 1))

        # 先执行签到再执行一遍校验是否全部签到，这里主要是为了防止当天第二次执行脚本
        if len(like_list) == 0:
            logging.info(f'{like_all_num} 个已完全签完')
            break

    return like_all_num, had_sign_num


def run():
    logging.info('Start run')
    tieba_config = configparser.ConfigParser()
    tieba_config.read(tieba_cf_path, encoding="utf-8")
    sections = tieba_config.sections()
    logging.info(sections)
    send_title = '贴吧签到成功'
    send_msg = ''
    for section in sections:
        _bduss = common_util.private_crypt.decrypt_aes_ebc(tieba_config.get(section, 'encrypt_bduss'), AES_KEY)
        _name = tieba_config.get(section, 'name')
        logging.info(f'开始签到 {_name}')
        like_all_num, had_sign_num = user_signin(_bduss)
        not_sign_num = like_all_num - had_sign_num
        if not_sign_num > 0:
            send_title = '!!!有贴吧签到失败'
        msg = f'{_name}: 贴吧总数：{like_all_num} 已签：{had_sign_num}，未签: {not_sign_num}' + '\n'
        logging.info(msg)
        send_msg += msg
    logging.info(send_msg)
    common_util.send_message.send_pushplus(cf.com_config.PUSH_TOKEN, send_title, send_msg)


if __name__ == '__main__':
    logging.info('****** 百度贴吧签到 开始运行 ******')
    run()
    logging.info('****** 百度贴吧签到 运行结束 ******')
