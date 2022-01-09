from flask.globals import g
from flask_restful import Resource
from app.models.RankingResults import RankingResults
from app.models.RankingListTestModel import RankingListTest
from app.Responses import ApiErrorResponse, ApiResponse
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required

class RankingsResource(Resource):
    @RankingListTest.from_request(many=True)
    def get(self):        
        return ApiResponse(g.rankings).response()
    
class RankingResource(Resource):
    def __init__(self) -> None:
        self.reqparse = RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=False, location="json")
        self.reqparse.add_argument('includedMarks', type=int, required=False, location="json")
        self.reqparse.add_argument('order', type=str, required=False, location="json")
        self.reqparse.add_argument('grouping', type=str, required=False, location="json")
        self.reqparse.add_argument('minMark', type=int, required=False, location="json")
        self.reqparse.add_argument('roundingPrecision', type=int, required=False, location="json")
        self.reqparse.add_argument('markType', type=str, required=False, location="json")
    
    @RankingListTest.from_request
    def get(self, id):
        return ApiResponse(g.ranking).response()
    
    @jwt_required
    @RankingListTest.from_request
    def patch(self, id):
        g.ranking.update(self.reqparse)

        try:
            g.ranking.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.ranking).response()
    
    @jwt_required
    @RankingListTest.from_request
    def delete(self, id):
        try:
            g.ranking.delete()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class RankingResultsRankingResource(Resource):
    def __init__(self):
        pass

    def get(self, id):
        results = []

        try:
            query = RankingResults.query.filter_by(test_id=id).order_by(RankingResults.rank)
            results = RankingResults.load_many(query=query)
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        
        return ApiResponse(results).response()

