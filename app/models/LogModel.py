from datetime import datetime
from .. import db
from .RestMixin import RestMixin
from datetime import datetime

class Log(db.Model, RestMixin):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'))
    horse = db.relationship("Horse", back_populates="log_items")

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f'<Log {self.text}>'