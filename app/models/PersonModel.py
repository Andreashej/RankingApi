import csv
from datetime import date

from app.Responses import ApiErrorResponse

from .. import db
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app

from .PersonAliasModel import PersonAlias
from .ResultModel import Result
from .TestModel import Test
from sqlalchemy.orm.exc import NoResultFound

from .RestMixin import RestMixin

class Person(db.Model, RestMixin):
    RESOURCE_NAME = 'person'
    RESOURCE_NAME_PLURAL = 'persons'

    INCLUDE_IN_JSON = ['fullname', 'email', 'number_of_results','age_group']
    EXCLUDE_FROM_JSON = ['_email', 'date_of_birth', 'age']

    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(250))
    lastname = db.Column(db.String(250))
    _email = db.Column('email', db.String(128), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_of_birth = db.Column(db.Date)
    user = db.relationship('User', back_populates='person')
    results = db.relationship("Result", back_populates="rider", lazy="dynamic")
    aliases = db.relationship("PersonAlias", backref="person", lazy="dynamic")

    def __init__(self, first, last):
        exists = Person.query.with_entities(Person.id).filter_by(fullname = first + " " + last).scalar()

        if exists:
            raise Exception("A person with that name already exists")

        alias = PersonAlias.query.with_entities(PersonAlias.id).filter_by(alias = first + " " + last).scalar()

        if alias:
            raise Exception("A person alias already exists with this name")

        self.firstname = first
        self.lastname = last

    @hybrid_property
    def fullname(self):
        return self.firstname + ' ' + self.lastname
    
    @hybrid_property
    def email(self):
        if current_app.config['DEBUG'] and self._email:
            return "andreas@hejndorf-foto.dk"
        return self._email
    
    @email.setter
    def email(self, email):
        if '@' not in email and '.' not in email:
            raise ValueError('An email address must contain both @ and .')
        
        self._email = email
    
    @email.expression
    def email(cls):
        return cls._email
    
    @hybrid_property
    def age(self):
        if self.date_of_birth is None:
            return None
        return date.today().year - self.date_of_birth.year

    @hybrid_property
    def age_group(self):
        if self.age < 16:
            return 'Junior'
        if self.age < 22:
            return 'Young Rider'
        return 'Senior'

    @hybrid_property
    def number_of_results(self):
        return self.results.count()

    @number_of_results.expression
    def number_of_results(cls):
        return db.session.query('results').filter_by(rider_id = cls.id).count()

    @hybrid_property
    def testlist(self):
        return map(
            lambda test_tuple: test_tuple[0],
            Result.query\
            .filter_by(rider_id=self.id)\
            .join(Result.test).order_by(Test.testcode)\
            .with_entities(Test.testcode)\
            .distinct()\
            .all()
        )

    @testlist.expression
    def testlist(cls):
        return db.session.query('results.rider_id, results.test_id').filter_by(rider_id = cls.id).join('tests').order_by('tests.testcode').distinct('tests.testcode')

    # def get_results(self, testcode, **kwargs):
    #     from . import Result, Test, Competition

    #     limit = kwargs.get('limit', None)

    #     return Result.query.filter_by(rider_id = self.id).join(Result.test).filter(Test.testcode == testcode).join(Test.competition).order_by(Competition.last_date.desc()).limit(limit).all()
    
    # def get_best_result(self, testcode):
    #     from . import Result, Test, TestCatalog

    #     query = Result.query.filter_by(rider_id = self.id).join(Result.test).filter(Test.testcode == testcode)

    #     test = TestCatalog.query.filter_by(testcode = testcode).first()
    #     if test.order == 'asc':
    #         query = query.filter(Result.mark > 0).order_by(Result.mark.asc())
    #     else:
    #         query = query.order_by(Result.mark.desc())
        
    #     return query.first()
    
    # def get_best_rank(self, testcode):
    #     from . import RankingResults, TestCatalog, RankingListTest
    #     query = RankingResults.query.filter(RankingResults.riders.contains(self)).join(RankingResults.test).filter(RankingListTest.testcode == testcode)

    #     test = TestCatalog.query.filter_by(testcode = testcode).first()
    #     if test.order == 'asc':
    #         query = query.order_by(RankingResults.mark.asc())
    #     else:
    #         query = query.order_by(RankingResults.mark.desc())

    #     return query.first()

    # def get_results_for_ranking(self, test):
    #     from . import Result, Test, Competition, RankingList

    #     results_query = Result.query.filter_by(rider_id = self.id)

    #     # if test.order == 'desc':
    #     #     results_query = results_query.filter(Result.mark >= test.min_mark)
    #     # else:
    #     #     results_query = results_query.filter(Result.mark > 0)

    #     results_query = results_query.join(Test, Result.test_id == Test.id)

    #     queries = {}
    #     if test.testcode == 'C4' or test.testcode == 'C5':
    #         queries['tolt'] = results_query.filter((Test.testcode == 'T1') | (Test.testcode == 'T2'))

    #         if (test.testcode == 'C4'):
    #             queries['gait'] = results_query.filter(Test.testcode == 'V1')

    #         if (test.testcode == 'C5'):
    #             queries['gait'] = results_query.filter(Test.testcode == 'F1')
    #             queries['pace'] = results_query.filter((Test.testcode == 'PP1') | (Test.testcode == 'P1') | (Test.testcode == 'P2') | (Test.testcode == 'P3'))
    #     else:
    #         queries['all'] = results_query.filter_by(testcode=test.testcode)

    #     query = None
        
    #     for key in queries:
    #         queries[key] = queries[key].join(RankingList, Test.include_in_ranking).filter_by(shortname=test.rankinglist.shortname)
    #         if query is None:
    #             query = queries[key]
    #         else:
    #             query.union(query[key])
    #         # queries[key] = queries[key]\
    #         #     .join(Competition).filter(Competition.last_date >= (datetime.now() - timedelta(days=test.rankinglist.results_valid_days)))\
    #         #     .join(RankingList, Competition.include_in_ranking).filter_by(shortname=test.rankinglist.shortname)

    #         # if test.order == 'desc':
    #         #     queries[key] = queries[key].order_by(Result.mark.desc())
    #         # else:
    #         #     queries[key] = queries[key].order_by(Result.mark.asc())

    #         # queries[key] = queries[key].all()

    #         # for result in queries[key]:
    #         #     results.append(result)
        
    #     return query.all()
    
    # @hybrid_method
    # def count_results_for_ranking(self, test):
    #     return len(list(
    #         filter(
    #             lambda result: (
    #                 result.test.testcode in result.test.included_tests and
    #                 result.test.competition in test.rankinglist.competitions
    #                 ),
    #             self.results
    #         )
    #     ))

    # @count_results_for_ranking.expression
    # def count_results_for_ranking(cls, test):
    #     from . import Result, Test, Competition

    #     competition_ids = list(map(lambda comp: comp.id, test.rankinglist.competitions))

    #     query = db.session.query(func.count(Result.id)).filter_by(rider_id = cls.id)\

    #     if test.order == 'desc':
    #         query = query.filter(Result.mark >= test.min_mark)
    #     else:
    #         query = query.filter(Result.mark > 0)

    #     query = query\
    #         .join(Result.test).filter(Test.testcode.in_(test.included_tests))\
    #         .join(Test.competition).filter(
    #             and_(
    #                 Competition.id.in_(competition_ids), 
    #                 Competition.last_date >= (datetime.now() - timedelta(days=test.rankinglist.results_valid_days))
    #             )
    #         )
    #     return query.as_scalar()
    
    def add_alias(self, alias_name = None, person_id = None):
        alias = None

        if alias_name:
            existing = Person.find_by_name(alias_name)
            if existing:
                raise ApiErrorResponse(f'Cannot create alias that already exists for person {existing.fullname} (ID: {existing.id}). Merge the riders instead by including an ID to merge from in the request body.', 409)
            
            alias = PersonAlias(alias_name)

            self.aliases.append(alias)
        
        elif person_id:
            merge = Person.query.get(person_id)

            if not merge:
                raise ApiErrorResponse(f'Could not find person with ID {person_id} to merge from.', 404)
            
            alias = PersonAlias(merge.fullname)
            self.aliases.append(alias)

            for result in merge.results:
                result.rider_id = self.id
        
        if alias is None:
            raise ApiErrorResponse("You must provide either an alias name or person ID to merge.", 400)
        return alias

    def __repr__(self):
        return '<Person {} {}>'.format(self.firstname, self.lastname)

    @staticmethod
    def import_aliases(filename):
        from . import Task
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
        
        rider = cls.query.join(Person.aliases, aliased = True).filter_by(alias = name).first()

        if rider:
            return rider

        raise NoResultFound