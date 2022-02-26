from .. import db

from .RestMixin import RestMixin

class TestEntry(db.Model, RestMixin):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(20), default="NOT STARTED")
    rider_id = db.Column(db.Integer, db.ForeignKey('persons.id', ondelete='CASCADE'),nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id', ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    sta = db.Column(db.Integer)
    color = db.Column(db.String(12))
    phase = db.Column(db.String(4))

    rider = db.relationship('Person')
    horse = db.relationship('Horse')
    test = db.relationship('Test', back_populates='_results')
    
    def __repr__(self):
        return '<Result {} {} {} >'.format(self.test.testcode, self.mark, self.rider.firstname)