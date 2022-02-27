from flask import current_app as app
from . import db
import click
from .models import Horse, Task, RankingListTest
from app.events import icetest

# app = create_app()
# app.app_context().push()

@app.cli.command()
@click.option('--limit')
def lookup_horse(limit = 500):
    """Lookup a horse"""

    horses = Horse.query.filter_by(last_lookup=None).filter(Horse.lookup_error.isnot(True)).limit(limit).with_entities('id').all()
    
    rq_job = app.task_queue.enqueue('app.tasks.horse_lookup', [id for id, in horses])

    task = Task(id=rq_job.get_id(), name='horse_lookup', description=f"Look up {len(horses)} horses in WF")
    try:
        db.session.add(task)
        db.session.commit()
    except:
        db.session.rollback()

@app.cli.command()
def flush_rankings():
    """Recompute all rankings"""

    test = RankingListTest.query.first()

    test.launch_task('flush_ranking', 'Flushing {} ranking for {}'.format(test.testcode, test.rankinglist.shortname))
    # for test in tests:

@app.cli.command()
def recompute_rankings():
    test = RankingListTest.query.first()

    test.launch_task('recompute_ranking', 'Recalculating {} ranking for {}'.format(test.testcode, test.rankinglist.shortname))

@app.cli.command()
def icetest_listener():
    icetest.run()
