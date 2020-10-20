from marshmallow import fields
from app import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import desc, func, and_
from flask import current_app

from datetime import datetime, timedelta

class Rider(db.Model):
    __tablename__ = 'riders'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(250))
    lastname = db.Column(db.String(250))
    results = db.relationship("Result", backref="rider", lazy="joined")

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
        t =[result.test.testcode for result in self.results]
        return set(t)
    
    @testlist.expression
    def testlist(cls):
        return db.session.query('results.rider_id, results.test_id').filter_by(rider_id = cls.id).join('tests').distinct('tests.testcode')

    def get_results(self, testcode, **kwargs):
        from app.models import Result, Test, Competition

        limit = kwargs.get('limit', None)

        return Result.query.filter_by(rider_id = self.id).join(Result.test).filter(Test.testcode == testcode).join(Test.competition).order_by(Competition.last_date.desc()).limit(limit).all()
    
    def get_best_result(self, testcode):
        from app.models import Result, Test, Competition

        return Result.query.filter_by(rider_id = self.id).join(Result.test).filter(Test.testcode == testcode).order_by(Result.mark.desc()).first()

    def get_results_for_ranking(self, test):
        from app.models import Result, Test, Competition, RankingList

        results_query = Result.query.filter_by(rider_id = self.id)

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
        from app.models import Result, Test, Competition

        competition_ids = list(map(lambda comp: comp.id, test.rankinglist.competitions))

        query = db.session.query(func.count(Result.id)).filter_by(rider_id = cls.id)\

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

    def __init__(self, first, last):
        self.firstname = first
        self.lastname = last
    
    def __repr__(self):
        return '<Rider {} {}>'.format(self.firstname, self.lastname)