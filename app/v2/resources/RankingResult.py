from flask.globals import g
from flask_restful import Resource
from app.models.RankingResults import use_ranking_results, use_ranking_result
from app.models.RestMixin import ApiErrorResponse, ApiResponse
from app.models.RankingResults import RankingResults
from app.models.schemas import ResultSchema, RankingListResultSchemaV2 as RankingListResultSchema

marks_schema = ResultSchema(many=True, exclude=("test",))

results_schema = RankingListResultSchema(many=True)
result_schema = RankingListResultSchema()

class RankingResultsResource(Resource):
    def __init__(self):
        pass
    
    @use_ranking_results
    def get(self):
        return ApiResponse(g.ranking_results, results_schema).response()

class RankingResultResource(Resource):
    def __init__(self):
        pass
    
    @use_ranking_result
    def get(self, result_id):
        return ApiResponse(g.ranking_result, result_schema).response()

class RankingResultMarksResource(Resource):
    def __init__(self):
        pass

    @use_ranking_result
    def get(self, result_id):        
        return ApiResponse(g.ranking_result.marks, marks_schema).response()