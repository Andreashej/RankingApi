from flask_restful import Resource
from app.models.RestMixin import ApiErrorResponse, ApiResponse
from app.models.RankingResults import RankingResults
from app.models.schemas import ResultSchema, RankingListResultSchemaV2 as RankingListResultSchema

marks_schema = ResultSchema(many=True, exclude=("test",))

results_schema = RankingListResultSchema(many=True)
result_schema = RankingListResultSchema()

class RankingResultsResource(Resource):
    def __init__(self):
        pass

    def get(self):
        results = []

        try:
            results = RankingResults.load()
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(results, results_schema).response()

class RankingResultResource(Resource):
    def __init__(self):
        pass

    def get(self, result_id):
        result = None

        try:
            result = RankingResults.load(result_id)
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(result, result_schema).response()

class RankingResultMarksResource(Resource):
    def __init__(self):
        pass

    def get(self, result_id):
        result = None

        try:
            result = RankingResults.load(result_id)
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(result.marks, marks_schema).response()