from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource, reqparse
from app.models.RestMixin import ApiResponse, ApiErrorResponse
from app.models.schemas import TestSchema, ResultSchema
from app.models import Test, Result, Competition, Rider, Horse
from app import db

tests_schema = TestSchema(many=True, exclude=("results","competition"))
test_schema = TestSchema(exclude=("results","competition"))

results_schema = ResultSchema(many=True, exclude=("test",))
result_schema = ResultSchema(exclude=("test",))

class TestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('competition_id')

    def get(self):
        tests = None
        try:
            tests = Test.load()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(tests, tests_schema).response()
    
    @jwt_required
    def delete(self):
        try:
            Competition.filter().delete()
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e))
        
        return ApiResponse(response_code=204).response()


class TestResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('order', type=str, required=False, location='json')
        self.reqparse.add_argument('mark_type', type=str, required=False, location='json')
        self.reqparse.add_argument('rounding_precision', type=int, required=False, location='json')
    
    def get(self, test_id):
        test = None
        try:
            test = Test.load(test_id)
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(test, test_schema).response()
    
    @jwt_required
    def patch(self, test_id):
        test = None

        try:
            test = Test.load(test_id)
        except ApiErrorResponse as e:
            return e.response()

        args = self.reqparse.parse_args()

        if args['order']:
            test.order = args['order']

        if args['mark_type']:
            test.mark_type = args['mark_type']

        if args['rounding_precision']:
            test.rounding_precision = args['rounding_precision']

        try:
            test.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(test, test_schema).response()
    
    @jwt_required
    def delete(self, test_id):
        test = None
        try:
            test = Test.load(test_id)
            test.delete()
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class TestResultsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('rider_id', type=int, required=True, location='json')
        self.reqparse.add_argument('horse_id', type=int, required=True, location='json')
        self.reqparse.add_argument('mark', type=float, required=True, location='json')
        self.reqparse.add_argument('state', type=str, required=False, location='json')

    def get(self, test_id):
        test = None

        try:
            test = Test.load(test_id)
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(test.results, results_schema).response()
    
    def post(self, test_id):
        test = None

        try:
            test = Test.load(test_id)
        except ApiErrorResponse as e:
            return e.response()

        args = self.reqparse.parse_args()

        result = None
        try:
            rider = Rider.load(args['rider_id'])
            horse = Horse.load(args['horse_id'])
            result = test.add_result(rider, horse, args['mark'], args['state'])
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        try:
            result.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(result, result_schema).response()

        
