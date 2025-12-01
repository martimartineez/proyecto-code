from os import environ


class Config:
    TESTING = False
    SECRET_KEY = "secret-key"
    SESSION_TYPE = "filesystem"
    CORS_RESOURCES = [r"/api/*"]
    CORS_ORIGINS = ["*"]
    SQALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }


class ProductionConfig(Config):
    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = True
    MINIO_BUCKET = "grupo25"

    SQLALCHEMY_ENGINES = {"default": environ.get("DATABASE_URL")}
    CORS_ORIGINS = ["https://grupo25.proytecto2025.linti.unlp.edu.ar/"]


class DevelopmentConfig(Config):
    MINIO_SERVER = "minio.proyecto2025.linti.unlp.edu.ar"
    MINIO_ACCESS_KEY = "whAj4qyqOlN7FQaIhZX6"
    MINIO_SECRET_KEY = "IXI2aks5WHEv8adbGdsOlAOCPezebkGKKObLc76p"
    MINIO_SECURE = False
    MINIO_BUCKET = "grupo25"

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
