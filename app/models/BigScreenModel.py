from .. import db
from .RestMixin import RestMixin
from uuid import uuid4

class BigScreen(db.Model, RestMixin):
    RESOURCE_NAME = 'bigscreen'
    RESOURCE_NAME_PLURAL = 'bigscreens'

    __tablename__ = 'screens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.String(50))
    role = db.Column(db.String(10), default="default")
    screen_group_id = db.Column(db.Integer, db.ForeignKey('screengroups.id'))
    screen_group = db.relationship("ScreenGroup")
    root_font_size = db.Column(db.String(20))

    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'))
    competition = db.relationship("Competition")