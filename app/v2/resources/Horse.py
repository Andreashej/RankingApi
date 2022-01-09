from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from app.models.ResultModel import Result
from app.Responses import ApiErrorResponse
from app.models import Horse
from app.Responses import ApiResponse
from flask.globals import g
from flask_restful import reqparse
from app import db

class HorsesResource(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('feifId', type=str, required=True, location='json')
        self.reqparse.add_argument('horseName', type=str, required=False, default='', location='json')
    
    @Horse.from_request(many=True)
    def get(self):
        return ApiResponse(g.horses).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        horse = Horse(args['feifId'], args['horseName'])

        try:
            horse.wf_lookup(True)
            horse.save()
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        return ApiResponse(horse, 201).response()

class HorseResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('feifId', type=str, required=False, location='json')
        self.reqparse.add_argument('horseName', type=str, required=False, default='', location='json')
    
    @Horse.from_request
    def get(self, id):
        return ApiResponse(g.horse).response()
    
    @jwt_required
    @Horse.from_request
    def patch(self, id):
        if g.horse.last_lookup is not None and g.horse.lookup_error is not True:
            return ApiErrorResponse("It is not allowed to modify a horse that has been validated against WorldFengur", 40).response()

        g.horse.update(self.reqparse)

        try:
            g.horse.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.horse).response()
    
    @jwt_required
    @Horse.from_request
    def delete(self, id):
        if len(g.horse.results) > 0:
            return ApiErrorResponse("You cannot delete a horse that has results!", 403).response()

        try:
            g.horse.delete()
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()
    
class HorseResultsResource(Resource):

    @Horse.from_request
    def get(self, id):
        try:
            results = Result.load_many(g.horse.results)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(results).response()