import configparser
import logging

from core import common_util
from core.common_util import private_crypt


def add_bduss():
    tieba_config = configparser.ConfigParser()
    tieba_cf_path = 'tieba_config'
    tieba_config.read(tieba_cf_path, encoding="utf-8")
    sections = tieba_config.sections()
    aes_key = private_crypt.get_aes_key()
    has_next = 'y'
    while has_next != 'n':
        phone = input(f'请输入贴吧绑定的手机号前三位和后四位 [1336789]:').strip()

        if phone in sections:
            modify = input(f'{phone}已存在，是要更新该账号信息吗  [Y/N] :').strip().lower()
            if modify == 'n':
                continue
        else:
            tieba_config.add_section(phone)

        name = input(f'请为{phone}输入标识,可以是账号名或者起个别名:').strip()
        start_date = common_util.input_date.input_start_date(phone)
        end_date = common_util.input_date.input_end_date(phone)

        bduss = input(f'请输入{phone}的BDUSS,如果不知道怎么获取自行百度:').strip()
        encrypt_bduss = private_crypt.encrypt_aes_ebc(bduss, aes_key)

        tieba_config.set(phone, 'name', name)
        tieba_config.set(phone, 'start_date', start_date)
        tieba_config.set(phone, 'end_date', end_date)
        tieba_config.set(phone, 'encrypt_bduss', encrypt_bduss)

        with open(tieba_cf_path, 'w+', encoding="utf-8") as configfile:
            tieba_config.write(configfile)
            logging.info(f'{phone}配置已写入成功')

        has_next = input('是否继续添加账号 [Y/N] :').strip().lower()


if __name__ == '__main__':
    add_bduss()
