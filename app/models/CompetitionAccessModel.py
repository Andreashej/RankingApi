from .. import db
from .RestMixin import RestMixin

class CompetitionAccess(db.Model, RestMixin):
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    user = db.relationship('User')