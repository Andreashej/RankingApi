from datetime import datetime, timedelta

from flask_restful import Resource, reqparse
from app import db, cache, auth
from app.models import Result, RankingListSchema, RankingList, RankingListSchema, Competition, RankingList, Test, Rider, RiderSchema, RankingListTest, RankingListTestSchema

from sqlalchemy import func
from sqlalchemy.orm import contains_eager

ranking_lists_schema = RankingListSchema(many=True)
ranking_list_schema = RankingListSchema()

riders_schema = RiderSchema(many=True)

test_schema = RankingListTestSchema()
tests_schema = RankingListTestSchema(many=True)

class RankingsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type= str, required = True, location = 'json')
        self.reqparse.add_argument('shortname', type= str, required = True, location = 'json')
    
    def get(self):
        rankings = RankingList.query.all()

        rankings = ranking_lists_schema.dump(rankings).data

        return {'status': 'OK', 'data': rankings}
    
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        ranking = RankingList(
            name=args['name'],
            shortname=args['shortname']
        )

        try:
            db.session.add(ranking)
            db.session.commit()
        except Exception as inst:
            print (inst.args)
            return {'status': 'ERROR', 'message': inst.args}

        ranking = ranking_list_schema.dump(ranking).data
        return {'status': 'OK', 'data': ranking}
    
    @auth.login_required
    def delete(self):
        try:
            RankingList.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204
        
class RankingResource(Resource):
    def __init__(self):
        pass

    def get(self, listname):
        ranking = RankingList.query.filter_by(shortname=listname).first()

        if ranking is None:
            return {'status': 'NOT FOUND'}, 404

        ranking = ranking_list_schema.dump(ranking).data
        return {'status': 'OK', 'data': ranking},200

class RankingListsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type= str, required = True, location = 'json')
        self.reqparse.add_argument('included_marks', type=int, required = False, location = 'json')
        self.reqparse.add_argument('order', type=str, required = False, location = 'json')
        self.reqparse.add_argument('grouping', type=str, required = False, location = 'json')
        self.reqparse.add_argument('min_mark', type=float, required = False, location = 'json')
        self.reqparse.add_argument('rounding_precision', type=int, required = False, location = 'json')
    
    def get(self, listname):
        rankinglist = RankingList.query.filter_by(shortname=listname).first()

        tests = tests_schema.dump(rankinglist.tests).data
        return {'status': 'OK', 'data': tests}

    @auth.login_required
    def post(self, listname):
        args = self.reqparse.parse_args()

        rankinglist = RankingList.query.filter_by(shortname=listname).first()

        test = RankingListTest.query.filter_by(testcode=args['testcode'], rankinglist=rankinglist).first()
        if test is not None:
            return {'status': 'DUPLICATE ENTRY'}, 409

        test = RankingListTest(
            testcode = args['testcode'],
            rankinglist = rankinglist
        )

        if 'included_marks' in args:
            test.included_marks = args['included_marks']
        
        if 'order' in args:
            test.order = args['order']
        
        if 'grouping' in args:
            test.grouping = args['grouping']

        if 'min_mark' in args:
            test.min_mark = args['min_mark']
        
        if 'rounding_precision' in args:
            test.rounding_precision = args['rounding_precision']

        try:
            db.session.add(test)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        test = test_schema.dump(test).data

        return {'status': 'OK', 'data': test}

class RankingListResource(Resource):
    def get(self, listname, testcode):
        rankinglist = RankingList.query.filter_by(shortname=listname).first()

        test = RankingListTest.query.filter_by(testcode=testcode, rankinglist=rankinglist).first()

        if test is None:
            return {'status': 'NOT FOUND'},404
        
        test = test_schema.dump(test).data

        return {'status': 'OK', 'data': test}
        
    
class RankingListResultsResource(Resource):
    def get(self, listname, testcode):
        ranking = RankingList.query.filter_by(shortname = listname).first()

        test = RankingListTest.query.filter_by(testcode = testcode, rankinglist=ranking).first()

        if test is None:
            return {'status': 'NOT FOUND'},404
        
        valid_results = test.get_ranking()

        return {'status': 'OK', 'data': valid_results }