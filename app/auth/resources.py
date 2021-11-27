from flask.globals import request
from flask_jwt_extended.utils import create_access_token, get_jwt_identity
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, get_raw_jwt

from app.models import User, UserSchema, RevokedToken

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=False, location='json')
        self.parser.add_argument('password', type=str, required=False, location='json')

    def post(self):
        args = self.parser.parse_args()
        username = args['username'] or request.form.get("username")
        password = args['password'] or request.form.get("password")
        
        if not (username and password):
            return { 'message': 'Could not find username and password in request payload' }, 400

        current_user = User.find_by_username(username)

        if not current_user:
            return { 'message': f"User {username} does not exist" }, 404

        if current_user.verify_password(password):
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