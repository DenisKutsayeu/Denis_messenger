import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', '')
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', '')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', '')
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '')
    RECAPTCHA_USE_SSL = os.getenv('RECAPTCHA_USE_SSL', '')
    REDIS_URL = os.getenv('REDIS_URL', '')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
    EMAIL_PASS = os.getenv('EMAIL_PASS', '')
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')