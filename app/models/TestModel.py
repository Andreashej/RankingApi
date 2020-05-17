from app import db

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    rounding_precision = db.Column(db.Integer, default=2)
    results = db.relationship('Result', backref='test', lazy="joined")

    def __init__(self, testcode):
        self.testcode = testcode