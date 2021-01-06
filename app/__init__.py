from flask import Flask, g
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
from redis import Redis
import rq

from . import config

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

api_bp = Blueprint('api', __name__)
api = FixedApi(api_bp)

cache = Cache()

auth = HTTPBasicAuth()

jwt = JWTManager()

def create_app():
    app = Flask(__name__)   
    app.config.from_object(config)

    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app import routes, models

        db.create_all()

        app.redis = Redis.from_url(app.config['REDIS_URL'])
        
        app.task_queue = rq.Queue(app.config['QUEUE'], connection=app.redis, default_timeout=-1)


        app.register_blueprint(api_bp, url_prefix='/api')

        @app.route('/')
        def healthcheck():
            return "Application is running"

        return app

from .models import User
@auth.verify_password
def verify_password(username_or_token, password):

    user = User.verify_auth_token(username_or_token)

    if not user:
        user = User.query.filter_by(username = username_or_token).first()

        if not user or not user.verify_password(password):
            return False
    
    g.user = user

    return True

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)