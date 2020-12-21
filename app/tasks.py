from datetime import date
import time
from rq import get_current_job, job
import sqlalchemy

from app import db, cache, create_app
from app.models import Task, Test, Result, Rider, Horse, Competition, RankingListTest, RankingResultsCache, RankingList, RiderAlias, TestCatalog
import datetime

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
            print(f"Processing line {i+1} of {lines}")
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

            rider = Rider.query.filter_by(fullname = fields[0]).first()
            rider = Rider.find_by_name(fields[0])
            if rider is None:
                rider = Rider.create_by_name(fields[0])
                try:
                    db.session.add(rider)
                except:
                    db.sesion.rollback()
            
            horse = Horse.query.filter_by(feif_id=fields[3]).first()

            if horse is None:
                horse = Horse(fields[3], fields[4])
                try:
                    db.session.add(horse)
                except:
                    db.session.rollback()
            
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

        db.session.commit()
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
        db.session.rollback()

def compute_ranking(test_id):
    try:
        test = RankingListTest.query.get(test_id)

        RankingResultsCache.query.filter_by(test_id = test.id).delete()

        try:
            db.session.commit()
        except:
            pass

        if test.grouping == 'rider':
            group = Rider.query.filter(Rider.count_results_for_ranking(test) >= test.included_marks).all()

        if test.grouping == 'horse':
            group = Horse.query.filter(Horse.count_results_for_ranking(test) >= test.included_marks).all()

        for i, g in enumerate(group):
            results = g.get_results_for_ranking(test)

            result = RankingResultsCache(results, test)
            try:
                db.session.add(result)
            except Exception as e:
                app.logger.error(e, exc_info=sys.exc_info())
                
            _set_task_progress(50 * i // len(group))

        try:
            db.session.commit()

            if test.order == 'desc':
                results = RankingResultsCache.query.filter_by(test_id = test.id).order_by(RankingResultsCache.mark.desc()).all()
            else:
                results = RankingResultsCache.query.filter_by(test_id = test.id).order_by(RankingResultsCache.mark.asc()).all()

            rank = 0
            prev_score = 0
            for result in results:
                if prev_score != result.mark:
                    rank += 1
                
                print(rank, result)
                result.rank = rank

                prev_score = result.mark

                _set_task_progress(50 + (50 * rank // len(results)))

            db.session.commit()
        except Exception as e:
            app.logger.error(e, exc_info=sys.exc_info())
        finally:
            _set_task_progress(100)
    except:
        _set_task_progress(100)
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())

def import_competitions(ranking_id, competitions):
    ranking = RankingList.query.get(ranking_id)
    try:
        total_lines = len(competitions)
        for i, c in enumerate(competitions):
            startdate = datetime.datetime.strptime(c['startdate'], '%Y-%m-%d')
            enddate = datetime.datetime.strptime(c['enddate'], '%Y-%m-%d')

            competition = Competition.query.filter_by(isirank_id = c["isirank_id"]).first()

            if competition is None:
                competition = Competition(c['competition_name'], startdate, enddate, c['isirank_id'])
                competition.include_in_ranking.append(ranking)

                try:
                    db.session.add(competition)
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(e, exc_info=sys.exc_info())
            else:
                if ranking not in competition.include_in_ranking:
                    competition.include_in_ranking.append(ranking)
            _set_task_progress(i / total_lines * 100)
        
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(e, exc_info=sys.exc_info())
        finally:
            _set_task_progress(100)

    except Exception as e:
        _set_task_progress(100)
        app.logger.error(e, exc_info=sys.exc_info())

def import_results(ranking_id, results):
    ranking = RankingList.query.get(ranking_id)
    try:
        total_lines = len(results)
        for i, r in enumerate(results):
            rider = Rider.find_by_name(r['rider'])

            if not rider:
                rider = Rider.create_by_name(r['rider'])
                db.session.add(rider)

            feif_id = 'IR0000000000' if r['horse'] == 'nn' else r['feif_id']
            horse = Horse.query.filter_by(feif_id = feif_id).first()

            if not horse:
                horse = Horse(feif_id, r['horse'])
                db.session.add(horse)

            competition = Competition.query.filter_by(isirank_id = r['competition_id']).first()

            if not competition:
                print (f"Competition {r['competition_id']} not found, skipping result")
                continue
                
            test = Test.query.filter_by(testcode=r['testcode'], competition=competition).first()

            if not test:
                try:
                    testdef = TestCatalog.get_by_testcode(r['testcode'])
                    test = Test(r['testcode'])
                    test.competition = competition
                    test.rounding_precision = testdef.rounding_precision
                    test.order = testdef.order
                    test.mark_type = testdef.mark_type
                except Exception as e:
                    app.logger.error(e, exc_info=sys.exc_info())
                    print(e)
                    continue

            try:
                result = test.add_result(rider, horse, r['mark'], skip_check = True if horse.horse_name == 'nn' else False)
                db.session.add(result)
                print(result)
            except Exception as e:
                app.logger.error(e, exc_info=sys.exc_info())
            finally:
                _set_task_progress(i / total_lines * 100)

        db.session.commit()
    except Exception as e:
        app.logger.error(e, exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)

def import_aliases(aliases):
    items = len(aliases)
    try:
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
    except Exception as e:
        db.session.rollback()
        app.logger.error(e, exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)

