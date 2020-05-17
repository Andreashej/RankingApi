from marshmallow import fields
from app import db
from sqlalchemy.ext.hybrid import hybrid_property
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
        return db.session.query('results.rider_id, results.test_id').filter_by(rider_id = cls.id).join('tests').distinct()

    def __init__(self, first, last):
        self.firstname = first
        self.lastname = last
    
    def __repr__(self):
        return '<Rider {} {}>'.format(self.firstname, self.lastname)