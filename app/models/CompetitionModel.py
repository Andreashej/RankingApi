from marshmallow import fields
from app import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from flask import current_app

from .TaskModel import Task

competitions_rankinglists = db.Table('competition_ranking_association',
    db.Column('competition_id', db.Integer, db.ForeignKey('competitions.id'), primary_key=True),
    db.Column('rankinglist_id', db.Integer, db.ForeignKey('rankinglists.id'), primary_key=True)
)

class Competition(db.Model):
    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    isirank_id = db.Column(db.String(10), unique=True)
    first_date = db.Column(db.Date)
    last_date = db.Column(db.Date)
    include_in_ranking = db.relationship('RankingList', secondary=competitions_rankinglists, lazy='dynamic', backref=db.backref('competitions', lazy=True))
    tests = db.relationship("Test", backref="competition", lazy='dynamic')
    tasks = db.relationship("Task", backref="competition", lazy='dynamic')

    def __init__(self, isi_id, startdate=None, enddate=None, name=''):
        self.name = name
        self.isirank_id = isi_id
        self.first_date = startdate
        self.last_date = enddate

    def launch_task(self, name, descripton, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, *args, **kwargs)

        task = Task(id=rq_job.get_id(), name=name, description=descripton, competition=self)
        db.session.add(task)

        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(competition=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, competition=self, complete=False).first()