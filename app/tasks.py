from rq import get_current_job
from sentry_sdk import capture_exception

from app import db, create_app
from app.models import Task, Test, Result, Person, Horse, Competition, RankingListTest, RankingResults, RankingList, PersonAlias, JudgeMark
import datetime
from flask_mail import Message
from app import mail
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_

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

            if task.job is not None:
                task.job.last_run_at = datetime.datetime.utcnow()

        if progress >= 100:
            task.completed_at = datetime.datetime.utcnow()
            task.complete = True
            task.error = error

            if task.job is not None:
                if error:
                    task.job._stop()
                else:
                    task.job.queue_next()
 
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

            rider = Person.query.filter_by(fullname = fields[0]).first()
            rider = Person.find_by_name(fields[0])

            if not rider:
                rider = Person.create_by_name(fields[0])
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
            print(result)
            ranking.register_result(result)
            _set_task_progress(100 * i // len(results))

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

        # results = RankingResults.query.filter_by(test_id = ranking.id).filter(RankingResults.mark.isnot(None)).all()
        results = RankingResults.query.filter_by(test_id = ranking.id).all()

        for i, result in enumerate(results):
            print(result)
            result.calculate_mark()
            _set_task_progress(100 * i // len(results))

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
            rider = Person.query.filter_by(fullname = alias['real_name']).first()

            if not rider:
                (fname, sep, lname) = alias['real_name'].rpartition(' ')
                rider = Person(fname, lname)
                db.session.add(rider)

            a = PersonAlias.query.filter_by(alias = alias['alias']).first()
            if not a:
                a = PersonAlias(alias['alias'])

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

def send_mail(subject, sender , recipients , text_body , html_body):
    try:
        _set_task_progress(0)
        subject_prefix = "[DEV] " if app.config["DEBUG"] else ""
        msg = Message(subject_prefix + subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
        _set_task_progress(100)
    except Exception as e:
        print (e)
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

def recompute_all():
    try:
        _set_task_progress(0)

        rankings = RankingListTest.query.all()

        for i, ranking in enumerate(rankings):
            ranking.recompute()
            _set_task_progress(i / len(rankings) * 100)

        _set_task_progress(100)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

def set_test_ranking_link():
    try:
        _set_task_progress(0)

        competitions = Competition.query.filter(Competition.first_date < datetime.datetime(2021, 12, 31)).all()

        for i, competition in enumerate(competitions):
            for test in competition.tests:
                test.include_in_ranking = competition.include_in_ranking.all()
                            
            _set_task_progress(i / len(competitions) * 100)

        db.session.commit()

        _set_task_progress(100)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

def set_competition_ranking_link():
    try:
        _set_task_progress(0)

        tests = Test.query.filter(Test.include_in_ranking.any()).all()
            
        for i, test in enumerate(tests):
            for ranking in test.include_in_ranking:
                if ranking in test.competition.include_in_ranking.all():
                    continue
                
                test.competition.include_in_ranking.append(ranking)

            _set_task_progress(i / len(tests) * 100)

        db.session.commit()
        _set_task_progress(100)
    except Exception as e:
        db.session.rollback()
        app.logger.error(e, exc_info=sys.exc_info())
        _set_task_progress(100, True)

def test_scheduler():
    try:
        print("Task started!")
        for i in range(0, 11):
            _set_task_progress(i * 10)
    except Exception:
        _set_task_progress(100, True)

def create_results_from_icetest(test_id, data):
    try:
        _set_task_progress(0)
        test = Test.query.get(test_id)

        for i, result_raw in enumerate(data):
            result = test.add_icetest_result(result_raw)
            
            print(f"Result saved {result}")
            _set_task_progress(i * len(data))

        db.session.commit()
        _set_task_progress(100)
    except Exception as e:
        raise e
        capture_exception(e)
        _set_task_progress(100, True)