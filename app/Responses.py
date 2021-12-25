from math import exp
from flask.globals import request, g

class ApiResponse:
    def __init__(
        self,
        data = None, 
        response_code = 200, 
        *, 
        task = None, 
        message = "", 
    ):
        self.data = data
        self.response_code = response_code
        self.task = task
        
        self.message = message

    
    def define_schema(self, Schema, schema_options):
        fields = request.args.get('fields')
        only = fields.split(",") if fields else schema_options['only'].copy() if 'only' in schema_options and schema_options['only'] is not None else None

        default_exclude = schema_options['exclude'].copy() if 'exclude' in schema_options and schema_options['exclude'] is not None else []
        excluded_fields = request.args.get('exclude')
        exclude = excluded_fields.split(",") + default_exclude if excluded_fields else default_exclude

        expanded_fields = request.args.get('expand')
        for expanded_field in expanded_fields.split(",") if expanded_fields else []:
            
            if exclude is not None and len(exclude) > 0 and expanded_field in exclude: exclude.remove(expanded_field)
            if only is not None and len(only) > 0: only.append(expanded_fields)
        
        many = isinstance(self.data, list)

        self.schema = Schema(many=many, exclude=exclude, only=only)
    
    def get_data(self):
        if self.data is None: return { }
        data = {}
        
        fields = request.args.get('fields')
        expanded_fields = request.args.get('expand')

        fields = fields.split(',') if fields is not None else []
        expanded_fields = expanded_fields.split(',') if expanded_fields is not None else []

        if isinstance(self.data, list):
            data = [item.to_json(fields=fields, expand=expanded_fields) for item in self.data]
        else:
            data = self.data.to_json(fields=fields, expand=expanded_fields)

        return { 'data': data }
    
    def get_task(self):
        if self.task is None: return { }
        return { 'task': self.task.to_json() }
    
    def get_message(self):
        if not self.message: return { }
        return { 'message': self.message }
    
    def get_pagination(self):
        if not hasattr(g, 'pagination'): return { }

        return {
            'pagination': {
                'page': g.pagination.page,
                'total_pages': g.pagination.pages,
                'per_page': g.pagination.per_page,
                'has_next': g.pagination.has_next,
                'has_previous': g.pagination.has_prev,
                'previous_page': g.pagination.prev_num,
                'next_page': g.pagination.next_num,
                'total_items': g.pagination.total
            } 
        }

    
    def response(self):
        response = {}

        response.update(self.get_data())
        response.update(self.get_task())
        response.update(self.get_message())
        response.update(self.get_pagination())

        return response, self.response_code
        
class ApiErrorResponse(Exception, ApiResponse):
    def __init__(self, message: str, response_code = 500):
        self.data = None
        self.task = None
        self.tasks = []
        self.message = message
        self.response_code = response_code
        super().__init__(self.message)