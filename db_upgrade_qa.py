import os
from flask_migrate import upgrade, Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

os.environ['RDS_USERNAME'] = 'iceapp'
os.environ['RDS_PASSWORD'] = 'YqJh1os3oMiu8fZ53p0N'
os.environ['RDS_HOSTNAME'] = 'iceranking-qa.c8fmxoomvwpn.eu-central-1.rds.amazonaws.com'
os.environ['RDS_PORT'] = '3306'
os.environ['RDS_DB_NAME'] = 'iceranking'

# from app import create_app
from app import config

migrate = Migrate()
db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    from app import models

    upgrade()