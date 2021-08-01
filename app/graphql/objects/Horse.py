import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from ...models import Horse as HorseModel
from sqlalchemy import or_

class Horse(SQLAlchemyObjectType):
    class Meta:
        model = HorseModel
        interfaces = (relay.Node, )

class HorseQuery(graphene.ObjectType):
    horses = graphene.List(Horse, term=graphene.String())
    def resolve_horses(self, info, term=None):
        query = Horse.get_query(info)
        if term:
            query = query.filter(or_(
                HorseModel.horse_name.ilike(f"%{term}%"),
                HorseModel.feif_id.ilike(f"%{term}%")
            ))
        
        return query.all()

    horse = graphene.Field(Horse, id=graphene.Int(), feifid=graphene.String())
    def resolve_horse(self, info, id=None, feifid=None):
        query = Horse.get_query(info)

        if id:
            return query.get(id)
        
        if feifid:
            return query.filter(HorseModel.feif_id == feifid).first()