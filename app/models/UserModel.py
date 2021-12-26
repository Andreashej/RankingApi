from flask_jwt_extended.exceptions import WrongTokenError
from flask_jwt_extended.view_decorators import jwt_optional, verify_jwt_in_request
from .. import db
from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from flask.globals import g
from flask_jwt_extended import get_jwt_identity
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from flask_jwt_extended import create_access_token, create_refresh_token

from .RestMixin import RestMixin

class User(db.Model, RestMixin):
    RESOURCE_NAME = 'user'
    RESOURCE_NAME_PLURAL = 'users'
    INCLUDE_IN_JSON = ['email']
    BLOCK_FROM_JSON = ['password_hash','_email']

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    _email = db.Column('email', db.String(128), nullable=False)
    password_hash = db.Column(db.String(128))

    @hybrid_property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        if '@' not in email and '.' not in email:
            raise ValueError('An email address must contain both @ and .')
        
        self._email = email
    
    @email.expression
    def email(cls):
        return cls._email

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 1440):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)

        return s.dumps({'id' : self.id})
    
    def create_access_token(self):
        return create_access_token(identity = self.username)
    
    def create_refresh_token(self):
        return create_refresh_token(identity = self.username)
    
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        
        user = User.query.get(data['id'])
        return user
    
    @staticmethod
    def load_profile():
        current_user = None
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
        except Exception as e:
            return

        if current_user is None: return

        g.profile = User.find_by_username(current_user)
    
    @classmethod 
    def with_profile(cls, func):
        def user_decorator(*args, **kwargs):
            cls.load_profile()

            return func(*args, **kwargs)
        
        return user_decorator