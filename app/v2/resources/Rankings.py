from flask_restful import Resource
from app.models.RankingResults import RankingResults
from app.models.RankingListTestModel import RankingListTest
from app.models.RestMixin import ApiErrorResponse, ApiResponse
from app.models.schemas import RankingListTestSchema, RankingListResultSchemaV2 as RankingListResultSchema, ResultSchema
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required

tests_schema = RankingListTestSchema(many=True, exclude=("rankinglist","tasks_in_progress"))
test_schema = RankingListTestSchema(exclude=("rankinglist","tasks_in_progress"))

results_schema = RankingListResultSchema(many=True)

class RankingsResource(Resource):
    def get(self):
        tests = []

        try:
            tests = RankingListTest.load()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(tests, tests_schema).response()
    
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
    
    def get(self, ranking_id):
        test = None

        try:
            test = RankingListTest.load(ranking_id)
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(test, test_schema).response()
    
    @jwt_required
    def patch(self, ranking_id):
        test = None

        try:
            test = RankingListTest.load(ranking_id)
        except ApiErrorResponse as e:
            return e.response()
        
        test.update(self.reqparse)

        try:
            test.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(test, test_schema).response()
    
    @jwt_required
    def delete(self, ranking_id):
        try:
            test = RankingListTest.load(ranking_id)
            test.delete()
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class RankingResultsRankingResource(Resource):
    def __init__(self):
        pass

    def get(self, ranking_id):
        results = []

        try:
            query = RankingResults.query.filter_by(test_id=ranking_id).order_by(RankingResults.rank)
            results = RankingResults.load(query=query)
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        
        return ApiResponse(results, results_schema).response()

