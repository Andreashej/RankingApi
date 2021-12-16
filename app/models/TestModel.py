from .. import db
from sqlalchemy.ext.hybrid import hybrid_property
from .ResultModel import Result
from .RestMixin import ApiErrorResponse, RestMixin

tests_rankinglists = db.Table('tests_ranking_association',
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'), primary_key=True),
    db.Column('rankinglist_id', db.Integer, db.ForeignKey('rankinglists.id'), primary_key=True)
)

class Test(db.Model, RestMixin):
    RESOURCE_NAME = 'test'
    RESOURCE_NAME_PLURAL = 'tests'

    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    rounding_precision = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    mark_type = db.Column(db.String(4), default='mark')
    _results = db.relationship('Result', backref='test', lazy='dynamic', cascade="all,delete")
    _include_in_ranking = db.relationship('RankingList', secondary=tests_rankinglists, lazy='dynamic')

    def __init__(self, testcode):
        self.testcode = testcode
    
    @hybrid_property
    def include_in_ranking(self):
        if self._include_in_ranking.count() > 0: 
            return self._include_in_ranking
        
        return self.competition.include_in_ranking

    @hybrid_property
    def results(self):
        query = self._results.join(Test)
        
        if self.order == 'asc':
            return query.filter(Result.mark > 0).order_by(Result.mark.asc())
        else:
            return query.order_by(Result.mark.desc())

    def add_result(self, rider, horse, mark, state = None, **kwargs):
    
        if (not kwargs.get('skip_check', False)):
            exists = Result.query.with_entities(Result.id).filter(Result.rider_id == rider.id, Result.horse_id == horse.id, Result.test_id==self.id).scalar()

            if exists:
                raise ApiErrorResponse("A combination cannot have more than one result per test", 400)

        result = Result(self, mark)
        result.rider = rider
        result.horse = horse

        if state is not None:
            result.state = state
        
        for rankinglist in self.include_in_ranking:
            rankinglist.propagate_result(result)

        return result
    
    @classmethod
    def create_from_catalog(cls, testcode):
        from ..models import TestCatalog

        test = cls(testcode)

        try:
            catalog = TestCatalog.get_by_testcode(testcode)

            test.rounding_precision = catalog.rounding_precision
            test.mark_type = catalog.mark_type
            test.order = catalog.order
        except:
            raise ValueError(f"Testcode {testcode} does not exist in catalog")

        return test
