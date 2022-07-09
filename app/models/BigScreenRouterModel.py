from app import db
from app.models.RestMixin import RestMixin
from sqlalchemy.ext.hybrid import hybrid_property

test_routes = db.Table('test_bigscreenroutes',
    db.Column('route_id', db.Integer, db.ForeignKey('bigscreen_routes.id'), primary_key=True),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'), primary_key=True)
)

# class TemplateRoute(db.Model, RestMixin):
#     __tablename__ = 'bigscreen_template_routes'
#     route_id = db.Column(db.Integer, db.ForeignKey('bigscreen_routes.id'), primary_key=True)
#     template_name = db.Column(db.String(50), primary_key=True)

#     route = db.relationship('BigScreenRoute', back_populates='templates')


class BigScreenRoute(db.Model, RestMixin):
    RESOURCE_NAME = 'bigscreen_route'
    RESOURCE_NAME_PLURAL = 'bigscreen_routes'

    EXCLUDE_FROM_JSON = ['_templates']
    INCLUDE_IN_JSON = ['templates']

    __tablename__ = 'bigscreen_routes'

    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer, default=100)
    screen_group_id = db.Column(db.Integer, db.ForeignKey('screengroups.id'))
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'))
    _templates = db.Column('templates', db.String(255))

    screen_group = db.relationship('ScreenGroup', back_populates='routes')
    tests = db.relationship('Test', secondary=test_routes, lazy='dynamic')
    # templates = db.relationship('TemplateRoute', back_populates='route', lazy='dynamic', cascade="all, delete")
    competition = db.relationship('Competition', back_populates='bigscreen_routes')

    @hybrid_property
    def templates(self):
        if self._templates is None:
            return []

        return self._templates.split(',')
    
    @templates.setter
    def templates(self, new_value):
        if new_value is None:
            self._templates = None
            return

        self._templates = ','.join(new_value)
    
    @templates.expression
    def templates(cls):
        return cls._templates