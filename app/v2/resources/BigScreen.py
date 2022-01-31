from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse, ApiResponse
from flask import g, request
from app import socketio

from app.models.BigScreenModel import BigScreen
from app.models.ScreenGroupModel import ScreenGroup

class ScreenGroupsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('competitionId', type=int, location='json', required=True)
    
    @ScreenGroup.from_request(many=True)
    def get(self):
        return ApiResponse(g.screengroups).response()
    
    def post(self):
        args = self.reqparse.parse_args()

        group = ScreenGroup(competition_id=args['competitionId'])

        try:
            group.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(group).response()

class ScreenGroupResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('template', type=str, location='json')

    @ScreenGroup.from_request
    def get(self, id):
        return ApiResponse(g.screengroup).response()
    
    @ScreenGroup.from_request
    def patch(self, id):
        try:
            g.screengroup.update(self.reqparse)
            g.screengroup.save()
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(g.screengroup).response()

class BigScreensResource(Resource):
    @BigScreen.from_request(many=True)
    def get(self):
        return ApiResponse(g.bigscreens).response()

class BigScreenResource(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('screenGroupId', type=int, location='json')

    @BigScreen.from_request
    def get(self, id):
        return ApiResponse(g.bigscreen).response()
    
    @BigScreen.from_request
    def patch(self, id):
        try:
            g.bigscreen.update(self.reqparse)
            g.bigscreen.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(g.bigscreen).response()

class CollectingRingCallResource(Resource):
    def post(self):
        args = request.json
        target_groups = ScreenGroup.query.filter_by(competition_id=args['competitionId'], template="collectingring").all()

        end_time = datetime.now() + timedelta(seconds=args['time'])

        for target_group in target_groups:
            socketio.emit("CollectingRing.Call",{
                "riders": args['riders'],
                "endTime": end_time.isoformat(),
                "competition": target_group.competition.to_json()
            }, to=target_group.id, namespace="/bigscreen")

        return None, 201
