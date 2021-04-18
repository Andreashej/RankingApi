from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from requests import NullHandler
from .. import db

from ..models import Horse, HorseSchema, ResultSchema, TestSchema, RankingListResultSchema

horses_schema = HorseSchema(many=True, exclude=("results","testlist",))
horse_schema = HorseSchema(exclude=("results",))

results_schema = ResultSchema(many=True, exclude=("horse",))
result_schema = ResultSchema(exclude=("horse",))

tests_schema = TestSchema(many=True, exclude=("results",))
rankinglist_result_schema = RankingListResultSchema(only=("rank","test.rankinglist",))

class HorsesResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('feif_id', type=str, required=True, location='json')
    
    def get(self):
        try:
            horses = Horse.filter().all()
        except Exception as e:
            return { 'message': str(e) }, 500

        horses = horses_schema.dump(horses)

        return {'status': 'OK', 'data': horses}, 200
    
    @jwt_required
    def post(self):
        args = self.reqparse.parse_args()

        horse = Horse(
            feif_id=args['feif_id'],
            name=args['name']
        )

        try:
            db.session.add(horse)
            db.session.commit()
        except Exception as inst:
            print (inst.args)
            return {'status': 'ERROR'}, 500
        
        horse = horse_schema.dump(horse)

        return {'status': 'OK', 'data': horse},200

    @jwt_required
    def delete(self):
        try:
            Horse.filter().delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204
    
class HorseResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=False, location='json')
        self.reqparse.add_argument('feif_id', type=str, required=False, location='json')
        self.reqparse.add_argument('force_update', type=bool, required=False, location='json')
        self.reqparse.add_argument('ignore_wf_error', type=bool, required=False, location='json')
    
    def get(self,horse_id):
        horse = Horse.query.get(horse_id)

        if not horse:
            return {'status': 'NOT FOUND'},404

        horse = horse_schema.dump(horse)
        
        return {'status': 'OK', 'data': horse},200
    
    @jwt_required
    def patch(self, horse_id):
        horse = Horse.query.get(horse_id)

        if not horse:
            return { 'message': f'Horse with id {horse_id} was not found' }, 404

        args = self.reqparse.parse_args()

        if args['name'] is not None:
            horse.horse_name = args['name']
        
        if args['feif_id'] is not None:
            horse.feif_id = args['feif_id']
        
        if args['force_update']:
            horse.wf_lookup(True)
        
        if args['ignore_wf_error']:
            horse.lookup_error = False
        
        horse.save()

        return { 'data': horse_schema.dump(horse) }
        


class HorseResultResource(Resource):
    def __init__(self):
        pass

    def get(self, horse_id, testcode):
        horse = Horse.query.get(horse_id)

        # results_for_test = Result.query.filter_by(horse_id=horse_id).join(Result.test).filter(Test.testcode == testcode).join(Test.competition).order_by(Competition.last_date.desc()).all()
        results_for_test = horse.get_results(testcode)
        # best = Result.query.filter_by(horse_id = horse_id).join(Result.test).filter(Test.testcode == testcode).order_by(Result.mark.desc()).limit(1).first()
        best = horse.get_best_result(testcode)
        best_rank = horse.get_best_rank(testcode)

        if (len(results_for_test) == 0):
            return {'status': 'NOT FOUND', 'message': 'The horse has no results in this test.'}, 404
        
        return {
            'status': 'OK',
            'data': {
                'history': results_schema.dump(results_for_test),
                'best': result_schema.dump(best),
                'best_rank': rankinglist_result_schema.dump(best_rank)
            }
        }