from flask_restful import Resource, reqparse
from app import db
from app import auth

from app.models import Horse, Result, Competition, Test, HorseSchema, ResultSchema, TestSchema

horses_schema = HorseSchema(many=True, exclude=("results",))
horse_schema = HorseSchema(exclude=("results",))

results_schema = ResultSchema(many=True, exclude=("horse",))
result_schema = ResultSchema(exclude=("horse",))

tests_schema = TestSchema(many=True, exclude=("results",))

class HorsesResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('feif_id', type=str, required=True, location='json')
    
    def get(self):
        horses = Horse.query.all()
        horses = horses_schema.dump(horses)

        return {'status': 'OK', 'data': horses}, 200
    
    @auth.login_required
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

    @auth.login_required
    def delete(self):
        try:
            Horse.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204
    
class HorseResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('feif_id', type=str, required=True, location='json')
    
    def get(self,horse_id):
        horse = Horse.query.get(horse_id)

        if not horse:
            return {'status': 'NOT FOUND'},404

        horse = horse_schema.dump(horse)
        
        return {'status': 'OK', 'data': horse},200

class HorseResultResource(Resource):
    def __init__(self):
        pass

    def get(self, horse_id, testcode):
        results_for_test = Result.query.filter_by(horse_id=horse_id).join(Result.test).filter(Test.testcode == testcode).join(Test.competition).order_by(Competition.last_date.desc()).all()
        best = Result.query.filter_by(horse_id = horse_id).join(Result.test).filter(Test.testcode == testcode).order_by(Result.mark.desc()).limit(1).first()

        if (len(results_for_test) == 0):
            return {'status': 'NOT FOUND', 'message': 'The horse has no results in this test.'}, 404
        
        return {
            'status': 'OK',
            'data': {
                'history': results_schema.dump(results_for_test),
                'best': result_schema.dump(best)
            }
        }