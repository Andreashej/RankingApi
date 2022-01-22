from flask.globals import g
from flask_jwt_extended.view_decorators import jwt_optional
from flask_restful import Resource, reqparse
from app.models.PersonAliasModel import PersonAlias
from app.models.ResultModel import Result
from app.Responses import ApiResponse, ApiErrorResponse
from app.models.PersonModel import Person
from flask_jwt_extended import jwt_required
from app import db

class PersonsResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firstname', type= str, required = True, location = 'json')
        self.reqparse.add_argument('lastname', type= str, required = True, location = 'json')

    @Person.from_request(many=True)
    def get(self):
        return ApiResponse(g.persons).response()
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        try:
            person = Person(args['firstname'], args['lastname'])
            person.save()
        except Exception as e:
            return ApiErrorResponse(e.args, 403).response()
        
        return ApiResponse(person).response()

class PersonResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('firstname', type= str, required = False, location = 'json')
        self.reqparse.add_argument('lastname', type= str, required = False, location = 'json')
        self.reqparse.add_argument('email', type=str, required=False, location='json')
    
    @Person.from_request
    def get(self, id):
        return ApiResponse(g.person).response()
    
    @jwt_required
    @Person.from_request
    def patch(self, id):
        try:
            g.person.update(self.reqparse)
            g.person.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(g.person).response()
    
    @jwt_required
    @Person.from_request
    def delete(self, id):
        if len(g.person.results) > 0:
            return ApiErrorResponse("You cannot delete a person that has results", 403)

        try:
            g.person.delete()
            db.session.commit()
        except Exception as e:
            return ApiErrorResponse(str(e)).response()
        
        return ApiResponse(response_code=204).response()

class PersonResultsResource(Resource):
    @Person.from_request
    def get(self, id):
        try:
            results = Result.load_many(g.person.results)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(results).response()

class PersonAliasesResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('alias', type=str, location='json', required=False)
        self.reqparse.add_argument('personId', type=str, location='json', required=False)
    
    @Person.from_request
    def get(self, id):
        try:
            aliases = Result.load_many(g.person.aliases)
        except ApiErrorResponse as e:
            return e.response()

        return ApiResponse(aliases).response()

    @jwt_required
    @Person.from_request
    def post(self, id):
        args = self.reqparse.parse_args()
        
        try:
            alias = g.person.add_alias(args['alias'], args['personId'])
            
            alias.save()
        except ApiErrorResponse as e:
            return e.response()
        
        return ApiResponse(alias).response()