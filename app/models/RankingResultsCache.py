from .. import db, cache

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

class RankingResultsCache(db.Model, RestMixin):
    __tablename__ = 'results_cache'
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer)
    mark = db.Column(db.Float)
    
    test_id = db.Column(db.Integer, db.ForeignKey('rankinglist_tests.id'), nullable=False, index=True)
    riders = db.relationship("Rider", secondary=rider_result, lazy='dynamic', backref=db.backref('ranking_results', lazy='dynamic'))
    horses = db.relationship("Horse", secondary=horse_result, lazy='dynamic', backref=db.backref('ranking_results', lazy='dynamic'))
    marks = db.relationship("Result", secondary=cached_results_based_on, lazy='dynamic')

    def __init__(self, results, test):
        testcount = 2 if test.testcode == 'C4' else 3 if test.testcode == 'C5' else 1

        if len(results) < test.included_marks * testcount:
            raise Exception("Not enough marks to generate result")

        final_mark = 0
        self.test_id = test.id

        for result in results:
            final_mark += result.get_mark(test.testcode == 'C5')
            
            if result.rider not in self.riders:
                self.riders.append(result.rider)

            if result.horse not in self.horses:
                self.horses.append(result.horse)

            self.marks.append(result)
        
        self.mark = round(final_mark / len(results), test.rounding_precision)
        

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