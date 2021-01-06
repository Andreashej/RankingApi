import redis
import rq
import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from .. import db
from flask import current_app

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), default=None)
    rankinglist_test_id = db.Column(db.Integer, db.ForeignKey('rankinglist_tests.id'), default=None)
    rankinglist_id = db.Column(db.Integer, db.ForeignKey('rankinglists.id'), default=None)
    complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        
        return rq_job
    
    @hybrid_property
    def progress(self):
        return self.get_progress()

    @hybrid_property
    def state(self):
        if self.complete:
            return 'COMPLETE'
        
        if self.progress == 100:
            return 'ERROR'
        
        if self.progress > 0:
            return 'PROGRESS'
        
        return 'WAITING'

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100