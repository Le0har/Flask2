from pathlib import Path


BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = 'supeR secret KeyS'
    JSON_AS_ASCII = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'quotes.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_ECHO = True