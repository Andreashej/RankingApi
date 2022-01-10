from flask.globals import g
from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse
from app.models.ResultModel import Result
from app.Responses import ApiResponse
from app.models.RiderModel import Rider
from app.models.HorseModel import Horse
from flask_jwt_extended.view_decorators import jwt_required

class ResultsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('riderId', type=int, required=True, location='json')
        self.reqparse.add_argument('horseId', type=int, required=True, location='json')
        self.reqparse.add_argument('mark', type=float, required=True, location='json')
        self.reqparse.add_argument('state', type=str, required=False, location='json')

    @Result.from_request(many=True)
    def get(self):   
        return ApiResponse(g.results).response()

    @jwt_required
    @Result.from_request    
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

class ResultResource(Resource):

    @Result.from_request
    def get(self, id):
        return ApiResponse(g.result).response()