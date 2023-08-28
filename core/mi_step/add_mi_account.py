import configparser
import logging

from core import common_util


def add_mi_account():
    _config = configparser.ConfigParser()
    _config_path = 'mi_step_config'
    _config.read(_config_path, encoding="utf-8")
    sections = _config.sections()
    aes_key = common_util.private_crypt.get_aes_key()
    has_next = 'y'
    while has_next != 'n':
        phone = input(f'请输入手机号,会自动隐藏中间四位 [13344556677]:').strip()
        if not common_util.string_utils.valid_phone_number(phone):
            print(f'{phone}不是合法的手朷号')
            continue
        hide_phone = phone.replace(phone[3:7], '****')

        if hide_phone in sections:
            modify = input(f'[{phone}]已存在，是要更新该账号信息吗  [Y/N] :').strip().lower()
            if modify == 'n':
                continue
        else:
            _config.add_section(hide_phone)

        name = input(f'请为[{hide_phone}]输入标识,可以是账号名或者起个别名:').strip()
        start_date = common_util.input_date.input_start_date(hide_phone)
        end_date = common_util.input_date.input_end_date(hide_phone)

        pwd = input(f'请输入[{hide_phone}]的小米运动密码,会加密保存:').strip()

        step_way = input(f'设置[{hide_phone}]的步数方式,[0]数值区间；[1]指定步数。[0]:').strip()
        step_num = 0
        if step_way == '1':
            step_num = input(f'请指定[{hide_phone}]的步数 1~99999:').strip()
        elif step_way == '0' or len(step_way) == 0:
            step_lower = input(f'设置[{hide_phone}]的区间下限 >= 1:').strip()
            if int(step_lower) <= 0:
                print(f'错误，下限必须大以1')
                continue
            step_upper = input(f'设置[{hide_phone}]的区间上限 <= 99999:').strip()
            if int(step_upper) > 99999:
                print(f'错误，上限必须小于等于99999')
                continue
            if int(step_upper) <= int(step_lower):
                print(f'错误，上限小于下限')
                continue
            step_num = step_lower + '#' + step_upper

        _config.set(hide_phone, 'name', name)
        _config.set(hide_phone, 'start_date', start_date)
        _config.set(hide_phone, 'end_date', end_date)
        encrypt_phone = common_util.private_crypt.encrypt_aes_ebc(phone, aes_key)
        _config.set(hide_phone, 'encrypt_phone', encrypt_phone)
        encrypt_pwd = common_util.private_crypt.encrypt_aes_ebc(pwd, aes_key)
        _config.set(hide_phone, 'encrypt_pwd', encrypt_pwd)
        _config.set(hide_phone, 'step_num', step_num)

        with open(_config_path, 'w+', encoding="utf-8") as configfile:
            _config.write(configfile)
            logging.info(f'[{phone}]配置已成功写入')

        has_next = input('是否继续添加账号 [Y/N] :').strip().lower()


if __name__ == '__main__':
    add_mi_account()
