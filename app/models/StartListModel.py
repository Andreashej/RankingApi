from app.models.TestEntryModel import TestEntry
from app import db

class StartListEntry(TestEntry):
    phase = db.Column(db.String(4))
    start_group = db.Column(db.Integer)
    sta = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)