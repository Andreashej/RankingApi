from flask.globals import g
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.models.RankingListModel import use_rankinglists, use_rankinglist
from app.models.RankingListTestModel import RankingListTest
from app.models.schemas import RankingListSchema, RankingListTestSchema, TaskSchema

from app.models.RankingListModel import RankingList
from app.models.RestMixin import ApiErrorResponse, ApiResponse

ranking_lists_schema = RankingListSchema(many=True,exclude=("competitions","tasks","tests"))
ranking_list_schema = RankingListSchema(exclude=("competitions","tasks","tests"))

tests_schema = RankingListTestSchema(many=True, exclude=("rankinglist","tasks_in_progress"))
test_schema = RankingListTestSchema(exclude=("rankinglist","tasks_in_progress"))

tasks_schema = TaskSchema(many=True)

class RankingListsResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=True, location='json')
        self.reqparse.add_argument('shortname', type=str, required=True, location='json')
        self.reqparse.add_argument('results_valid_days', type=str, required=False, location='json')

    @use_rankinglists
    def get(self):
        return ApiResponse(g.rankinglists, ranking_lists_schema).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        rankinglist = RankingList(args['listname'], args['shortname'])

        rankinglist.update(self.reqparse)
        
        try:
            rankinglist.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(rankinglist, ranking_list_schema).response()

class RankingListResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=False, location='json')
        self.reqparse.add_argument('shortname', type=str, required=False, location='json')
        self.reqparse.add_argument('results_valid_days', type=str, required=False, location='json')

    @use_rankinglist
    def get(self, rankinglist_id):
        return ApiResponse(g.rankinglist, ranking_list_schema).response()
    
    @jwt_required
    @use_rankinglist
    def patch(self, rankinglist_id):
        g.rankinglist.update(self.reqparse)
        
        try:
            g.rankinglist.save()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(g.rankinglist, ranking_list_schema).response()
    
    @jwt_required
    @use_rankinglist
    def delete(self, rankinglist_id):
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

    @use_rankinglist
    def get(self, rankinglist_id):        
        return ApiResponse(g.rankinglist.tests, tests_schema).response()
    
    @jwt_required
    @use_rankinglist
    def post(self, rankinglist_id):
        test = RankingListTest()
        test.update(self.reqparse)

        try:
            g.rankinglist.add_test(test)
            test.save()
        except ApiErrorResponse as e:
            return e.response()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(test, test_schema).response()

class RankingListTasksResource(Resource):
    @use_rankinglist
    def get(self, rankinglist_id):
        return ApiResponse(g.rankinglist.tasks, tasks_schema).response()