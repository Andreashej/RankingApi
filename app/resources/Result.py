from flask_restful import Resource, reqparse
from flask import request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.log import echo_property
from .. import db
from ..models import Result, ResultSchema, TaskSchema

import os

results_schema = ResultSchema(many=True)
result_schema = ResultSchema()

task_schema = TaskSchema()

class ResultsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required = True, location = 'json')
        self.reqparse.add_argument('rider_id', type=int, required = True, location = 'json')
        self.reqparse.add_argument('horse_id', type=int, required = True, location = 'json')
        self.reqparse.add_argument('mark', type=float, required = True, location = 'json')

    def get(self):
        try:
            results = Result.filter().all()
        except Exception as e:
            return { 'message': str(e) }, 500

        results = results_schema.dump(results)

        return { 'data': results }, 200
    
    @jwt_required
    def post(self):
        if request.files:
            file = request.files['file']

            file.save(os.path.join(current_app.config["ISIRANK_FILES"], file.filename))

            task = Result.load_from_file(file.filename)

            try:
                db.session.commit()
            except:
                db.session.rollback()

            task = task_schema.dump(task)
            return {'status': 'OK', 'data': task}
        else:
            return {'status': 'ERROR', 'message': 'File not found'},500

    @jwt_required
    def delete(self):
        try:
            Result.filter().delete()
            db.session.commit()
        except Exception as e:
            return { 'message': str(e)}, 500
        
        return {}, 204

class ResultResource(Resource):
    def __init__(self):
        pass

    def get(self, result_id):
        result = Result.query.get(result_id)
        result = result_schema.dump(result)

        return {'status': 'OK', 'data': result}
