from marshmallow import fields
from .. import db
from flask import current_app

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Float)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id', ondelete='CASCADE'),nullable=False)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id', ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    
    def __init__(self, test, mark):
        self.test = test
        self.mark = mark
    
    def __repr__(self):
        return '<Result {} {} {} >'.format(self.test.testcode, self.mark, self.rider.firstname)
    
    @staticmethod
    def load_from_file(filename):
        from . import Competition, Test, RankingList
        
        competition_id = filename.split('.')[0]
        competition = Competition.query.filter_by(isirank_id=competition_id).first()
        
        task = None
        if competition is not None:
            print("Task already started")
            task = competition.get_task_in_progress('import_competition')
        
        if task is not None:
            return task            
        else:
            file = open(current_app.config['ISIRANK_FILES'] + filename,"r",encoding="cp1252")

            contents = file.read()

            lines = contents.splitlines()

            if competition is None:
                competition = Competition(competition_id)

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