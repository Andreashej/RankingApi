from flask_restful import Resource
from flask_jwt_extended import jwt_required

from ..models import Log, LogSchema

logs_schema = LogSchema(many=True)

class LogsResource(Resource):
    def get(self):
        try:
            logs = Log.filter().all()
        except Exception as e:
            return { 'message': str(e) }, 500
    
        logs = logs_schema.dump(logs)

        return { 'data': logs }, 200