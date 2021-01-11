from .. import db

from .RestMixin import RestMixin

class RiderAlias(db.Model, RestMixin):
    __tablename__ = 'rider_aliases'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(250), unique=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'))

    def __init__(self, alias):
        self.alias = alias