from app import db
from app.models.RestMixin import RestMixin

class TestSection(db.Model, RestMixin):
    __tablename__ = "test_sections"

    testcode = db.Column(db.String(5), primary_key=True)
    section_no = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(50), nullable=False)