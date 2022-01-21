from app.Responses import ApiErrorResponse
from .. import db

from .RestMixin import RestMixin

class PersonAlias(db.Model, RestMixin):
    RESOURCE_NAME = 'alias'
    RESOURCE_NAME_PLURAL = 'aliases'

    __tablename__ = 'person_aliases'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(250), unique=True)
    person_id = db.Column(db.Integer, db.ForeignKey('persons.id'))

    def __init__(self, alias):
        alias_exists = PersonAlias.query.with_entities(PersonAlias.id).filter_by(alias = alias).scalar()

        if alias_exists:
            raise ApiErrorResponse("An alias already exists with this name", 409)

        self.alias = alias