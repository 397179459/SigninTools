import datetime

date_format_error = 'Error:日期格式错误，请重新输入'


def input_start_date(section):
    while 1:
        default_date = datetime.date.today().strftime("%Y%m%d")
        start_date = input(f'请输入[{section}]生效日期[YYYYMMDD],如果不输入则默认[{default_date}]:').strip()
        if start_date == '':
            return default_date
        elif len(start_date) == 8:
            return start_date
        else:
            print(date_format_error)


def input_end_date(section):
    while 1:
        default_date = '99999999'
        end_date = input(f'请输入[{section}]关闭日期[YYYYMMDD],如果不输入则默认[{default_date}]:').strip()
        if end_date == '':
            return default_date
        elif len(end_date) == 8:
            return end_date
        else:
            print(date_format_error)
