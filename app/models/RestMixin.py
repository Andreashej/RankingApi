
import datetime
from flask import request
from flask.globals import g
from flask_restful.reqparse import RequestParser
from app.Responses import ApiErrorResponse
from .. import db
import math
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from flask_sqlalchemy import BaseQuery
from datetime import date, datetime
from app.utils import split, camel_to_snake, snake_to_camel

class RestMixin():
    BLOCK_FROM_JSON = []
    EXCLUDE_FROM_JSON = []
    INCLUDE_IN_JSON = []

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

        per_page = request.args.get('perPage', 10, int)
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
    def join_by_mapper(cls, query, fields, parent_class):
        field = getattr(parent_class, fields[0])

        if len(fields) == 1:
            return query, field
        
        if hasattr(field, 'property') and hasattr(field.property, 'mapper'):
            relationship_class = field.property.mapper.class_
        elif hasattr(field, 'class_'):
            relationship_class = field.class_
        else:
            raise ApiErrorResponse(f'Field {field} is not joinable.', 400)

        if relationship_class not in [mapper.class_ for mapper in query._join_entities]:
            query = query.join(relationship_class)

        return cls.join_by_mapper(query, fields[1:], relationship_class)

    @classmethod
    def apply_filter(cls, query, filter):
        [fieldpath, operator, value] = split(filter, 2)

        fields = [camel_to_snake(field) for field in fieldpath.split('.')]
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
            
            if (field.type == 'BOOL'):
                value = value.lower() != 'true'
            
        if value == 'null':
            value = None
        
        if operator == 'contains':
            query = query.filter(field.contains(value))
        elif operator == '<' :
            query = query.filter(field < value)
        elif operator == '>' :
            query = query.filter(field > value)
        elif operator == '<=':
            query = query.filter(field <= value)
        elif operator == '>=':
            query = query.filter(field >= value)
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
        
        order = request.args.get('orderBy')

        if order:
            [fieldpath, direction] = order.split()
            fields = [camel_to_snake(field) for field in fieldpath.split('.')]
            query, field = cls.join_by_mapper(query, fields, cls)

            if isinstance(field, str):
                field = getattr(cls, field)

            if direction == 'desc':
                query = query.order_by(field.desc())
            else:
                query = query.order_by(field.asc())

        limit = request.args.get('limit')

        if limit:
            query = query.limit(limit)

        return query

    @property
    def default_fields(self):
        return [attr.key for attr in self.__mapper__.attrs if isinstance(attr, ColumnProperty) and attr.key not in self.EXCLUDE_FROM_JSON + self.BLOCK_FROM_JSON] + self.INCLUDE_IN_JSON
    
    @property
    def nested_fields(self):
        return [attr.key for attr in self.__mapper__.attrs if isinstance(attr, RelationshipProperty)]
    
    def to_json(self, fields = [], expand = []):
        if len(fields) == 0: fields = self.default_fields

        fields = camel_to_snake(fields)
        expand = camel_to_snake(expand)

        json = { }

        valid_fields = [field for field in fields if hasattr(self, field) and field not in self.BLOCK_FROM_JSON]
        
        for field in valid_fields:
            value = getattr(self, field)

            if isinstance(value, date):
                value = value.isoformat()
            
            if isinstance(value, map):
                value = list(value)

            json.update({
                snake_to_camel(field): value
            })

        for field in expand:
            if hasattr(self, field) and field not in self.BLOCK_FROM_JSON:
                attr = getattr(self, field)

                if isinstance(attr, BaseQuery):
                    attr = attr.all()

                expand_obj = attr.to_json() if hasattr(attr, 'to_json') else None

                if isinstance(attr, list):
                    expand_obj = [item.to_json() for item in attr]

                json.update({
                    snake_to_camel(field): expand_obj
                })


        # nested_fields = { }

        # for field in expand:
        #     children = field.split('.', 1)

        #     if children[0] not in nested_fields:
        #         nested_fields[children[0]] = {
        #             'fields': [],
        #             'expand': []
        #         }

        #     if len(children) > 1:
        #         if '.' in children[1]:
        #             nested_fields[children[0]]['expand'].append(children[1])
        #         else:
        #             nested_fields[children[0]]['fields'].append(children[1])
        
        # for field in nested_fields:
        #     if hasattr(self, field):
        #         attr = getattr(self, field)
        #         if attr is None:
        #             continue

        #         if isinstance(attr, BaseQuery):
        #             attr = attr.all()

        #         data = None
        #         if isinstance(attr, list):
        #             data = [child.to_json(fields=nested_fields[field]['fields'], expand=nested_fields[field]['expand']) for child in attr]
        #         else:
        #             data = attr.to_json(fields=nested_fields[field]['fields'], expand=nested_fields[field]['expand'])


        #         json.update({
        #             field: data
        #         })

        return json

    
    def update(self, reqparser: RequestParser):
        args = reqparser.parse_args()
        for attr in args:
            value = args[attr]

            prop = camel_to_snake(attr)

            if value is not None and hasattr(self, prop):
                try:
                    setattr(self, prop, value)
                except ValueError as e:
                    raise ApiErrorResponse(str(e), 400)
                except Exception as e:
                    raise ApiErrorResponse(str(e))
        return args
    
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
