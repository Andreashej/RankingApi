import csv

from flask import current_app

from .. import db
from .TaskModel import Task

class RankingList(db.Model):
    __tablename__ = 'rankinglists'
    id = db.Column(db.Integer, primary_key=True)
    listname = db.Column(db.String(250))
    shortname = db.Column(db.String(3), unique=True)
    results_valid_days = db.Column(db.Integer)
    tests = db.relationship("RankingListTest", backref="rankinglist", lazy='dynamic', order_by="RankingListTest.testcode")
    branding_image = db.Column(db.String(250))
    tasks = db.relationship("Task", backref="rankinglist", lazy='dynamic')

    def __init__(self, name, shortname):
        self.listname = name
        self.shortname = shortname

    def import_competitions(self, filename):
        with open(current_app.config['ISIRANK_FILES'] + filename, mode='r', encoding="utf-8-sig") as csv_file:
            lines = csv.DictReader(csv_file)

            rq_job = current_app.task_queue.enqueue('app.tasks.import_competitions', self.id, list(lines))

            task = Task(id=rq_job.get_id(), name="import_competition", description="Import competitions to ranking " +  self.shortname, rankinglist=self)
            
            db.session.add(task)

            return task
    
    def import_results(self, filename):
        with open(current_app.config['ISIRANK_FILES'] +  filename, mode='r', encoding='utf-8-sig') as csv_file:
            lines = csv.DictReader(csv_file)

            rq_job = current_app.task_queue.enqueue('app.tasks.import_results', self.id, list(lines))

            task = Task(id=rq_job.get_id(), name="import_results", description="Import results to ranking " + self.shortname, rankinglist=self)
            
            db.session.add(task)

            return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(rankinglist=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, rankinglist=self, complete=False).first()