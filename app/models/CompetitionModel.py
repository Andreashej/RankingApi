from .. import db
from sqlalchemy.ext.hybrid import hybrid_property

from flask import current_app

from .TaskModel import Task

from .RestMixin import RestMixin

competitions_rankinglists = db.Table('competition_ranking_association',
    db.Column('competition_id', db.Integer, db.ForeignKey('competitions.id'), primary_key=True),
    db.Column('rankinglist_id', db.Integer, db.ForeignKey('rankinglists.id'), primary_key=True)
)

class Competition(db.Model, RestMixin):
    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    isirank_id = db.Column(db.String(12), unique=True)
    first_date = db.Column(db.Date)
    last_date = db.Column(db.Date)
    country = db.Column(db.String(2), default='DK')
    state = db.Column(db.String(12), default="NORMAL") # { NORMAL, BLOCKED, CANCELLED, UNLISTED }
    include_in_ranking = db.relationship('RankingList', secondary=competitions_rankinglists, lazy='dynamic', backref=db.backref('competitions', lazy=True))
    tests = db.relationship("Test", backref="competition", lazy='dynamic', cascade='all,delete')
    tasks = db.relationship("Task", backref="competition", lazy='dynamic')

    def __init__(self, name='', startdate=None, enddate=None, isi_id = None):
        self.name = name
        self.first_date = startdate
        self.last_date = enddate
        self.isirank_id = isi_id
    
    def __repr__(self):
        return f'<Competition {self.name} from {self.first_date} to {self.last_date}>'
    
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

    def get_tasks_in_progress(self):
        return Task.query.filter_by(competition=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, competition=self, complete=False).first()