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
        self.reqparse.add_argument('competitionId')

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
        self.reqparse.add_argument('markType', type=str, required=False, location='json')
        self.reqparse.add_argument('roundingPrecision', type=int, required=False, location='json')
    
    @Test.from_request
    def get(self, id):
        return ApiResponse(g.test).response()
    
    @jwt_required
    @Test.from_request
    def patch(self, id):
        args = self.reqparse.parse_args()

        g.test.update(self.reqparse)

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
        self.reqparse.add_argument('riderId', type=int, required=True, location='json')
        self.reqparse.add_argument('horseId', type=int, required=True, location='json')
        self.reqparse.add_argument('mark', type=float, required=True, location='json')
        self.reqparse.add_argument('state', type=str, required=False, location='json')

    @Test.from_request
    def get(self, id):   
        try:
            results = Result.load_many(g.test.results)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(results).response()

    @jwt_required
    @Test.from_request    
    def post(self, id):

        args = self.reqparse.parse_args()

        result = None
        try:
            rider = Rider.load_one(args['riderId'])
            horse = Horse.load_one(args['horseId'])
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

        
