from flask.globals import request, g, current_app
from flask_jwt_extended.utils import create_access_token, get_jwt_identity
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, get_raw_jwt
from app.Responses import ApiErrorResponse, ApiResponse

from app.models import User, RevokedToken

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
            auth_object = { 
                'data': current_user.to_json(),
                'accessToken': current_user.create_access_token(),
                'refreshToken': current_user.create_refresh_token()
            }

            if current_app.config['DEBUG']:
                auth_object.update({
                    'access_token': auth_object['accessToken']
                })

            return auth_object
        
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
        return { 'accessToken': access_token }

class ProfileResource(Resource):
    @jwt_required
    @User.with_profile
    def get(self):
        return ApiResponse(g.profile).response()

class UsersResource(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        self.reqparse.add_argument('email', type=str, required=True, location='json')
    
    @User.from_request(many=True)
    def get(self):
        return ApiResponse(g.users).response()
    
    @jwt_required
    def post(self):
        user = User()
        try:
            user.update(self.reqparse)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(user, 201).response()

class UserResource(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=False, location='json')
        self.reqparse.add_argument('password', type=str, required=False, location='json')

    @User.from_request
    def get(self, id):
        return ApiResponse(g.user).response()
    
    @jwt_required
    @User.from_request
    def patch(self, id):
        args = self.reqparse.parse_args()
        
        if args['password'] is not None:
            g.user.hash_password(args['password'])

        try:
            g.user.update(self.reqparse)
            g.user.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(g.user).response()
