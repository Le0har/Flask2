class Config:
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    SERVER_NAME = '0.0.0.0:8888'


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME = '0.0.0.0:5555'
    PORT = 3333