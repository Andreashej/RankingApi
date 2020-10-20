from flask_restful import Resource, reqparse
from app import db

from app.models import Task, TaskSchema

task_schema = TaskSchema()

class TaskResource(Resource):
    def get(self, task_id):
        task = Task.query.get(task_id)

        if task is None:
            return {'status': 'NOT FOUND'}, 404
        
        task = task_schema.dump(task)
        return {'status': 'OK', 'data': task}