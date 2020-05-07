from marshmallow import fields
from app import db

class Horse(db.Model):
    __tablename__ = 'horses'
    id = db.Column(db.Integer, primary_key=True)
    feif_id = db.Column(db.String(12), unique=True)
    horse_name = db.Column(db.String(250))
    results = db.relationship("Result", backref="horse", lazy="joined")

    def __init__(self, feif_id, name):
        self.feif_id = feif_id
        self.horse_name = name
    
    def __repr__(self):
        return '<Horse {}>'.format(self.horse_name)