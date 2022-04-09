import sentry_sdk
from socket import SocketIO
from flask import Flask, g, request
from flask import Blueprint
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt import PyJWTError
from flask_mail import Mail
from redis import Redis
import rq
import os
from app.utils import camel_to_snake
from flask_socketio import SocketIO
from sentry_sdk.integrations.flask import FlaskIntegration
from . import config

if config.SENTRY_DSN is not None:
  sentry_sdk.init(
      dsn=config.SENTRY_DSN,
      integrations=[FlaskIntegration()],

      # Set traces_sample_rate to 1.0 to capture 100%
      # of transactions for performance monitoring.
      # We recommend adjusting this value in production.
      traces_sample_rate=0.2
  )


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name == "search_results":
        return False
    else:
        return True

def request_camel_to_snake(*args, **kwargs):
  if request.json is not None:
    new_json = { }
    for key in request.json:
      print(key)
      new_json[camel_to_snake(key)] = request.json[key]
    request.json = new_json
    print ("Done")

class FixedApi(Api):
  def error_router(self, original_handler, e):
    if not isinstance(e, PyJWTError) and not isinstance(e, JWTExtendedException) and self._has_fr_route():
      try:
        return self.handle_error(e)
      except Exception:
        pass  # Fall through to original handler
    return original_handler(e)

migrate = Migrate()
ma = Marshmallow()
cors = CORS()
db = SQLAlchemy()

api_v2_bp = Blueprint('v2', __name__)
api_v2 = FixedApi(api_v2_bp)

socketio = SocketIO()

cache = Cache()

auth = HTTPBasicAuth()

jwt = JWTManager()

mail = Mail()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')   
    app.config.from_object(config)

    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    db.init_app(app)
    migrate.init_app(app, db, include_object = include_object)
    ma.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*', message_queue=app.config['REDIS_URL'], cors_credentials=True)

    with app.app_context():
        from app import models, commands
        from app.v2 import routes as routes_v2
        from app import events

        app.redis = Redis.from_url(app.config['REDIS_URL'])
        
        app.task_queue = rq.Queue(app.config['QUEUE'], connection=app.redis, default_timeout=-1)
        app.before_request(models.UserModel.User.load_profile)
        app.register_blueprint(api_v2_bp, url_prefix='/v2')

        os.makedirs(app.config['ISIRANK_FILES'], exist_ok=True)
        os.makedirs(app.config['IMAGE_FILES'], exist_ok=True)

        def healthcheck():
          return { "message": "I am healthy :)"}, 200

        app.add_url_rule('/', view_func=healthcheck)
          
        return app

from .models import RevokedToken
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)
    