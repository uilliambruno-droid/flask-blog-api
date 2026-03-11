import os


class Config:
    TESTING = False
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.sqlite"
    JWT_SECRET_KEY = "dev-jwt-secret-key-32chars-minimum"


class TestingConfig(Config):
    DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret-key-32chars-minx"
