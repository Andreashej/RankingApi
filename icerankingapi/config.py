import os

SECRET_KEY = 'verySecretKey#noGuess'

JWT_SECRET_KEY = 'thisIs3xtremelyZcret'
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'

# from dotenv import load_dotenv

DB_USERNAME = os.environ.get('RDS_USERNAME') or 'andreas2_ranking'
DB_PASSWORD = os.environ.get('RDS_PASSWORD') or 'V+Zr1cD09XiX'
DB_HOSTNAME = os.environ.get('RDS_HOSTNAME') or 'cp02.azehosting.net'
DB_PORT = os.environ.get('RDS_PORT') or '3306'
DB_NAME = os.environ.get('RDS_DB_NAME') or 'andreas2_iceranking'

# You need to replace the next values with the appropriate values for your configuration

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_POOL_RECYCLE = 499
SQLALCHEMY_POOL_TIMEOUT = 20

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_HOSTNAME + ':' + DB_PORT + '/' + DB_NAME

ISIRANK_FILES = basedir + '/files/'

RIDERS_PER_PAGE = 100

API_VERSION = "0.1.0"

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

QUEUE = 'iceranking-tasks'

# RDS_HOST iceranking-api.c8fmxoomvwpn.eu-central-1.rds.amazonaws.com
# RDS_DB_NAME iceranking
# RDS_USERNAME iceranking
# RDS_PASSWORD qmkL2YvhtuSS7FZM
# RDS_PORT 3306