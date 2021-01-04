import datetime, os

from flask_restful import Resource, reqparse
from flask import request, current_app
from .. import db
from .. import cache, auth
from ..models import Competition, RankingList, RankingListTest, CompetitionSchema, TestCatalog, Test, TaskSchema, Result
from sqlalchemy import not_, func

competitions_schema = CompetitionSchema(many=True, exclude=("tests","include_in_ranking","tasks",))
competition_schema = CompetitionSchema()
task_schema = TaskSchema()

class CompetitionsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('isirank', type=str, required=False, location='json')
        self.reqparse.add_argument('startdate', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('enddate', type=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), required=True, location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')
        self.reqparse.add_argument('tests', type=str, action='append', location='json')
    
    def get(self):
        noresults = request.args.get('noresults', False, type=bool)

        query = Competition.query

        if noresults:
            # tests = Test.query.all()
            # # tests_without_results = [test.competition_id for test in tests if test._results.count() == 0]
            # for test in tests:
            #     if (test._results.count() == 0):
            #         print(f"Test {test.id} has no results!")

            query = query.filter(not_(Competition.tests.any()))\
            #     .join(Competition.tests)\
            #     .filter(Test._results == 0)
            
        competitions = query.all()

        competitions = competitions_schema.dump(competitions)

        return {'status': 'OK', 'data': competitions}, 200

    @auth.login_required
    def post(self):        
        args = self.reqparse.parse_args()

        competition = Competition(args['name'], args['startdate'], args['enddate'])

        if args['isirank']:
            competition.isirank_id = args['isirank']

        for ranking in args['ranking_scopes']:
            rankinglist = RankingList.query.filter_by(shortname=ranking).first()

            competition.include_in_ranking.append(rankinglist)

        for testcode in args['tests']:
            origtest = TestCatalog.query.filter_by(testcode = testcode).first()

            test = Test(testcode)
            test.rounding_precision = origtest.rounding_precision
            test.order = origtest.order
            competition.tests.append(test)

        try:
            db.session.add(competition)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500

        competition = competition_schema.dump(competition)
        
        return {'status': 'OK', 'data': competition}, 200
    
    @auth.login_required
    def delete(self):
        try:
            Competition.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204

class CompetitionResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('isirank', type=str, location='json')
        self.reqparse.add_argument('startdate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('enddate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')

    def get(self, competition_id):
        competition = Competition.query.get(competition_id)

        if competition is None:
            return {'status': 'NOT FOUND'}, 404

        competition = competition_schema.dump(competition)

        return {'status': 'OK', 'data': competition}
    
    @auth.login_required
    def patch(self, competition_id):
        args = self.reqparse.parse_args()

        competition = Competition.query.get(competition_id)

        if competition is None:
            return {'status': 'NOT FOUND'}, 404

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
        
        try:
            db.session.commit()
        except:
            return {'status': 'ERROR'},500

        competition = competition_schema.dump(competition)
        
        cache.delete_memoized(RankingListTest.get_ranking)
        
        return {'status': 'OK', 'data': competition}

    @auth.login_required
    def delete(self, competition_id):
        competition = Competition.query.get(competition_id)

        if competition is None:
            return { 'status': 'NOT FOUND' }, 404

        try:
            db.session.delete(competition)
            db.session.commit()
        except:
            return { 'status': 'ERROR'},500
        
        return { 'STATUS': 'OK' }, 204
