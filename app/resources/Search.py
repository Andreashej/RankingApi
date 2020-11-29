from flask_restful import Resource, request
from sqlalchemy import or_

from ..models import RankingList, Rider, Horse, Competition, RankingListSchema, RiderSchema, HorseSchema, CompetitionSchema

rankings_schema = RankingListSchema(many = True, exclude=('competitions',"tests",))
riders_schema = RiderSchema(many = True, exclude=('results',))
horses_schema = HorseSchema(many = True, exclude=('results',))
competitions_schema = CompetitionSchema(many = True, exclude=('include_in_ranking', 'tests', 'tasks'))

class SearchResource(Resource):

    def get(self):
        term = '%' + request.args.get('term', '').lower() + '%'

        rankings = RankingList.query.filter(or_(RankingList.listname.like(term), RankingList.shortname.like(term))).limit(10).all()
        riders = Rider.query.filter(Rider.fullname.like(term)).limit(10).all()
        horses = Horse.query.filter(or_(Horse.horse_name.like(term), Horse.feif_id.like(term))).limit(10).all()
        competitions = Competition.query.filter(Competition.name.like(term)).order_by(Competition.first_date).limit(10).all()

        results = rankings_schema.dump(rankings) + riders_schema.dump(riders) + horses_schema.dump(horses) + competitions_schema.dump(competitions)

        return {
            'status': 'OK',
            'data': results
        }

