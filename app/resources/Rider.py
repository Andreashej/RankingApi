import os

from flask_restful import Resource, reqparse, current_app, request, url_for
from flask_jwt_extended import jwt_required
from .. import db
from ..models import Rider, RiderSchema, ResultSchema, TestSchema, TaskSchema, RankingListResultSchema

from sqlalchemy import and_

riders_schema = RiderSchema(many=True, exclude=("results","testlist","aliases",))
rider_schema = RiderSchema(exclude=("results",))

results_schema = ResultSchema(many=True, exclude=("rider",))
result_schema = ResultSchema(exclude=("rider",))

tests_schema = TestSchema(many=True, exclude=("results",))

task_schema = TaskSchema()

rankinglist_result_schema = RankingListResultSchema(only=("rank","test.rankinglist",))

class RidersResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('fname', type= str, required = True, location = 'json')
        self.reqparse.add_argument('lname', type= str, required = True, location = 'json')

    def get(self):

        try:
            riders = Rider.filter()
        except Exception as e:
            return { 'message': str(e) }, 500

        riders_json = riders_schema.dump(riders.all())

        return { 'data': riders_json }, 200
    
    @jwt_required
    def post(self):

        file = request.files.get('aliases')
        if file:
            file.save(os.path.join(current_app.config["ISIRANK_FILES"], file.filename))

            task = Rider.import_aliases(file.filename)

            os.remove(current_app.config["ISIRANK_FILES"] + file.filename)

            try:
                db.session.commit()
            except:
                return { 'status': 'ERROR', 'message': 'Database error'}, 500

            task = task_schema.dump(task)

            return {'status': 'OK', 'data': task}

        args = self.reqparse.parse_args()
        try:
            rider = Rider(
                first=args['fname'],
                last=args['lname']
            )
        except Exception as e:
            return { 'status': 'EXISTS', 'message' : e.args}, 403

        try:
            db.session.add(rider)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500

        rider = rider_schema.dump(rider)

        return {'status': 'OK', 'data': rider}, 200
    
    @jwt_required
    def delete(self):
        try:
            Rider.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204

class RiderResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('fname', type= str, required = True, location = 'json')
        self.reqparse.add_argument('lname', type= str, required = True, location = 'json')

    def get(self, rider_id):
        rider = Rider.query.get(rider_id)
        if not rider:
            return {'status': 'NOT FOUND'}, 404
        
        rider = rider_schema.dump(rider)

        return {'status': 'OK', 'data': rider}
    
    @jwt_required
    def patch(self, rider_id):
        args = self.reqparse.parse_args()
        
        rider = Rider.query.get(rider_id)
        if not rider:
            return {'status': 'NOT FOUND'}, 404
        
        if args['fname'] is not None:
            rider.firstname = args['fname']

        if args['lname'] is not None:
            rider.lastname = args['lname']
        
        rider = rider_schema.dump(rider)
        rider['results'] = {}
        
        return {'status': 'OK', 'data': rider}

    @jwt_required
    def delete(self, rider_id):
        rider = Rider.query.get(rider_id)

        try:
            db.session.delete(rider)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        return {'status': 'OK'}, 204

class RiderResultResource(Resource):
    def __init__(self):
        pass

    def get(self, rider_id, testcode):
        rider = Rider.query.get(rider_id)
        results_for_test = rider.get_results(testcode, limit=request.args.get('limit'))
        best = rider.get_best_result(testcode)
        best_rank = rider.get_best_rank(testcode)

        if len(results_for_test) == 0:
            return { 'status': 'NOT FOUND', 'message': 'The rider has no results in this test'}, 404

        return {
            'status': 'OK',
            'data':{
                'history': results_schema.dump(results_for_test),
                'best': result_schema.dump(best),
                'best_rank': rankinglist_result_schema.dump(best_rank)
            }
        }
