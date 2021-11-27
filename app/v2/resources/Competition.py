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
        self.reqparse.add_argument('first_date', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('last_date', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')
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

        competition = Competition(args['name'], args['startdate'], args['enddate'], args['isirank_id'])

        competition.update(self.reqparse)

        try:
            competition.save()
        except Exception as e:
            return ErrorResponse(str(e)).response()

        if args['ranking_scopes']:
            for ranking in args['ranking_scopes']:
                rankinglist = RankingList.query.filter_by(shortname=ranking).first()

                competition.include_in_ranking.append(rankinglist)

        try:
            competition.save()
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
        
        return ApiResponse(response_code=204).response()

class CompetitionResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('isirank_id', type=str, location='json')
        self.reqparse.add_argument('first_date', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('last_date', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
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
        competition = None

        try:
            competition = Competition.load(competition_id)
        except ErrorResponse as e:
            return e.response()

        competition.update(self.reqparse)
        
        args = self.reqparse.parse_args()
        if args['ranking_scopes'] is not None:
            for ranking in args['ranking_scopes']:
                rankinglist = RankingList.query.filter_by(shortname=ranking).one()
                competition.include_in_ranking.append(rankinglist)

        try:
            competition.save()
        except Exception as e:
            return ErrorResponse(str(e), 500).response()
        
        return ApiResponse(competition, competition_schema).response()

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
        
        test.update(self.reqparse)
        
        try:
            test.save()
        except Exception as e:
            return ErrorResponse(str(e)).response()

        return ApiResponse(test, test_schema).response()
