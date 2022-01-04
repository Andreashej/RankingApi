from sqlalchemy.ext import hybrid
from .. import db
from sqlalchemy.ext.hybrid import hybrid_property

from flask import current_app

from .TaskModel import Task

from .RestMixin import ApiErrorResponse, RestMixin

competitions_rankinglists = db.Table('competition_ranking_association',
    db.Column('competition_id', db.Integer, db.ForeignKey('competitions.id'), primary_key=True),
    db.Column('rankinglist_id', db.Integer, db.ForeignKey('rankinglists.id'), primary_key=True)
)

class Competition(db.Model, RestMixin):
    RESOURCE_NAME = 'competition'
    RESOURCE_NAME_PLURAL = 'competitions'

    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250))
    ext_id = db.Column('isirank_id', db.String(12), unique=True)
    first_date = db.Column(db.Date)
    last_date = db.Column(db.Date)
    country = db.Column(db.String(2), default='DK')
    state = db.Column(db.String(12), default="NORMAL") # { NORMAL, BLOCKED, CANCELLED, UNLISTED }
    include_in_ranking = db.relationship('RankingList', secondary=competitions_rankinglists, lazy='dynamic', back_populates='competitions')
    tests = db.relationship("Test", backref="competition", lazy='dynamic', cascade='all,delete', order_by='Test.testcode')
    tasks = db.relationship("Task", backref="competition", lazy='dynamic')

    def __init__(self, name='', startdate=None, enddate=None, isi_id = None, country='XX'):
        self.name = name
        self.first_date = startdate
        self.last_date = enddate
        self.country = country

        db.session.add(self)
        db.session.flush()

        self.ext_id = isi_id or self.create_id()
    
    def __repr__(self):
        return f'<Competition {self.name} from {self.first_date} to {self.last_date}>'

    @hybrid_property
    def isirank_id(self):
        return self.ext_id
    
    @isirank_id.setter
    def isirank_id(self, ext_id):
        self.ext_id = ext_id
    
    @hybrid_property
    def tasks_in_progress(self):
        return self.get_tasks_in_progress()

    def launch_task(self, name, descripton, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, *args, **kwargs)

        task = Task(id=rq_job.get_id(), name=name, description=descripton, competition=self)
        db.session.add(task)

        return task

    def create_id(self):
        return f'{self.country}{self.last_date.year}{self.id:06}'
    
    def add_test(self, test):
        if test.testcode in [test.testcode for test in self.tests]:
            raise ValueError(f"Duplicate testcode {test.testcode} for competition")
            
        self.tests.append(test)

    def get_tasks_in_progress(self):
        return Task.query.filter_by(competition=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, competition=self, complete=False).first()