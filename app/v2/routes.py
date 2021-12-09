from app.v2.resources.Rankings import RankingsResource, RankingResource, RankingResultsRankingResource
from app.v2.resources.RankingList import RankingListsResource, RankingListResource, RankingListTestsResource, RankingListTasksResource
from app.v2.resources.Competition import CompetitionResource, CompetitionsResource, CompetitionTestsResource
from app.v2.resources.Test import TestsResource, TestResource, TestResultsResource
from app.v2.resources.RankingResult import RankingResultResource, RankingResultMarksResource,RankingResultsResource
from app import api_v2 as api

api.add_resource(CompetitionsResource, '/competitions', endpoint='competitions')
api.add_resource(CompetitionResource, '/competitions/<int:competition_id>', endpoint='competition')
api.add_resource(CompetitionTestsResource, '/competitions/<int:competition_id>/tests', endpoint='competition_tests')

api.add_resource(TestsResource, '/tests', endpoint='tests')
api.add_resource(TestResource, '/tests/<int:test_id>', endpoint='test')
api.add_resource(TestResultsResource, '/tests/<int:test_id>/results', endpoint='test_results')

api.add_resource(RankingListsResource, '/rankinglists', endpoint="rankinglists")
api.add_resource(RankingListResource, '/rankinglists/<int:rankinglist_id>', endpoint="rankinglist")
api.add_resource(RankingListTestsResource, '/rankinglists/<int:rankinglist_id>/rankings', endpoint="rankinglist_rankings")
api.add_resource(RankingListTasksResource, '/rankinglists/<int:rankinglist_id>/tasks', endpoint="rankinglist_tasks")

api.add_resource(RankingsResource, '/rankings', endpoint='rankings')
api.add_resource(RankingResource, '/rankings/<int:ranking_id>', endpoint='ranking')
api.add_resource(RankingResultsRankingResource, '/rankings/<int:ranking_id>/results', endpoint='ranking_results_per_ranking')

api.add_resource(RankingResultsResource, '/rankingresults', endpoint='ranking_results')
api.add_resource(RankingResultResource, '/rankingresults/<int:result_id>', endpoint='ranking_result')
api.add_resource(RankingResultMarksResource, '/rankingresults/<int:result_id>/marks', endpoint='ranking_result_marks')

