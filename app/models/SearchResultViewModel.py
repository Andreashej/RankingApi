from app.models import Competition, Person, Horse, RankingList
from app import db
from app.models.RestMixin import RestMixin
from sqlalchemy.ext.hybrid import hybrid_property

# SearchResultView = db.Table("search_results",
    
# )

class SearchResult(db.Model, RestMixin):
    __tablename__ = 'search_results'
    __table_args__ = {'info': dict(is_view=True)}

    search_string = db.Column("search_string", db.String)
    id = db.Column("id", db.Integer, primary_key=True)
    type = db.Column("type", primary_key=True)

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

    def include_object(object, name, type_, reflected, compare_to):
        if (
            type_ == "table" and name == "search_results"
        ):
            return False
        else:
            return True