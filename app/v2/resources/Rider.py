from flask.globals import g
from flask_restful import Resource, reqparse
from app.Responses import ApiResponse, ApiErrorResponse
from app.models.schemas import RiderSchema
from app.models.RiderModel import Rider
from flask_jwt_extended import jwt_required
from app import db

rider_schema_options = {
    'exclude': ["results", "aliases", "testlist"]
}

class RidersResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firstname', type= str, required = True, location = 'json')
        self.reqparse.add_argument('lastname', type= str, required = True, location = 'json')

    @Rider.from_request(many=True)
    def get(self):
        return ApiResponse(g.riders, RiderSchema, schema_options=rider_schema_options).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        try:
            rider = Rider(args['firstname'], args['lastname'])
            rider.save()
        except Exception as e:
            return ApiErrorResponse(e.args, 403).response()
        
        return ApiResponse(rider, RiderSchema, schema_options=rider_schema_options).response()

class RiderResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firstname', type= str, required = False, location = 'json')
        self.reqparse.add_argument('lastname', type= str, required = False, location = 'json')
    
    @Rider.from_request
    def get(self, id):
        return ApiResponse(g.rider, RiderSchema, schema_options=rider_schema_options).response()
    
    @jwt_required
    @Rider.from_request
    def patch(self, id):
        g.rider.update(self.reqparse)

        try:
            g.rider.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.rider, RiderSchema, schema_options=rider_schema_options).response()
    
    @jwt_required
    @Rider.from_request
    def delete(self, id):
        try:
            g.rider.delete()
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()