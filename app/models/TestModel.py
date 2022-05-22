
from sentry_sdk import capture_exception
from app.utils import cached_hybrid_property
from .. import db
from sqlalchemy.ext.hybrid import hybrid_property
from .ResultModel import Result
from .RestMixin import RestMixin
from sqlalchemy.sql.functions import rank
from app.models.TestSectionModel import TestSection
from sqlalchemy import case, func
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

tests_rankinglists = db.Table('tests_ranking_association',
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'), primary_key=True),
    db.Column('rankinglist_id', db.Integer, db.ForeignKey('rankinglists.id'), primary_key=True)
)

class Test(db.Model, RestMixin):
    RESOURCE_NAME = 'test'
    RESOURCE_NAME_PLURAL = 'tests'

    BLOCK_FROM_JSON = ['_test_name']
    INCLUDE_IN_JSON = ['test_name']

    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    _test_name = db.Column("test_name", db.String(20))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    rounding_precision = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    mark_type = db.Column(db.String(4), default='mark')

    _results = db.relationship('Result', back_populates='test', lazy='dynamic')
    startlist = db.relationship('StartListEntry', back_populates='test', lazy='dynamic', order_by='StartListEntry.start_group')
    include_in_ranking = db.relationship('RankingList', secondary=tests_rankinglists, lazy='dynamic')

    def __init__(self, testcode):
        self.testcode = testcode

    @hybrid_property
    def test_name(self):
        if self._test_name is None or self._test_name == '':
            return self.testcode
        
        return self._test_name

    @test_name.expression
    def test_name(self):
        return case(
            [
                (self._test_name == '', self.testcode),
                (self._test_name.is_(None), self.testcode)
            ], else_=self._test_name
        )
    
    @test_name.setter
    def test_name(self, test_name):
        self._test_name = test_name
    
    def add_rankinglist(self, ranking_list):
        if ranking_list not in self.include_in_ranking:
            self.include_in_ranking.append(ranking_list)
        
        if ranking_list not in self.competition.include_in_ranking:
            self.competition.include_in_ranking.append(ranking_list)
    
    def remove_rankinglist(self, ranking_list):
        self.include_in_ranking.remove(ranking_list)

        for test in self.competition.tests:
            if ranking_list in test.include_in_ranking:
                return
        
        self.competition.include_in_ranking.remove(ranking_list)

    @hybrid_property
    def results(self):
        query = self._results.join(Test)\
            .filter(Result.state != 'NOT STARTED')\
            .order_by(func.field(Result.state, "NOSHOW", "DISQ", "ELIM", "RESIGN", "PENDING", "VALID").desc())
        
        if self.order == 'asc':
            query = query.filter(Result.mark > 0).order_by(Result.mark.asc())
        else:
            query = query.order_by(Result.mark.desc())

        return query
    
    @cached_hybrid_property
    def ranks(self):
        ordering = Result.mark if self.order == 'asc' else Result.mark.desc()

        query = db.session.query(
            Result.id, 
            rank().over(
                partition_by=Result.test_id,
                order_by=ordering
            ).label('rank'))\
            .filter(Result.test_id==self.id, Result.mark > 0)\
            .filter(Result.state == 'VALID')

        return { id: rank for (id, rank) in query.all() }
    
    @hybrid_property
    def sections(self):
        return TestSection.query.filter_by(testcode=self.testcode).order_by(TestSection.section_no).all()

    def add_result(self, rider, horse, mark, *, state = None, sta = None, marks = None, phase=None, rider_class=None, updated_at=None, **kwargs):
        try:
            result = Result.query.filter_by(test_id=self.id, rider_id=rider.id, horse_id=horse.id, phase=phase).one()
            result.mark = mark
            result.state = state
        except NoResultFound:
            result = Result(self, mark, rider, horse, phase, state)
            result.created_at = updated_at
            db.session.add(result)

        result.rider_class = rider_class
        result.updated_at = updated_at

        result.sta = sta

        if marks is not None:
            result.marks = marks
        
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
    
    def add_icetest_result(self, result):
        from app.models import Person, Horse, JudgeMark
        try:
            rider = Person.find_by_name(result['RIDER'])
        except NoResultFound:
            rider = Person.create_by_name(result['RIDER'])
            db.session.add(rider)
        
        if 'BIRTHDAY' in result:
            birthday = result['BIRTHDAY']
            if hasattr(birthday, 'to_pydatetime'): birthday = birthday.to_pydatetime()

            rider.date_of_birth = datetime.strptime(birthday, "%Y-%m-%d")

        try:
            horse = Horse.query.filter_by(feif_id = result['FEIFID']).one()
        except NoResultFound:
            horse = Horse(result['FEIFID'], result['HORSE'])
            db.session.add(horse)

        marks = []
        if 'MARKS' in result:
            for mark_raw in result['MARKS']:
                try:
                    m = mark_raw['MARK']
                    judge_no = mark_raw['JUDGE']
                except KeyError:
                    m = mark_raw['mark']
                    judge_no = mark_raw['judge']

                mark = JudgeMark(mark = m, judge_no = int(judge_no), judge_id=mark_raw['JUDGEID'], mark_type="mark")

                # Find cards associated with this mark
                for card in result['CARDS']:
                    try:
                        card_judge = card['judge']
                    except KeyError:
                        card_judge = card['JUDGE']
                    
                    if card_judge != mark.judge_no:
                        continue

                    try:
                        card_color = card['color']
                    except KeyError:
                        card_color = card['COLOR']

                    mark.red_card = card_color == 'R'
                    mark.yellow_card = card_color == 'Y'
                    mark.blue_card = card_color == 'B'

                marks.append(mark)
        
        try:
            updated_at = datetime.fromtimestamp(result['TIMESTAMP'])
        except TypeError:
            if hasattr(result['TIMESTAMP'], 'to_pydatetime'): updated_at = result['TIMESTAMP'].to_pydatetime()

        return self.add_result(
            rider, 
            horse, 
            result['MARK'], 
            state=result['STATE'], 
            sta=result['STA'],
            marks=marks,
            phase=result['PHASE'],
            rider_class=result['CLASS'],
            updated_at=updated_at
        )