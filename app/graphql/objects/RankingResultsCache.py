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

    marks = graphene.List(Result)

    # def resolve_marks(self, info):
    #     query = RankingResultsCache.get_results_query()
    #     return query.all()