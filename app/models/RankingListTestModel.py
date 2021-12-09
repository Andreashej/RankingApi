from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import rank
from app.models.TestModel import Test
from app.models.CompetitionModel import Competition
from app.models.RankingResults import rider_result, horse_result, RankingResults
from app.models.ResultModel import Result
from .. import db

from flask import current_app

from .TaskModel import Task

from .RestMixin import RestMixin

class RankingListTest(db.Model, RestMixin):
    __tablename__ = 'rankinglist_tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    rankinglist_id = db.Column(db.Integer, db.ForeignKey('rankinglists.id', ondelete="CASCADE"), nullable=False)
    included_marks = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    grouping = db.Column(db.String(5), default='rider')
    min_mark = db.Column(db.Float)
    rounding_precision = db.Column(db.Integer)
    mark_type = db.Column(db.String(4), default='mark') # Allowed values: {mark, time, comb}
    tasks = db.relationship("Task", backref="test", lazy='dynamic', cascade="all, delete")

    ranking_results_cached = db.relationship("RankingResults", backref="test", lazy="joined", order_by="RankingResults.rank")

    @hybrid_property
    def included_tests(self):
        if self.testcode == 'C4':
            return ['T1', 'T2', 'V1']

        if self.testcode == 'C5':
            return ['T1', 'T2', 'F1', 'PP1', 'P1', 'P2', 'P3']
        
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
            db.session.rollback()

        return task        

    def get_tasks_in_progress(self):
        return Task.query.filter_by(test=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, test=self, complete=False).first()
    
    def register_result(self, result):
        ranking_result = None

        if self.grouping == 'rider':
            try:
                ranking_result = RankingResults.query\
                    .filter(RankingResults.test_id==self.id)\
                    .join(rider_result, RankingResults.id==rider_result.c.result_id)\
                    .filter(rider_result.c.rider_id==result.rider_id)\
                    .one()
            except NoResultFound as e:
                ranking_result = RankingResults(self)
            
        elif self.grouping == 'horse':
            try:
                ranking_result = db.session.query(horse_result)\
                    .filter(horse_result.c.horse_id==result.horse_id)\
                    .join(RankingResults, RankingResults.id==horse_result.c.result_id)\
                    .filter(RankingResults.test_id==self.id)\
                    .one()
            except NoResultFound as e:
                ranking_result = RankingResults(self)
        
        ranking_result.add_result(result)
        ranking_result.calculate_mark()
        db.session.add(ranking_result)

        self.compute_rank()


    def compute_rank(self):
        ordering = RankingResults.mark if self.order == 'asc' else RankingResults.mark.desc()

        ranked_results = RankingResults.query.with_entities(
            RankingResults.id, 
            rank().over(
                partition_by=RankingResults.test_id,
                order_by=ordering
            ))\
            .filter(RankingResults.test_id==self.id)\
            .all()

        mappings = [{ 'id': result[0], 'rank': result[1] } for result in ranked_results]
        db.session.bulk_update_mappings(RankingResults, mappings)
        db.session.commit()
    
    @hybrid_method
    def result_is_valid(self, result):
        return result.test.competition.last_date >= (datetime.now() -  timedelta(days=self.rankinglist.results_valid_days))
    
    @result_is_valid.expression
    def result_is_valid(cls, Result):
        Result.query.filter()
    
    @hybrid_property
    def valid_competition_results(self):
        results = Result.query.join(Result.test).filter(Test.testcode==self.testcode)\
            .filter(Test.competition.last_date >= (datetime.now() - timedelta(days=self.rankinglist.results_valid_days)),
                Result.test.competition.rankinglist.shortname == self.rankinglist.shortname
            )\
            .all()
        print(results)