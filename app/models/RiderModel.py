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


    def __init__(self, first, last):
        self.firstname = first
        self.lastname = last
    
    def __repr__(self):
        return '<Rider {} {}>'.format(self.firstname, self.lastname)