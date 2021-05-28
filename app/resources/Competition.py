import datetime, os

from flask_restful import Resource, reqparse
from flask import request, current_app
import jwt
from sqlalchemy.sql.expression import text
from .. import db, cache
from ..models import Competition, RankingList, RankingListTest, CompetitionSchema, TestCatalog, Test, TaskSchema, Result
from sqlalchemy import func, not_
from flask_jwt_extended import jwt_required

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
        self.reqparse.add_argument('country', type=str, location='json')
    
    def get(self):
        noresults = request.args.get('noresults', False, type=bool)

        query = Competition.query

        if noresults:
            res_count = func.count(Result.id).label('res_count')
            subquery = Result.query.with_entities(res_count, Result.test_id, Test.competition_id).join(Result.test).group_by(Test.id)
            subquery = subquery.with_entities(Test.competition_id)

            query = query.filter(Competition.id.notin_(subquery))

        try:
            query = Competition.filter(query)
        except Exception as e:
            return { 'message': str(e) }
            
        competitions = query.all()

        competitions = competitions_schema.dump(competitions)

        return {'status': 'OK', 'data': competitions}, 200

    # @jwt_required
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
            return {'message': str(e)}, 500

        competition = competition_schema.dump(competition)
        
        return { 'data': competition }, 200
    
    @jwt_required
    def delete(self):
        try:
            Competition.filter().delete()
            db.session.commit()
        except Exception as e:
            return { 'message': str(e)}, 500
        
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
        competition = Competition.query.get(competition_id)

        if competition is None:
            return {'status': 'NOT FOUND'}, 404

        competition = competition_schema.dump(competition)

        return {'status': 'OK', 'data': competition}
    
    @jwt_required
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
        
        if args['country']:
            competition.country = args['country']

        try:
            db.session.commit()
        except:
            return {'status': 'ERROR'},500

        competition = competition_schema.dump(competition)
        
        cache.delete_memoized(RankingListTest.get_ranking)
        
        return {'status': 'OK', 'data': competition}

    @jwt_required
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
