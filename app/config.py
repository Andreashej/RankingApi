import os

SECRET_KEY = 'verySecretKey#noGuess'

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

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_HOSTNAME + ':' + DB_PORT + '/' + DB_NAME
# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://andreas2_ranking:V+Zr1cD09XiX@cp02.azehosting.net/andreas2_iceranking'
# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:79137913@localhost/iceranking'


ISIRANK_FILES = basedir + '/files/'

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

RIDERS_PER_PAGE = 100

API_VERSION = "0.1.0"

# RDS_HOST iceranking-api.c8fmxoomvwpn.eu-central-1.rds.amazonaws.com
# RDS_DB_NAME iceranking
# RDS_USERNAME iceranking
# RDS_PASSWORD qmkL2YvhtuSS7FZM
# RDS_PORT 3306