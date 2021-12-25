from flask.globals import g
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource, reqparse
from app.Responses import ApiResponse, ApiErrorResponse
from app.models import Test, Result, Rider, Horse
from app import db

class TestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('competition_id')

    @Test.from_request(many=True)
    def get(self):
        return ApiResponse(g.tests).response()
    
    @jwt_required
    @Test.from_request(many=True)
    def delete(self):
        try:
            g.tests.delete()
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
    
    @Test.from_request
    def get(self, id):
        return ApiResponse(g.test).response()
    
    @jwt_required
    @Test.from_request
    def patch(self, id):
        args = self.reqparse.parse_args()

        if args['order']:
            g.test.order = args['order']

        if args['mark_type']:
            g.test.mark_type = args['mark_type']

        if args['rounding_precision']:
            g.test.rounding_precision = args['rounding_precision']

        try:
            g.test.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.test).response()
    
    @jwt_required
    @Test.from_request
    def delete(self, id):
        try:
            g.test.delete()
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

    @Test.from_request
    def get(self, id):        
        return ApiResponse(Result.load_many(g.test.results)).response()

    @jwt_required
    @Test.from_request    
    def post(self, id):

        args = self.reqparse.parse_args()

        result = None
        try:
            rider = Rider.load_one(args['rider_id'])
            horse = Horse.load_one(args['horse_id'])
            result = g.test.add_result(rider, horse, args['mark'], args['state'])
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        try:
            result.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(result).response()

        
