from flask.globals import g
from flask_restful import Resource
from app.models.RankingResults import RankingResults
from app.models.RankingListTestModel import RankingListTest
from app.Responses import ApiErrorResponse, ApiResponse
from app.models.schemas import RankingListTestSchema, RankingListResultSchemaV2 as RankingListResultSchema
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required

tests_schema = RankingListTestSchema(many=True, exclude=("rankinglist","tasks_in_progress"))
test_schema = RankingListTestSchema(exclude=("rankinglist","tasks_in_progress"))

results_schema = RankingListResultSchema(many=True)

class RankingsResource(Resource):
    @RankingListTest.from_request(many=True)
    def get(self):        
        return ApiResponse(g.rankings, tests_schema).response()
    
class RankingResource(Resource):
    def __init__(self) -> None:
        self.reqparse = RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=False, location="json")
        self.reqparse.add_argument('included_marks', type=int, required=False, location="json")
        self.reqparse.add_argument('order', type=str, required=False, location="json")
        self.reqparse.add_argument('grouping', type=str, required=False, location="json")
        self.reqparse.add_argument('min_mark', type=int, required=False, location="json")
        self.reqparse.add_argument('rounding_precision', type=int, required=False, location="json")
        self.reqparse.add_argument('mark_type', type=str, required=False, location="json")
    
    @RankingListTest.from_request
    def get(self, id):
        return ApiResponse(g.test, test_schema).response()
    
    @jwt_required
    @RankingListTest.from_request
    def patch(self, id):
        g.ranking.update(self.reqparse)

        try:
            g.ranking.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.ranking, test_schema).response()
    
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

        
        return ApiResponse(results, results_schema).response()

