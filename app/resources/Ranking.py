import os

from flask import request, current_app
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from .. import db, cache
from ..models import RankingList, RankingListTest, RankingListSchema, RankingListSchema, RiderSchema, RankingListTestSchema, TaskSchema, RankingResultsCache, Competition, Task

ranking_lists_schema = RankingListSchema(many=True,exclude=("competitions",))
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
        try:
            rankings = RankingList.filter().all()
        except Exception as e:
            return { 'message': str(e) }, 500

        rankings = ranking_lists_schema.dump(rankings)

        return { 'data': rankings }
    
    @jwt_required
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
            return { 'message': inst.args }, 500

        ranking = ranking_list_schema.dump(ranking)
        return { 'data': ranking }
    
    @jwt_required
    def delete(self):
        try:
            RankingList.filter().delete()
            db.session.commit()
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {}, 204
        
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

        if not ranking:
            return { 'status': 'NOT FOUND'}, 404

        file = request.files.get('competitions')
        if file:
            file.save(os.path.join(current_app.config["ISIRANK_FILES"], file.filename))

            task = ranking.import_competitions(file.filename)

            os.remove(current_app.config["ISIRANK_FILES"] + file.filename)

            try:
                db.session.commit()
            except:
                return { 'status': 'ERROR', 'message': 'Database error'}, 500

            task = task_schema.dump(task)

            return {'status': 'OK', 'data': task}

        file = request.files.get('results')
        if file:
            file.save(os.path.join(current_app.config["ISIRANK_FILES"], file.filename))

            tasks = ranking.import_results(file.filename, filter=request.form.getlist('filter'))

            os.remove(current_app.config["ISIRANK_FILES"] + file.filename)

            try:
                db.session.commit()
            except Exception as e:
                return { 'status': 'ERROR', 'message': e.args}
            
            tasks = tasks_schema.dump(tasks)
            return { 'status': 'OK', 'data': tasks }

        file = request.files.get('logo')

        if file:
            file.save(os.path.join(current_app.config["IMAGE_FILES"], file.filename))
            ranking.branding_image = file.filename

        args = self.reqparse.parse_args()

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
    
    def delete(self, listname):
        
        try:
            RankingList.query.filter_by(shortname=listname).delete()
            db.session.commit()
        except Exception as e:
            return { 'message': str(e) }, 500

        return {}, 204



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

    @jwt_required
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

        if ranking is None:
            return {'status': 'NOT FOUND', 'message': f'Rankinglist {listname} does not exist'}, 404

        test = RankingListTest.query.filter_by(testcode = testcode, rankinglist=ranking).first()

        if test is None:
            return {'status': 'NOT FOUND', 'message': 'No test with testcode {} exist for ranking {}.'.format(testcode, listname)},404
        
        clear_cache = request.args.get('clearcache', None)

        if clear_cache:
            cache.delete_memoized(RankingResultsCache.get_results, RankingResultsCache, test)

        results = RankingResultsCache.get_results(test)

        return {'status': 'OK', 'data': results}
    
    def post(self, listname, testcode):
        ranking = RankingList.query.filter_by(shortname = listname).first()

        test = RankingListTest.query.filter_by(testcode = testcode, rankinglist=ranking).first()

        if test is None:
            return {'status': 'NOT FOUND'},404

        task = test.launch_task('compute_ranking', 'Recalculating {} ranking for {}'.format(test.testcode, ranking.shortname))

        return {'status': 'OK', 'data': task_schema.dump(task) }