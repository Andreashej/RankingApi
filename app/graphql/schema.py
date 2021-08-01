from graphene import Schema
from .query import Query

schema = Schema(query=Query)