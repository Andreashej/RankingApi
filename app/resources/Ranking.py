from datetime import datetime, timedelta

from flask_restful import Resource, reqparse
from app import db
from app import cache, auth
from app.models import Result, RankingList, Test, Rider, RankingListTest, RankingListSchema, RankingListSchema, RiderSchema, RankingListTestSchema, TaskSchema, RankingResultsCache, Horse

from sqlalchemy import func
from sqlalchemy.orm import contains_eager

ranking_lists_schema = RankingListSchema(many=True)
ranking_list_schema = RankingListSchema(exclude=("competitions",))

riders_schema = RiderSchema(many=True)

test_schema = RankingListTestSchema()
tests_schema = RankingListTestSchema(many=True)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

class RankingsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type= str, required = True, location = 'json')
        self.reqparse.add_argument('shortname', type= str, required = True, location = 'json')
    
    def get(self):
        rankings = RankingList.query.all()

        rankings = ranking_lists_schema.dump(rankings)

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

        ranking = ranking_list_schema.dump(ranking)
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
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('listname', type= str, required = False, location = 'json')
        self.reqparse.add_argument('shortname', type= str, required = False, location = 'json')
        self.reqparse.add_argument('results_valid_days', type = int, required = False, location = 'json')

    def get(self, listname):
        ranking = RankingList.query.filter_by(shortname=listname).first()

        if ranking is None:
            return {'status': 'NOT FOUND'}, 404

        ranking = ranking_list_schema.dump(ranking)

        return {'status': 'OK', 'data': ranking},200
    
    def patch(self, listname):
        ranking = RankingList.query.filter_by(shortname=listname).first()

        args = self.reqparse.parse_args()

        if not ranking:
            return { 'status': 'NOT FOUND'}, 404
        
        if args['listname'] is not None:
            ranking.listname = args['listname']
        
        if args['shortname'] is not None:
            ranking.shortname = args['shortname']
        
        if args['results_valid_days'] is not None:
            ranking.results_valid_days = args['results_valid_days']
        
        try:
            db.session.commit()
        except Exception as e:
            return {'status': 'ERROR', 'message': e}, 500
        
        return {'status': 'OK', 'data': ranking_list_schema.dump(ranking)}



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

        tests = tests_schema.dump(rankinglist.tests)
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
        
        test = test_schema.dump(test)

        return {'status': 'OK', 'data': test}

class RankingListResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type= str, required = False, location = 'json')
        self.reqparse.add_argument('included_marks', type=int, required = False, location = 'json')
        self.reqparse.add_argument('order', type=str, required = False, location = 'json')
        self.reqparse.add_argument('grouping', type=str, required = False, location = 'json')
        self.reqparse.add_argument('min_mark', type=float, required = False, location = 'json')
        self.reqparse.add_argument('rounding_precision', type=int, required = False, location = 'json')

    def get(self, listname = None, testcode = None, id = None):

        if id:
            test = RankingListTest.query.get(id)

        else:
            rankinglist = RankingList.query.filter_by(shortname=listname).first()
            test = RankingListTest.query.filter_by(testcode=testcode, rankinglist=rankinglist).first()

        if test is None:
            return {'status': 'NOT FOUND'},404
        
        test = test_schema.dump(test)

        return {'status': 'OK', 'data': test}
    
    def patch(self, listname = None, testcode = None, id = None):

        if id:
            test = RankingListTest.query.get(id)
        
        else:
            rankinglist = RankingList.query.filter_by(shortname=listname).first()
            test = RankingListTest.query.filter_by(testcode=testcode, rankinglist=rankinglist).first()

        if test is None:
            return {'status': 'NOT FOUND'},404

        args = self.reqparse.parse_args()

        if 'testcode' in args:
            test.testcode = args['testcode']

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
            db.session.commit()
        except:
            return {'status': 'ERR', 'message': 'Could not save test definition.'}, 500

        task = test.launch_task('compute_ranking', 'Recalculating {} ranking for {}'.format(test.testcode, test.rankinglist.shortname))
        
        test = test_schema.dump(test)

        return {'status': 'OK', 'data': test}

class RankingListResultsResource(Resource):

    def get(self, listname, testcode):
        ranking = RankingList.query.filter_by(shortname = listname).first()

        test = RankingListTest.query.filter_by(testcode = testcode, rankinglist=ranking).first()

        if test is None:
            return {'status': 'NOT FOUND', 'message': 'No test with testcode {} exist for ranking {}.'.format(testcode, ranking)},404

        results = RankingResultsCache.get_results(test)

        return {'status': 'OK', 'data': results}
    
    def post(self, listname, testcode):
        ranking = RankingList.query.filter_by(shortname = listname).first()

        test = RankingListTest.query.filter_by(testcode = testcode, rankinglist=ranking).first()

        if test is None:
            return {'status': 'NOT FOUND'},404

        task = test.launch_task('compute_ranking', 'Recalculating {} ranking for {}'.format(test.testcode, ranking.shortname))

        return {'status': 'OK', 'data': task_schema.dump(task) }