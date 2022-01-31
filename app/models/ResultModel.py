from app.models.TestEntryModel import TestEntry
from .. import db
from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

class Result(TestEntry):
    RESOURCE_NAME = 'result'
    RESOURCE_NAME_PLURAL = 'results'

    INCLUDE_IN_JSON = ['rank']

    rider_id = db.Column(db.Integer, db.ForeignKey('persons.id', ondelete='CASCADE'),nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id', ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    
    def __init__(self, test, mark, rider, horse, state = "VALID"):
        self.test = test
        self.mark = mark
        self.rider = rider
        self.horse = horse
        self.state = state
    
    @hybrid_property
    def rank(self):
        return self.test.ranks[self.id] if self.id in self.test.ranks else None

    def get_mark(self, convertTime = False):
        mark = None
        
        if convertTime and self.test.mark_type == 'time':
            if self.test.testcode == 'P1':
                mark = (32.50 - self.mark) / 1.25 
            
            if (self.test.testcode == 'P2'):
                mark = (12.00 - self.mark ) / 0.55
            
            if (self.test.testcode == 'P3'):
                mark = 22.00 - self.mark
            
            mark = max(min(mark, 10.00), 0.00)

        if mark == None:
            mark = self.mark

        return round(mark, self.test.rounding_precision)
    
    @classmethod
    def load_from_file(cls, filename):
        from ..models import Competition, Test, RankingList
        
        competition_id = filename.split('.')[0]
        competition = Competition.query.filter_by(isirank_id=competition_id).first()

        to_be_deleted = cls.query.join(cls.test).filter(Test.competition_id==competition.id).with_entities(cls.id)

        cls.query.filter(cls.id.in_(to_be_deleted)).delete(synchronize_session = False)
        
        task = None
        if competition is not None:
            task = competition.get_task_in_progress('import_competition')
        
        if task is not None:
            return task            
        else:
            file = open(current_app.config['ISIRANK_FILES'] + filename,"r",encoding="cp1252")

            contents = file.read()

            lines = contents.splitlines()

            if competition is None:
                raise Exception('Competition does not exist')

            task = competition.launch_task('import_competition', 'Importing competition ' + competition_id, lines)

            return task