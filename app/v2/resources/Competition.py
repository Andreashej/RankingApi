import datetime
from flask.globals import g

from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse, ApiResponse
from app import db
from app.models import Competition, RankingList, CompetitionSchema, Test, TestSchema
from flask_jwt_extended import jwt_required

competition_schema_options = {
    'exclude': ["tests","include_in_ranking","tasks","tasks_in_progress"]
}

test_schema_options = {
    'exclude': ["results","competition","_include_in_ranking","include_in_ranking"]
}

class CompetitionsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('isirank', type=str, required=False, location='json')
        self.reqparse.add_argument('first_date', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('last_date', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')
        self.reqparse.add_argument('country', type=str, location='json')
    
    @Competition.from_request(many=True)
    def get(self):
        return ApiResponse(g.competitions, CompetitionSchema, schema_options=competition_schema_options).response()

    @jwt_required
    def post(self):        
        args = self.reqparse.parse_args()

        competition = Competition(args['name'], args['startdate'], args['enddate'], args['isirank_id'])

        competition.update(self.reqparse)

        try:
            competition.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        if args['ranking_scopes']:
            for ranking in args['ranking_scopes']:
                rankinglist = RankingList.query.filter_by(shortname=ranking).first()

                competition.include_in_ranking.append(rankinglist)

        try:
            competition.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(competition, CompetitionSchema, 201, competition_schema_options).response()
    
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
        self.reqparse.add_argument('isirank_id', type=str, location='json')
        self.reqparse.add_argument('first_date', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('last_date', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')
        self.reqparse.add_argument('country', type=str, location='json')
        self.reqparse.add_argument('state', type=str, location='json')

    @Competition.from_request
    def get(self, id):
        return ApiResponse(g.competition, CompetitionSchema, schema_options=competition_schema_options).response()
    
    @jwt_required
    @Competition.from_request
    def patch(self, id):
        g.competition.update(self.reqparse)
        
        args = self.reqparse.parse_args()
        if args['ranking_scopes'] is not None:
            for ranking in args['ranking_scopes']:
                rankinglist = RankingList.query.filter_by(shortname=ranking).one()
                g.competition.include_in_ranking.append(rankinglist)

        try:
            g.competition.save()
        except Exception as e:
            return ApiErrorResponse(str(e), 500).response()
        
        return ApiResponse(g.competition, CompetitionSchema,schema_options=competition_schema_options).response()


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
        self.reqparse.add_argument('mark_type', type=str, required=False, location='json')
        self.reqparse.add_argument('rounding_precision', type=str, required=False, location='json')

    @Competition.from_request
    def get(self, id):
        return ApiResponse(Test.filter(g.competition.tests).all(), TestSchema, schema_options=test_schema_options).response()
    
    @jwt_required
    @Competition.from_request
    def post(self, id):
        args = self.reqparse.parse_args()

        try:
            test = Test.create_from_catalog(args['testcode'])
            g.competition.add_test(test)
        except ValueError as e:
            return ApiErrorResponse(str(e), 400).response()
        
        test.update(self.reqparse)
        

        try:
            test.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()

        return ApiResponse(test, TestSchema, schema_options=test_schema_options).response()

