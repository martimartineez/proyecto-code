from os import environ

from sqlalchemy import sql

class Config:
    TESTING = False
    SECRET_KEY = ''
    SESSION_TYPE = 'filesystem'

class ProductionConfig(Config):
    SQLALCHEMY_ENGINES = {
        "default": environ.get('DATABASE_URL')
    }

class DevelopmentConfig(Config):
    SECRET_KEY = ''
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'grupo25'
    DB_SCHEME = 'postgresql+psycopg2'
    SQLALCHEMY_ENGINES = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }

class TestConfig:
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig
}