from os import environ


class Config:
    TESTING = False
    SECRET_KEY = "secret-key"
    SESSION_TYPE = "filesystem"
    CORS_RESOURCES = [
        r"/api/*"
    ]
    CORS_ORIGINS = [
        "*"
    ]
    SQALCHEMY_ENGINE_OPTIONS = {
        "pool_size" : 10,
        "pool_recycle" : 60,
        "pool_pre_ping" : True,
    }


class ProductionConfig(Config):
    SQLALCHEMY_ENGINES = {"default": environ.get("DATABASE_URL")}
    CORS_ORIGINS = [
        "https://grupo25.proytecto2025.linti.unlp.edu.ar/"
    ]


class DevelopmentConfig(Config):
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "grupo25"
    DB_SCHEME = "postgresql+psycopg2"
    SQLALCHEMY_ENGINES = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }


class TestConfig:
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestConfig,
}
