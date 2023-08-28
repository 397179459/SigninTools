import re


def valid_phone_number(_phone_number):
    pattern = "^1[123456789]\d{9}$"
    if re.match(pattern, _phone_number):
        return True
    else:
        return False
