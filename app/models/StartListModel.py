from app.models.TestEntryModel import TestEntry
from app import db

class StartListEntry(TestEntry):
    RESOURCE_NAME = 'startlist_entry'
    RESOURCE_NAME_PLURAL = 'startlist_entries'

    start_group = db.Column(db.Integer)

    test = db.relationship('Test', back_populates='startlist')