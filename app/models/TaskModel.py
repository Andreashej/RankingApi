import redis
import rq

from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from flask import current_app

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), default=None)
    rankinglist_test_id = db.Column(db.Integer, db.ForeignKey('rankinglist_tests.id'), default=None)
    rankinglist_id = db.Column(db.Integer, db.ForeignKey('rankinglists.id'), default=None)
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        
        return rq_job
    
    @hybrid_property
    def progress(self):
        return self.get_progress()

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100