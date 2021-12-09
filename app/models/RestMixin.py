
import datetime
from flask import request, abort
from flask_restful.reqparse import RequestParser
from flask_sqlalchemy import Pagination
from werkzeug.exceptions import HTTPException
from .. import db

class ApiResponse:
    def __init__(self, data = None, schema = None, response_code = 200):
        self.data = data
        self.schema = schema
        self.response_code = response_code
    
    def response(self):
        if not self.data:
            return None, self.response_code

        return {
            'data': self.schema.dump(self.data),
        }, self.response_code

class ApiErrorResponse(Exception):
    def __init__(self, message: str, response_code = 500):
        self.error_message = message
        self.response_code = response_code
        super().__init__(self.error_message)
    
    def response(self):
        return { 'message': self.error_message }, self.response_code

class RestMixin():

    @classmethod
    def load(cls, instance_id = None, query = None):
        if query is None:
            query = cls.query

        if instance_id:
            instance = query.get(instance_id)

            if not instance:
                raise ApiErrorResponse(f'Could not find instance of {cls.__name__} with ID {instance_id}', 404)
            
            return instance
        
        try:
            query = cls.filter(query)
        except Exception as e:
            raise ApiErrorResponse(str(e))

        if request.args.get('per_page') or request.args.get('page'):
            return query.paginate().items
        
        return query.all()
        

    @classmethod
    def filter(cls, query = None):
        if not query:
            query = cls.query

        filters = request.args.getlist('filter[]')

        for filter in filters:
            pack = filter.split()
            [field, operator, value, mapper_field] = pack if len(pack) == 4 else pack + [None]

            field = getattr(cls, field)

            if hasattr(field, 'property') and hasattr(field.property, 'mapper'):
                if mapper_field:
                    relationship_class = field.property.mapper.class_
                    mapper = getattr(relationship_class, mapper_field)
                    value = relationship_class.query.filter(mapper == value).first()
                    query.join(relationship_class, mapper==field)

            if hasattr(field, 'type'):
                if (field.type == 'DATE'):
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
            
            if operator == 'contains':
                query = query.filter(field.contains(value))
            elif operator == '<' :
                query = query.filter(field < value)
            elif operator == '>' :
                query = query.filter(field > value)
            elif operator == 'eq' or operator == '==':
                query = query.filter(field == value)
            elif operator == 'like':
                query = query.filter(field.like(value))
        
        order = request.args.get('order_by')

        if order:
            [field, direction] = order.split()
            if direction == 'desc':
                query = query.order_by(getattr(cls, field).desc())
            else:
                query = query.order_by(getattr(cls, field).asc())

        limit = request.args.get('limit')

        if limit:
            query = query.limit(limit)

        return query
    
    def update(self, reqparser: RequestParser):
        args = reqparser.parse_args()
        for attr in args:
            value = args[attr]

            if value and hasattr(self, attr):
                setattr(self, attr, value)
    
    def save(self):
        try:
            if not self.id:
                db.session.add(self)
                
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def remove(self):
        try:
            db.session.remove(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
