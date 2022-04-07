from flask_restful import Resource, reqparse
from app.models.JobModel import Job
from app.Responses import ApiErrorResponse
from app.models.TaskModel import Task
from app.Responses import ApiResponse
from flask import g, request
from app.models.RankingListTestModel import RankingListTest
from flask_jwt_extended import jwt_required

class TasksResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('rankingId', type=int, required=False, location="json")
        self.reqparse.add_argument('taskName', type=str, required=True, location="json")
        self.reqparse.add_argument('taskDescription', type=str, required=False, location="json")

    @Task.from_request(many=True)
    def get(self):
        return ApiResponse(g.tasks).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        task = None

        if args['rankingId'] is not None:
            ranking = RankingListTest.query.get(args['rankingId'])

            if ranking is None:
                return ApiErrorResponse(f"Ranking with ID {args['rankingId']} does not exist", 400).response()

            if args['taskName'] == 'flush':
                task = ranking.flush()
            elif args['taskName'] == 'recompute':
                task = ranking.recompute()
            
            if task is None:
                return ApiErrorResponse(f"Task with name {args['taskName']} does not exist for rankings").response()
        else:
            if args['taskDescription'] is None:
                return ApiErrorResponse("Cannot start a named task without a description", 400).response()
                
            task = Task.start(args['taskName'], args['taskDescription'])
            task.save()
        
        return ApiResponse(task, 201).response()
    
class TaskResource(Resource):
    @Task.from_request
    def get(self, id):
        return ApiResponse(g.task).response()

class JobsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('description', type=str, required=True, location='json')
        self.reqparse.add_argument('active', type=bool, required=True, location='json')
        self.reqparse.add_argument('cronExpr', type=str, required=True, location='json')
        self.reqparse.add_argument('taskName', type=str, required=True, location='json')

    @Job.from_request(many=True)
    def get(self):
        return ApiResponse(g.jobs).response()

    @jwt_required
    def post(self):
        job = Job()
        job.update(self.reqparse)
        

        try:
            job.save()
        except ApiErrorResponse as e:
            return e.response()
        
        if job.active:
            job._start()
        
        return ApiResponse(job, 201).response()

class JobResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('description', type=str, required=False, location='json')
        self.reqparse.add_argument('taskName', type=str, required=False, location='json')
        self.reqparse.add_argument('cronExpr', type=str, required=False, location='json')
        self.reqparse.add_argument('active', type=bool, required=False, location='json')

    @Job.from_request
    def get(self, id):
        return ApiResponse(g.job).response()
    
    @jwt_required
    @Job.from_request
    def patch(self, id):
        g.job.update(self.reqparse)

        if g.job.active:
            g.job.restart()
        else:
            g.job._stop()

        try:
            g.job.save()
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(g.job).response()