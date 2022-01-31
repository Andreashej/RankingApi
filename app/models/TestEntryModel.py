from .. import db
from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from .RestMixin import RestMixin

class TestEntry(db.Model, RestMixin):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(20), default="NOT STARTED")
    rider_id = db.Column(db.Integer, db.ForeignKey('persons.id', ondelete='CASCADE'),nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id', ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    # phase = db.Column(db.String(4))
    # start_group = db.Column(db.Integer)
    # sta = db.Column(db.Integer)
    # timestamp = db.Column(db.DateTime)
    
    def __repr__(self):
        return '<Result {} {} {} >'.format(self.test.testcode, self.mark, self.rider.firstname)