from flask_restful import Resource
from app.models import TestCatalog
from app.Responses import ApiResponse
from flask.globals import g

class TestCatalogResource(Resource):
    
    @TestCatalog.from_request(many=True)
    def get(self):
        return ApiResponse(g.catalog_tests).response()
