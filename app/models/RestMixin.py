
import datetime
from flask import request
from flask.globals import g
from flask_restful.reqparse import RequestParser
from app.Responses import ApiErrorResponse
from .. import db
import shlex
import math

def split(string, maxsplit=-1):
    """ Split a string with shlex when possible, and add support for maxsplit. """
    if maxsplit == -1:
        try:
            split_object = shlex.shlex(string, posix=True)
            split_object.quotes = '"`'
            split_object.whitespace_split = True
            split_object.commenters = ""
            return list(split_object)
        except ValueError:
            return string.split(" ", maxsplit)

    split_object = shlex.shlex(string, posix=True)
    split_object.quotes = '"`'
    split_object.whitespace_split = True
    split_object.commenters = ""
    maxsplit_object = []
    splits = 0

    while splits < maxsplit:
        maxsplit_object.append(next(split_object))

        splits += 1

    maxsplit_object.append(split_object.instream.read())

    return maxsplit_object

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

        per_page = request.args.get('per_page', 10)
        if request.args.get('page'):
            if request.args.get('limit') is not None:
                raise ApiErrorResponse('Limit is not compatible with pagination', 400)
            try:
                g.pagination = query.paginate(per_page=per_page)
                return g.pagination.items
            except Exception as e:
                result_count = query.count()
                max_page = math.ceil(result_count / per_page)
                raise ApiErrorResponse(f'The requested page number was not found. You query resulted in {result_count} results, and the maximum page number is {max_page}.', 400)
        
        return query.all()
    
    @classmethod
    def join_by_mapper(cls, query, fields, parent_class, ):
        field = getattr(parent_class, fields[0])

        if len(fields) == 1:
            return query, field
        
        if hasattr(field, 'property') and hasattr(field.property, 'mapper'):
            relationship_class = field.property.mapper.class_
        elif hasattr(field, 'class_'):
            relationship_class = field.class_
        else:
            raise ApiErrorResponse(f'Field {field} is not joinable.', 400)


        query = query.join(relationship_class)

        return cls.join_by_mapper(query, fields[1:], relationship_class)

    @classmethod
    def apply_filter(cls, query, filter):
        [fieldpath, operator, value] = split(filter, 2)

        fields = fieldpath.split('.')
        query, field = cls.join_by_mapper(query, fields, cls)
        
        if isinstance(field, str):
            field = getattr(cls, field)

        if hasattr(field, 'property') and hasattr(field.property, 'mapper'):
            if " " in value:
                relationship_class = field.property.mapper.class_
                child_query = relationship_class.apply_filter(relationship_class.query, value)
                value = child_query.first()
                query.join(field)

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
        else:
            raise ApiErrorResponse(f"Unknown comparator {operator}", 400)
        
        return query
        
    @classmethod
    def filter(cls, query = None):
        if not query:
            query = cls.query

        filters = request.args.getlist('filter[]')

        for filter in filters:
            query = cls.apply_filter(query, filter)
        
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
