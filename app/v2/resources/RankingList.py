from flask.globals import g
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.models import RankingListTest, Task
from app.models.schemas import RankingListSchema, RankingListTestSchema

from app.models.RankingListModel import RankingList
from app.Responses import ApiErrorResponse, ApiResponse

rankinglist_schema_options = {
    'exclude': ["competitions","tasks","tests"]
}

ranking_schema_options = {
    'exclude': ["rankinglist","tasks_in_progress"]
}

class RankingListsResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=True, location='json')
        self.reqparse.add_argument('shortname', type=str, required=True, location='json')
        self.reqparse.add_argument('results_valid_days', type=str, required=False, location='json')

    @RankingList.from_request(many=True)
    def get(self):
        return ApiResponse(g.rankinglists, RankingListSchema, schema_options=rankinglist_schema_options).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        rankinglist = RankingList(args['listname'], args['shortname'])

        rankinglist.update(self.reqparse)
        
        try:
            rankinglist.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(rankinglist, RankingListSchema, schema_options=rankinglist_schema_options).response()

class RankingListResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=False, location='json')
        self.reqparse.add_argument('shortname', type=str, required=False, location='json')
        self.reqparse.add_argument('results_valid_days', type=str, required=False, location='json')

    @RankingList.from_request
    def get(self, id):
        return ApiResponse(g.rankinglist, RankingListSchema, schema_options=rankinglist_schema_options).response()
    
    @jwt_required
    @RankingList.from_request
    def patch(self, id):
        g.rankinglist.update(self.reqparse)
        
        try:
            g.rankinglist.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.rankinglist, RankingListSchema, schema_options=rankinglist_schema_options).response()
    
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
        self.reqparse.add_argument('included_marks', type=int, required=True, location='json')
        self.reqparse.add_argument('order', type=str, required=True, location='json')
        self.reqparse.add_argument('grouping', type=str, required=True, location='json')
        self.reqparse.add_argument('min_mark', type=float, required=True, location='json')
        self.reqparse.add_argument('rounding_precision', type=int, required=True, location='json')
        self.reqparse.add_argument('mark_type', type=str, required=True, location='json')

    @RankingList.from_request
    def get(self, id):        
        return ApiResponse(g.rankinglist.tests, RankingListTestSchema, schema_options=ranking_schema_options).response()
    
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
        
        return ApiResponse(test, RankingListTestSchema, schema_options=ranking_schema_options).response()

class RankingListTasksResource(Resource):
    @RankingList.from_request
    def get(self, id):
        return ApiResponse(tasks=Task.filter(g.rankinglist.tasks).all()).response()