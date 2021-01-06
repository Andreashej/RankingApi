from flask_restful import Resource, reqparse
from flask import request, current_app
from flask_jwt_extended import jwt_required
from icerankingapi import db
from icerankingapi.models import Result, ResultSchema, TaskSchema

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
        results = Result.query.all()
        results = results_schema.dump(results)

        return {'status': 'OK', 'data': results}, 200
    
    @jwt_required
    def post(self):
        if request.files:
            file = request.files['file']

            file.save(os.path.join(current_app.config["ISIRANK_FILES"], file.filename))

            task = Result.load_from_file(file.filename)

            try:
                db.session.commit()
            except:
                pass

            task = task_schema.dump(task)
            return {'status': 'OK', 'data': task}
        else:
            return {'status': 'ERROR', 'message': 'File not found'},500

    @jwt_required
    def delete(self):
        try:
            Result.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204

class ResultResource(Resource):
    def __init__(self):
        pass

    def get(self, result_id):
        result = Result.query.get(result_id)
        result = result_schema.dump(result)

        return {'status': 'OK', 'data': result}