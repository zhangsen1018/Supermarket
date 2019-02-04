import hashlib

from market.settings import SECRET_KEY


def set_password(password):
    # 循环加密 + 加盐
    for _ in range(1000):
        pass_str = "{}{}".format(password, SECRET_KEY)
        h = hashlib.md5(pass_str.encode('utf-8'))
        password = h.hexdigest()

    # 返回密码
    return password
