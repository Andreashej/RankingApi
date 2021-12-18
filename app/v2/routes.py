from app.v2.resources.Rider import RidersResource, RiderResource
from app.v2.resources.Rankings import RankingsResource, RankingResource, RankingResultsRankingResource
from app.v2.resources.RankingList import RankingListsResource, RankingListResource, RankingListTestsResource, RankingListTasksResource
from app.v2.resources.Competition import CompetitionResource, CompetitionsResource, CompetitionTestsResource
from app.v2.resources.Test import TestsResource, TestResource, TestResultsResource
from app.v2.resources.RankingResult import RankingResultResource, RankingResultMarksResource,RankingResultsResource
from app import api_v2 as api

api.add_resource(CompetitionsResource, '/competitions', endpoint='competitions')
api.add_resource(CompetitionResource, '/competitions/<int:id>', endpoint='competition')
api.add_resource(CompetitionTestsResource, '/competitions/<int:id>/tests', endpoint='competition_tests')

api.add_resource(TestsResource, '/tests', endpoint='tests')
api.add_resource(TestResource, '/tests/<int:id>', endpoint='test')
api.add_resource(TestResultsResource, '/tests/<int:id>/results', endpoint='test_results')

api.add_resource(RankingListsResource, '/rankinglists', endpoint="rankinglists")
api.add_resource(RankingListResource, '/rankinglists/<int:id>', endpoint="rankinglist")
api.add_resource(RankingListTestsResource, '/rankinglists/<int:id>/rankings', endpoint="rankinglist_rankings")
api.add_resource(RankingListTasksResource, '/rankinglists/<int:id>/tasks', endpoint="rankinglist_tasks")

api.add_resource(RankingsResource, '/rankings', endpoint='rankings')
api.add_resource(RankingResource, '/rankings/<int:id>', endpoint='ranking')
api.add_resource(RankingResultsRankingResource, '/rankings/<int:id>/results', endpoint='ranking_results_per_ranking')

api.add_resource(RankingResultsResource, '/rankingresults', endpoint='ranking_results')
api.add_resource(RankingResultResource, '/rankingresults/<int:id>', endpoint='ranking_result')
api.add_resource(RankingResultMarksResource, '/rankingresults/<int:id>/marks', endpoint='ranking_result_marks')

api.add_resource(RidersResource, '/riders', endpoint='riders')
api.add_resource(RiderResource, '/riders/<int:id>', endpoint='rider')