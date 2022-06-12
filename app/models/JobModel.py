
from app import db
from app.models.RestMixin import RestMixin
from flask import current_app
from datetime import datetime, timezone
from app.models import Task
from croniter import croniter
from rq.job import Job as RQJob
from rq import get_current_job
from rq.exceptions import NoSuchJobError

class Job(db.Model, RestMixin):
    RESOURCE_NAME = 'job'
    RESOURCE_NAME_PLURAL = 'jobs'

    __tablename__ = 'jobs'

    BLOCK_FROM_JSON = ['_cron_expr', '_active']
    INCLUDE_IN_JSON = ['cron_expr', 'active']

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))

    cron_expr = db.Column(db.String(50), default='0 0 * * * *')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)

    active = db.Column(db.Boolean, default=True)

    task_name = db.Column(db.String(128))

    tasks = db.relationship('Task', lazy='dynamic', backref='job')

    def queue_next(self, **kwargs):
        current_job = get_current_job()

        if current_job is not None:
            is_scheduled = self.tasks.filter(Task.complete == False, Task.id != current_job.id).count()
        else:
            is_scheduled = 0
        
        # If the job is not active or it already has tasks running, don't start a new one
        if not self.active or is_scheduled > 0:
            return


        cron = croniter(self.cron_expr, datetime.now(timezone.utc), datetime)

        if not cron.is_valid(self.cron_expr):
            raise ValueError('Cron Expression is not valid')
        
        next_time = cron.get_next()

        self.next_run_at = next_time

        rq_job = current_app.task_queue.enqueue_at(next_time, 'app.tasks.' + self.task_name)
        
        task = Task(id=rq_job.get_id(), name=self.task_name, description=self.description, job_id=self.id, **kwargs)
        db.session.add(task)

        try:
            db.session.commit()
        except:
            db.session.rollback()

        return task

    def restart(self):
        self._stop()
        self._start()     

    def _start(self):
        self.active = True
        self.queue_next()
    
    def _stop(self):
        self.active = False
        self.next_run_at = None
        tasks = self.tasks.filter_by(complete=0).all()

        for task in tasks:
            try:
                job = RQJob.fetch(task.id, connection=current_app.redis)
                job.cancel()
            except NoSuchJobError:
                pass

            task.complete = True
            task.completed_at = datetime.utcnow()
    
    @classmethod
    def start_active(cls):
        active_jobs = cls.query.filter_by(active=True).all()

        for job in active_jobs:
            job.queue_next()
