import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from ...models import RankingResultsCache as RankingResultsCacheModel
from .Result import Result
from ...models import ResultModel

class RankingResultsCache(SQLAlchemyObjectType):
    class Meta:
        model = RankingResultsCacheModel
        interfaces = (relay.Node, )

    marks = graphene.List(Result, page=graphene.Int(), pageLength=graphene.Int())

    def resolve_marks(self, info, page = 1, pageLength = 10):
        return ResultModel.marks.offset(pageLength).limit(page).all()