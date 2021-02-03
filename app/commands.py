from flask import current_app as app
from . import db
import click
from .models import Horse, Task

# app = create_app()
# app.app_context().push()

@app.cli.command()
def lookup_horse():
    """Lookup a horse"""

    horses = Horse.query.filter_by(last_lookup=None).limit(10).with_entities('id').all()
    
    rq_job = app.task_queue.enqueue('app.tasks.horse_lookup', [id for id, in horses])

    task = Task(id=rq_job.get_id(), name='horse_lookup', description=f"Looking up {len(horses)} in WF");
    try:
        db.session.add(task)
        db.session.commit()
    except:
        db.session.rollback()