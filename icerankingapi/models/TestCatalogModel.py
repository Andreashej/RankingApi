from icerankingapi import db

class TestCatalog(db.Model):
    __tablename__ = 'test_catalog'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3), unique=True, index=True)
    rounding_precision = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    mark_type = db.Column(db.String(4), default='mark')
    grouping = db.Column(db.String(5), default='rider')

    def __init__(self, testcode):
        self.testcode = testcode

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.testcode}"
    
    @classmethod
    def get_by_testcode(cls, testcode):
        test = cls.query.filter_by(testcode = testcode).first()

        if not test:
            raise Exception("Test not defined in catalog")

        return test
