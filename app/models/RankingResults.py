import functools
from flask.globals import g
from flask.json import load
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.ResultModel import Result
from app import db, cache

from functools import reduce

from .RestMixin import ApiErrorResponse, RestMixin

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
    __tablename__ = 'results_cache'
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer)
    mark = db.Column(db.Float)
    
    test_id = db.Column(db.Integer, db.ForeignKey('rankinglist_tests.id'), nullable=False, index=True)
    riders = db.relationship("Rider", secondary=rider_result, lazy='dynamic', backref=db.backref('ranking_results', lazy='dynamic'))
    horses = db.relationship("Horse", secondary=horse_result, lazy='dynamic', backref=db.backref('ranking_results', lazy='dynamic'))
    marks = db.relationship("Result", secondary=cached_results_based_on, lazy='dynamic')

    def __init__(self, test, results = []):
        self.test = test

        for result in results:
            self.add_result(result)

    def add_result(self, result):
        self.marks.append(result)

        if result.rider not in self.riders:
            self.riders.append(result.rider)

        if result.horse not in self.horses:
            self.horses.append(result.horse)
    
    def calculate_mark(self):
        testcount = 2 if self.test.testcode == 'C4' else 3 if self.test.testcode == 'C5' else 1

        number_of_marks = self.test.included_marks * testcount

        if self.marks.count() < self.test.included_marks * testcount:
            self.mark = None
            self.rank = None
            return
        
        valid_marks_query = self.marks


        if self.test.order == 'asc':
            valid_marks_query = valid_marks_query.order_by(Result.mark).limit(number_of_marks)
        else:
            valid_marks_query = valid_marks_query.order_by(Result.mark.desc()).limit(number_of_marks)
        
        valid_marks = valid_marks_query.all()

        sum_of_marks = reduce(lambda sum, current: sum + current.get_mark(self.test.testcode == 'C5'), valid_marks, 0)

        self.mark = round(sum_of_marks / number_of_marks, self.test.rounding_precision)
        

    @hybrid_property
    def rider(self):
        if self.test.grouping == 'rider':
            return self.riders[0]
        
        return None
    
    @hybrid_property
    def horse(self):
        if self.test.grouping == 'horse':
            return self.horses[0]
        
        return None

    def __repr__(self):
        return "<{}.{}>".format(self.__class__.__name__, self.id)

    @classmethod
    @cache.memoize(timeout=1440)
    def get_results(cls, test):
        from ..models import RankingListResultSchema
        
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

def use_ranking_result(func):
    """Load ranking to global flask variable"""
    functools.wraps(func)

    def load_ranking_result(*args, **kwargs):
        ranking_result_id = kwargs.get("result_id")

        if not ranking_result_id:
            return ApiErrorResponse("No ranking with ID found in request", 400).response()

        try:
            g.ranking_result = RankingResults.load_one(ranking_result_id)
        except ApiErrorResponse as e:
            return e.response()

        return func(*args, **kwargs)
    
    return load_ranking_result

def use_ranking_results(func):
    """Load rankings to global flask variable"""
    functools.wraps(func)

    def load_ranking_results(*args, **kwargs):
        try:
            g.ranking_results = RankingResults.load_many()
        except ApiErrorResponse as e:
            return e.response()
        
        return func(*args, **kwargs)
    
    return load_ranking_results