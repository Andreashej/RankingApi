import csv

from marshmallow import fields
from .. import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import desc, func, and_
from flask import current_app

from datetime import datetime, timedelta

from .RiderAliasModel import RiderAlias

from .RestMixin import RestMixin

class Rider(db.Model, RestMixin):
    __tablename__ = 'riders'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(250))
    lastname = db.Column(db.String(250))
    results = db.relationship("Result", backref="rider", lazy="joined")
    aliases = db.relationship("RiderAlias", backref="rider", lazy="dynamic")

    def __init__(self, first, last):
        exists = Rider.query.with_entities(Rider.id).filter_by(fullname = first + " " + last).scalar()

        if exists:
            raise Exception("A rider with that name already exists")

        alias = RiderAlias.query.with_entities(RiderAlias.id).filter_by(alias = first + " " + last).scalar()

        if alias:
            raise Exception("A rider alias already exists with this name")

        self.firstname = first
        self.lastname = last

    @hybrid_property
    def fullname(self):
        return self.firstname + ' ' + self.lastname

    @hybrid_property
    def number_of_results(self):
        return len(self.results)

    @number_of_results.expression
    def number_of_results(cls):
        return db.session.query('results').filter_by(rider_id = cls.id).count()

    @hybrid_property
    def testlist(self):
        t = []
        for result in self.results:
            if result.test.testcode in t:
                continue

            t.append(result.test.testcode)
        t.sort()
        return t
    
    @testlist.expression
    def testlist(cls):
        return db.session.query('results.rider_id, results.test_id').filter_by(rider_id = cls.id).join('tests').order_by('tests.testcode').distinct('tests.testcode')

    def get_results(self, testcode, **kwargs):
        from ..models import Result, Test, Competition

        limit = kwargs.get('limit', None)

        return Result.query.filter_by(rider_id = self.id).join(Result.test).filter(Test.testcode == testcode).join(Test.competition).order_by(Competition.last_date.desc()).limit(limit).all()
    
    def get_best_result(self, testcode):
        from ..models import Result, Test, Competition, TestCatalog

        query = Result.query.filter_by(rider_id = self.id).join(Result.test).filter(Test.testcode == testcode)

        test = TestCatalog.query.filter_by(testcode = testcode).first()
        if test.order == 'asc':
            query = query.filter(Result.mark > 0).order_by(Result.mark.asc())
        else:
            query = query.order_by(Result.mark.desc())
        
        return query.first()
    
    def get_best_rank(self, testcode):
        from ..models import RankingResultsCache, TestCatalog, RankingListTest
        query = RankingResultsCache.query.filter(RankingResultsCache.riders.contains(self)).join(RankingResultsCache.test).filter(RankingListTest.testcode == testcode)

        test = TestCatalog.query.filter_by(testcode = testcode).first()
        if test.order == 'asc':
            query = query.order_by(RankingResultsCache.mark.asc())
        else:
            query = query.order_by(RankingResultsCache.mark.desc())

        return query.first()

    def get_results_for_ranking(self, test):
        from ..models import Result, Test, Competition, RankingList

        results_query = Result.query.filter_by(rider_id = self.id)

        if test.order == 'desc':
            results_query = results_query.filter(Result.mark >= test.min_mark)
        else:
            results_query = results_query.filter(Result.mark > 0)

        results_query = results_query.join(Test, Result.test_id == Test.id)

        queries = {}
        if test.testcode == 'C4' or test.testcode == 'C5':
            queries['tolt'] = results_query.filter((Test.testcode == 'T1') | (Test.testcode == 'T2'))

            queries['gait'] = results_query.filter((Test.testcode == 'V1') | (Test.testcode == 'F1'))

            if (test.testcode == 'C5'):
                queries['pace'] = results_query.filter((Test.testcode == 'PP1') | (Test.testcode == 'P1') | (Test.testcode == 'P2') | (Test.testcode == 'P3'))
        else:
            queries['all'] = results_query.filter_by(testcode=test.testcode)

        results = list()
        
        for key in queries:
            queries[key] = queries[key]\
                .join(Competition).filter(Competition.last_date >= (datetime.now() - timedelta(days=test.rankinglist.results_valid_days)))\
                .join(RankingList, Competition.include_in_ranking).filter_by(shortname=test.rankinglist.shortname)

            if test.order == 'desc':
                queries[key] = queries[key].order_by(Result.mark.desc())
            else:
                queries[key] = queries[key].order_by(Result.mark.asc())

            queries[key] = queries[key].limit(test.included_marks).all()

            for result in queries[key]:
                results.append(result)
        
        return results
    
    @hybrid_method
    def count_results_for_ranking(self, test):
        return len(list(
            filter(
                lambda result: (
                    result.test.testcode in result.test.included_tests and
                    result.test.competition in test.rankinglist.competitions
                    ),
                self.results
            )
        ))

    @count_results_for_ranking.expression
    def count_results_for_ranking(cls, test):
        from ..models import Result, Test, Competition

        competition_ids = list(map(lambda comp: comp.id, test.rankinglist.competitions))

        query = db.session.query(func.count(Result.id)).filter_by(rider_id = cls.id)\

        if test.order == 'desc':
            query = query.filter(Result.mark >= test.min_mark)
        else:
            query = query.filter(Result.mark > 0)

        query = query\
            .join(Result.test).filter(Test.testcode.in_(test.included_tests))\
            .join(Test.competition).filter(
                and_(
                    Competition.id.in_(competition_ids), 
                    Competition.last_date >= (datetime.now() - timedelta(days=test.rankinglist.results_valid_days))
                )
            )
        return query.as_scalar()
    
    def add_alias(self, alias):
        self.aliases.append(alias)

    def __repr__(self):
        return '<Rider {} {}>'.format(self.firstname, self.lastname)

    @staticmethod
    def import_aliases(filename):
        from ..models import Task
        with open(current_app.config['ISIRANK_FILES'] + filename, mode='r', encoding="utf-8-sig") as csv_file:
            lines = csv.DictReader(csv_file)

            rq_job = current_app.task_queue.enqueue('app.tasks.import_aliases', list(lines))

            task = Task(id=rq_job.get_id(), name="import_aliases", description="Import rider aliases")

            db.session.add(task)

            return task

    @classmethod
    def create_by_name(cls, name):
        (fname, sep, lname) = name.rpartition(' ')
        rider = cls(fname, lname)

        return rider
    
    @classmethod
    def find_by_name(cls, name):
        rider = cls.query.filter_by(fullname = name).first()

        if rider:
            return rider
        
        rider = cls.query.join(Rider.aliases, aliased = True).filter_by(alias = name).first()

        if rider:
            return rider

        return None