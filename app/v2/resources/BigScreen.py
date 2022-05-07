from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse, ApiResponse
from flask import g, request
from app import socketio
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

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
        self.reqparse.add_argument('showOsd', type=bool, location='json')

    @ScreenGroup.from_request
    def get(self, id):
        return ApiResponse(g.screengroup).response()
    
    @jwt_required
    @ScreenGroup.from_request
    def patch(self, id):
        try:    
            template = request.json.get('template')
            template_data = request.json.get('templateData')
            hide = request.json.get('hide', False)

            if template is not None and template_data is not None:
                socketio.emit('ScreenGroup.TemplateChanged', {
                    'template': template,
                    'templateData': template_data
                }, namespace="/bigscreen", to=id)
            
            if hide:
                socketio.emit('ScreenGroup.HideAll', namespace="/bigscreen", to=id)

            g.screengroup.update(self.reqparse)
            g.screengroup.save()
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(g.screengroup).response()

class BigScreensResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('screenGroupId', type=int, location='json', required=True)

    @BigScreen.from_request(many=True)
    def get(self):
        return ApiResponse(g.bigscreens).response()

    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()
        try:
            screen_group = ScreenGroup.query.get(args['screenGroupId'])
        except NoResultFound:
            return ApiErrorResponse('Screengroup not found', 400).response()

        screen = BigScreen(screen_group_id=args['screenGroupId'], competition_id=screen_group.competition_id)

        try:
            screen.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(screen).response()

class BigScreenResource(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('screenGroupId', type=int, location='json')
        self.reqparse.add_argument('competitionId', type=int, location='json')
        self.reqparse.add_argument('role', type=str, location='json')
        self.reqparse.add_argument('rootFontSize', type=str, location='json')

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

        
        
        if g.bigscreen.screen_group is None and g.bigscreen.competition is not None:
            try:
                unassigned_screen_group = g.bigscreen.competition.screen_groups.filter_by(name="Unassigned").one()
            except NoResultFound:
                unassigned_screen_group = ScreenGroup(name="Unassigned", competition_id=g.bigscreen.competition.id)
                g.bigscreen.competition.screen_groups.append(unassigned_screen_group)
            except ApiErrorResponse as e:
                return e.response()
            
            unassigned_screen_group.screens.append(g.bigscreen)
            try:
                unassigned_screen_group.save()
            except ApiErrorResponse as e:
                return e.response()
        
        return ApiResponse(g.bigscreen).response()
    
    @jwt_required
    @BigScreen.from_request
    def delete(self, id):
        try:
            g.bigscreen.screen_group_id = None
            g.bigscreen.competition_id = None
            g.bigscreen.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(response_code=204).response()

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
