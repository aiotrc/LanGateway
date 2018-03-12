import os

basedir = os.path.abspath(os.path.dirname(__file__))
postgres_local_base = 'postgresql://postgres:{password}@localhost/'.format(
    password=os.getenv('POSTGRES_PASS', 'postgres'))
database_name = 'postgres'


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_REMEMBER_DAYS = 7


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    LOGIN_DISABLED = True
    MQTT_BROKER_HOST = 'localhost'
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    MQTT_BROKER_HOST = '172.23.132.37'
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name
