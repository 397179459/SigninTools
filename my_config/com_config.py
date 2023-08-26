import os

'''
*********** 消息推送配置 ***********
如没有配置则不推送消息,为了安全,这里使用的环境配置.git里面请自行百度如何添加secrets.pycharm也可以自主添加.
如果你实在不会,就直接用明文吧（O.o）
'''
# push plus 微信推送。使用参考 https://www.pushplus.plus
PUSH_TOKEN = os.environ.get('PUSHPLUS_KEY')
# server酱 微信推送。使用参考 https://sct.ftqq.com/
SCKEY = os.environ.get('SCKEY')

'''
*********** 个人加解密密钥 ***********
采用AES私钥加密,保障账号安全.
这里采用ECB,没有采用CBC.
key用了SHA-256转化,所以这里可以配置任意字符串,不用遵守AES算法要求密钥长度必须是16、24或32字节
如果不会配置环境变量(建议学习)、不care安全性、非开源运行,你可以在这里明文指定,eg:PRIVATE_AES_KEY = '666666'
'''
PRIVATE_AES_KEY = os.environ.get("PRIVATE_AES_KEY")

'''
*********** logging级别设置 ***********
'''
# LOG_LEVEL = 'DEBUG'
LOG_LEVEL = 'INFO'


def get_author_info(project):
    '''
    打印作者信息
    '''
    return f'''
        **************************************
            欢迎使用: {project}
            作者GitHub：https://github.com/3 9 7 1 7 9 4 5 9
            vx：L 3 9 7 1 7 9 4 5 9 加好友注明来意
        **************************************
        '''
