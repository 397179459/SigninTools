import logging

from core.baiduTieba import tieba_signin

import my_config as cf

logging.basicConfig(level=cf.com_config.LOG_LEVEL, format='%(asctime)s-%(levelname)s: %(message)s')

logging.info(r'''
    **************************************
        欢迎使用百度贴吧自动签到
        作者GitHub：https://github.com/3 9 7 1 7 9 4 5 9
        vx：L 3 9 7 1 7 9 4 5 9 加好友注明来意
    **************************************
    ''')


def run():
    if cf.com_config.BAIDUTIEBA_ON:
        logging.info('****** 百度贴吧签到 开始运行 ******')
        tieba_signin.run()
        logging.info('****** 百度贴吧签到 完成 ******')


if __name__ == '__main__':
    run()
