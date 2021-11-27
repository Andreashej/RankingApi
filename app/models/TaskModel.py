from flask_restful import Resource
import redis
import rq
import datetime

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import case, and_, not_

from .. import db
from flask import current_app

from .RestMixin import RestMixin

class Task(db.Model, RestMixin):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), default=None)
    rankinglist_test_id = db.Column(db.Integer, db.ForeignKey('rankinglist_tests.id', ondelete="SET NULL"), default=None)
    rankinglist_id = db.Column(db.Integer, db.ForeignKey('rankinglists.id', ondelete="SET NULL"), default=None)
    complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        
        return rq_job
    
    @hybrid_property
    def state(self):
        if self.error:
            return "ERROR"
        elif self.complete:
            return "COMPLETE"
        elif self.started_at and not self.complete:
            return "PROGRESS"
        else:
            return "WAITING"
    
    @state.expression
    def state(cls):
        return case([
                (cls.error, "ERROR"),
                (cls.complete, "COMPLETE"),
                (and_(cls.started_at, not_(cls.complete)), "PROGRESS")
            ], 
            else_='WAITING'
        )
    
    @hybrid_property
    def progress(self):
        return self.get_progress()

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100