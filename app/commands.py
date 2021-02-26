from flask import current_app as app
from . import db
import click
from .models import Horse, Task

# app = create_app()
# app.app_context().push()

@app.cli.command()
@click.option('--limit')
def lookup_horse(limit = 500):
    """Lookup a horse"""

    horses = Horse.query.filter_by(last_lookup=None).limit(limit).with_entities('id').all()
    
    rq_job = app.task_queue.enqueue('app.tasks.horse_lookup', [id for id, in horses])

    task = Task(id=rq_job.get_id(), name='horse_lookup', description=f"Look up {len(horses)} horses in WF");
    try:
        db.session.add(task)
        db.session.commit()
    except:
        db.session.rollback()