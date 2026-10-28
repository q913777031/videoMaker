"""纸片风（引擎原样）：只让带 role 参数的人物调用兼容原版纸片人。"""

from adler import kit as K


def install():
    orig = K.figure

    def figure(*args, role=None, **kw):
        return orig(*args, **kw)

    K.figure = figure
