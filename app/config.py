import os

# Always supply secret key from environment var in production!
SECRET_KEY = os.environ.get('SECRET_KEY') or "thisIs3xtremelyZcret"

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

ISIRANK_FILES = basedir + '/files/'
IMAGE_FILES = basedir + '/static/images/'

API_VERSION = "0.1.0"

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

QUEUE = 'iceranking-tasks'