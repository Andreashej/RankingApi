from flask.globals import g
from flask_restful import Resource
from app.models.TestModel import Test
from app.models.CompetitionModel import Competition
from app.Responses import ApiErrorResponse
from app.models.ResultModel import Result
from app.Responses import ApiResponse
from app.models.RankingResultsModel import RankingResults

class RankingResultsResource(Resource):
    def __init__(self):
        pass
    
    @RankingResults.from_request(many=True)
    def get(self):
        return ApiResponse(g.ranking_results).response()

class RankingResultResource(Resource):
    def __init__(self):
        pass
    
    @RankingResults.from_request
    def get(self, id):
        return ApiResponse(g.ranking_result).response()

class RankingResultMarksResource(Resource):
    def __init__(self):
        pass

    @RankingResults.from_request
    def get(self, id):        
        try:
            query = g.ranking_result.marks.join(Test).join(Competition).order_by(Competition.last_date)
            results = Result.load_many(query)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(results).response()