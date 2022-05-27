from .. import db
from .RestMixin import RestMixin

class ScreenGroup(db.Model, RestMixin):
    RESOURCE_NAME = 'screengroup'
    RESOURCE_NAME_PLURAL = 'screengroups'

    __tablename__ = 'screengroups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    template = db.Column(db.String(50))
    name = db.Column(db.String(50))
    show_osd = db.Column(db.Boolean)

    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    competition = db.relationship("Competition")

    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=True)
    test = db.relationship("Test")

    screens = db.relationship("BigScreen")
    routes = db.relationship('BigScreenRoute', back_populates="screen_group")