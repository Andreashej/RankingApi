from marshmallow import fields
from .. import db
from flask import current_app

from .RestMixin import RestMixin

class Result(db.Model, RestMixin):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Float)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id', ondelete='CASCADE'),nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id', ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    
    def __init__(self, test, mark):
        self.test = test
        self.mark = mark
    
    def __repr__(self):
        return '<Result {} {} {} >'.format(self.test.testcode, self.mark, self.rider.firstname)

    def get_mark(self):
        mark = None

        if self.test.mark_type == 'time':
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
    
    @staticmethod
    def load_from_file(filename):
        from ..models import Competition, Test, RankingList
        
        competition_id = filename.split('.')[0]
        competition = Competition.query.filter_by(isirank_id=competition_id).first()
        
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
                competition = Competition('', None, None, competition_id)

                if competition_id[2] == "2" or competition_id[2] == "3":
                    rsn = 'DRL'
                
                ranking = RankingList.query.filter_by(shortname=rsn).first()
                competition.include_in_ranking.append(ranking)
                db.session.add(competition)
            else:
                tests = Test.query.filter_by(competition=competition).all()
                for test in tests:
                    Result.query.filter_by(test=test).delete()
                    db.session.delete(test)
            
            db.session.commit()

            task = competition.launch_task('import_competition', 'Importing competition ' + competition_id, lines)
            db.session.commit()

            return task