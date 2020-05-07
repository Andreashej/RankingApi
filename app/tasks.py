import time
from rq import get_current_job

from app import db, cache, create_app
from app.models import Task, Test, Result, Rider, Horse, Competition, RankingListTest

import sys

app = create_app()
app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())

        if progress >= 100:
            task.complete = True
        
        db.session.commit()
    
def import_competition(competition_id, lines):
    try:
        competition = Competition.query.get(competition_id)
        _set_task_progress(0)
        results = []

        total_lines = len(lines)
        i = 0

        for line in lines:
            if line == '[END]':
                _set_task_progress(100)
                cache.delete_memoized(RankingListTest.get_ranking)
                break

            fields = line.split('\t')
            
            test = Test.query.filter_by(testcode=fields[1], competition=competition).first()
            if test is None:
                test = Test(fields[1])
                competition.tests.append(test)

            if not test.testcode:
                test.testcode = fields[1]

            (fname, sep, lname) = fields[0].rpartition(' ')
            rider = Rider.query.filter_by(fullname = fields[0]).first()
            if rider is None:
                rider = Rider(fname, lname)
                try:
                    db.session.add(rider)
                except:
                    pass
            
            horse = Horse.query.filter_by(feif_id=fields[3]).first()

            if horse is None:
                horse = Horse(fields[3], fields[4])
                try:
                    db.session.add(horse)
                except:
                    pass
            
            result = Result(test, fields[2])
            result.horse = horse
            result.rider = rider

            try:
                db.session.add(result)
            except:
                pass

            results.append(result)

            i += 1
            _set_task_progress(100 * i // total_lines)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
