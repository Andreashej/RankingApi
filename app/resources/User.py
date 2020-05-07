from flask_restful import Resource, reqparse
from flask import g
from app import db, auth

from app.models import User, UserSchema

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class UsersResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
    
    def get(self):
        users = User.query.all()

        if len(users) == 0:
            return { 'status': 'NOT FOUND', 'message': "No users found."}, 404
        
        return { 'status': 'OK', 'data': users_schema.dump(users).data }
    
    def post(self):
        args = self.reqparse.parse_args()

        if User.query.filter_by(username = args['username']).first() is not None:
            return {'status': 'EXISTS', 'message': 'The username {} is already taken.'.format(args['username'])}, 400
        
        user = User(username=args['username'])
        user.hash_password(args['password'])

        try:
            db.session.add(user)
            db.session.commit()
        except:
            return {'status': 'ERROR', 'message': 'Unknown error'}, 500

        return { 'status': 'OK', 'data': user_schema.dump(user).data}, 201

class UserResource(Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first()

        if user is None:
            return { 'status': 'NOT FOUND'}, 404
        
        return { 'status': 'OK', 'data': user_schema.dump(user).data }

class TokenResource(Resource):
    @auth.login_required
    def post(self):
        token = g.user.generate_auth_token()

        return {'status': 'OK', 'data': user_schema.dump(g.user).data, 'token': token.decode('ascii')}

class ProfileResource(Resource):
    decorators = [auth.login_required]

    def get(self):
        return { 'status': 'OK', 'data': user_schema.dump(g.user).data }