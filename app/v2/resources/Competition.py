import datetime
import re
from flask.globals import g
from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse, ApiResponse
from app import db
from app.models import Competition, RankingList, Test, User
from flask_jwt_extended import jwt_required

class CompetitionsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('isirank', type=str, required=False, location='json')
        self.reqparse.add_argument('firstDate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), required=True, location='json')
        self.reqparse.add_argument('lastDate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), required=True, location='json')
        self.reqparse.add_argument('country', type=str, location='json', required=True)
        self.reqparse.add_argument('contactPersonId', type=int, location='json', required=True)
    
    @Competition.from_request(many=True)
    def get(self):
        return ApiResponse(g.competitions).response()

    @jwt_required
    def post(self):        
        args = self.reqparse.parse_args()

        try:
            competition = Competition(args['name'], args['firstDate'], args['lastDate'], args['isirank'], args['country'])
            competition.update(self.reqparse)
            competition.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(competition, 201).response()
    
    @jwt_required
    @Competition.from_request(many=True)
    def delete(self):
        try:
            g.competitions.delete()
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class CompetitionResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('extId', type=str, location='json')
        self.reqparse.add_argument('firstDate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('lastDate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('rankingScopes', type=str, action='append', location='json')
        self.reqparse.add_argument('country', type=str, location='json')
        self.reqparse.add_argument('state', type=str, location='json')
        self.reqparse.add_argument('contactPersonId', type=int, location='json')

    @Competition.from_request
    def get(self, id):
        return ApiResponse(g.competition).response()
    
    @jwt_required
    @Competition.from_request
    def patch(self, id):
        try:
            g.competition.update(self.reqparse)
            
            args = self.reqparse.parse_args()
            if args['rankingScopes'] is not None:
                for ranking in args['rankingScopes']:
                    rankinglist = RankingList.query.filter_by(shortname=ranking).one()
                    g.competition.include_in_ranking.append(rankinglist)

            g.competition.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(g.competition).response()


    @jwt_required
    @Competition.from_request
    def delete(self, id):
        try:
            db.session.delete(g.competition)
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        return ApiResponse(response_code=204).response()

class CompetitionTestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('order', type=str, required=False, location='json')
        self.reqparse.add_argument('markType', type=str, required=False, location='json')
        self.reqparse.add_argument('roundingPrecision', type=str, required=False, location='json')
        self.reqparse.add_argument('rankinglists', type=str, required=False, location='json', action="append")

    @Competition.from_request
    def get(self, id):
        try:
            tests = Test.load_many(g.competition.tests)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(tests).response()
    
    @jwt_required
    @Competition.from_request
    def post(self, id):
        args = self.reqparse.parse_args()

        try:
            test = Test.create_from_catalog(args['testcode'])
            if args['rankinglists'] is not None:
                for shortname in args['rankinglists']:
                    rankinglist = RankingList.query.filter_by(shortname=shortname).one()
                    test.include_in_ranking.append(rankinglist)

            g.competition.add_test(test)
        except ValueError as e:
            return ApiErrorResponse(str(e), 400).response()
        
        test.update(self.reqparse)
        

        try:
            test.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        return ApiResponse(test).response()

class CompetitionAdminUsersResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, location='json', required=True)

    @jwt_required
    @Competition.from_request
    def post(self, id):
        if not g.competition.is_admin:
            return ApiErrorResponse('You are not an admin of this competition', response_code=401).response()
        
        args = self.reqparse.parse_args()

        user_to_add = User.query.filter_by(username=args['username']).first()

        if user_to_add is None:
            return ApiErrorResponse(f"A user with username {args['username']} does not exist", 400).response()
        
        g.competition.admin_users.append(user_to_add)
        g.competition.save()

        return ApiResponse(user_to_add).response()

class CompetitionAdminUserResource(Resource):

    @jwt_required
    @Competition.from_request
    def delete(self, id, user_id):
        if not g.competition.is_admin:
            return ApiErrorResponse('You are not an admin of this competition', response_code=401).response()
        
        user_to_remove = User.query.get(user_id)

        g.competition.admin_users.remove(user_to_remove)
        g.competition.save()

        return ApiResponse(response_code=204).response()