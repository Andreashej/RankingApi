from flask_restful import Resource
from flask import request
from app.Responses import ApiResponse
from app.models.SearchResultViewModel import SearchResult
from app import db

class SearchResultsResource(Resource):
    def get(self):
        search_term = request.args.get("q")
        query = SearchResult.query.filter(SearchResult.search_string.like(f"%{search_term}%"))

        search_results = SearchResult.load_many(query)

        return ApiResponse(search_results).response()