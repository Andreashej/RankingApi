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
                'totalPages': g.pagination.pages,
                'perPage': g.pagination.per_page,
                'hasNext': g.pagination.has_next,
                'hasPrevious': g.pagination.has_prev,
                'previousPage': g.pagination.prev_num,
                'nextPage': g.pagination.next_num,
                'totalItems': g.pagination.total
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