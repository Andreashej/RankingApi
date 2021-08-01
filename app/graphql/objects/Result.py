import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from ...models import Result as ResultModel
from .Rider import Rider
from .Horse import Horse

class Result(SQLAlchemyObjectType):
    class Meta:
        model = ResultModel
        interfaces = (relay.Node, )
    
    rider = graphene.Field(Rider)
    horse = graphene.Field(Horse)