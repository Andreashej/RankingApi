
import datetime
from flask import request


class RestMixin(object):

    @classmethod
    def filter(cls, query = None):
        if not query:
            query = cls.query

        filters = request.args.getlist('filter')

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
                    value = datetime.datetime.strptime(value, '%d/%m/%Y')
            
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