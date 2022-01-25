from app.models import Competition, Person, Horse, RankingList
from app import db
from app.models.RestMixin import RestMixin
from sqlalchemy.ext.hybrid import hybrid_property

SearchResultView = db.Table("search_results",
    db.Column("search_string", db.String),
    db.Column("id", db.Integer, primary_key=True),
    db.Column("type", primary_key=True)
)

class SearchResult(db.Model, RestMixin):
    __table__ = SearchResultView

    @hybrid_property
    def competition(self):
        if self.type == 'Competition':
            return Competition.query.get(self.id)
        
    @hybrid_property
    def person(self):
        if self.type == 'Person':
            return Person.query.get(self.id)

    @hybrid_property
    def horse(self):
        if self.type == 'Horse':
            return Horse.query.get(self.id)

    @hybrid_property
    def ranking_list(self):
        if self.type == 'RankingList':
            return RankingList.query.get(self.id)