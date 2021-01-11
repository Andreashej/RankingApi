from flask_restful import Resource, reqparse

from ..models import TestCatalog, TestCatalogSchema

test_schema = TestCatalogSchema()
tests_schema = TestCatalogSchema(many=True)

class TestCatalogResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testcode', type=str, required=True, location='json')
    
    def get(self):
        try:
            tests = TestCatalog.filter().all()
        except Exception as e:
            return { 'message': str(e) }
            
        tests = tests_schema.dump(tests)

        return {'status': 'OK', 'data': tests}, 200

class TestDefinitionResource(Resource):
    def __init__(self):
        pass

    def get(self, testcode):
        test = TestCatalog.query.filter_by(testcode = testcode).first()

        if test is None:
            return {'status': 'NOT FOUND'}, 404
        
        test = test_schema.dump(test)

        return {'status': 'OK', 'data': test}