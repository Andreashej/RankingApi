from datetime import datetime, timedelta

from sqlalchemy.ext.hybrid import hybrid_property
from app.models.CompetitionModel import Competition
from app.models.TestModel import Test
from app.models.ResultModel import Result
from app import db, cache

from functools import reduce

from .RestMixin import RestMixin

rider_result = db.Table('rider_results', 
    db.Column('result_id', db.Integer, db.ForeignKey('results_cache.id', ondelete='CASCADE'), primary_key=True),
    db.Column('rider_id', db.Integer, db.ForeignKey('riders.id', ondelete='CASCADE'), primary_key=True),
)

horse_result = db.Table('horse_results',
    db.Column('result_id', db.ForeignKey('results_cache.id', ondelete='CASCADE'), primary_key=True),
    db.Column('horse_id', db.ForeignKey('horses.id', ondelete='CASCADE'), primary_key=True)
)

cached_results_based_on = db.Table('rank_result_marks',
    db.Column('result_id', db.ForeignKey('results_cache.id', ondelete='CASCADE'), primary_key=True),
    db.Column('competition_result_id', db.ForeignKey('results.id', ondelete='CASCADE'), primary_key=True)
)

class RankingResults(db.Model, RestMixin):
    RESOURCE_NAME = 'ranking_result'
    RESOURCE_NAME_PLURAL = 'ranking_results'

    INCLUDE_IN_JSON = ['rank']

    __tablename__ = 'results_cache'
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Float)
    
    test_id = db.Column(db.Integer, db.ForeignKey('rankinglist_tests.id'), nullable=False, index=True)

    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'), index=True)
    rider = db.relationship("Rider")

    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), index=True)
    horse = db.relationship("Horse")

    riders = db.relationship("Rider", secondary=rider_result, lazy='dynamic', backref=db.backref('ranking_results', lazy='dynamic'))
    horses = db.relationship("Horse", secondary=horse_result, lazy='dynamic', backref=db.backref('ranking_results', lazy='dynamic'))
    marks = db.relationship("Result", secondary=cached_results_based_on, lazy='dynamic')

    def __init__(self, test, results = []):
        self.test = test

        for result in results:
            self.add_result(result)
        
    @hybrid_property
    def rank(self):
        print (self.id)
        rank = self.test.ranks[self.id] if self.id in self.test.ranks else None
        return rank

    def add_result(self, result):
        self.marks.append(result)

        if result.rider not in self.riders:
            if self.test.grouping == 'rider':
                if self.riders.count() > 0: raise ValueError('Result cannot have marks with different riders when test is grouped by rider')
                self.rider_id = result.rider.id

            self.riders.append(result.rider)

        if result.horse not in self.horses:
            if self.test.grouping == 'horse':
                if self.horses.count() > 0: raise ValueError('Result cannot have marks with different horses when test is grouped by horse')
                self.horse_id = result.horse.id

            self.horses.append(result.horse)
            
    
    def calculate_mark(self):
        valid_marks_query = self.marks\
            .filter(Result.mark > self.test.min_mark)\
            .join(Result.test)\
            .join(Test.competition)\
            .filter(Competition.last_date >= (datetime.now() - timedelta(days=self.test.rankinglist.results_valid_days)))

        ordering = Result.mark if self.test.order == 'asc' else Result.mark.desc()

        valid_marks_query = valid_marks_query.order_by(ordering)

        valid_group_marks = None
        for testgroup in self.test.testgroups:
            q = valid_marks_query.filter(Test.testcode.in_(testgroup)).limit(self.test.included_marks)
            print (q.count(), self.test.included_marks)
            if q.count() < self.test.included_marks:
                self.mark = None
                return

            if valid_group_marks is None:
                valid_group_marks = q
            else:
                valid_group_marks.union(q)
        
        valid_marks = valid_group_marks.all()

        print (valid_marks)

        sum_of_marks = reduce(lambda sum, current: sum + current.get_mark(self.test.testcode == 'C5'), valid_marks, 0)

        self.mark = round(sum_of_marks / valid_group_marks.count(), self.test.rounding_precision)

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.id)

    @classmethod
    @cache.memoize(timeout=1440)
    def get_results(cls, test):
        from . import RankingListResultSchema
        
        if test.grouping == 'rider':
            results_schema = RankingListResultSchema(many=True, exclude=("horses",))

        elif test.grouping == 'horse':
            results_schema = RankingListResultSchema(many=True, exclude=("riders",))

        results = cls.query.filter_by(test_id = test.id).order_by(cls.rank.asc()).all()

        results = results_schema.dump(results)

        return results
    
    @classmethod
    def get_results_query(cls, test):
        return cls.query.filter_by(test_id = test.id).order_by(cls.rank.asc())