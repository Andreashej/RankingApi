from .. import db
from sqlalchemy.ext.hybrid import hybrid_property
from . import Result

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    rounding_precision = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    _results = db.relationship('Result', backref='test', lazy='dynamic')

    def __init__(self, testcode):
        self.testcode = testcode

    @hybrid_property
    def results(self):
        query = self._results.join(Test)
        
        if self.order == 'asc':
            return query.filter(Result.mark > 0).order_by(Result.mark.asc())
        else:
            return query.order_by(Result.mark.desc())
