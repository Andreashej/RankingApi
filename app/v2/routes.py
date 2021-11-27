from app.v2.resources.Rankings import RankingsResource, RankingResource
from app.v2.resources.RankingList import RankingListsResource, RankingListResource, RankingListTestsResource, RankingListTasksResource
from app.v2.resources.Competition import CompetitionResource, CompetitionsResource, CompetitionTestsResource
from app.v2.resources.Test import TestsResource, TestResource
from app import api_v2 as api

api.add_resource(CompetitionsResource, '/competitions', endpoint='competitions')
api.add_resource(CompetitionResource, '/competitions/<int:competition_id>', endpoint='competition')
api.add_resource(CompetitionTestsResource, '/competitions/<int:competition_id>/tests', endpoint='competition_tests')

api.add_resource(TestsResource, '/tests', endpoint='tests')
api.add_resource(TestResource, '/tests/<int:test_id>', endpoint='test')

api.add_resource(RankingListsResource, '/rankinglists', endpoint="rankinglists")
api.add_resource(RankingListResource, '/rankinglists/<int:rankinglist_id>', endpoint="rankinglist")
api.add_resource(RankingListTestsResource, '/rankinglists/<int:rankinglist_id>/tests', endpoint="rankinglist_tests")
api.add_resource(RankingListTasksResource, '/rankinglists/<int:rankinglist_id>/tasks', endpoint="rankinglist_tasks")

api.add_resource(RankingsResource, '/rankings', endpoint='rankings')
api.add_resource(RankingResource, '/rankings/<int:ranking_id>', endpoint='ranking')