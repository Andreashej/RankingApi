from app.v1.resources.Logs import LogsResource
from app.v1.resources.Result import ResultsResource, ResultResource
from app.v1.resources.Rider import RiderAliasResource, RiderResource, RidersResource, RiderResultResource
from app.v1.resources.Ranking import RankingResource, RankingsResource, RankingListResource, RankingListResultsResource, RankingListsResource
from app.v1.resources.Competition import CompetitionsResource, CompetitionResource
from app.v1.resources.Test import TestsResource, TestResource
from app.v1.resources.Horse import HorsesResource, HorseResource, HorseResultResource
from app.v1.resources.Task import TaskResource, TasksResource
from app.v1.resources.User import TokenRefresh, UserLogin, UserLogoutAccess, UserLogoutRefresh, UsersResource, UserResource, ProfileResource
from app.v1.resources.Search import SearchResource
from app.v1.resources.TestCatalog import TestCatalogResource, TestDefinitionResource

from app import api, graphql_bp

api.add_resource(ResultsResource, '/results', endpoint="results")
api.add_resource(ResultResource, '/results/<int:result_id>', endpoint="result")

api.add_resource(RidersResource, '/riders', endpoint='riders')
api.add_resource(RiderResource, '/riders/<int:rider_id>', endpoint='rider')
api.add_resource(RiderResultResource, '/riders/<int:rider_id>/results/<testcode>', endpoint='result_for_rider')
api.add_resource(RiderAliasResource, '/riders/<int:rider_id>/aliases', endpoint='rider_alias')

api.add_resource(HorsesResource, '/horses', endpoint='horses')
api.add_resource(HorseResource, '/horses/<int:horse_id>', endpoint='horse')
api.add_resource(HorseResultResource, '/horses/<int:horse_id>/results/<string:testcode>', endpoint='result_for_horse')

api.add_resource(RankingsResource, '/rankings', endpoint='rankings')
api.add_resource(RankingResource, '/rankings/<string:listname>', endpoint='ranking')

api.add_resource(RankingListsResource, '/rankings/<string:listname>/tests', endpoint='rankinglists')
api.add_resource(RankingListResource, '/rankings/<string:listname>/tests/<string:testcode>', endpoint='rankinglist-pretty')
api.add_resource(RankingListResource, '/rankingtest/<int:id>', endpoint='rankinglist')

api.add_resource(RankingListResultsResource, '/rankings/<string:listname>/tests/<string:testcode>/results', endpoint='resultlist')


api.add_resource(CompetitionsResource, '/competitions', endpoint='competitions')
api.add_resource(CompetitionResource, '/competitions/<int:competition_id>', endpoint='competition')

api.add_resource(TestsResource, '/tests', endpoint='tests')
api.add_resource(TestResource, '/tests/<int:test_id>', endpoint='test')

api.add_resource(TasksResource, '/tasks', endpoint='tasks')
api.add_resource(TaskResource, '/tasks/<string:task_id>', endpoint='task')

api.add_resource(UsersResource, '/users', endpoint='users')
api.add_resource(UserResource, '/users/<string:username>', endpoint='user')
api.add_resource(UserLogin, '/login', endpoint='login')
api.add_resource(UserLogoutAccess, '/logout/access', endpoint='logoutaccess')
api.add_resource(UserLogoutRefresh, '/logout/refresh', endpoint='logoutrefresh')
api.add_resource(TokenRefresh, '/token/refresh', endpoint='tokenrefresh')

api.add_resource(ProfileResource, '/profile', endpoint='profile')

api.add_resource(SearchResource, '/search', endpoint='search')

api.add_resource(TestCatalogResource, '/test-catalog', endpoint="test-catalog")
api.add_resource(TestDefinitionResource, '/test-catalog/<string:testcode>', endpoint="test-definition")

api.add_resource(LogsResource, "/logs", endpoint="logs")

from flask_graphql import GraphQLView
from app.graphql.schema import schema

graphql_bp.add_url_rule('/', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))