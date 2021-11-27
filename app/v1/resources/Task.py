from flask_restful import Resource, reqparse
from flask import request
from sqlalchemy import and_, not_
from app import db

from app.models import Task, TaskSchema

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

class TasksResource(Resource):
    def get(self):
        try:
            tasks = Task.filter().all()
        except Exception as e:
            return { 'message': str(e) }

        tasks = tasks_schema.dump(tasks)
        
        return { 'status': 'OK', 'data': tasks }, 200
    
    def delete(self):
        try:
            self._filter(Task.query).delete()
            db.session.commit()
        except Exception as e:
            return { 'status': 'ERROR', 'message': str(e)}
        
        return { 'status': 'OK'}, 204

class TaskResource(Resource):
    def get(self, task_id):
        task = Task.query.get(task_id)

        if task is None:
            return {'status': 'NOT FOUND'}, 404
        
        task = task_schema.dump(task)
        return {'status': 'OK', 'data': task}