import graphene
from graphene import relay
from .objects.RankingList import RankingListQuery
from .objects.RankingListTest import RankingListTestQuery
from .objects.Horse import HorseQuery
from .objects.Rider import RiderQuery

class Query(
    RankingListQuery, 
    RankingListTestQuery, 
    HorseQuery,
    RiderQuery,
    graphene.ObjectType
):
    node = relay.Node.Field()