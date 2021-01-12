import csv

from flask import current_app
from flask_migrate import current
from sqlalchemy.ext.hybrid import hybrid_property

from .. import db
from .TaskModel import Task

from .RestMixin import RestMixin

class RankingList(db.Model, RestMixin):
    __tablename__ = 'rankinglists'
    id = db.Column(db.Integer, primary_key=True)
    listname = db.Column(db.String(250))
    shortname = db.Column(db.String(3), unique=True)
    results_valid_days = db.Column(db.Integer)
    tests = db.relationship("RankingListTest", backref="rankinglist", lazy='dynamic', order_by="RankingListTest.testcode", cascade="all,delete")
    branding_image = db.Column(db.String(250))
    tasks = db.relationship("Task", backref="rankinglist", lazy='dynamic', cascade="all,delete")

    def __init__(self, name, shortname):
        self.listname = name
        self.shortname = shortname

    @hybrid_property
    def logo(self):
        if self.branding_image:
            return '//' + current_app.config['SERVER_NAME'] + '/images/' + self.branding_image
        
        # return '//' + current_app.config['SERVER_NAME'] + '/images/default.png'
        return 'https://via.placeholder.com/150'

    def import_competitions(self, filename):
        with open(current_app.config['ISIRANK_FILES'] + filename, mode='r', encoding="utf-8-sig") as csv_file:
            lines = csv.DictReader(csv_file)

            rq_job = current_app.task_queue.enqueue('app.tasks.import_competitions', self.id, list(lines))

            task = Task(id=rq_job.get_id(), name="import_competition", description="Import competitions to ranking " +  self.shortname, rankinglist=self)
            
            db.session.add(task)

            return task
    
    def import_results(self, filename, filter=None):
        from ..models import Competition
        with open(current_app.config['ISIRANK_FILES'] +  filename, mode='r', encoding='utf-8-sig') as csv_file:

            lines = csv.DictReader(csv_file)
            tasks = []

            current_competition = ''
            current_competition_results = []
            for line in lines:
                if not current_competition:
                    current_competition = line['competition_id']

                if current_competition != line['competition_id']:
                    competition = Competition.query.filter_by(isirank_id = current_competition).first()

                    if not competition:
                        print (f"Competition {current_competition} does not exist")
                        continue

                    current_competition_results.append("[END]")

                    if (filter and current_competition in filter) or not filter:
                        print(current_competition)
                        task = competition.launch_task('import_competition', 'Importing competition ' + current_competition, current_competition_results)

                        try:
                            db.session.commit()
                            tasks.append(task)
                        except:
                            print ("Database error")

                    current_competition = line['competition_id']
                    current_competition_results = []
                    
                current_competition_results.append(f"{line['rider']}\t{line['testcode']}\t{line['mark']}\t{line['feif_id']}\t{line['horse']}")

            return tasks

    def get_tasks_in_progress(self):
        return Task.query.filter_by(rankinglist=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, rankinglist=self, complete=False).first()