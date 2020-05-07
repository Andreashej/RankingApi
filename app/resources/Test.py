from flask_restful import Resource, reqparse
from app import db, auth

from app.models import Test, TestSchema, Competition

test_schema = TestSchema()
tests_schema = TestSchema(many=True)

class TestsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
        self.reqparse.add_argument('competition_id')
    
    def get(self):
        tests = Test.query.all()
        tests = tests_schema.dump(tests).data

        return {'status': 'OK', 'data': tests}, 200
    
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()

        test = Test(args['testcode'])

        competition = Competition.query.get(args['competition_id'])

        test.competition = competition

        try:
            db.session.add(test)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        test = test_schema.dump(test).data
        return {'status': 'OK', 'data': test},200
    
    @auth.login_required
    def delete(self):
        try:
            Test.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204

class TestResource(Resource):
    def __init__(self):
        pass

    def get(self, test_id):
        test = Test.query.get(test_id)

        if test is None:
            return {'status': 'NOT FOUND'}, 404
        
        test = test_schema.dump(test).data

        return {'status': 'OK', 'data': test}

    @auth.login_required
    def patch(self):
        pass