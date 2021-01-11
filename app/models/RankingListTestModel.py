from sqlalchemy.ext.hybrid import hybrid_property
from .. import db

from flask import current_app

from .TaskModel import Task

from .RestMixin import RestMixin

class RankingListTest(db.Model, RestMixin):
    __tablename__ = 'rankinglist_tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    rankinglist_id = db.Column(db.Integer, db.ForeignKey('rankinglists.id'), nullable=False)
    included_marks = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    grouping = db.Column(db.String(5), default='rider')
    min_mark = db.Column(db.Float)
    rounding_precision = db.Column(db.Integer)
    mark_type = db.Column(db.String(4), default='mark') # Allowed values: {mark, time, comb}
    tasks = db.relationship("Task", backref="test", lazy='dynamic')

    ranking_results_cached = db.relationship("RankingResultsCache", backref="cached_results", lazy="joined")

    @hybrid_property
    def included_tests(self):
        tests = ['T1', 'T1', 'V1', 'F1']
        if self.testcode == 'C4':
            return tests

        if self.testcode == 'C5':
            return tests + ['PP1', 'P1', 'P2', 'P3']
        
        return [self.testcode]
    
    @hybrid_property
    def tasks_in_progress(self):
        return self.get_tasks_in_progress()

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.id)
    
    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, *args, **kwargs)

        task = Task(id=rq_job.get_id(), name=name, description=description, test=self)
        db.session.add(task)

        try:
            db.session.commit()
        except:
            pass

        return task        

    def get_tasks_in_progress(self):
        return Task.query.filter_by(test=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, test=self, complete=False).first()