from operator import or_
from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse, ApiResponse
from flask import g, request
from app import socketio, db
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app.models import Competition, BigScreenRoute, Test
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

class BigScreenRoutesResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('priority', type=int, location='json', required=True)
        self.reqparse.add_argument('screenGroupId', type=int, location='json', required=True)
        self.reqparse.add_argument('tests', type=int, action='append', location='json')
        self.reqparse.add_argument('templates', type=str, action='append', location='json')
    
    @jwt_required
    @Competition.from_request
    def get(self, id):
        return ApiResponse(BigScreenRoute.load_many(g.competition.bigscreen_routes)).response()
    
    @jwt_required
    def post(self, id):
        args = self.reqparse.parse_args()
        competition = Competition.query.get(id)

        if not competition.is_admin:
            return ApiErrorResponse('You are not an admin of this competition', 401).response()

        if competition is None:
            return ApiErrorResponse('Competition not found', 404).response()
        
        if not competition.is_admin:
            return ApiErrorResponse('You are not an admin of this competition', 401).response()
        
        route_exists = competition.bigscreen_routes.filter_by(screen_group_id = args['screenGroupId']).first()

        if route_exists is not None:
            return ApiErrorResponse(f"Route for screen group {args['screenGroupId']} already exists for this competition", 400).response()

        screen_group = ScreenGroup.query.get(args['screenGroupId'])

        if screen_group is None:
            return ApiErrorResponse('Screen Group not found', 404).response()

        if screen_group.competition.id != competition.id:
            return ApiErrorResponse('Screen Group is not a child of this competition', 400).response()
        
        route = BigScreenRoute(priority=args['priority'], screen_group=screen_group, competition=competition, templates=args['templates'])

        for test_id in args['tests']:
            test = Test.query.get(test_id)

            if test is None:
                continue
            
            route.tests.append(test)
        
        # for template in args['templates']:
        #     template_route = TemplateRoute(template_name=template)
        #     db.session.add(template_route)
        #     route.templates.append(template_route)
        
        route.save()

        return ApiResponse(route).response()

class BigScreenRouteResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('priority', type=int, location='json', required=False)
        self.reqparse.add_argument('screenGroupId', type=int, location='json', required=False)
        self.reqparse.add_argument('tests', type=int, action='append', location='json')
        self.reqparse.add_argument('templates', type=str, action='append', location='json')

    @jwt_required
    @Competition.from_request
    def patch(self, id, route_id):
        if not g.competition.is_admin:
            return ApiErrorResponse('You are not an admin of this competition', 401).response()

        route = g.competition.bigscreen_routes.filter_by(id=route_id).first()

        if route is None:
            return ApiErrorResponse('Route not found', 404).response()

        args = self.reqparse.parse_args()

        if args['priority'] is not None:
            route.priority = args['priority']
        
        if args['screenGroupId'] is not None:
            route.screenGroupId = args['screenGroupId']

        route.tests = []

        for test_id in args['tests']:
            test = Test.query.get(test_id)

            if test is None:
                continue
            
            route.tests.append(test)

        route.templates = args['templates']
        
        route.save()

        return ApiResponse(route).response()
    
    @jwt_required
    @Competition.from_request
    def delete(self, id, route_id):
        if not g.competition.is_admin:
            return ApiErrorResponse('You are not an admin of this competition', 401).response()

        route = g.competition.bigscreen_routes.filter_by(id=route_id).first()

        if route is None:
            return ApiErrorResponse('Route not found', 404).response()

        db.session.delete(route)
        db.session.commit()

        return ApiResponse(response_code=204).response()



class CompetitionBigScreenRouterResource(Resource):
    @jwt_required
    def post(self, id):
        try:
            competition = Competition.query.filter(or_(Competition.id == id, Competition.ext_id == id)).first()

            if competition is None:
                return ApiErrorResponse('Competition not found', 404).response()

            template = request.json.get('template')
            template_data = request.json.get('templateData')
            hide = request.json.get('hide', False)

            matched_route = competition.bigscreen_routes\
                .filter(BigScreenRoute.templates.like(f'%{template}%'))\
                .filter(BigScreenRoute.tests.any(Test.test_name == template_data['test']['testName']))\
                .order_by(BigScreenRoute.priority.asc())\
                .first()
            
            if not matched_route:
                # Should this just fail silently?
                return ApiErrorResponse(f"No route exists for test {template_data['test']['testName']} and template {template}", 400).response()

            if template is not None and template_data is not None:
                socketio.emit('ScreenGroup.TemplateChanged', {
                    'template': template,
                    'templateData': template_data
                }, namespace="/bigscreen", to=matched_route.screen_group_id)
            
            if hide:
                socketio.emit('ScreenGroup.HideAll', namespace="/bigscreen", to=matched_route.screen_group_id)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(matched_route.screen_group).response()