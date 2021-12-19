from flask.globals import g
from flask_restful import Resource
from app.Responses import ApiErrorResponse, ApiResponse
from app.models.RankingResults import RankingResults
from app.models.schemas import ResultSchema, RankingListResultSchemaV2 as RankingListResultSchema


mark_schema_options = {
    'exclude': ['test']
}

class RankingResultsResource(Resource):
    def __init__(self):
        pass
    
    @RankingResults.from_request(many=True)
    def get(self):
        return ApiResponse(g.ranking_results, RankingListResultSchema).response()

class RankingResultResource(Resource):
    def __init__(self):
        pass
    
    @RankingResults.from_request
    def get(self, id):
        return ApiResponse(g.ranking_result, RankingListResultSchema).response()

class RankingResultMarksResource(Resource):
    def __init__(self):
        pass

    @RankingResults.from_request
    def get(self, id):        
        return ApiResponse(g.ranking_result.marks, ResultSchema, schema_options=mark_schema_options).response()