from flask.globals import request, g

class ApiResponse:
    def __init__(
        self,
        data = None, 
        Schema = None, 
        response_code = 200, 
        *, 
        task = None, 
        tasks = [], 
        message = "", 
        schema_options = { 
            'many': False, 
            'exclude': None,
            'only': None 
        }
    ):
        from app.models.schemas import TaskSchema
        self.task_schema = TaskSchema()
        self.tasks_schema = TaskSchema(many=True)
        self.data = data
        self.response_code = response_code
        self.task = task
        self.tasks = tasks
        if task is not None and len(self.tasks) > 0:
            self.tasks.append(self.task)
            self.task = None
        
        self.message = message
        if Schema is not None:
            self.define_schema(Schema, schema_options)

    
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
        if self.schema:
            return { 'data': self.schema.dump(self.data) }
        
        return self.data
    
    def get_task(self):
        if self.task is None: return { }
        return { 'task': self.task_schema.dump(self.task) }
    
    def get_tasks(self):
        if len(self.tasks) == 0: return { }
        return { 'tasks': self.tasks_schema.dump(self.tasks) }
    
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
        response.update(self.get_tasks())
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