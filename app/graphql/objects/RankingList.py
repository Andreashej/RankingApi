from flask_sqlalchemy import SQLAlchemy
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from ...models import RankingList as RankingListModel, RankingListTest as RankingListTestModel
from .RankingListTest import RankingListTest

class RankingList(SQLAlchemyObjectType):
    class Meta:
        model = RankingListModel
        interfaces = (relay.Node, )
    
    tests = graphene.List(lambda: RankingListTest, testcode=graphene.String())

    def resolve_tests(self, info, testcode=None):
        query = RankingListTest.get_query(info)
        query = query.filter(RankingListTestModel.rankinglist_id == self.id)

        if testcode:
            query = query.filter(RankingListTestModel.testcode == testcode)
        
        return query.all()

class RankingListQuery(graphene.ObjectType):
    rankinglists = graphene.List(RankingList, shortname=graphene.String())

    def resolve_rankinglists(self, info, shortname=None):
        query = RankingList.get_query(info)

        if shortname:
            query = query.filter(RankingListModel.shortname == shortname)
        
        return query.all()