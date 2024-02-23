import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(object):
    TESTING = True
    JWT_SECRET_KEY = os.getenv('DEV_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOCAL_DATABASE_URL', 'No production secret key found')


class ProductionConfig(Config):
    JWT_SECRET_KEY = os.getenv('PRODUCTION_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCTION_DATABASE_URL')


class DevelopmentConfig(Config):
    JWT_SECRET_KEY = os.getenv('DEV_SECRET_KEY')


class StagingConfig(Config):
    TESTING = True
    JWT_SECRET_KEY = os.getenv('STAGING_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('LOCAL_DATABASE_URL')
