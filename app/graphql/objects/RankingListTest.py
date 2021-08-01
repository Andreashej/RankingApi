import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import RankingListTest as RankingListTestModel, RankingResultsCache as RankingResultsCacheModel
from .RankingResultsCache import RankingResultsCache

class RankingListTest(SQLAlchemyObjectType):
    class Meta:
        model = RankingListTestModel
        interfaces = (relay.Node, )

    results = graphene.List(RankingResultsCache)

    def resolve_results(self, info):
        return RankingResultsCacheModel.get_results_query(self).all()

class RankingListTestInput(graphene.InputObjectType):
    testcode = graphene.String()
    included_marks = graphene.Int()
    order = graphene.String()
    grouping = graphene.String()
    min_mark = graphene.Float()
    rounding_precision = graphene.Int()
    mark_type = graphene.String()

class RankingListTestQuery(graphene.ObjectType):
    rankinglist_tests = graphene.List(RankingListTest)

    def resolve_rankinglist_tests(self, info):
        query = RankingListTest.get_query(info)

        return query.all()