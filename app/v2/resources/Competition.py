import datetime

from flask_restful import Resource, reqparse
from app.models.RestMixin import ErrorResponse, ApiResponse
from app import db
from app.models import Competition, RankingList, CompetitionSchema, Test, TestSchema
from flask_jwt_extended import jwt_required

competitions_schema = CompetitionSchema(many=True, exclude=("tests","include_in_ranking","tasks","tasks_in_progress"))
competition_schema = CompetitionSchema(exclude=("tests","include_in_ranking","tasks","tasks_in_progress"))

tests_schema = TestSchema(many=True, exclude=("results","competition"))
test_schema = TestSchema(exclude=("results","competition"))

class CompetitionsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('isirank', type=str, required=False, location='json')
        self.reqparse.add_argument('startdate', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('enddate', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')
        self.reqparse.add_argument('tests', type=str, action='append', location='json')
        self.reqparse.add_argument('country', type=str, location='json')
    
    def get(self):
        try:
            competitions = Competition.load()
        except ErrorResponse as e:
            return e.response()

        return ApiResponse(competitions, competitions_schema).response()

    @jwt_required
    def post(self):        
        args = self.reqparse.parse_args()

        competition = Competition(args['name'], args['startdate'], args['enddate'])
        try:
            db.session.add(competition)
            db.session.commit()
        except:
            db.session.rollback()
            return { 'Something went wrong' },500

        if args['isirank']:
            competition.isirank_id = args['isirank']

        else:
            competition.isirank_id = competition.create_id()

        if args['ranking_scopes']:
            for ranking in args['ranking_scopes']:
                rankinglist = RankingList.query.filter_by(shortname=ranking).first()

                competition.include_in_ranking.append(rankinglist)

        if args['tests']:
            for testcode in args['tests']:
                test = Test.create_from_catalog(testcode)
                competition.tests.append(test)

        if args['country']:
            competition.country = args['country']

        try:
            db.session.commit()
        except Exception as e:
            return ErrorResponse(str(e)).response()
        
        return ApiResponse(competition, competition_schema, 201).response()
    
    @jwt_required
    def delete(self):
        try:
            Competition.filter().delete()
            db.session.commit()
        except Exception as e:
            return ErrorResponse(str(e)).response()
        
        return {}, 204

class CompetitionResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('isirank', type=str, location='json')
        self.reqparse.add_argument('startdate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('enddate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')

    def get(self, competition_id):
        competition = None
        try:
            competition = Competition.load(competition_id)
        except ErrorResponse as e:
            return e.response()

        return ApiResponse(competition, competition_schema).response()
    
    @jwt_required
    def patch(self, competition_id):
        args = self.reqparse.parse_args()

        competition = None

        try:
            competition = Competition.load(competition_id)
        except ErrorResponse as e:
            return e.response()

        if args['name'] is not None:
            competition.name = args['name']
        
        if args['isirank'] is not None:
            competition.isirank_id = args['isirank']
        
        if args['startdate'] is not None:
            competition.first_date = args['startdate']
        
        if args['enddate'] is not None:
            competition.last_date = args['enddate']
        
        if args['ranking_scopes'] is not None:
            for ranking in args['ranking_scopes']:
                rankinglist = RankingList.query.filter_by(shortname=ranking).one()
                competition.include_in_ranking.append(rankinglist)
        
        if args['country']:
            competition.country = args['country']

        try:
            db.session.commit()
        except Exception as e:
            return ErrorResponse(str(e), 500).response()
        
        return ApiResponse(competition, competition_schema)

    @jwt_required
    def delete(self, competition_id):
        competition = Competition.query.get(competition_id)

        if competition is None:
            return None, 404

        try:
            db.session.delete(competition)
            db.session.commit()
        except Exception as e:
            return ErrorResponse(str(e)).response()

        return ApiResponse(response_code=204).response()

class CompetitionTestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('order', type=str, required=False, location='json')
        self.reqparse.add_argument('mark_type', type=str, required=False, location='json')
        self.reqparse.add_argument('rounding_precision', type=str, required=False, location='json')

    def get(self, competition_id):
        competition = None
        try:
            competition = Competition.load(competition_id)
        except ErrorResponse as e:
            return e.response()

        return ApiResponse(competition.tests, tests_schema).response()
    
    @jwt_required
    def post(self, competition_id):
        competition = Competition.load(competition_id)
        args = self.reqparse.parse_args()

        try:
            test = Test.create_from_catalog(args['testcode'])
            competition.add_test(test)
        except ValueError as e:
            return ErrorResponse(str(e), 400).response()

        if args['order']:
            test.order = args['order']
        
        if args['mark_type']:
            test.mark_type = args['mark_type']
        
        if args['rounding_precision']:
            test.rounding_precision = args['rounding_precision']
        
        try:
            test.add()
        except Exception as e:
            return ErrorResponse(str(e)).response()

        return ApiResponse(test, test_schema).response()

