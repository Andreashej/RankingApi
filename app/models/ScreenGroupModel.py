from .. import db
from .RestMixin import RestMixin
from app import socketio

class ScreenGroup(db.Model, RestMixin):
    RESOURCE_NAME = 'screengroup'
    RESOURCE_NAME_PLURAL = 'screengroups'

    __tablename__ = 'screengroups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    template = db.Column(db.String(50))

    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    competition = db.relationship("Competition")

    screens = db.relationship("BigScreen")