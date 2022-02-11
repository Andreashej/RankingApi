from app.models.RestMixin import RestMixin
from app import db
from sqlalchemy.orm import backref

class BaseMark(db.Model):
    __tablename__ = "marks"

    id = db.Column(db.Integer, primary_key=True)
    mark_type = db.Column(db.String(4)) # mark, flag or time

    judge_no = db.Column(db.Integer)
    judge_id = db.Column(db.String(12))

    result_id = db.Column(db.Integer, db.ForeignKey('results.id')) # if this is the parent, the mark is a judge mark
    section_mark_id = db.Column(db.Integer, db.ForeignKey('marks.id')) # if this is the parent, the mark is a section mark

    result = db.relationship("Result", back_populates="marks")

    section_marks = db.relationship("BaseMark", backref=backref("judge_mark", remote_side=[id]))

    red_card = db.Column(db.Boolean)
    yellow_card = db.Column(db.Boolean)
    blue_card = db.Column(db.Boolean)

    __mapper_args__ = { 'polymorphic_on': mark_type }

class Mark(BaseMark, RestMixin):
    __mapper_args__ = { 'polymorphic_identity': 'mark' }
    mark = db.Column(db.Float)

class Flag(BaseMark, RestMixin):
    __mapper_args__ = { 'polymorphic_identity': 'flag' }

    is_ok = db.Column(db.Boolean)

class Time(BaseMark, RestMixin):
    __mapper_args__ = { 'polymorphic_identity': 'time' }

    time = db.Column(db.Float)

