
class Config(object):
    DEBUG = False
    TESTING = False
    USUARIO = "promo2022"
    PASSWORD = "promo2022"
    DNS = "localhost/XE"


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'