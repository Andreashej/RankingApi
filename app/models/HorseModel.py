from app.models.ResultModel import Result
from app.models.TestModel import Test
from app.Responses import ApiErrorResponse
from app import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func, and_
import requests
from xml.etree import ElementTree
import re

from datetime import datetime, timedelta

from .RestMixin import RestMixin

class Horse(db.Model, RestMixin):
    RESOURCE_NAME = 'horse'
    RESOURCE_NAME_PLURAL = 'horses'

    INCLUDE_IN_JSON = ['number_of_results', 'testlist']

    __tablename__ = 'horses'
    id = db.Column(db.Integer, primary_key=True)
    feif_id = db.Column(db.String(12), unique=True)
    horse_name = db.Column(db.String(250))
    results = db.relationship("Result", back_populates="horse", lazy="dynamic")
    last_lookup = db.Column(db.DateTime)
    log_items = db.relationship("Log", back_populates="horse")
    lookup_error = db.Column(db.Boolean, default=False)

    def __init__(self, feif_id, name):
        self.feif_id = feif_id.upper()
        self.horse_name = name

    @hybrid_property
    def number_of_results(self):
        return self.results.count()
    
    @number_of_results.expression
    def number_of_results(cls):
        return db.session.query('results').filter_by(horse_id = cls.id).count()
    
    @hybrid_property
    def testlist(self):
        return map(
            lambda test_tuple: test_tuple[0],
            Result.query\
            .filter_by(horse_id=self.id)\
            .join(Result.test).order_by(Test.testcode)\
            .with_entities(Test.testcode)\
            .distinct()\
            .all()
        )
    
    @testlist.expression
    def testlist(cls):
        return db.session.query('results.horse_id, results.test_id').filter_by(horse_id = cls.id).join('tests').order_by('tests.testcode').distinct('tests.testcode')

    def get_results_for_ranking(self, test):
        from . import Result, Test, Competition, RankingList

        results_query = Result.query.filter_by(horse_id = self.id)

        if test.order == 'desc':
            results_query = results_query.filter(Result.mark >= test.min_mark)
        else:
            results_query = results_query.filter(Result.mark > 0)
        
        results_query = results_query.join(Test, Result.test_id == Test.id).filter_by(testcode=test.testcode)\
            .join(Competition).filter(Competition.last_date >= (datetime.now() - timedelta(days=test.rankinglist.results_valid_days)))\
            .join(RankingList, Competition.include_in_ranking).filter_by(shortname=test.rankinglist.shortname)\
        
        if test.order == 'desc':
            results_query = results_query.order_by(Result.mark.desc())
        else:
            results_query = results_query.order_by(Result.mark.asc())

        return results_query.limit(test.included_marks).all()

    def get_results(self, testcode, **kwargs):
        from ..models import Result, Test, Competition

        limit = kwargs.get('limit', None)

        return Result.query.filter_by(horse_id = self.id).join(Result.test).filter(Test.testcode == testcode).join(Test.competition).order_by(Competition.last_date.desc()).limit(limit).all()
    
    def get_best_result(self, testcode):
        from ..models import Result, Test, TestCatalog

        query = Result.query.filter_by(horse_id = self.id).join(Result.test).filter(Test.testcode == testcode)

        test = TestCatalog.query.filter_by(testcode = testcode).first()
        if test.order == 'asc':
            query = query.filter(Result.mark > 0).order_by(Result.mark.asc())
        else:
            query = query.order_by(Result.mark.desc())
        
        return query.first()
    
    def get_best_rank(self, testcode):
        from ..models import RankingResults, TestCatalog, RankingListTest
        
        query = RankingResults.query.filter(RankingResults.horses.contains(self)).join(RankingResults.test).filter(RankingListTest.testcode == testcode)

        test = TestCatalog.query.filter_by(testcode = testcode).first()
        if test.order == 'asc':
            query = query.order_by(RankingResults.mark.asc())
        else:
            query = query.order_by(RankingResults.mark.desc())

        return query.first()

    @hybrid_method
    def count_results_for_ranking(self, test):
        return len(list(
            filter(
                lambda result: (
                    result.test.testcode == test.testcode and
                    result.test.competition in test.rankinglist.competitions
                    ),
                self.results
            )
        ))
    
    @count_results_for_ranking.expression
    def count_results_for_ranking(cls, test):
        from ..models import Result, Test, Competition

        competition_ids = list(map(lambda comp: comp.id, test.rankinglist.competitions))

        query = db.session.query(func.count(Result.id)).filter_by(horse_id = cls.id)\

        if test.order == 'desc':
            query = query.filter(Result.mark >= test.min_mark)
        else:
            query = query.filter(Result.mark > 0)

        query = query\
            .join(Result.test).filter(Test.testcode == test.testcode)\
            .join(Test.competition).filter(
                and_(
                    Competition.id.in_(competition_ids), 
                    Competition.last_date >= (datetime.now() - timedelta(days=test.rankinglist.results_valid_days))
                )
            )

        return query.as_scalar()

    def wf_lookup(self, force_update = False):
        response = requests.get(f"https://www.worldfengur.com/bondiws/HorseInfo/?invoke=getHorseInfo&pUsername=DI_ws&pPassword=blEsi458&pHorseID={self.feif_id.upper()}", verify=False)


        response = ElementTree.fromstring(response.content).find("{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://is/bondi/webservices/fengur/WSFengur.wsdl}getHorseInfoResponse/return")

        if response is None:
            try:
                self.log(f'FEIF-ID {self.feif_id} does not exist')
                db.session.commit()
            except:
                db.session.rollback()
            finally:
                raise ApiErrorResponse(f'FEIF-ID {self.feif_id} does not exist')

        name = f"{response.find('name').text} {response.find('prefix').text} {response.find('origin').text}"
        horseID = response.find('horseID').text

        name_match = re.sub('[áðéíóúýþæöåäüßø]', '.+', response.find('name').text + " .{3,4} " + response.find('origin').text + '\s?I{0,}')

        match = re.match(name_match, self.horse_name)
        if not match:
            match = re.match(self.horse_name + '\s?I{0,}', name)
            isMatch = match.start() == 0 and match.end() == len(name) if match else False
        else:
            isMatch = match.start() == 0 and match.end() == len(self.horse_name)

        if isMatch or force_update:
            self.horse_name = name
            self.feif_id = horseID
            self.lookup_error = False
        else:
            self.log(f'Horse name "{self.horse_name}" does not match WorldFengur "{name}"')
            self.lookup_error = True
        
        self.last_lookup = datetime.utcnow()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    def log(self, message):
        from ..models import Log
        log = Log(message)
        log.horse = self

        db.session.add(log)

    def __repr__(self):
        return '<Horse {}>'.format(self.horse_name)