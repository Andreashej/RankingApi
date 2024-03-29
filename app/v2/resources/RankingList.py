from flask.globals import g
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.models import RankingListTest, Task
from app.models.RankingListModel import RankingList
from app.Responses import ApiErrorResponse, ApiResponse

class RankingListsResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=True, location='json')
        self.reqparse.add_argument('shortname', type=str, required=True, location='json')
        self.reqparse.add_argument('resultsValidDays', type=str, required=False, location='json')

    @RankingList.from_request(many=True)
    def get(self):
        return ApiResponse(g.rankinglists).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        rankinglist = RankingList(args['listname'], args['shortname'])

        rankinglist.update(self.reqparse)
        
        try:
            rankinglist.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(rankinglist).response()

class RankingListResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=False, location='json')
        self.reqparse.add_argument('shortname', type=str, required=False, location='json')
        self.reqparse.add_argument('resultsValidDays', type=str, required=False, location='json')

    @RankingList.from_request
    def get(self, id):
        return ApiResponse(g.rankinglist).response()
    
    @jwt_required
    @RankingList.from_request
    def patch(self, id):
        g.rankinglist.update(self.reqparse)
        
        try:
            g.rankinglist.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.rankinglist).response()
    
    @jwt_required
    @RankingList.from_request
    def delete(self, id):
        try:
            g.rankinglist.delete()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class RankingListTestsResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('includedMarks', type=int, required=True, location='json')
        self.reqparse.add_argument('order', type=str, required=True, location='json')
        self.reqparse.add_argument('grouping', type=str, required=True, location='json')
        self.reqparse.add_argument('minMark', type=float, required=True, location='json')
        self.reqparse.add_argument('roundingPrecision', type=int, required=True, location='json')
        self.reqparse.add_argument('markType', type=str, required=True, location='json')

    @RankingList.from_request
    def get(self, id):     
        try:
            tests = RankingListTest.load_many(g.rankinglist.tests)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(tests).response()
    
    @jwt_required
    @RankingList.from_request
    def post(self, id):
        test = RankingListTest()
        test.update(self.reqparse)

        try:
            g.rankinglist.add_test(test)
            test.save()
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(test).response()

class RankingListTasksResource(Resource):
    @RankingList.from_request
    def get(self, id):
        try:
            tasks = Task.load_many(g.rankinglist.tasks)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(tasks).response()