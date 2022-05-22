from flask.globals import g, request, current_app
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource, reqparse
from app.models.TestEntryModel import TestEntry
from app.Responses import ApiResponse, ApiErrorResponse
from app.models import Test, Result, Person, Horse, RankingList, StartListEntry, Task
from app import db
import pandas as pd

class TestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('competitionId')

    @Test.from_request(many=True)
    def get(self):
        return ApiResponse(g.tests).response()
    
    @jwt_required
    @Test.from_request(many=True)
    def delete(self):
        try:
            g.tests.delete()
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e))
        
        return ApiResponse(response_code=204).response()


class TestResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=False, location='json')
        self.reqparse.add_argument('testName', type=str, required=False, location='json')
        self.reqparse.add_argument('order', type=str, required=False, location='json')
        self.reqparse.add_argument('markType', type=str, required=False, location='json')
        self.reqparse.add_argument('roundingPrecision', type=int, required=False, location='json')
        self.reqparse.add_argument('rankinglists', type=str, required=False, location='json', action="append")
    
    @Test.from_request
    def get(self, id):
        return ApiResponse(g.test).response()
    
    @jwt_required
    @Test.from_request
    def patch(self, id):
        args = self.reqparse.parse_args()

        try:
            g.test.update(self.reqparse)

            if 'rankinglists' in request.json:
                if args['rankinglists'] is not None:
                    for shortname in args['rankinglists']:
                        rankinglist = RankingList.query.filter_by(shortname=shortname).one()
                        if rankinglist not in g.test.include_in_ranking.all():
                            g.test.add_rankinglist(rankinglist)
                
                for ranking in g.test.include_in_ranking:
                    if args['rankinglists'] is None or ranking.shortname not in args['rankinglists']:
                        g.test.remove_rankinglist(ranking)

            g.test.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(g.test).response()
    
    @jwt_required
    @Test.from_request
    def delete(self, id):
        try:
            g.test.delete()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class TestResultsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('riderId', type=int, required=True, location='json')
        self.reqparse.add_argument('horseId', type=int, required=True, location='json')
        self.reqparse.add_argument('mark', type=float, required=True, location='json')
        self.reqparse.add_argument('state', type=str, required=False, location='json')

    @Test.from_request
    def get(self, id):   
        try:
            results = Result.load_many(g.test.results)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(results).response()

    @jwt_required
    @Test.from_request    
    def post(self, id):

        if 'file' in request.files:
            file = request.files['file']

            content = pd.read_excel(file)
            content = content.reset_index()

            data = []
            
            for i, row in content.iterrows():
                score = row['SCORE'].strip('"')

                result = {
                    'RIDER': row['FULLNAME'],
                    'HORSE': row['NAME_HORSE'],
                    'FEIFID': row['FEIFID_HORSE'],
                    'MARK': float(score.replace(',', '.')),
                    'STATE': row['RESULT_STATE'],
                    'PHASE': row['PHASE'],
                    'TIMESTAMP': row['MODIFIED'],
                    'STA': row['STA'],
                    'CLASS': row['CLASS']
                }
                data.append(result)
            
            task = Task.start('create_results_from_icetest', f'Import results to {g.test.testcode} for competition {g.test.competition.id}', g.test.id, data)
            task.save()

            return ApiResponse(task=task, response_code=202).response()

        args = self.reqparse.parse_args()

        result = None
        try:
            rider = Person.load_one(args['riderId'])
            horse = Horse.load_one(args['horseId'])
            result = g.test.add_result(rider, horse, args['mark'], args['state'])
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        try:
            result.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(result).response()

        
class TestStartListResource(Resource):
    @Test.from_request
    def get(self, id):
        try:
            startlist = StartListEntry.load_many(g.test.startlist)
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(startlist).response()

class TestSectionResultsResource(Resource):
    @Test.from_request
    def get(self, id, section_no):
        entries = TestEntry.query.filter_by(test_id = g.test.id)