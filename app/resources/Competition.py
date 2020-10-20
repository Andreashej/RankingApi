import datetime

from flask_restful import Resource, reqparse
from flask import request
from app import db
from app import cache, auth
from app.models import Competition, RankingList, RankingListTest, CompetitionSchema

competitions_schema = CompetitionSchema(many=True)
competition_schema = CompetitionSchema()

class CompetitionsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('isirank', type=str, required=True, location='json')
        self.reqparse.add_argument('startdate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), required=True, location='json')
        self.reqparse.add_argument('enddate', type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), required=True, location='json')
        self.reqparse.add_argument('ranking_scopes', type=str, action='append', location='json')
    
    def get(self):
        competitions = Competition.query.all()
        competitions = competitions_schema.dump(competitions)

        return {'status': 'OK', 'data': competitions}, 200

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()

        competition = Competition(args['name'], args['isirank'], args['startdate'], args['enddate'])

        for ranking in args['ranking_scopes']:
            rankinglist = RankingList.query.filter_by(shortname=ranking).first()

            competition.include_in_ranking.append(rankinglist)

        try:
            db.session.add(competition)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500

        competition = competition_schema.dump(competition)

        cache.delete_memoized(RankingListTest.get_ranking)
        
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


