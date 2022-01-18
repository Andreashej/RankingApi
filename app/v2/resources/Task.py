from flask_restful import Resource, reqparse
from app.Responses import ApiErrorResponse
from app.models.TaskModel import Task
from app.Responses import ApiResponse
from flask.globals import g
from app.models.RankingListTestModel import RankingListTest

class TasksResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('rankingId', type=int, required=False, location="json")
        self.reqparse.add_argument('taskName', type=str, required=False, location="json")

    @Task.from_request(many=True)
    def get(self):
        return ApiResponse(g.tasks).response()
    
    def post(self):
        args = self.reqparse.parse_args()

        task = None

        if 'rankingId' in args:
            ranking = RankingListTest.query.get(args['rankingId'])

            if ranking is None:
                return ApiErrorResponse(f"Ranking with ID {args['rankingId']} does not exist", 400)

            if args['taskName'] == 'flush':
                task = ranking.flush()
            elif args['taskName'] == 'recompute':
                task = ranking.recompute()
            
            if task is None:
                return ApiErrorResponse(f"Task with name {args['taskName']} does not exist for rankings")
        
        return ApiResponse(task, 201).response()
    
class TaskResource(Resource):
    @Task.from_request
    def get(self, id):
        return ApiResponse(g.task).response()