
import datetime
from flask import request
from flask.globals import g
from flask_restful.reqparse import RequestParser
from app.Responses import ApiErrorResponse
from .. import db

class RestMixin():

    @classmethod
    def from_request(cls, _func=None, *, many=False):
        def load_decorator(func):
            def load_wrapper(*args, **kwargs):
                value = None
                name = ""
                if not many:
                    id = kwargs.get("id")

                    if not id:
                        return ApiErrorResponse("No ID found in request", 400).response()
                    
                    name = cls.RESOURCE_NAME
                    try:
                        value = cls.load_one(id)
                    except ApiErrorResponse as e:
                        return e.response()
                else:
                    name = cls.RESOURCE_NAME_PLURAL
                    try:
                        value = cls.load_many()
                    except ApiErrorResponse as e:
                        return e.response()

                try:
                    setattr(g, name, value)
                except ApiErrorResponse as e:
                    return e.response()
                except Exception as e:
                    return ApiErrorResponse(str(e)).response()

                return func(*args, **kwargs)
            
            return load_wrapper
    
        if _func is None:
            return load_decorator
        else:
            return load_decorator(_func)

    @classmethod
    def load_one(cls, instance_id):
        instance = cls.query.get(instance_id)

        if not instance:
            raise ApiErrorResponse(f'Could not find instance of {cls.__name__} with ID {instance_id}', 404)
        
        return instance

    @classmethod
    def load_many(cls, query = None):
        if query is None:
            query = cls.query
     
        try:
            query = cls.filter(query)
        except Exception as e:
            raise ApiErrorResponse(str(e))

        if request.args.get('per_page') or request.args.get('page'):
            if request.args.get('limit') is not None:
                raise ApiErrorResponse('Limit is not compatible with pagination', 400)
            g.pagination = query.paginate()
            return g.pagination.items
        
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
