from os import execv
from flask_jwt_extended.utils import create_access_token, get_jwt_identity
from flask_migrate import current
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, get_raw_jwt, jwt_optional
from .. import db

from ..models import User, UserSchema, RevokedToken

user_schema = UserSchema()
users_schema = UserSchema(many=True)

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, location='json')
parser.add_argument('password', type=str, required=True, location='json')

class UsersResource(Resource):
    def get(self):
        try:
            users = User.filter().all()
        except Exception as e:
            return { 'message': str(e) }

        if len(users) == 0:
            return { 'message': "No users found." }, 404
        
        return { 'data': users_schema.dump(users) }
    
    def post(self):
        args = parser.parse_args()

        if User.find_by_username(args['username']):
            return { 'message': 'The username {} is already taken.'.format(args['username']) }, 400
        
        user = User(username=args['username'])
        user.hash_password(args['password'])

        try:
            db.session.add(user)
            db.session.commit()
        except:
            return { 'message': 'Unknown error' }, 500

        return { 
            'data': user_schema.dump(user),
            'access_token': user.create_access_token(),
            'refresh_token': user.create_refresh_token()
        }, 201

class UserResource(Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first()

        if user is None:
            return { 'status': 'NOT FOUND'}, 404
        
        return { 'data': user_schema.dump(user) }

class UserLogin(Resource):
    def post(self):
        args = parser.parse_args()

        current_user = User.find_by_username(args['username'])

        if not current_user:
            return { 'message': f"User {args['username']} does not exist" }, 404

        if current_user.verify_password(args['password']):
            return { 
                'data': user_schema.dump(current_user),
                'access_token': current_user.create_access_token(),
                'refresh_token': current_user.create_refresh_token()
            }
        
        return { 'message': "Wrong credentials" }

class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']

        try:
            RevokedToken.revoke(jti)
        except:
            return { 'message': 'Something went wrong' }, 500

        return { 'message': 'Access token has been revoked'}

class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']

        try:
            RevokedToken.revoke(jti)
        except:
            return { 'message': 'Something went wrong' }, 500

        return { 'message': 'Refresh token has been revoked'}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()

        access_token = create_access_token(identity=current_user)
        return { 'access_token': access_token }

class ProfileResource(Resource):
    @jwt_optional
    def get(self):
        current_user = User.find_by_username(get_jwt_identity())

        if not current_user:
            return { 'message': 'You are not logged in.' }, 401
        
        return { 'data': user_schema.dump(current_user) }