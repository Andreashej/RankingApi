import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from ...models import RankingResults as RankingResultsModel
from .Result import Result
from ...models import ResultModel

class RankingResults(SQLAlchemyObjectType):
    class Meta:
        model = RankingResultsModel
        interfaces = (relay.Node, )

    marks = graphene.List(Result)

    # def resolve_marks(self, info):
    #     query = RankingResults.get_results_query()
    #     return query.all()