from flask_restful import Resource, reqparse
from flask import request
from .. import db

from ..models import Task, TaskSchema

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

class TasksResource(Resource):
    def _filter(self, query):
        filters = request.args.to_dict()

        for key, value in filters.items():
            try:
                query = query.filter(getattr(Task, key) == value)
            except Exception as e:
                return { 'status': 'ERROR', 'message': str(e)}

        return query

    def get(self):
        tasks = self._filter(Task.query)

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