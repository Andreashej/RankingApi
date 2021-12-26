from app.auth.resources import TokenRefresh, UserLogin, UserLogoutAccess, UserLogoutRefresh, ProfileResource, UsersResource, UserResource

from app import api_auth as api

api.add_resource(UserLogin, '/login', endpoint='login')
api.add_resource(UserLogoutAccess, '/logout/access', endpoint='logoutaccess')
api.add_resource(UserLogoutRefresh, '/logout/refresh', endpoint='logoutrefresh')
api.add_resource(TokenRefresh, '/token/refresh', endpoint='tokenrefresh')
api.add_resource(ProfileResource, '/profile', endpoint='profile')
api.add_resource(UsersResource, '/users', endpoint='users')
api.add_resource(UserResource, '/users/<int:id>', endpoint='user')