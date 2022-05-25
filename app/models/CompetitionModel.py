from app.models.PersonModel import Person
from .. import db
from sqlalchemy.ext.hybrid import hybrid_property

from flask import current_app, render_template, g

from .TaskModel import Task

from .RestMixin import RestMixin

competitions_rankinglists = db.Table('competition_ranking_association',
    db.Column('competition_id', db.Integer, db.ForeignKey('competitions.id'), primary_key=True),
    db.Column('rankinglist_id', db.Integer, db.ForeignKey('rankinglists.id'), primary_key=True)
)

class Competition(db.Model, RestMixin):
    RESOURCE_NAME = 'competition'
    RESOURCE_NAME_PLURAL = 'competitions'

    EXCLUDE_FROM_JSON = ['_contact_person_id', '_state']
    INCLUDE_IN_JSON = ['contact_person_id', 'state', 'is_admin']

    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250))
    ext_id = db.Column('isirank_id', db.String(12), unique=True)
    first_date = db.Column(db.Date)
    last_date = db.Column(db.Date)
    country = db.Column(db.String(2), default='DK')
    _state = db.Column("state", db.String(12), default="PENDING") # { PENDING, NORMAL, BLOCKED, CANCELLED, UNLISTED }
    include_in_ranking = db.relationship('RankingList', secondary=competitions_rankinglists, lazy='dynamic', back_populates='competitions')
    tests = db.relationship("Test", backref="competition", lazy='dynamic', cascade='all,delete', order_by='Test.testcode')
    tasks = db.relationship("Task", backref="competition", lazy='dynamic')
    _contact_person_id = db.Column('contact_person_id', db.Integer, db.ForeignKey('persons.id'))
    contact_person = db.relationship("Person")
    screen_groups = db.relationship("ScreenGroup", lazy="dynamic")
    admin_users = db.relationship("CompetitionAccess", lazy="dynamic")

    def __init__(self, name='', startdate=None, enddate=None, isi_id = None, country='XX'):
        self.name = name
        self.first_date = startdate
        self.last_date = enddate
        self.country = country

        db.session.add(self)
        db.session.flush()

        self.ext_id = isi_id or self.create_id()
    
    def __repr__(self):
        return f'<Competition {self.name} from {self.first_date} to {self.last_date}>'

    @hybrid_property
    def isirank_id(self):
        return self.ext_id
    
    @isirank_id.setter
    def isirank_id(self, ext_id):
        self.ext_id = ext_id
    
    @hybrid_property
    def contact_person_id(self):
        return self._contact_person_id
    
    @contact_person_id.setter
    def contact_person_id(self, contact_person_id):
        contact_person = Person.query.get(contact_person_id)
        if contact_person.email == '':
            raise ValueError("Cannot assign a person without email address as contact.")
        
        self._contact_person_id = contact_person_id
    
    @contact_person_id.expression
    def contact_person_id(cls):
        return cls._contact_person_id

    @hybrid_property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, new_state):
        if self.state == 'PENDING' and new_state == 'NORMAL':
            self.notify_user_create()
        
        self._state = new_state

    @hybrid_property
    def tasks_in_progress(self):
        return self.get_tasks_in_progress()

    def launch_task(self, name, descripton, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, *args, **kwargs)

        task = Task(id=rq_job.get_id(), name=name, description=descripton, competition=self)
        db.session.add(task)

        return task

    def create_id(self):
        return f'{self.country}{self.last_date.year}{self.id:06}'
    
    def add_test(self, test):
        if test.test_name in [test.test_name for test in self.tests]:
            raise ValueError(f"Duplicate testcode {test.testcode} for competition")
            
        self.tests.append(test)

    def get_tasks_in_progress(self):
        return Task.query.filter_by(competition=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, competition=self, complete=False).first()
    
    def notify_user_create(self):
        if self.contact_person is None or not self.contact_person.email:
            return

        rq_job = current_app.task_queue.enqueue('app.tasks.send_mail',
            **{
                'subject': "Your competition was created",
                'sender': "noreply@icecompass.com",
                'recipients': [self.contact_person.email],
                'text_body': render_template("emails/competition_create.txt", competition=self),
                'html_body': render_template("emails/competition_create.html", competition=self),
            }
        )

        task = Task(
            id=rq_job.get_id(), 
            name='send_mail', 
            description=f'Sending user notification to {self.contact_person.email}: Competition id {self.id} created.', 
            competition=self
        )

        db.session.add(task)

        try:
            db.session.commit()
        except:
            db.session.rollback()

    @hybrid_property
    def is_admin(self):
        if not hasattr(g, 'profile') or g.profile is None:
            return False
        
        if g.profile.super_user:
            return True

        user = self.admin_users.filter_by(user_id=g.profile.id, competition_id=self.id).first()

        if user is not None:
            return True

        return False