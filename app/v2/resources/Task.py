from flask_restful import Resource
from app.models.TaskModel import Task
from app.Responses import ApiResponse
from flask.globals import g

class TasksResource(Resource):
    @Task.from_request(many=True)
    def get(self):
        return ApiResponse(g.tasks).response()
    
class TaskResource(Resource):
    @Task.from_request
    def get(self, id):
        return ApiResponse(g.task).response()