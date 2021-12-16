class ApiResponse:
    def __init__(self, data = None, schema = None, response_code = 200, *, task = None, tasks = [], message = ""):
        from app.models.schemas import TaskSchema
        self.task_schema = TaskSchema()
        self.tasks_schema = TaskSchema(many=True)
        self.data = data
        self.schema = schema
        self.response_code = response_code
        if (len(tasks) == 0):
            self.task = task
        else:
            tasks.append(task)
        self.tasks = tasks
        self.message = message
    
    def get_data(self):
        if not self.data: return { }
        if self.schema:
            return { 'data': self.schema.dump(self.data) }
        
        return self.data
    
    def get_task(self):
        if not self.task: return { }
        return { 'task': self.task_schema.dump(self.task) }
    
    def get_tasks(self):
        if len(self.tasks) == 0: return { }
        return { 'tasks': self.tasks_schema.dump(self.tasks) }
    
    def get_message(self):
        if not self.message: return { }
        return { 'message': self.message }
    
    def response(self):
        response = {}

        response.update(self.get_data())
        response.update(self.get_task())
        response.update(self.get_tasks())
        response.update(self.get_message())

        return response, self.response_code
        
class ApiErrorResponse(Exception, ApiResponse):
    def __init__(self, message: str, response_code = 500):
        self.data = None
        self.task = None
        self.tasks = []
        self.message = message
        self.response_code = response_code
        super().__init__(self.message)