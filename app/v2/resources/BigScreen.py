from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse, ApiResponse
from flask import g, request
from app import socketio
from flask_jwt_extended import jwt_required

from app.models.BigScreenModel import BigScreen
from app.models.ScreenGroupModel import ScreenGroup

class ScreenGroupsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('competitionId', type=int, location='json', required=True)
        self.reqparse.add_argument('name', type=str, location='json', required=True)
    
    @ScreenGroup.from_request(many=True)
    def get(self):
        return ApiResponse(g.screengroups).response()
    
    def post(self):
        args = self.reqparse.parse_args()

        group = ScreenGroup(competition_id=args['competitionId'], name=args['name'])

        try:
            group.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(group).response()

class ScreenGroupResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('template', type=str, location='json')
        # self.reqparse.add_argument('templateData', type=dict, location='json')
        self.reqparse.add_argument('testId', type=int, location='json')

    @ScreenGroup.from_request
    def get(self, id):
        return ApiResponse(g.screengroup).response()
    
    @jwt_required
    @ScreenGroup.from_request
    def patch(self, id):
        try:    
            template = request.json.get('template')
            template_data = request.json.get('templateData')

            if template is not None and template_data is not None:
                socketio.emit('ScreenGroup.TemplateChanged', {
                    'template': template,
                    'templateData': template_data
                }, namespace="/bigscreen", to=id)

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
    
    @jwt_required
    @BigScreen.from_request
    def patch(self, id):
        try:
            g.bigscreen.update(self.reqparse)
            g.bigscreen.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(g.bigscreen).response()

class CollectingRingCallResource(Resource):
    @jwt_required
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
