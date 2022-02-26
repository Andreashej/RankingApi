from app.models.RestMixin import RestMixin
from app import db
from sqlalchemy.orm import backref

class BaseMark(db.Model):
    __tablename__ = "marks"
    RESOURCE_NAME = "mark"
    RESOURCE_NAME_PLURAL = "marks"

    id = db.Column(db.Integer, primary_key=True)
    mark_type = db.Column(db.String(4)) # mark, flag or time
    type = db.Column(db.String(10), nullable=False)
    
    mark = db.Column(db.Float)
    flag_ok = db.Column(db.Boolean)

    judge_no = db.Column(db.Integer)
    judge_id = db.Column(db.String(12))

    red_card = db.Column(db.Boolean)
    yellow_card = db.Column(db.Boolean)
    blue_card = db.Column(db.Boolean)

    __mapper_args__ = { 'polymorphic_on': type }

class JudgeMark(BaseMark, RestMixin):
    __mapper_args__ = { 'polymorphic_identity': 'judge' }

    result_id = db.Column(db.Integer, db.ForeignKey('results.id'))
    
    result = db.relationship("Result", back_populates="marks")
    section_marks = db.relationship("SectionMark", lazy="dynamic")

class SectionMark(BaseMark, RestMixin):
    __mapper_args__ = { 'polymorphic_identity': 'section' }

    section_no = db.Column("section_no", db.Integer)

    judge_mark_id = db.Column("judge_mark_id", db.Integer, db.ForeignKey('marks.id'))
    

