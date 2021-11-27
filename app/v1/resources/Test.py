from flask.globals import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from app import db

from app.models import Test, Competition, TestSchema

test_schema = TestSchema()
tests_schema = TestSchema(many=True, exclude=("results",))

class TestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('competition_id')
    
    def get(self):
        try:
            tests = Test.filter().all()
        except Exception as e:
            return { 'message': str(e) }

        tests = tests_schema.dump(tests)

        return { 'data': tests }, 200
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        test = Test(args['testcode'])

        competition = Competition.query.get(args['competition_id'])

        test.competition = competition

        try:
            db.session.add(test)
            db.session.commit()
        except:
            return {}, 500
        
        test = test_schema.dump(test)
        return { 'data': test },200
    
    @jwt_required
    def delete(self):
        try:
            Competition.filter().delete()
            db.session.commit()
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}, 500
        
        return {}, 204

class TestResource(Resource):
    def __init__(self):
        pass

    def get(self, test_id):
        test = Test.query.get(test_id)

        if test is None:
            return {'status': 'NOT FOUND'}, 404
        
        test = test_schema.dump(test)

        return { 'data': test }

    @jwt_required
    def patch(self):
        pass