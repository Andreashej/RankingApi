import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from ...models import Rider as RiderModel

class Rider(SQLAlchemyObjectType):
    class Meta:
        model = RiderModel
        interfaces = (relay.Node, )

class RiderQuery(graphene.ObjectType):
    riders = graphene.List(Rider, term=graphene.String())
    def resolve_riders(self, info, term=None):
        query = Rider.get_query(info)
        if term:
            query = query.filter(RiderModel.fullname.ilike(f"%{term}%"))
        
        return query.all()

    rider = graphene.Field(Rider, id=graphene.Int())
    def resolve_rider(self, info, id=None):
        query = Rider.get_query(info)

        if id:
            return query.get(id)