from flask_restful import Resource, reqparse
from flask import request
from sqlalchemy import and_, not_
from .. import db

from ..models import Task, TaskSchema

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

class TasksResource(Resource):
    def _filter(self, query):
        filters = request.args.to_dict()

        for key, value in filters.items():
            try:
                if key == 'state':
                    if value == 'ERROR':
                        query = query.filter_by(error = True)
                    elif value == 'COMPLETE':
                        query = query = query.filter_by(complete = True, error = False)
                    elif value == 'IN PROGRESS':
                        query = query.filter(and_(not_(Task.started_at == None), Task.complete == False))
                    elif value == 'WAITING':
                        query = query.filter(and_(Task.started_at == None, not_(Task.complete == True)))
                else:
                    query = query.filter(getattr(Task, key) == value)
            except Exception as e:
                print(e)
                continue

        return query

    def get(self):
        tasks = self._filter(Task.query).order_by(Task.started_at.desc()).all()

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