from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.models.RankingListTestModel import RankingListTest
from app.models.schemas import RankingListSchema, RankingListTestSchema, TaskSchema

from app.models.RankingListModel import RankingList
from app.models.RestMixin import ErrorResponse, ApiResponse

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

    def get(self):
        ranking_lists = []
        try:
            ranking_lists = RankingList.load()
        except ErrorResponse as e:
            return e.response()
        
        return ApiResponse(ranking_lists, ranking_lists_schema).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        rankinglist = RankingList(args['listname'], args['shortname'])

        rankinglist.update(self.reqparse)
        
        try:
            rankinglist.save()
        except Exception as e:
            return ErrorResponse(str(e)).response()
        
        return ApiResponse(rankinglist, ranking_list_schema).response()

class RankingListResource(Resource):
    def __init__(self):
        self.reqparse = RequestParser()
        self.reqparse.add_argument('listname', type=str, required=False, location='json')
        self.reqparse.add_argument('shortname', type=str, required=False, location='json')
        self.reqparse.add_argument('results_valid_days', type=str, required=False, location='json')

    def get(self, rankinglist_id):
        rankinglist = None

        try:
            rankinglist = RankingList.load(rankinglist_id)
        except ErrorResponse as e:
            return e.response()
        
        return ApiResponse(rankinglist, ranking_list_schema).response()
    
    @jwt_required
    def patch(self, rankinglist_id):
        rankinglist = None

        try:
            rankinglist = RankingList.load(rankinglist_id)
        except ErrorResponse as e:
            return e.response()
        
        rankinglist.update(self.reqparse)
        
        try:
            rankinglist.save()
        except Exception as e:
            return ErrorResponse(str(e)).response()
        
        return ApiResponse(rankinglist, ranking_list_schema).response()
    
    @jwt_required
    def delete(self, rankinglist_id):
        rankinglist = None

        try:
            rankinglist = RankingList.load(rankinglist_id)
            rankinglist.delete()
        except ErrorResponse as e:
            return e.response()
        except Exception as e:
            return ErrorResponse(str(e))
        
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

    def get(self, rankinglist_id):
        rankinglist = None

        try:
            rankinglist = RankingList.load(rankinglist_id)
        except ErrorResponse as e:
            return e.response()
        
        return ApiResponse(rankinglist.tests, tests_schema).response()
    
    @jwt_required
    def post(self, rankinglist_id):
        rankinglist = None

        try:
            rankinglist = RankingList.load(rankinglist_id)
        except ErrorResponse as e:
            return e.response()

        test = RankingListTest()
        test.update(self.reqparse)

        try:
            rankinglist.add_test(test)
            test.save()
        except ErrorResponse as e:
            return e.response()
        except Exception as e:
            return ErrorResponse(str(e)).response()
        
        return ApiResponse(test, test_schema).response()

class RankingListTasksResource(Resource):
    def get(self, rankinglist_id):
        rankinglist = None

        try:
            rankinglist = RankingList.load(rankinglist_id)
        except ErrorResponse as e:
            return e.response()
        
        return ApiResponse(rankinglist.tasks, tasks_schema).response()