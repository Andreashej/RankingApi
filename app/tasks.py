from rq import get_current_job

from . import db, create_app
from .models import Task, Test, Result, Rider, Horse, Competition, RankingListTest, RankingResults, RankingList, RiderAlias, TestCatalog
import datetime

import requests

import sys

app = create_app()
app.app_context().push()

def _set_task_progress(progress, error = False):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())

        if not task.started_at:
            task.started_at = datetime.datetime.utcnow()

        if progress >= 100:
            task.completed_at = datetime.datetime.utcnow()
            task.complete = True
            task.error = error
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e, exc_info=sys.exc_info())
    
def import_competition(competition_id, lines):
    try:
        _set_task_progress(0)
        competition = Competition.query.get(competition_id)
        results = []

        total_lines = len(lines)
        i = 0

        for line in lines:
            print(f"Processing line {i+1} of {total_lines}")
            if line == '[END]':
                _set_task_progress(100)
                print(f"Finished processing competition {competition.isirank_id}")
                break

            fields = line.split('\t')
            
            test = Test.query.filter_by(testcode=fields[1], competition=competition).first()

            if not test:
                # Test is not ranked - do not process results
                continue
                # test = Test.create_from_catalog(fields[1])
                # competition.tests.append(test)

            rider = Rider.query.filter_by(fullname = fields[0]).first()
            rider = Rider.find_by_name(fields[0])

            if not rider:
                rider = Rider.create_by_name(fields[0])
                try:
                    db.session.add(rider)
                except:
                    db.sesion.rollback()

            
            feif_id = 'XX0000000000' if (fields[4] == 'nn' or fields[4] == 'NULL') else fields[3]
            horse_name = 'nn' if (fields[4] == 'nn' or fields[4] == 'NULL' or fields[4] == 'XX0000000000') else fields[4]

            horse = Horse.query.filter_by(feif_id=feif_id).first()


            if not horse:
                horse = Horse(feif_id, horse_name)
                try:
                    db.session.add(horse)
                except:
                    db.session.rollback()
            
            result = Result(test, fields[2])
            result.horse = horse
            result.rider = rider

            try:
                db.session.add(result)
            except Exception as e:
                db.session.rollback()
                app.logger.error(e, exc_info=sys.exc_info())

            results.append(result)

            i += 1
            _set_task_progress(100 * i // total_lines)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.error(e, exc_info=sys.exc_info())
    except:
        db.session.rollback()
        _set_task_progress(100, True)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

def flush_ranking(ranking_id):
    try:
        _set_task_progress(0)
        ranking = RankingListTest.query.get(ranking_id)

        RankingResults.query.filter_by(test_id = ranking.id).delete()

        results = ranking.valid_competition_results

        for i, result in enumerate(results):
            ranking.register_result(result)
            _set_task_progress(100 * i // len(results))
        
        ranking.compute_rank()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e, exc_info=sys.exc_info())
        finally:
            _set_task_progress(100)
        
    except:
        _set_task_progress(100, True)
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())

def recompute_ranking(ranking_id):
    try:
        _set_task_progress(0)
        ranking = RankingListTest.query.get(ranking_id)

        ranking_results = RankingResults.query.filter_by(test_id = ranking.id).all()

        for i, result in enumerate(ranking_results):
            result.calculate_mark()

            _set_task_progress(i * 100 // len(ranking_results))
        
        ranking.compute_rank()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e, exc_info=sys.exc_info())
        finally:
            _set_task_progress(100)
        
    except:
        _set_task_progress(100, True)
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())

def import_competitions(ranking_id, competitions):
    try:
        _set_task_progress(0)

        ranking = RankingList.query.get(ranking_id)
        total_lines = len(competitions)
        for i, c in enumerate(competitions):
            startdate = datetime.datetime.strptime(c['startdate'], '%d-%m-%Y')
            enddate = datetime.datetime.strptime(c['enddate'], '%d-%m-%Y')

            competition = Competition.query.filter_by(isirank_id = c["isirank_id"]).first()

            if competition is None:
                competition = Competition(c['competition_name'], startdate, enddate, c['isirank_id'])

                if c['status'] == 'not listed any longer':
                    competition.state = 'UNLISTED'
                elif c['status'] == 'cancelled':
                    competition.state = 'CANCELLED'
                elif c['status'] == 'blocked':
                    competition.state = 'BLOCKED'
                elif c['status'] == 'to be ignored':
                    competition.state = 'IGNORE'

                try:
                    db.session.add(competition)
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(e, exc_info=sys.exc_info())

            if ranking not in competition.include_in_ranking:
                competition.include_in_ranking.append(ranking)

            _set_task_progress(i / total_lines * 100)
        
        try:
            db.session.commit()
            _set_task_progress(100)
        except Exception as e:
            db.session.rollback()
            app.logger.error(e, exc_info=sys.exc_info())
            _set_task_progress(100, True)

    except Exception as e:
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

def import_aliases(aliases):
    try:
        _set_task_progress(0)

        items = len(aliases)
        for i, alias in enumerate(aliases):
            rider = Rider.query.filter_by(fullname = alias['real_name']).first()

            if not rider:
                (fname, sep, lname) = alias['real_name'].rpartition(' ')
                rider = Rider(fname, lname)
                db.session.add(rider)

            a = RiderAlias.query.filter_by(alias = alias['alias']).first()
            if not a:
                a = RiderAlias(alias['alias'])

                rider.add_alias(a)
                
            else:
                print(f"Alias {alias['alias']} already exists")
            
            _set_task_progress(i / items * 100)

            db.session.commit()
            print(rider)
            
        _set_task_progress(100)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

def horse_lookup(horses = []):
    try:
        _set_task_progress(0)
        horses = Horse.query.filter(Horse.id.in_(horses)).all()

        for i, horse in enumerate(horses):
            horse.wf_lookup()
            
            progress = i / len(horses) * 100
            _set_task_progress(progress)
        
        _set_task_progress(100)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

    
if __name__ == '__main__':
    recompute_ranking(1)