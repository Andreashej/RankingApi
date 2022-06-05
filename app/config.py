import os

# Always supply secret key from environment var in production!
SECRET_KEY = os.environ.get('SECRET_KEY') or "thisIs3xtremelyZcret"

DEBUG = os.environ.get('FLASK_ENV') == 'development'

JWT_SECRET_KEY = SECRET_KEY
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

DB_USERNAME = os.environ.get('RDS_USERNAME')
DB_PASSWORD = os.environ.get('RDS_PASSWORD')
DB_HOSTNAME = os.environ.get('RDS_HOSTNAME')
DB_NAME = os.environ.get('RDS_DB_NAME')
DB_PORT = os.environ.get('RDS_PORT') or '3306'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_POOL_RECYCLE = 499
SQLALCHEMY_POOL_TIMEOUT = 20

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_HOSTNAME + ':' + DB_PORT + '/' + DB_NAME

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = os.environ.get("MAIL_PORT")
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or 1
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

ISIRANK_FILES = basedir + '/files/'
IMAGE_FILES = basedir + '/static/images/'

API_VERSION = "0.1.0"

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

QUEUE = 'iceranking-tasks'

ICETEST_RABBIT_HOST = os.environ.get('ICETEST_RABBIT_HOST')
ICETEST_RABBIT_USER = os.environ.get('ICETEST_RABBIT_USER')
ICETEST_RABBIT_PASSWORD = os.environ.get('ICETEST_RABBIT_PASSWORD')
ICETEST_RABBIT_VHOST = os.environ.get('ICETEST_RABBIT_VHOST')

SENTRY_DSN = os.environ.get("SENTRY_DSN")

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}