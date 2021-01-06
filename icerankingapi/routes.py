from .resources.Result import ResultsResource, ResultResource
from icerankingapi.resources.Rider import RiderResource, RidersResource, RiderResultResource
from icerankingapi.resources.Ranking import RankingResource, RankingsResource, RankingListResource, RankingListResultsResource, RankingListsResource
from icerankingapi.resources.Competition import CompetitionsResource, CompetitionResource
from icerankingapi.resources.Test import TestsResource, TestResource
from icerankingapi.resources.Horse import HorsesResource, HorseResource, HorseResultResource
from icerankingapi.resources.Task import TaskResource, TasksResource
from icerankingapi.resources.User import TokenRefresh, UserLogin, UserLogoutAccess, UserLogoutRefresh, UsersResource, UserResource, ProfileResource
from icerankingapi.resources.Search import SearchResource
from icerankingapi.resources.TestCatalog import TestCatalogResource, TestDefinitionResource

from icerankingapi import api

api.add_resource(ResultsResource, '/results', endpoint="results")
api.add_resource(ResultResource, '/results/<int:result_id>', endpoint="result")

api.add_resource(RidersResource, '/riders', endpoint='riders')
api.add_resource(RiderResource, '/riders/<int:rider_id>', endpoint='rider')
api.add_resource(RiderResultResource, '/riders/<int:rider_id>/results/<testcode>', endpoint='result_for_rider')

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