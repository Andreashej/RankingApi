from marshmallow import fields
from app import db

class RankingList(db.Model):
    __tablename__ = 'rankinglists'
    id = db.Column(db.Integer, primary_key=True)
    listname = db.Column(db.String(250))
    shortname = db.Column(db.String(3), unique=True)
    results_valid_days = db.Column(db.Integer)
    tests = db.relationship("RankingListTest", backref="rankinglist", lazy='dynamic', order_by="RankingListTest.testcode")
    branding_image = db.Column(db.String(250))

    def __init__(self, name, shortname):
        self.listname = name
        self.shortname = shortname